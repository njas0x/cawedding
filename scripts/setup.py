#!/usr/bin/env python3
"""
Setup script for the Wedding Planner Hiring System
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.config import Config
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger("setup")

def install_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        logger.error("requirements.txt not found")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    logger.info("Setting up directories...")
    
    directories = [
        Config.DATA_DIR,
        Config.LOGS_DIR,
        project_root / "exports",
        project_root / "backups"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True

def setup_credentials():
    """Setup credentials from environment variables"""
    logger.info("Setting up credentials...")
    
    creds_manager = CredentialsManager()
    
    # Check if credentials are already set up
    existing_creds = creds_manager.decrypt_credentials()
    if existing_creds and len(existing_creds) > 0:
        logger.info("Credentials already configured")
        return True
    
    # Setup from environment variables
    success = creds_manager.setup_credentials_from_env()
    
    if success:
        logger.info("Credentials configured successfully")
        return True
    else:
        logger.error("Failed to configure credentials. Please check your .env file")
        return False

def validate_apis():
    """Validate API connections"""
    logger.info("Validating API connections...")
    
    creds_manager = CredentialsManager()
    validation_results = creds_manager.validate_api_keys()
    
    all_valid = True
    for service, is_valid in validation_results.items():
        if is_valid:
            logger.info(f"✅ {service.upper()} API: Valid")
        else:
            logger.error(f"❌ {service.upper()} API: Invalid")
            all_valid = False
    
    return all_valid

def create_env_template():
    """Create .env template if it doesn't exist"""
    env_file = project_root / ".env"
    env_template = project_root / ".env.example"
    
    if not env_file.exists() and env_template.exists():
        logger.info("Creating .env file from template...")
        with open(env_template, 'r') as template:
            with open(env_file, 'w') as env:
                env.write(template.read())
        logger.info("Please edit .env file with your actual API keys")
        return True
    
    return env_file.exists()

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup Wedding Planner Hiring System")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-validation", action="store_true", help="Skip API validation")
    parser.add_argument("--force", action="store_true", help="Force setup even if already configured")
    
    args = parser.parse_args()
    
    logger.info("🎯 Starting Wedding Planner Hiring System Setup")
    logger.info("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    logger.info(f"✅ Python {sys.version.split()[0]} detected")
    
    # Setup steps
    steps = [
        ("Creating directories", setup_directories),
        ("Creating .env template", create_env_template),
    ]
    
    if not args.skip_deps:
        steps.append(("Installing dependencies", install_dependencies))
    
    steps.extend([
        ("Setting up credentials", setup_credentials),
    ])
    
    if not args.skip_validation:
        steps.append(("Validating API connections", validate_apis))
    
    # Execute setup steps
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"🔄 {step_name}...")
        try:
            success = step_func()
            if success:
                logger.info(f"✅ {step_name} completed")
            else:
                logger.error(f"❌ {step_name} failed")
                failed_steps.append(step_name)
        except Exception as e:
            logger.error(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)
    
    # Summary
    logger.info("=" * 60)
    if failed_steps:
        logger.error(f"❌ Setup completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            logger.error(f"   • {step}")
        logger.error("\nPlease fix the issues and run setup again.")
        sys.exit(1)
    else:
        logger.info("✅ Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Edit .env file with your actual API keys")
        logger.info("2. Run: python scripts/run_system.py --help")
        logger.info("3. Start the system: python scripts/run_system.py")

if __name__ == "__main__":
    main()