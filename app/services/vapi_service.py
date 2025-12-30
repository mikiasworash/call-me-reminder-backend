import httpx
from typing import Optional
from app.config import settings


class VapiService:
    def __init__(self):
        self.api_key = settings.vapi_api_key
        self.phone_number_id = settings.vapi_phone_number_id
        self.base_url = "https://api.vapi.ai"

    async def create_call(
        self, phone_number: str, message: str, reminder_id: int
    ) -> Optional[str]:
        """
        Create a Vapi call to deliver the reminder message
        
        Returns the call ID if successful, None otherwise
        """
        if not self.api_key or not self.phone_number_id:
            raise ValueError("Vapi API key and phone number ID must be configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Vapi call payload
        # Note: Adjust this based on actual Vapi API documentation
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("id")  # Return call ID
        except httpx.HTTPStatusError as e:
            error_msg = f"Vapi API error: {e.response.status_code} - {e.response.text}"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Failed to create Vapi call: {str(e)}")

