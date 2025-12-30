"""
Configuration module for Star Citizen App.
Loads and validates environment variables required for the application.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    UEX_API_TOKEN: str
    DATABASE_URL: str
    
    def __init__(self):
        """
        Initialize configuration and validate required environment variables.
        
        Raises:
            RuntimeError: If required environment variables are missing
        """
        self.UEX_API_TOKEN = self._get_required_env("UEX_API_TOKEN")
        self.DATABASE_URL = self._get_env(
            "DATABASE_URL",
            "postgresql://sc_user:qsp1MhWM9S4QWHvaruNv@localhost:5432/starcitizen_prod"
        )
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        """
        Get required environment variable.
        
        Args:
            key: Environment variable name
            
        Returns:
            Environment variable value
            
        Raises:
            RuntimeError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"{key} is missing (environment variable required)")
        return value
    
    @staticmethod
    def _get_env(key: str, default: str) -> str:
        """
        Get optional environment variable with default value.
        
        Args:
            key: Environment variable name
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)


# Global configuration instance
config = Config()

# Backward compatibility exports
UEX_API_TOKEN = config.UEX_API_TOKEN
DATABASE_URL = config.DATABASE_URL