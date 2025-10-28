"""
Configuration management for Hospital Multi-Agent Information Retrieval System
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Main configuration class for the hospital multi-agent system"""

    # Google Cloud Project Settings
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")

    # Vertex AI Search Datastore IDs
    NURSING_DATASTORE_ID: str = os.getenv("NURSING_DATASTORE_ID", "")
    HR_DATASTORE_ID: str = os.getenv("HR_DATASTORE_ID", "")
    PHARMACY_DATASTORE_ID: str = os.getenv("PHARMACY_DATASTORE_ID", "")

    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

    # Search Configuration
    DYNAMIC_THRESHOLD: float = float(os.getenv("DYNAMIC_THRESHOLD", "0.3"))
    MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "5"))

    # System Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30"))

    # Conversation Settings
    CONVERSATION_ENABLED: bool = os.getenv("CONVERSATION_ENABLED", "true").lower() == "true"
    MAX_CONVERSATION_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "3"))

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @classmethod
    def validate(cls) -> None:
        """Validate that all required configuration variables are set"""
        required_vars = {
            "GCP_PROJECT_ID": cls.PROJECT_ID,
            "NURSING_DATASTORE_ID": cls.NURSING_DATASTORE_ID,
            "HR_DATASTORE_ID": cls.HR_DATASTORE_ID,
            "PHARMACY_DATASTORE_ID": cls.PHARMACY_DATASTORE_ID,
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please set them in your .env file or environment."
            )

    @classmethod
    def get_datastore_id(cls, agent_type: str) -> str:
        """Get datastore ID for a specific agent type"""
        datastore_map = {
            "nursing": cls.NURSING_DATASTORE_ID,
            "hr": cls.HR_DATASTORE_ID,
            "pharmacy": cls.PHARMACY_DATASTORE_ID,
        }

        datastore_id = datastore_map.get(agent_type.lower())
        if not datastore_id:
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Valid types: {', '.join(datastore_map.keys())}"
            )

        return datastore_id

    @classmethod
    def display_config(cls) -> None:
        """Display current configuration (masking sensitive data)"""
        print("=" * 60)
        print("CONFIGURATION")
        print("=" * 60)
        print(f"Project ID: {cls.PROJECT_ID}")
        print(f"Location: {cls.LOCATION}")
        print(f"Model: {cls.MODEL_NAME}")
        print(f"Temperature: {cls.TEMPERATURE}")
        print(f"Environment: {cls.ENVIRONMENT}")
        print(f"Nursing Datastore: {'✓ Set' if cls.NURSING_DATASTORE_ID else '✗ Missing'}")
        print(f"HR Datastore: {'✓ Set' if cls.HR_DATASTORE_ID else '✗ Missing'}")
        print(f"Pharmacy Datastore: {'✓ Set' if cls.PHARMACY_DATASTORE_ID else '✗ Missing'}")
        print("=" * 60)


# Create a singleton instance
config = Config()
