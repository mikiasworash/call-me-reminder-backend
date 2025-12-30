import httpx
import logging
import uuid
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class VapiService:
    def __init__(self):
        self.api_key = settings.vapi_api_key
        self.phone_number_id = settings.vapi_phone_number_id
        self.assistant_id = settings.vapi_assistant_id
        self.base_url = "https://api.vapi.ai"

    def _validate_phone_number_id(self) -> None:
        """Validate that phone number ID is a valid UUID"""
        if not self.phone_number_id:
            raise ValueError("Vapi phone number ID is not configured. Please set VAPI_PHONE_NUMBER_ID in your .env file")
        
        try:
            # Try to parse as UUID to validate format
            uuid.UUID(self.phone_number_id)
        except ValueError:
            raise ValueError(
                f"Vapi phone number ID must be a valid UUID. "
                f"Current value: {self.phone_number_id}. "
                f"Please check your VAPI_PHONE_NUMBER_ID in .env file"
            )

    async def create_call(
        self, phone_number: str, message: str, reminder_id: int
    ) -> Optional[str]:
        """
        Create a Vapi call to deliver the reminder message
        
        Returns the call ID if successful, None otherwise
        """
        if not self.api_key:
            raise ValueError("Vapi API key is not configured. Please set VAPI_API_KEY in your .env file")
        
        self._validate_phone_number_id()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Vapi call payload
        # Option 1: Use assistantId if configured (recommended)
        # Option 2: Use inline assistant configuration
        if self.assistant_id:
            # Use pre-configured assistant (recommended approach)
            payload = {
                "phoneNumberId": self.phone_number_id,
                "customer": {
                    "number": phone_number,
                },
                "assistantId": self.assistant_id,
                "assistantOverrides": {
                    "firstMessage": message,
                },
            }
            logger.info(f"Using assistantId: {self.assistant_id}")
        else:
            # Use inline assistant configuration
            payload = {
                "phoneNumberId": self.phone_number_id,
                "customer": {
                    "number": phone_number,
                },
                "assistant": {
                    "firstMessage": message,
                    "model": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are calling to deliver a reminder. Say this message clearly and concisely: '{message}'. Be brief and professional.",
                            },
                        ],
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "21m00Tcm4TlvDq8ikWAM",
                    },
                },
            }
            logger.info("Using inline assistant configuration")
        
        logger.info(f"Call payload (sanitized): phoneNumberId={self.phone_number_id}, customer={phone_number}")

        try:
            logger.info(f"Creating Vapi call for reminder {reminder_id} to {phone_number}")
            logger.info(f"Using phone number ID: {self.phone_number_id}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try /calls endpoint (plural) first, fallback to /call
                endpoints = [f"{self.base_url}/calls", f"{self.base_url}/call"]
                
                for endpoint in endpoints:
                    try:
                        logger.info(f"Attempting to create call via {endpoint}")
                        response = await client.post(
                            endpoint,
                            headers=headers,
                            json=payload,
                        )
                        response.raise_for_status()
                        data = response.json()
                        call_id = data.get("id")
                        logger.info(f"✓ Vapi call created successfully via {endpoint}")
                        logger.info(f"✓ Call ID: {call_id}")
                        logger.info(f"✓ Full response: {data}")
                        return call_id
                    except httpx.HTTPStatusError as e:
                        if endpoint == endpoints[-1]:  # Last endpoint, re-raise
                            raise
                        logger.warning(f"Endpoint {endpoint} failed, trying next...")
                        continue
        except httpx.HTTPStatusError as e:
            error_response = e.response.text
            try:
                error_json = e.response.json()
                error_message = error_json.get("message", error_response)
            except:
                error_message = error_response
            
            error_msg = f"Vapi API error ({e.response.status_code}): {error_message}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to create Vapi call: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

