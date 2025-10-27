"""
Configuration management for the hospital chat system.
"""
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


class Settings(BaseSettings):
    """Application settings."""
    
    # Google Cloud
    gcp_project_id: str = Field(default="", env="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", env="GCP_LOCATION")
    
    # Buckets
    finance_bucket: str = Field(default="finance-bucket", env="FINANCE_BUCKET")
    legal_bucket: str = Field(default="legal-bucket", env="LEGAL_BUCKET")
    healthcare_bucket: str = Field(default="healthcare-bucket", env="HEALTHCARE_BUCKET")
    
    # Vertex AI Search Datastores
    finance_datastore_id: str = Field(default="", env="FINANCE_DATASTORE_ID")
    legal_datastore_id: str = Field(default="", env="LEGAL_DATASTORE_ID")
    healthcare_datastore_id: str = Field(default="", env="HEALTHCARE_DATASTORE_ID")
    
    # API Settings
    port: int = Field(default=8080, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


# Global settings instance
settings = Settings()
config = load_config()
