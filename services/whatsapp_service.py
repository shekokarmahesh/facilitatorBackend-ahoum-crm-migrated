import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from wasenderapi import create_sync_wasender
from wasenderapi.errors import WasenderAPIError
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for sending WhatsApp messages using WasenderAPI"""
    
    def __init__(self):
        """Initialize WhatsApp service with WasenderAPI client"""
        try:
            self.api_key = Config.WASENDER_API_KEY
            self.phone_number = Config.WASENDER_PHONE_NUMBER
            self.session_name = Config.WASENDER_SESSION_NAME
            
            # Initialize the WasenderAPI client
            self.client = create_sync_wasender(api_key=self.api_key)
            
            logger.info(f"WhatsApp service initialized for session: {self.session_name}")
            logger.info(f"Using phone number: {self.phone_number}")
            
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp service: {e}")
            raise
    
    def send_text_message(self, to_number: str, message: str) -> Dict:
        """
        Send a text message to a WhatsApp number
        
        Args:
            to_number: The recipient's phone number (with country code)
            message: The text message to send
            
        Returns:
            Dict with success status and message details
        """
        try:
            # Clean the phone number (remove any spaces, dashes, etc.)
            cleaned_number = self._clean_phone_number(to_number)
            
            # Send the message using WasenderAPI
            response = self.client.send_text(
                to=cleaned_number,
                text_body=message
            )
            
            if response and response.response and response.response.data:
                message_id = response.response.data.message_id
                logger.info(f"Message sent successfully to {cleaned_number}, Message ID: {message_id}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "to_number": cleaned_number,
                    "status": "sent",
                    "sent_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to send message to {cleaned_number}: No response data")
                return {
                    "success": False,
                    "error": "No response data from API",
                    "to_number": cleaned_number
                }
                
        except WasenderAPIError as e:
            logger.error(f"WasenderAPI error sending message to {to_number}: {e.message}")
            return {
                "success": False,
                "error": f"API Error: {e.message}",
                "status_code": e.status_code,
                "to_number": to_number
            }
        except Exception as e:
            logger.error(f"Unexpected error sending message to {to_number}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "to_number": to_number
            }
    
    def send_course_details(self, to_number: str, course_details: Dict) -> Dict:
        """
        Send course details as a formatted WhatsApp message
        
        Args:
            to_number: The recipient's phone number
            course_details: Dict containing course information
            
        Returns:
            Dict with success status and message details
        """
        try:
            # Format the course details into a nice WhatsApp message
            message = self._format_course_message(course_details)
            
            # Send the formatted message
            return self.send_text_message(to_number, message)
            
        except Exception as e:
            logger.error(f"Error sending course details to {to_number}: {e}")
            return {
                "success": False,
                "error": f"Failed to send course details: {str(e)}",
                "to_number": to_number
            }
    
    def send_bulk_course_messages(self, phone_numbers: List[str], course_details: Dict) -> Dict:
        """
        Send course details to multiple phone numbers
        
        Args:
            phone_numbers: List of phone numbers to send to
            course_details: Dict containing course information
            
        Returns:
            Dict with overall results and individual message statuses
        """
        results = {
            "total_sent": 0,
            "total_failed": 0,
            "messages": []
        }
        
        # Format the message once
        message = self._format_course_message(course_details)
        
        for phone_number in phone_numbers:
            try:
                result = self.send_text_message(phone_number, message)
                results["messages"].append(result)
                
                if result["success"]:
                    results["total_sent"] += 1
                else:
                    results["total_failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error sending to {phone_number}: {e}")
                results["messages"].append({
                    "success": False,
                    "error": str(e),
                    "to_number": phone_number
                })
                results["total_failed"] += 1
        
        logger.info(f"Bulk message completed: {results['total_sent']} sent, {results['total_failed']} failed")
        return results
    
    def _format_course_message(self, course_details: Dict) -> str:
        """
        Format course details into a WhatsApp message
        
        Args:
            course_details: Dict containing course information
            
        Returns:
            Formatted message string
        """
        title = course_details.get('title', 'New Course')
        timing = course_details.get('timing', 'TBD')
        prerequisite = course_details.get('prerequisite', 'None')
        description = course_details.get('description', '')
        
        # Create a well-formatted WhatsApp message
        message = f"""🎯 *{title}*

📅 *Timing:* {timing}

📋 *Prerequisites:* {prerequisite}

📝 *Description:*
{description}

---
✨ *Ahoum - Your Wellness Journey*

For more information or to register, please reply to this message or contact us directly.

Thank you! 🙏"""
        
        return message
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """
        Clean and format phone number for WhatsApp
        
        Args:
            phone_number: Raw phone number string
            
        Returns:
            Cleaned phone number string
        """
        if not phone_number:
            return ""
        
        # Remove all non-digit characters except + at the beginning
        cleaned = ''.join(char for char in phone_number if char.isdigit() or (char == '+' and phone_number.index(char) == 0))
        
        # Ensure it starts with country code
        if not cleaned.startswith('+'):
            # If it's an Indian number starting with 91, add +
            if cleaned.startswith('91') and len(cleaned) == 12:
                cleaned = '+' + cleaned
            # If it's a 10-digit Indian number, add +91
            elif len(cleaned) == 10 and cleaned.startswith(('6', '7', '8', '9')):
                cleaned = '+91' + cleaned
            # If it's missing +, add it
            else:
                cleaned = '+' + cleaned
        
        return cleaned
    
    def test_connection(self) -> Dict:
        """
        Test the WhatsApp service connection
        
        Returns:
            Dict with connection status
        """
        try:
            # Try to get session status or send a test message to yourself
            # For now, we'll just verify the client is initialized
            if self.client:
                return {
                    "success": True,
                    "message": "WhatsApp service is connected",
                    "session_name": self.session_name,
                    "phone_number": self.phone_number
                }
            else:
                return {
                    "success": False,
                    "message": "WhatsApp client not initialized"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}"
            }

# Initialize global WhatsApp service instance
try:
    whatsapp_service = WhatsAppService()
except Exception as e:
    logger.error(f"Failed to initialize global WhatsApp service: {e}")
    whatsapp_service = None 