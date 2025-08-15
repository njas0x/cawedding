"""
Configuration management for Wedding Planner Hiring System
"""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for managing API keys and settings"""
    
    # Project Settings
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") 
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    CALENDLY_ACCESS_TOKEN = os.getenv("CALENDLY_ACCESS_TOKEN")
    
    # Wedding Specifications
    WEDDING_DATE = "January 2026"
    GUEST_COUNT = "200-220"
    BUDGET_RANGE = "$25-30K"
    PLANNER_FEE = "$3-5K"
    LOCATION = "Orange County, CA"
    
    # Search Parameters
    TARGET_PLANNER_COUNT = 50
    SHORTLIST_SIZE = 10
    TARGET_CALLS = 5
    
    # Instagram Hashtags for Research
    INSTAGRAM_HASHTAGS = [
        "#OCWeddingPlanner",
        "#AsianWeddingOC", 
        "#MulticulturalWeddingCA",
        "#ChineseWeddingCA",
        "#CityPopWedding",
        "#FusionAsianWedding"
    ]
    
    # Wedding Site URLs
    WEDDING_SITES = [
        "https://www.weddingwire.com",
        "https://www.theknot.com"
    ]
    
    # Cost Limits
    MONTHLY_BUDGET_LIMIT = 150.0  # USD
    API_CALL_LIMITS = {
        "openai": 100000,  # tokens per day
        "apify": 1000,     # requests per day
        "twilio": 100,     # messages per day
    }
    
    # Scoring Weights
    SCORING_WEIGHTS = {
        "multicultural_fit": 0.4,
        "timeline_availability": 0.3, 
        "reviews_sentiment": 0.3
    }
    
    # Human Approval Gates
    APPROVAL_REQUIRED = [
        "shortlist_generation",
        "outreach_campaign", 
        "final_recommendations"
    ]
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate that all required configuration is present"""
        required_vars = [
            "OPENAI_API_KEY",
            "AIRTABLE_API_KEY", 
            "AIRTABLE_BASE_ID",
            "APIFY_API_TOKEN",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "SENDGRID_API_KEY"
        ]
        
        validation_results = {}
        for var in required_vars:
            validation_results[var] = bool(getattr(cls, var))
            
        return validation_results
    
    @classmethod
    def get_search_criteria(cls) -> Dict[str, Any]:
        """Get structured search criteria for agents"""
        return {
            "location": cls.LOCATION,
            "wedding_style": "Chinese banquet with city pop fusion",
            "guest_count": cls.GUEST_COUNT,
            "budget": cls.BUDGET_RANGE,
            "timeline": "3-4 months",
            "must_have_experience": [
                "Chinese restaurant banquet weddings",
                "Multicultural ceremonies",
                "Tea ceremony coordination",
                "Bilingual MC arrangements"
            ],
            "nice_to_have": [
                "City pop aesthetic",
                "Neon lighting setup", 
                "Wong Kar-wai style photography",
                "Orange County venue experience"
            ],
            "red_flags": [
                "Over-styled portfolio",
                "No Asian wedding experience",
                "Unavailable for rushed timeline",
                "Excessive vendor markup"
            ]
        }