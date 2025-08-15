"""
Secure credentials management for API keys and sensitive data
"""
import os
from typing import Dict, Optional
from pathlib import Path
import json
from cryptography.fernet import Fernet
from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("credentials")

class CredentialsManager:
    """Secure management of API credentials"""
    
    def __init__(self):
        self.credentials_file = Config.PROJECT_ROOT / ".credentials.enc"
        self.key_file = Config.PROJECT_ROOT / ".key"
        
    def _get_or_create_key(self) -> bytes:
        """Get encryption key or create new one"""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            self.key_file.chmod(0o600)  # Read/write for owner only
            return key
    
    def encrypt_credentials(self, credentials: Dict[str, str]) -> None:
        """Encrypt and store credentials"""
        key = self._get_or_create_key()
        fernet = Fernet(key)
        
        credentials_json = json.dumps(credentials)
        encrypted_data = fernet.encrypt(credentials_json.encode())
        
        self.credentials_file.write_bytes(encrypted_data)
        self.credentials_file.chmod(0o600)
        logger.info("Credentials encrypted and stored securely")
    
    def decrypt_credentials(self) -> Dict[str, str]:
        """Decrypt and return stored credentials"""
        if not self.credentials_file.exists():
            logger.warning("No encrypted credentials found")
            return {}
        
        key = self._get_or_create_key()
        fernet = Fernet(key)
        
        encrypted_data = self.credentials_file.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        
        return json.loads(decrypted_data.decode())
    
    def setup_credentials_from_env(self) -> bool:
        """Setup credentials from environment variables"""
        credentials = {}
        
        required_keys = [
            "OPENAI_API_KEY",
            "AIRTABLE_API_KEY", 
            "AIRTABLE_BASE_ID",
            "APIFY_API_TOKEN",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "SENDGRID_API_KEY"
        ]
        
        optional_keys = [
            "CALENDLY_ACCESS_TOKEN"
        ]
        
        # Check required keys
        missing_keys = []
        for key in required_keys:
            value = os.getenv(key)
            if value:
                credentials[key] = value
            else:
                missing_keys.append(key)
        
        # Add optional keys if present
        for key in optional_keys:
            value = os.getenv(key)
            if value:
                credentials[key] = value
        
        if missing_keys:
            logger.error(f"Missing required environment variables: {missing_keys}")
            return False
        
        self.encrypt_credentials(credentials)
        logger.info("Credentials setup complete")
        return True
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that API keys work by making test calls"""
        credentials = self.decrypt_credentials()
        validation_results = {}
        
        # OpenAI validation
        try:
            from openai import OpenAI
            client = OpenAI(api_key=credentials.get("OPENAI_API_KEY"))
            response = client.models.list()
            validation_results["openai"] = True
            logger.info("OpenAI API key validated")
        except Exception as e:
            validation_results["openai"] = False
            logger.error(f"OpenAI validation failed: {e}")
        
        # Airtable validation
        try:
            from pyairtable import Api
            api = Api(credentials.get("AIRTABLE_API_KEY"))
            base = api.base(credentials.get("AIRTABLE_BASE_ID"))
            validation_results["airtable"] = True
            logger.info("Airtable API key validated")
        except Exception as e:
            validation_results["airtable"] = False
            logger.error(f"Airtable validation failed: {e}")
        
        # Apify validation
        try:
            from apify_client import ApifyClient
            client = ApifyClient(credentials.get("APIFY_API_TOKEN"))
            user = client.user().get()
            validation_results["apify"] = True
            logger.info("Apify API key validated")
        except Exception as e:
            validation_results["apify"] = False
            logger.error(f"Apify validation failed: {e}")
        
        # Twilio validation
        try:
            from twilio.rest import Client
            client = Client(
                credentials.get("TWILIO_ACCOUNT_SID"),
                credentials.get("TWILIO_AUTH_TOKEN")
            )
            account = client.api.accounts(credentials.get("TWILIO_ACCOUNT_SID")).fetch()
            validation_results["twilio"] = True
            logger.info("Twilio API key validated")
        except Exception as e:
            validation_results["twilio"] = False
            logger.error(f"Twilio validation failed: {e}")
        
        return validation_results
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get specific credential"""
        credentials = self.decrypt_credentials()
        return credentials.get(key)

def setup_api_clients():
    """Setup and return authenticated API clients"""
    creds_manager = CredentialsManager()
    credentials = creds_manager.decrypt_credentials()
    
    clients = {}
    
    # OpenAI client
    try:
        from openai import OpenAI
        clients["openai"] = OpenAI(api_key=credentials.get("OPENAI_API_KEY"))
    except Exception as e:
        logger.error(f"Failed to setup OpenAI client: {e}")
    
    # Airtable client
    try:
        from pyairtable import Api
        api = Api(credentials.get("AIRTABLE_API_KEY"))
        clients["airtable"] = api.base(credentials.get("AIRTABLE_BASE_ID"))
    except Exception as e:
        logger.error(f"Failed to setup Airtable client: {e}")
    
    # Apify client
    try:
        from apify_client import ApifyClient
        clients["apify"] = ApifyClient(credentials.get("APIFY_API_TOKEN"))
    except Exception as e:
        logger.error(f"Failed to setup Apify client: {e}")
    
    # Twilio client
    try:
        from twilio.rest import Client
        clients["twilio"] = Client(
            credentials.get("TWILIO_ACCOUNT_SID"),
            credentials.get("TWILIO_AUTH_TOKEN")
        )
    except Exception as e:
        logger.error(f"Failed to setup Twilio client: {e}")
    
    # SendGrid (via Twilio)
    try:
        from sendgrid import SendGridAPIClient
        clients["sendgrid"] = SendGridAPIClient(api_key=credentials.get("SENDGRID_API_KEY"))
    except Exception as e:
        logger.error(f"Failed to setup SendGrid client: {e}")
    
    return clients