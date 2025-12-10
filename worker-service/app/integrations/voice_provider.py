"""
Voice Provider API client - Infobip Integration.

Handles communication with Infobip Voice API for TTS calls.
Includes mock mode for development/testing.
"""
import logging
import httpx
import uuid
from dataclasses import dataclass
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CallResponse:
    """Response from voice provider create call API."""
    call_id: str
    status: str
    success: bool
    error_message: Optional[str] = None


class InfobipVoiceClient:
    """
    Client for Infobip Voice API.
    
    Handles creating TTS voice calls through Infobip.
    Falls back to mock mode if no API key is configured.
    """
    
    def __init__(self):
        """Initialize the Infobip SMS client."""
        self.base_url = settings.INFOBIP_BASE_URL
        self.api_key = settings.INFOBIP_API_KEY
        self.from_number = settings.INFOBIP_FROM_NUMBER
        # Use mock mode if explicitly enabled OR if no API key
        self.mock_mode = settings.MOCK_MODE or not bool(self.api_key)
        self.mock_success_rate = settings.MOCK_CALL_SUCCESS_RATE
        
        if self.mock_mode:
            logger.warning("🎭 Infobip SMS running in MOCK mode - simulating SMS without real API")
            logger.info(f"Mock success rate: {self.mock_success_rate * 100}%")
            logger.info("💡 In mock mode: No real SMS sent, UI notifications shown instead")
        else:
            logger.info(f"📱 Infobip SMS configured: {self.base_url}")
            logger.info("📱 Real SMS will be sent to user's phone")
            if self.from_number:
                logger.info(f"Using Infobip sender: {self.from_number}")
            else:
                logger.warning("No Infobip sender configured - using default 'VoiceReminder'")
    
    async def create_call(
        self,
        phone_number: str,
        message: str,
        reminder_id: str
    ) -> CallResponse:
        """
        Create a voice call through the provider.
        
        Args:
            phone_number: Phone number to call
            message: Message to speak
            reminder_id: Associated reminder ID for metadata
            
        Returns:
            CallResponse with call details
        """
        logger.info(f"Creating call for reminder {reminder_id} to {phone_number}")
        
        if self.mock_mode:
            return await self._mock_create_call(phone_number, message, reminder_id)
        
        return await self._real_create_call(phone_number, message, reminder_id)
    
    async def _mock_create_call(
        self,
        phone_number: str,
        message: str,
        reminder_id: str
    ) -> CallResponse:
        """
        Mock call creation for development/testing.
        
        Simulates call success/failure based on success rate.
        Generates a fake call_id and mock transcript.
        """
        import random
        
        mock_call_id = f"mock-{reminder_id}"
        
        # Simulate success/failure based on configured rate
        is_success = random.random() < self.mock_success_rate
        
        if is_success:
            logger.info(
                f"🎭 [MOCK] Call created successfully: {mock_call_id}",
                extra={
                    "phone_number": phone_number,
                    "message_preview": message[:50],
                    "reminder_id": reminder_id,
                    "mock_status": "success"
                }
            )
            
            return CallResponse(
                call_id=mock_call_id,
                status="pending",
                success=True
            )
        else:
            logger.warning(
                f"🎭 [MOCK] Call failed (simulated): {mock_call_id}",
                extra={
                    "phone_number": phone_number,
                    "message_preview": message[:50],
                    "reminder_id": reminder_id,
                    "mock_status": "failed"
                }
            )
            
            return CallResponse(
                call_id=mock_call_id,
                status="failed",
                success=False,
                error_message="Mock failure simulation"
            )
    
    async def _real_create_call(
        self,
        phone_number: str,
        message: str,
        reminder_id: str
    ) -> CallResponse:
        """
        Send SMS through Infobip SMS API.
        
        Uses Infobip's SMS API to deliver text reminders to user's phone.
        User sees the reminder on their phone, and we get delivery confirmation.
        """
        try:
            # Infobip SMS API payload
            payload = {
                "messages": [
                    {
                        "from": self.from_number if self.from_number else "VoiceReminder",
                        "destinations": [
                            {
                                "to": phone_number
                            }
                        ],
                        "text": f"🔔 Reminder: {message}",
                        "callbackData": reminder_id,
                        "notifyUrl": f"{settings.WEBHOOK_URL}" if hasattr(settings, 'WEBHOOK_URL') else None,
                        "notifyContentType": "application/json"
                    }
                ]
            }
            
            # Remove notifyUrl if not configured
            if not payload["messages"][0]["notifyUrl"]:
                del payload["messages"][0]["notifyUrl"]
                del payload["messages"][0]["notifyContentType"]
            
            logger.info(f"Sending SMS via Infobip: {self.base_url}/sms/2/text/advanced")
            logger.info(f"Phone: {phone_number}, Message: {message[:50]}...")
            logger.debug(f"Full payload: {payload}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/sms/2/text/advanced",
                    headers={
                        "Authorization": f"App {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json=payload
                )
                
                logger.info(f"Infobip response status: {response.status_code}")
                logger.info(f"Infobip response body: {response.text}")
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    # Infobip returns bulkId and messages array
                    bulk_id = data.get("bulkId", "")
                    messages = data.get("messages", [])
                    
                    if messages and len(messages) > 0:
                        message_data = messages[0]
                        message_id = message_data.get("messageId", bulk_id)
                        status = message_data.get("status", {}).get("groupName", "PENDING")
                        
                        logger.info(f"SMS sent successfully: {message_id}")
                        logger.info(f"User will see reminder on their phone 📱")
                        
                        return CallResponse(
                            call_id=message_id,
                            status=status.lower(),
                            success=True
                        )
                    else:
                        error_msg = "No messages in response"
                        logger.error(f"Failed to send SMS: {error_msg}")
                        return CallResponse(
                            call_id="",
                            status="failed",
                            success=False,
                            error_message=error_msg
                        )
                else:
                    error_msg = f"API returned {response.status_code}: {response.text}"
                    logger.error(f"Failed to send SMS: {error_msg}")
                    
                    return CallResponse(
                        call_id="",
                        status="failed",
                        success=False,
                        error_message=error_msg
                    )
                    
        except httpx.TimeoutException:
            error_msg = "Request timeout"
            logger.error(f"Voice provider timeout: {error_msg}")
            return CallResponse(
                call_id="",
                status="failed",
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Voice provider error: {error_msg}", exc_info=True)
            return CallResponse(
                call_id="",
                status="failed",
                success=False,
                error_message=error_msg
            )


# Singleton instance
voice_provider = InfobipVoiceClient()
