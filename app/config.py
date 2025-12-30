from pydantic_settings import BaseSettings
from typing import Optional


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
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

