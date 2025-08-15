"""
Airtable database schema definition and management
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import datetime
from src.utils.logger import setup_logger

logger = setup_logger("airtable_schema")

class PlannerStatus(Enum):
    """Planner processing status"""
    DISCOVERED = "discovered"
    ANALYZED = "analyzed" 
    SHORTLISTED = "shortlisted"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    CALL_SCHEDULED = "call_scheduled"
    CALL_COMPLETED = "call_completed"
    REJECTED = "rejected"
    HIRED = "hired"

class CommunicationStatus(Enum):
    """Communication tracking status"""
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"

@dataclass
class PlannerRecord:
    """Schema for Planners table"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    instagram_handle: Optional[str] = None
    website: Optional[str] = None
    business_name: Optional[str] = None
    location: Optional[str] = None
    
    # Portfolio & Experience
    portfolio_links: List[str] = None
    years_experience: Optional[int] = None
    specializations: List[str] = None
    previous_venues: List[str] = None
    
    # Reviews & Ratings
    total_reviews: Optional[int] = None
    average_rating: Optional[float] = None
    review_sources: List[str] = None
    review_summary: Optional[str] = None
    
    # Multicultural Experience
    asian_weddings_count: Optional[int] = None
    chinese_wedding_experience: bool = False
    tea_ceremony_experience: bool = False
    bilingual_services: bool = False
    fusion_experience: bool = False
    
    # Availability & Logistics
    available_january_2026: Optional[bool] = None
    rush_timeline_comfort: Optional[bool] = None
    oc_venue_experience: bool = False
    
    # Scoring
    multicultural_score: Optional[float] = None
    availability_score: Optional[float] = None
    reviews_score: Optional[float] = None
    total_score: Optional[float] = None
    
    # Status & Metadata
    status: PlannerStatus = PlannerStatus.DISCOVERED
    source: Optional[str] = None  # Instagram, WeddingWire, etc.
    discovered_date: Optional[datetime.datetime] = None
    last_updated: Optional[datetime.datetime] = None
    flags: List[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.portfolio_links is None:
            self.portfolio_links = []
        if self.specializations is None:
            self.specializations = []
        if self.previous_venues is None:
            self.previous_venues = []
        if self.review_sources is None:
            self.review_sources = []
        if self.flags is None:
            self.flags = []
        if self.discovered_date is None:
            self.discovered_date = datetime.datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.datetime.now()

@dataclass 
class CommunicationRecord:
    """Schema for Communications table"""
    planner_id: str  # Link to Planners table
    communication_type: str  # email, sms, call
    subject: Optional[str] = None
    message_content: Optional[str] = None
    
    # Status & Tracking
    status: CommunicationStatus = CommunicationStatus.DRAFT
    sent_date: Optional[datetime.datetime] = None
    delivered_date: Optional[datetime.datetime] = None
    opened_date: Optional[datetime.datetime] = None
    replied_date: Optional[datetime.datetime] = None
    
    # Response Data
    response_content: Optional[str] = None
    response_sentiment: Optional[str] = None
    response_interest_level: Optional[int] = None  # 1-10 scale
    
    # Follow-up Tracking
    follow_up_required: bool = False
    follow_up_date: Optional[datetime.datetime] = None
    follow_up_count: int = 0
    
    # Metadata
    template_used: Optional[str] = None
    personalization_data: Optional[str] = None
    cost: Optional[float] = None
    created_date: Optional[datetime.datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.datetime.now()

@dataclass
class CallRecord:
    """Schema for Calls table"""
    planner_id: str  # Link to Planners table
    communication_id: Optional[str] = None  # Link to Communications table
    
    # Scheduling
    scheduled_date: Optional[datetime.datetime] = None
    duration_minutes: Optional[int] = None
    call_type: str = "intro"  # intro, follow_up, final
    
    # Call Content
    questions_asked: List[str] = None
    planner_responses: Optional[str] = None
    call_summary: Optional[str] = None
    
    # Assessment
    cultural_fit_score: Optional[int] = None  # 1-10
    availability_confirmed: Optional[bool] = None
    enthusiasm_level: Optional[int] = None  # 1-10
    red_flags_identified: List[str] = None
    green_flags_identified: List[str] = None
    
    # Follow-up
    next_steps: Optional[str] = None
    decision_timeline: Optional[str] = None
    proposal_requested: bool = False
    
    # Metadata
    conducted_by: str = "human"
    recording_link: Optional[str] = None
    transcript_link: Optional[str] = None
    created_date: Optional[datetime.datetime] = None
    
    def __post_init__(self):
        if self.questions_asked is None:
            self.questions_asked = []
        if self.red_flags_identified is None:
            self.red_flags_identified = []
        if self.green_flags_identified is None:
            self.green_flags_identified = []
        if self.created_date is None:
            self.created_date = datetime.datetime.now()

@dataclass
class LogRecord:
    """Schema for Logs table"""
    timestamp: datetime.datetime
    agent_name: str
    action: str
    details: Optional[str] = None
    
    # Data references
    planner_id: Optional[str] = None
    communication_id: Optional[str] = None
    call_id: Optional[str] = None
    
    # Monitoring
    api_calls_made: Optional[int] = None
    cost_incurred: Optional[float] = None
    error_occurred: bool = False
    error_message: Optional[str] = None
    
    # Performance
    execution_time_seconds: Optional[float] = None
    success: bool = True
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

class AirtableSchema:
    """Airtable schema management and validation"""
    
    TABLES = {
        "planners": {
            "name": "Planners",
            "fields": {
                "name": "Single line text",
                "email": "Email", 
                "phone": "Phone number",
                "instagram_handle": "Single line text",
                "website": "URL",
                "business_name": "Single line text",
                "location": "Single line text",
                "portfolio_links": "Long text",
                "years_experience": "Number",
                "specializations": "Multiple select",
                "previous_venues": "Long text",
                "total_reviews": "Number",
                "average_rating": "Number",
                "review_sources": "Multiple select",
                "review_summary": "Long text",
                "asian_weddings_count": "Number",
                "chinese_wedding_experience": "Checkbox",
                "tea_ceremony_experience": "Checkbox", 
                "bilingual_services": "Checkbox",
                "fusion_experience": "Checkbox",
                "available_january_2026": "Checkbox",
                "rush_timeline_comfort": "Checkbox",
                "oc_venue_experience": "Checkbox",
                "multicultural_score": "Number",
                "availability_score": "Number", 
                "reviews_score": "Number",
                "total_score": "Number",
                "status": "Single select",
                "source": "Single select",
                "discovered_date": "Date",
                "last_updated": "Date",
                "flags": "Multiple select",
                "notes": "Long text"
            }
        },
        "communications": {
            "name": "Communications", 
            "fields": {
                "planner": "Link to Planners",
                "communication_type": "Single select",
                "subject": "Single line text",
                "message_content": "Long text",
                "status": "Single select",
                "sent_date": "Date",
                "delivered_date": "Date",
                "opened_date": "Date",
                "replied_date": "Date",
                "response_content": "Long text",
                "response_sentiment": "Single select",
                "response_interest_level": "Number",
                "follow_up_required": "Checkbox",
                "follow_up_date": "Date",
                "follow_up_count": "Number",
                "template_used": "Single line text",
                "personalization_data": "Long text",
                "cost": "Currency",
                "created_date": "Date"
            }
        },
        "calls": {
            "name": "Calls",
            "fields": {
                "planner": "Link to Planners",
                "communication": "Link to Communications",
                "scheduled_date": "Date",
                "duration_minutes": "Number",
                "call_type": "Single select",
                "questions_asked": "Long text",
                "planner_responses": "Long text",
                "call_summary": "Long text",
                "cultural_fit_score": "Number",
                "availability_confirmed": "Checkbox",
                "enthusiasm_level": "Number",
                "red_flags_identified": "Multiple select",
                "green_flags_identified": "Multiple select",
                "next_steps": "Long text",
                "decision_timeline": "Single line text",
                "proposal_requested": "Checkbox",
                "conducted_by": "Single line text",
                "recording_link": "URL",
                "transcript_link": "URL",
                "created_date": "Date"
            }
        },
        "logs": {
            "name": "Logs",
            "fields": {
                "timestamp": "Date",
                "agent_name": "Single select",
                "action": "Single line text",
                "details": "Long text",
                "planner": "Link to Planners",
                "communication": "Link to Communications", 
                "call": "Link to Calls",
                "api_calls_made": "Number",
                "cost_incurred": "Currency",
                "error_occurred": "Checkbox",
                "error_message": "Long text",
                "execution_time_seconds": "Number",
                "success": "Checkbox"
            }
        }
    }
    
    @classmethod
    def get_table_schema(cls, table_name: str) -> Dict[str, Any]:
        """Get schema for specific table"""
        return cls.TABLES.get(table_name, {})
    
    @classmethod
    def validate_record(cls, table_name: str, record: Dict[str, Any]) -> List[str]:
        """Validate record against table schema"""
        errors = []
        schema = cls.get_table_schema(table_name)
        
        if not schema:
            errors.append(f"Unknown table: {table_name}")
            return errors
        
        required_fields = schema.get("required_fields", [])
        for field in required_fields:
            if field not in record:
                errors.append(f"Missing required field: {field}")
        
        return errors