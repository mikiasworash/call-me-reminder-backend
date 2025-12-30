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
        # Based on Vapi API v2 structure
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
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are calling to deliver a reminder. Say this message clearly and concisely: {message}",
                        },
                    ],
                },
            },
        }

        try:
            logger.info(f"Creating Vapi call for reminder {reminder_id} to {phone_number}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                call_id = data.get("id")
                logger.info(f"Vapi call created successfully. Call ID: {call_id}")
                return call_id
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

