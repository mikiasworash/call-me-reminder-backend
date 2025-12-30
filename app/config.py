from pydantic_settings import BaseSettings
from typing import Optional, Union
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./reminders.db"
    
    # Vapi
    vapi_api_key: Optional[str] = None
    vapi_phone_number_id: Optional[str] = None
    
    # Twilio (if needed separately)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # CORS - can be a string (comma-separated) or list
    cors_origins: Union[str, list[str]] = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from string or return list"""
        if isinstance(self.cors_origins, str):
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
            # Add default localhost origins if not present
            default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
            for origin in default_origins:
                if origin not in origins:
                    origins.append(origin)
            return origins
        # If it's already a list, ensure defaults are included
        if isinstance(self.cors_origins, list):
            origins = list(self.cors_origins)
            default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
            for origin in default_origins:
                if origin not in origins:
                    origins.append(origin)
            return origins
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

