"""
Airtable client for database operations
"""
from typing import Dict, List, Any, Optional
import time
from datetime import datetime
from pyairtable import Api, Table
from pyairtable.formulas import match
from src.database.airtable_schema import PlannerRecord, CommunicationRecord, CallRecord, LogRecord, AirtableSchema
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger("airtable_client")

class AirtableClient:
    """Client for interacting with Airtable database"""
    
    def __init__(self):
        self.creds_manager = CredentialsManager()
        self._setup_client()
        
    def _setup_client(self):
        """Setup Airtable API client"""
        credentials = self.creds_manager.decrypt_credentials()
        api_key = credentials.get("AIRTABLE_API_KEY")
        base_id = credentials.get("AIRTABLE_BASE_ID")
        
        if not api_key or not base_id:
            raise ValueError("Missing Airtable credentials")
        
        self.api = Api(api_key)
        self.base = self.api.base(base_id)
        
        # Setup table references
        self.planners_table = self.base.table("Planners")
        self.communications_table = self.base.table("Communications") 
        self.calls_table = self.base.table("Calls")
        self.logs_table = self.base.table("Logs")
        
        logger.info("Airtable client initialized")
    
    def create_planner(self, planner: PlannerRecord) -> str:
        """Create new planner record"""
        try:
            record_data = self._planner_to_dict(planner)
            result = self.planners_table.create(record_data)
            
            planner_id = result["id"]
            logger.info(f"Created planner record: {planner_id} - {planner.name}")
            
            # Log the action
            self.log_action(
                agent_name="airtable_client",
                action="create_planner",
                details=f"Created planner: {planner.name}",
                planner_id=planner_id
            )
            
            return planner_id
            
        except Exception as e:
            logger.error(f"Failed to create planner: {e}")
            raise
    
    def update_planner(self, planner_id: str, updates: Dict[str, Any]) -> None:
        """Update existing planner record"""
        try:
            updates["last_updated"] = datetime.now().isoformat()
            self.planners_table.update(planner_id, updates)
            
            logger.info(f"Updated planner: {planner_id}")
            
            self.log_action(
                agent_name="airtable_client",
                action="update_planner", 
                details=f"Updated fields: {list(updates.keys())}",
                planner_id=planner_id
            )
            
        except Exception as e:
            logger.error(f"Failed to update planner {planner_id}: {e}")
            raise
    
    def get_planner(self, planner_id: str) -> Optional[Dict[str, Any]]:
        """Get planner by ID"""
        try:
            record = self.planners_table.get(planner_id)
            return record["fields"]
        except Exception as e:
            logger.error(f"Failed to get planner {planner_id}: {e}")
            return None
    
    def get_planners_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get planners by status"""
        try:
            formula = match({"status": status})
            records = self.planners_table.all(formula=formula)
            return [{"id": r["id"], **r["fields"]} for r in records]
        except Exception as e:
            logger.error(f"Failed to get planners by status {status}: {e}")
            return []
    
    def get_shortlisted_planners(self) -> List[Dict[str, Any]]:
        """Get all shortlisted planners sorted by score"""
        try:
            formula = match({"status": "shortlisted"})
            records = self.planners_table.all(
                formula=formula,
                sort=["-total_score"]
            )
            return [{"id": r["id"], **r["fields"]} for r in records]
        except Exception as e:
            logger.error(f"Failed to get shortlisted planners: {e}")
            return []
    
    def create_communication(self, communication: CommunicationRecord) -> str:
        """Create communication record"""
        try:
            record_data = self._communication_to_dict(communication)
            result = self.communications_table.create(record_data)
            
            communication_id = result["id"]
            logger.info(f"Created communication record: {communication_id}")
            
            self.log_action(
                agent_name="airtable_client",
                action="create_communication",
                details=f"Type: {communication.communication_type}",
                planner_id=communication.planner_id,
                communication_id=communication_id
            )
            
            return communication_id
            
        except Exception as e:
            logger.error(f"Failed to create communication: {e}")
            raise
    
    def update_communication(self, communication_id: str, updates: Dict[str, Any]) -> None:
        """Update communication record"""
        try:
            self.communications_table.update(communication_id, updates)
            logger.info(f"Updated communication: {communication_id}")
            
            self.log_action(
                agent_name="airtable_client",
                action="update_communication",
                details=f"Updated fields: {list(updates.keys())}",
                communication_id=communication_id
            )
            
        except Exception as e:
            logger.error(f"Failed to update communication {communication_id}: {e}")
            raise
    
    def create_call(self, call: CallRecord) -> str:
        """Create call record"""
        try:
            record_data = self._call_to_dict(call)
            result = self.calls_table.create(record_data)
            
            call_id = result["id"]
            logger.info(f"Created call record: {call_id}")
            
            self.log_action(
                agent_name="airtable_client",
                action="create_call",
                details=f"Call type: {call.call_type}",
                planner_id=call.planner_id,
                call_id=call_id
            )
            
            return call_id
            
        except Exception as e:
            logger.error(f"Failed to create call: {e}")
            raise
    
    def log_action(self, agent_name: str, action: str, details: str = None, 
                   planner_id: str = None, communication_id: str = None, 
                   call_id: str = None, cost: float = None, 
                   execution_time: float = None, success: bool = True) -> None:
        """Log agent action"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "action": action,
                "success": success
            }
            
            if details:
                log_data["details"] = details
            if planner_id:
                log_data["planner"] = [planner_id]
            if communication_id:
                log_data["communication"] = [communication_id]
            if call_id:
                log_data["call"] = [call_id]
            if cost:
                log_data["cost_incurred"] = cost
            if execution_time:
                log_data["execution_time_seconds"] = execution_time
            
            self.logs_table.create(log_data)
            
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            stats = {}
            
            # Planner counts by status
            all_planners = self.planners_table.all()
            status_counts = {}
            total_score_sum = 0
            scored_count = 0
            
            for planner in all_planners:
                fields = planner["fields"]
                status = fields.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if fields.get("total_score"):
                    total_score_sum += fields["total_score"]
                    scored_count += 1
            
            stats["planner_status_counts"] = status_counts
            stats["total_planners"] = len(all_planners)
            stats["average_score"] = total_score_sum / scored_count if scored_count > 0 else 0
            
            # Communication stats
            all_communications = self.communications_table.all()
            comm_stats = {}
            for comm in all_communications:
                status = comm["fields"].get("status", "unknown")
                comm_stats[status] = comm_stats.get(status, 0) + 1
            
            stats["communication_status_counts"] = comm_stats
            stats["total_communications"] = len(all_communications)
            
            # Call stats
            all_calls = self.calls_table.all()
            stats["total_calls"] = len(all_calls)
            
            # Recent activity
            recent_logs = self.logs_table.all(
                sort=["-timestamp"],
                max_records=10
            )
            stats["recent_activity"] = [
                {
                    "timestamp": log["fields"].get("timestamp"),
                    "agent": log["fields"].get("agent_name"),
                    "action": log["fields"].get("action")
                }
                for log in recent_logs
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {}
    
    def _planner_to_dict(self, planner: PlannerRecord) -> Dict[str, Any]:
        """Convert PlannerRecord to Airtable format"""
        data = {
            "name": planner.name,
            "status": planner.status.value,
            "discovered_date": planner.discovered_date.isoformat() if planner.discovered_date else None,
            "last_updated": planner.last_updated.isoformat() if planner.last_updated else None
        }
        
        # Add optional fields if present
        optional_fields = [
            "email", "phone", "instagram_handle", "website", "business_name", 
            "location", "years_experience", "total_reviews", "average_rating",
            "review_summary", "asian_weddings_count", "chinese_wedding_experience",
            "tea_ceremony_experience", "bilingual_services", "fusion_experience",
            "available_january_2026", "rush_timeline_comfort", "oc_venue_experience",
            "multicultural_score", "availability_score", "reviews_score", 
            "total_score", "source", "notes"
        ]
        
        for field in optional_fields:
            value = getattr(planner, field, None)
            if value is not None:
                data[field] = value
        
        # Handle lists
        if planner.portfolio_links:
            data["portfolio_links"] = "\n".join(planner.portfolio_links)
        if planner.specializations:
            data["specializations"] = planner.specializations
        if planner.previous_venues:
            data["previous_venues"] = "\n".join(planner.previous_venues)
        if planner.review_sources:
            data["review_sources"] = planner.review_sources
        if planner.flags:
            data["flags"] = planner.flags
        
        return data
    
    def _communication_to_dict(self, communication: CommunicationRecord) -> Dict[str, Any]:
        """Convert CommunicationRecord to Airtable format"""
        data = {
            "planner": [communication.planner_id],
            "communication_type": communication.communication_type,
            "status": communication.status.value,
            "follow_up_required": communication.follow_up_required,
            "follow_up_count": communication.follow_up_count,
            "created_date": communication.created_date.isoformat() if communication.created_date else None
        }
        
        # Add optional fields
        optional_fields = [
            "subject", "message_content", "response_content", "response_sentiment",
            "response_interest_level", "template_used", "personalization_data", "cost"
        ]
        
        for field in optional_fields:
            value = getattr(communication, field, None)
            if value is not None:
                data[field] = value
        
        # Handle dates
        date_fields = ["sent_date", "delivered_date", "opened_date", "replied_date", "follow_up_date"]
        for field in date_fields:
            value = getattr(communication, field, None)
            if value:
                data[field] = value.isoformat()
        
        return data
    
    def _call_to_dict(self, call: CallRecord) -> Dict[str, Any]:
        """Convert CallRecord to Airtable format"""
        data = {
            "planner": [call.planner_id],
            "call_type": call.call_type,
            "conducted_by": call.conducted_by,
            "proposal_requested": call.proposal_requested,
            "created_date": call.created_date.isoformat() if call.created_date else None
        }
        
        if call.communication_id:
            data["communication"] = [call.communication_id]
        
        # Add optional fields
        optional_fields = [
            "duration_minutes", "planner_responses", "call_summary",
            "cultural_fit_score", "availability_confirmed", "enthusiasm_level",
            "next_steps", "decision_timeline", "recording_link", "transcript_link"
        ]
        
        for field in optional_fields:
            value = getattr(call, field, None)
            if value is not None:
                data[field] = value
        
        # Handle dates
        if call.scheduled_date:
            data["scheduled_date"] = call.scheduled_date.isoformat()
        
        # Handle lists
        if call.questions_asked:
            data["questions_asked"] = "\n".join(call.questions_asked)
        if call.red_flags_identified:
            data["red_flags_identified"] = call.red_flags_identified
        if call.green_flags_identified:
            data["green_flags_identified"] = call.green_flags_identified
        
        return data