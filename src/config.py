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
    
    # Buckets (existing)
    nursing_bucket: str = Field(default="nursing", env="NURSING_BUCKET")
    pharmacy_bucket: str = Field(default="pharmacy", env="PHARMACY_BUCKET")
    po_bucket: str = Field(default="po", env="PO_BUCKET")
    
    # Vertex AI Search Datastores (to be created)
    nursing_datastore_id: str = Field(default="", env="NURSING_DATASTORE_ID")
    pharmacy_datastore_id: str = Field(default="", env="PHARMACY_DATASTORE_ID")
    po_datastore_id: str = Field(default="", env="PO_DATASTORE_ID")
    
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
