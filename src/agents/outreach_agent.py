"""
Outreach Agent - Handles communications, scheduling, and follow-ups with wedding planners
"""
import re
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from langchain_openai import ChatOpenAI

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.database.airtable_schema import CommunicationRecord, CommunicationStatus, PlannerStatus
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger, log_agent_action, log_api_call, log_human_gate

logger = setup_logger("outreach_agent")

@dataclass
class OutreachCampaign:
    """Configuration for an outreach campaign"""
    name: str
    template_name: str
    target_status: str  # Which planner status to target
    communication_type: str  # email or sms
    batch_size: int = 5
    delay_between_batches: int = 300  # 5 minutes
    follow_up_delay_hours: int = 48
    max_follow_ups: int = 2

@dataclass
class MessageTemplate:
    """Template for outreach messages"""
    name: str
    subject: Optional[str] = None
    content: str = ""
    personalization_fields: List[str] = None
    communication_type: str = "email"
    
    def __post_init__(self):
        if self.personalization_fields is None:
            self.personalization_fields = []

class OutreachAgent:
    """Agent responsible for outreach communications and scheduling"""
    
    def __init__(self):
        self.creds_manager = CredentialsManager()
        self.airtable = AirtableClient()
        self._setup_clients()
        self._setup_templates()
        self._setup_compliance()
        
    def _setup_clients(self):
        """Setup communication API clients"""
        credentials = self.creds_manager.decrypt_credentials()
        
        # Twilio for SMS
        self.twilio_client = TwilioClient(
            credentials.get("TWILIO_ACCOUNT_SID"),
            credentials.get("TWILIO_AUTH_TOKEN")
        )
        
        # SendGrid for email
        self.sendgrid_client = SendGridAPIClient(
            api_key=credentials.get("SENDGRID_API_KEY")
        )
        
        # OpenAI for personalization
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=credentials.get("OPENAI_API_KEY"),
            temperature=0.3
        )
        
        logger.info("Outreach agent clients initialized")
    
    def _setup_templates(self):
        """Setup message templates"""
        self.templates = {
            "initial_email": MessageTemplate(
                name="initial_email",
                subject="Wedding Planner Needed - Authentic Chinese Banquet with Modern Twists (January 2026)",
                content=self._load_template_content("initial_email"),
                personalization_fields=["name", "business_name", "specializations", "location"],
                communication_type="email"
            ),
            "follow_up_email": MessageTemplate(
                name="follow_up_email", 
                subject="Following up - Chinese Wedding Planner Search (January 2026)",
                content=self._load_template_content("follow_up_email"),
                personalization_fields=["name", "business_name"],
                communication_type="email"
            ),
            "urgent_email": MessageTemplate(
                name="urgent_email",
                subject="URGENT: Chinese Wedding Planner Needed - Quick Response Appreciated",
                content=self._load_template_content("urgent_email"),
                personalization_fields=["name", "business_name"],
                communication_type="email"
            ),
            "sms_intro": MessageTemplate(
                name="sms_intro",
                content=self._load_template_content("sms_intro"),
                personalization_fields=["name"],
                communication_type="sms"
            ),
            "call_scheduling": MessageTemplate(
                name="call_scheduling",
                subject="Great to hear from you! Let's schedule a quick call",
                content=self._load_template_content("call_scheduling"),
                personalization_fields=["name", "availability"],
                communication_type="email"
            )
        }
    
    def _setup_compliance(self):
        """Setup compliance requirements"""
        self.sender_info = {
            "from_email": "jason@cawedding.com",  # Should be configured
            "from_name": "Jason & Suzie",
            "reply_to": "jason@cawedding.com",
            "phone_number": "+1234567890"  # Should be configured
        }
        
        self.compliance_footer = """
        
---
This is an AI-assisted inquiry on behalf of Jason & Suzie.
Reply directly to this email or call (XXX) XXX-XXXX to schedule.

Unsubscribe: Reply with 'UNSUBSCRIBE'
Address: [Your Address], Orange County, CA
"""
    
    def run_outreach_campaign(self, campaign: OutreachCampaign) -> Dict[str, Any]:
        """Run a complete outreach campaign"""
        logger.info(f"Starting outreach campaign: {campaign.name}")
        
        try:
            # Get target planners
            target_planners = self.airtable.get_planners_by_status(campaign.target_status)
            
            if not target_planners:
                logger.warning(f"No planners found with status: {campaign.target_status}")
                return {"sent": 0, "failed": 0, "planners_contacted": []}
            
            logger.info(f"Found {len(target_planners)} planners for outreach")
            
            # Process in batches for human approval
            results = {"sent": 0, "failed": 0, "planners_contacted": []}
            
            for i in range(0, len(target_planners), campaign.batch_size):
                batch = target_planners[i:i + campaign.batch_size]
                
                # Generate messages for batch
                batch_messages = self._generate_batch_messages(batch, campaign)
                
                # Human approval gate
                if not self._get_batch_approval(batch_messages, campaign):
                    logger.warning(f"Batch {i//campaign.batch_size + 1} not approved")
                    continue
                
                # Send batch
                batch_results = self._send_message_batch(batch_messages, campaign)
                
                # Update results
                results["sent"] += batch_results["sent"]
                results["failed"] += batch_results["failed"]
                results["planners_contacted"].extend(batch_results["planners_contacted"])
                
                # Delay between batches
                if i + campaign.batch_size < len(target_planners):
                    logger.info(f"Waiting {campaign.delay_between_batches}s before next batch")
                    time.sleep(campaign.delay_between_batches)
            
            log_agent_action(
                logger, "outreach_agent", "campaign_completed",
                {"campaign": campaign.name, "sent": results["sent"], "failed": results["failed"]}
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Outreach campaign failed: {e}")
            raise
    
    def run_follow_up_cycle(self) -> Dict[str, Any]:
        """Run follow-up cycle for unresponsive planners"""
        logger.info("Starting follow-up cycle")
        
        try:
            # Find communications needing follow-up
            cutoff_time = datetime.now() - timedelta(hours=48)
            
            # Get all sent communications without responses
            all_communications = self.airtable.communications_table.all()
            
            follow_ups_needed = []
            for comm in all_communications:
                fields = comm["fields"]
                
                # Check if follow-up is needed
                if (fields.get("status") == "sent" and
                    fields.get("follow_up_required", False) and
                    fields.get("follow_up_count", 0) < 2):
                    
                    sent_date = fields.get("sent_date")
                    if sent_date:
                        sent_datetime = datetime.fromisoformat(sent_date)
                        if sent_datetime < cutoff_time:
                            follow_ups_needed.append(comm)
            
            logger.info(f"Found {len(follow_ups_needed)} communications needing follow-up")
            
            results = {"sent": 0, "failed": 0}
            
            for comm in follow_ups_needed:
                try:
                    # Get planner info
                    planner_id = comm["fields"]["planner"][0]
                    planner = self.airtable.get_planner(planner_id)
                    
                    if not planner:
                        continue
                    
                    # Generate follow-up message
                    follow_up_count = comm["fields"].get("follow_up_count", 0)
                    
                    if follow_up_count == 0:
                        template_name = "follow_up_email"
                    else:
                        template_name = "urgent_email"
                    
                    message = self._generate_personalized_message(planner, template_name)
                    
                    # Send follow-up
                    success = self._send_single_message(planner, message, "email")
                    
                    if success:
                        # Update original communication
                        self.airtable.update_communication(comm["id"], {
                            "follow_up_count": follow_up_count + 1,
                            "follow_up_date": datetime.now().isoformat()
                        })
                        results["sent"] += 1
                    else:
                        results["failed"] += 1
                
                except Exception as e:
                    logger.error(f"Follow-up failed for communication {comm['id']}: {e}")
                    results["failed"] += 1
                
                # Rate limiting
                time.sleep(5)
            
            log_agent_action(
                logger, "outreach_agent", "follow_up_cycle_completed",
                {"sent": results["sent"], "failed": results["failed"]}
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Follow-up cycle failed: {e}")
            raise
    
    def process_responses(self) -> Dict[str, Any]:
        """Process incoming responses and update database"""
        logger.info("Processing responses")
        
        # This would integrate with email webhook/polling and SMS webhooks
        # For now, return empty results as this requires external integration
        
        results = {"processed": 0, "scheduled": 0, "interested": 0}
        
        log_agent_action(
            logger, "outreach_agent", "responses_processed",
            results
        )
        
        return results
    
    def _generate_batch_messages(self, planners: List[Dict], campaign: OutreachCampaign) -> List[Dict[str, Any]]:
        """Generate personalized messages for a batch of planners"""
        messages = []
        
        for planner in planners:
            try:
                message = self._generate_personalized_message(planner, campaign.template_name)
                messages.append({
                    "planner": planner,
                    "message": message,
                    "communication_type": campaign.communication_type
                })
            except Exception as e:
                logger.error(f"Failed to generate message for {planner.get('name', 'Unknown')}: {e}")
        
        return messages
    
    def _generate_personalized_message(self, planner: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Generate personalized message for a planner"""
        template = self.templates[template_name]
        
        # Gather personalization data
        personalization_data = self._extract_personalization_data(planner)
        
        # Use AI to personalize the message
        personalized_content = self._ai_personalize_content(
            template.content, 
            planner, 
            personalization_data
        )
        
        # Add compliance footer
        personalized_content += self.compliance_footer
        
        message = {
            "subject": template.subject,
            "content": personalized_content,
            "communication_type": template.communication_type,
            "template_used": template_name,
            "personalization_data": personalization_data
        }
        
        return message
    
    def _extract_personalization_data(self, planner: Dict[str, Any]) -> Dict[str, str]:
        """Extract personalization data from planner record"""
        data = {}
        
        # Basic info
        data["name"] = planner.get("name", "").split()[0] if planner.get("name") else "there"
        data["full_name"] = planner.get("name", "")
        data["business_name"] = planner.get("business_name", data["full_name"])
        data["location"] = planner.get("location", "Orange County")
        
        # Specializations and keywords
        specializations = planner.get("specializations", [])
        if isinstance(specializations, list):
            data["specializations"] = ", ".join(specializations[:3])  # Top 3
        else:
            data["specializations"] = str(specializations)
        
        # Experience indicators
        experience_indicators = []
        if planner.get("chinese_wedding_experience"):
            experience_indicators.append("Chinese wedding experience")
        if planner.get("tea_ceremony_experience"):
            experience_indicators.append("tea ceremony coordination")
        if planner.get("bilingual_services"):
            experience_indicators.append("bilingual services")
        if planner.get("oc_venue_experience"):
            experience_indicators.append("Orange County venue experience")
        
        data["experience_highlights"] = ", ".join(experience_indicators)
        
        # Source-specific data
        if planner.get("source") == "instagram":
            data["source_mention"] = f"your Instagram profile @{planner.get('instagram_handle', '')}"
        elif planner.get("source") == "weddingwire":
            data["source_mention"] = "your WeddingWire profile"
        elif planner.get("source") == "theknot":
            data["source_mention"] = "your profile on The Knot"
        else:
            data["source_mention"] = "your professional profile"
        
        return data
    
    def _ai_personalize_content(self, template_content: str, planner: Dict[str, Any], 
                              personalization_data: Dict[str, str]) -> str:
        """Use AI to personalize template content"""
        try:
            prompt = f"""
            Personalize this wedding outreach email template for a specific planner:
            
            Template:
            {template_content}
            
            Planner Info:
            - Name: {planner.get('name', 'Unknown')}
            - Business: {planner.get('business_name', 'Unknown')}
            - Location: {planner.get('location', 'Unknown')}
            - Source: {planner.get('source', 'Unknown')}
            - Specializations: {personalization_data.get('specializations', 'general wedding planning')}
            - Experience highlights: {personalization_data.get('experience_highlights', 'wedding planning')}
            
            Personalization Requirements:
            1. Replace [Name] with the planner's first name
            2. Mention their specific experience/specializations naturally
            3. Reference where we found them ({personalization_data.get('source_mention', 'online')})
            4. Keep the tone professional but personal
            5. Maintain urgency about the 3-4 month timeline
            6. Keep email under 200 words
            
            Return only the personalized email content.
            """
            
            response = self.llm.invoke(prompt)
            log_api_call(logger, "openai", "message_personalization")
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"AI personalization failed: {e}")
            # Fallback to simple template substitution
            content = template_content
            for key, value in personalization_data.items():
                content = content.replace(f"[{key}]", value)
            return content
    
    def _get_batch_approval(self, batch_messages: List[Dict], campaign: OutreachCampaign) -> bool:
        """Get human approval for message batch"""
        
        # Prepare approval summary
        summary_lines = [f"Campaign: {campaign.name}"]
        summary_lines.append(f"Batch size: {len(batch_messages)}")
        summary_lines.append(f"Communication type: {campaign.communication_type}")
        summary_lines.append("")
        summary_lines.append("Planners to contact:")
        
        for msg in batch_messages[:3]:  # Show first 3
            planner = msg["planner"]
            summary_lines.append(f"- {planner.get('name', 'Unknown')} ({planner.get('source', 'unknown')})")
        
        if len(batch_messages) > 3:
            summary_lines.append(f"... and {len(batch_messages) - 3} more")
        
        summary = "\n".join(summary_lines)
        
        log_human_gate(logger, "outreach_batch_approval", summary)
        
        # For automation, return True after logging
        # In production, this would wait for human approval
        return True
    
    def _send_message_batch(self, batch_messages: List[Dict], campaign: OutreachCampaign) -> Dict[str, Any]:
        """Send a batch of messages"""
        results = {"sent": 0, "failed": 0, "planners_contacted": []}
        
        for msg_data in batch_messages:
            try:
                planner = msg_data["planner"]
                message = msg_data["message"]
                communication_type = msg_data["communication_type"]
                
                success = self._send_single_message(planner, message, communication_type)
                
                if success:
                    results["sent"] += 1
                    results["planners_contacted"].append(planner["id"])
                    
                    # Update planner status
                    self.airtable.update_planner(planner["id"], {"status": "contacted"})
                else:
                    results["failed"] += 1
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to send message to {planner.get('name', 'Unknown')}: {e}")
                results["failed"] += 1
        
        return results
    
    def _send_single_message(self, planner: Dict[str, Any], message: Dict[str, Any], 
                           communication_type: str) -> bool:
        """Send a single message to a planner"""
        try:
            # Create communication record
            communication = CommunicationRecord(
                planner_id=planner["id"],
                communication_type=communication_type,
                subject=message.get("subject"),
                message_content=message["content"],
                status=CommunicationStatus.DRAFT,
                template_used=message.get("template_used"),
                personalization_data=str(message.get("personalization_data", {})),
                follow_up_required=True
            )
            
            communication_id = self.airtable.create_communication(communication)
            
            if communication_type == "email":
                success = self._send_email(planner, message, communication_id)
            elif communication_type == "sms":
                success = self._send_sms(planner, message, communication_id)
            else:
                logger.error(f"Unknown communication type: {communication_type}")
                return False
            
            if success:
                # Update communication status
                self.airtable.update_communication(communication_id, {
                    "status": "sent",
                    "sent_date": datetime.now().isoformat()
                })
                
                log_agent_action(
                    logger, "outreach_agent", "message_sent",
                    {"planner": planner.get("name"), "type": communication_type}
                )
                
                return True
            else:
                # Update communication status
                self.airtable.update_communication(communication_id, {
                    "status": "failed"
                })
                return False
                
        except Exception as e:
            logger.error(f"Failed to send {communication_type} to {planner.get('name', 'Unknown')}: {e}")
            return False
    
    def _send_email(self, planner: Dict[str, Any], message: Dict[str, Any], communication_id: str) -> bool:
        """Send email via SendGrid"""
        try:
            email = planner.get("email")
            if not email:
                logger.warning(f"No email for planner {planner.get('name')}")
                return False
            
            # Create SendGrid email
            mail = Mail(
                from_email=Email(self.sender_info["from_email"], self.sender_info["from_name"]),
                to_emails=To(email),
                subject=message.get("subject", "Wedding Planner Inquiry"),
                html_content=Content("text/plain", message["content"])
            )
            
            # Send email
            response = self.sendgrid_client.send(mail)
            
            log_api_call(logger, "sendgrid", "send_email", 0.01)  # Estimated cost
            
            if response.status_code in [200, 201, 202]:
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _send_sms(self, planner: Dict[str, Any], message: Dict[str, Any], communication_id: str) -> bool:
        """Send SMS via Twilio"""
        try:
            phone = planner.get("phone")
            if not phone:
                logger.warning(f"No phone for planner {planner.get('name')}")
                return False
            
            # Send SMS
            message_obj = self.twilio_client.messages.create(
                body=message["content"][:160],  # SMS character limit
                from_=self.sender_info["phone_number"],
                to=phone
            )
            
            log_api_call(logger, "twilio", "send_sms", 0.0075)  # Twilio SMS cost
            
            return message_obj.sid is not None
            
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False
    
    def _load_template_content(self, template_name: str) -> str:
        """Load template content from file or return default"""
        try:
            if template_name == "initial_email":
                with open(Config.PROJECT_ROOT / "templates" / "planner_outreach.txt", "r") as f:
                    return f.read()
        except:
            pass
        
        # Default templates
        templates_content = {
            "initial_email": """Dear [name],

We're seeking a wedding planner for an authentic 80s/90s-style Chinese restaurant wedding in Orange County, scheduled for January 2026.

Your [experience_highlights] caught our attention through [source_mention], and we believe you'd be perfect for this unique celebration.

Wedding Details:
• Date: January 2026 (mid-month for auspicious timing)
• Location: Orange County Chinese seafood restaurant
• Guest Count: 200-220 guests (20-22 round tables)
• Style: Traditional Cantonese banquet with city pop fusion elements
• Budget: $25-30K total (planner fee: $3-5K)

We need someone experienced with:
- Chinese restaurant banquet weddings
- Tea ceremony coordination
- Bilingual MC arrangements
- Modern fusion elements (neon lighting, retro touches)

Timeline is urgent - we need to begin planning within weeks for our 3-4 month execution window.

Available for a 15-20 minute call this week to discuss?

Best regards,
Jason & Suzie""",

            "follow_up_email": """Hi [name],

Following up on our Chinese banquet wedding inquiry from a few days ago. 

We're still actively seeking a planner for our January 2026 wedding and would love to connect with you about this unique project.

Quick reminder - we're looking for someone experienced with authentic Chinese restaurant weddings who can add modern city pop fusion elements.

Timeline is tight (3-4 months), so we're hoping to connect soon.

Available for a brief call this week?

Best,
Jason & Suzie""",

            "urgent_email": """Hi [name],

URGENT follow-up on our Chinese wedding planner search.

We're finalizing our planner selection this week for our January 2026 authentic Chinese banquet wedding in Orange County.

Your experience would be perfect for this project. Can we schedule a quick 15-minute call in the next 2-3 days?

Time-sensitive decision needed due to our 3-4 month timeline.

Please let us know your availability ASAP.

Thanks,
Jason & Suzie""",

            "sms_intro": """Hi [name]! Jason & Suzie here. Saw your wedding planning work and interested in discussing our January 2026 Chinese banquet wedding in OC. 3-4 month timeline. Quick call this week? Reply if interested!""",

            "call_scheduling": """Hi [name],

Great to hear from you! We're excited to discuss our wedding project.

Here are a few time slots that work for us this week:
- [availability]

The call will be about 15-20 minutes to discuss:
- Our authentic Chinese banquet vision
- Modern city pop fusion elements  
- Timeline and budget
- Your experience with similar weddings

Please let us know what works best for you, and we'll send over a Calendly link.

Looking forward to speaking with you!

Best,
Jason & Suzie"""
        }
        
        return templates_content.get(template_name, "Template not found")