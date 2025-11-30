"""
Configuration Management for DatasetDoctor

This file holds all the settings for our application.
Think of it like a settings menu - everything is configured here.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Main configuration class - stores all our settings"""
    
    # Google Gemini API settings
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    PROJECT_ID = os.getenv("PROJECT_ID", "")
    REGION = os.getenv("REGION", "us-central1")
    
    # Server settings
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))  # Cloud Run uses PORT env var
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # File upload settings
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'csv', 'json'}  # xlsx support can be added later
    
    # Cleanup settings
    AUTO_CLEANUP_ENABLED = os.getenv('AUTO_CLEANUP_ENABLED', 'true').lower() == 'true'
    CLEANUP_MAX_AGE_HOURS = int(os.getenv('CLEANUP_MAX_AGE_HOURS', '24'))  # Keep files for 24 hours
    CLEANUP_KEEP_RECENT = int(os.getenv('CLEANUP_KEEP_RECENT', '10'))  # Always keep 10 most recent files
    
    # Output directories
    UPLOAD_FOLDER = "uploads"
    OUTPUT_FOLDER = "outputs"
    LOGS_FOLDER = "logs"
    TRACES_FOLDER = "traces"
    
    @staticmethod
    def validate():
        """Check if all required settings are present"""
        if not Config.GOOGLE_API_KEY:
            print("⚠️  Warning: GOOGLE_API_KEY not set. Some AI features may not work.")
        return True

