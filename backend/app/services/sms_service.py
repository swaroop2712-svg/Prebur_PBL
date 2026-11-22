import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger("preburn.sms")


class SMSService:
    """Service to handle SMS notifications for agriculture officers with Demo and Gateway modes."""

    @staticmethod
    def format_alert_message(district_name: str, state_name: str, horizon_days: int = 3) -> str:
        """Standardized early-warning alert message."""
        return (
            f"PREBURN ALERT: High stubble-burning risk predicted in {district_name}, {state_name} "
            f"within the next {horizon_days} days. Agriculture officer intervention recommended."
        )

    @classmethod
    def send_sms(
        cls,
        phone: str,
        message: str,
        district_name: str = "",
        state_name: str = ""
    ) -> Dict[str, Any]:
        """Send an SMS notification to the agriculture officer.
        
        If provider is 'demo' or credentials are not configured, logs the message
        in DEMO SMS MODE.
        """
        if not settings.SMS_ENABLED:
            logger.info("SMS alerting is disabled in settings. Skipping dispatch.")
            return {
                "success": False,
                "mode": "disabled",
                "message": "SMS alerts disabled in settings."
            }

        recipient_phone = phone or settings.SMS_DEFAULT_OFFICER_PHONE
        provider = (settings.SMS_PROVIDER or "demo").lower()

        # Check if actual credentials exist for provider
        if provider == "twilio" and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            return cls._send_twilio(recipient_phone, message)
        elif provider == "fast2sms" and settings.FAST2SMS_API_KEY:
            return cls._send_fast2sms(recipient_phone, message)
        else:
            # DEMO SMS MODE
            return cls._send_demo(recipient_phone, message, district_name, state_name)

    @classmethod
    def _send_demo(
        cls,
        phone: str,
        message: str,
        district_name: str,
        state_name: str
    ) -> Dict[str, Any]:
        """Demo SMS mode: Logs the exact SMS message to console and server logs."""
        border = "=" * 70
        log_output = (
            f"\n{border}\n"
            f"  [PREBURN DEMO SMS GATEWAY]\n"
            f"  To (Agriculture Officer): {phone}\n"
            f"  Location: {district_name}, {state_name}\n"
            f"  Status: SIMULATED / DISPATCHED (Demo Mode)\n"
            f"  Content:\n"
            f"  \"{message}\"\n"
            f"{border}"
        )
        logger.info(log_output)
        print(log_output)

        return {
            "success": True,
            "mode": "demo",
            "provider": "demo",
            "recipient": phone,
            "message": message,
            "note": "Message simulated and logged via PreBurn Demo SMS Mode."
        }

    @classmethod
    def _send_twilio(cls, phone: str, message: str) -> Dict[str, Any]:
        """Dispatch via Twilio REST API."""
        try:
            import httpx
            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
            data = {
                "From": settings.TWILIO_FROM_PHONE,
                "To": phone,
                "Body": message
            }
            resp = httpx.post(
                url,
                data=data,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                timeout=10.0
            )
            if resp.status_code in (200, 201):
                logger.info(f"Twilio SMS dispatched to {phone}")
                return {
                    "success": True,
                    "mode": "live",
                    "provider": "twilio",
                    "recipient": phone,
                    "message": message
                }
            else:
                logger.error(f"Twilio SMS failed with status {resp.status_code}: {resp.text}")
                return {
                    "success": False,
                    "mode": "live",
                    "provider": "twilio",
                    "error": resp.text
                }
        except Exception as e:
            logger.error(f"Twilio dispatch exception: {e}")
            return {
                "success": False,
                "mode": "live",
                "provider": "twilio",
                "error": str(e)
            }

    @classmethod
    def _send_fast2sms(cls, phone: str, message: str) -> Dict[str, Any]:
        """Dispatch via Fast2SMS REST API."""
        try:
            import httpx
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {"authorization": settings.FAST2SMS_API_KEY}
            payload = {
                "route": "v3",
                "sender_id": "TXTIND",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": phone.replace("+91", "").strip()
            }
            resp = httpx.post(url, json=payload, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                logger.info(f"Fast2SMS dispatched to {phone}")
                return {
                    "success": True,
                    "mode": "live",
                    "provider": "fast2sms",
                    "recipient": phone,
                    "message": message
                }
            else:
                logger.error(f"Fast2SMS failed with status {resp.status_code}: {resp.text}")
                return {
                    "success": False,
                    "mode": "live",
                    "provider": "fast2sms",
                    "error": resp.text
                }
        except Exception as e:
            logger.error(f"Fast2SMS dispatch exception: {e}")
            return {
                "success": False,
                "mode": "live",
                "provider": "fast2sms",
                "error": str(e)
            }
