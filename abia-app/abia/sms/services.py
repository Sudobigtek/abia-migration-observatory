import requests
from django.conf import settings
from django.utils import timezone

AFRICASTALKING_USERNAME = getattr(settings, "AFRICASTALKING_USERNAME", "")
AFRICASTALKING_API_KEY = getattr(settings, "AFRICASTALKING_API_KEY", "")
TWILIO_SID = getattr(settings, "TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = getattr(settings, "TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE = getattr(settings, "TWILIO_PHONE_NUMBER", "")

def send_sms_africastalking(phone, message, sender_id=None):
    if not AFRICASTALKING_API_KEY:
        return {"status": "error", "error": "AfricasTalking not configured"}
    url = "https://api.africastalking.com/version1/messaging"
    headers = {
        "ApiKey": AFRICASTALKING_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "username": AFRICASTALKING_USERNAME,
        "to": phone,
        "message": message,
    }
    if sender_id:
        data["from"] = sender_id
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        resp.raise_for_status()
        return {"status": "sent", "provider": "africastalking", "response": resp.json()}
    except Exception as e:
        return {"status": "error", "provider": "africastalking", "error": str(e)}

def send_sms_twilio(phone, message):
    if not TWILIO_SID or not TWILIO_TOKEN:
        return {"status": "error", "error": "Twilio not configured"}
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    data = {
        "From": TWILIO_PHONE,
        "To": phone,
        "Body": message
    }
    try:
        resp = requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_TOKEN), timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return {
            "status": "sent",
            "provider": "twilio",
            "message_id": result.get("sid"),
            "response": result
        }
    except Exception as e:
        return {"status": "error", "provider": "twilio", "error": str(e)}

def send_sms(phone, message, provider=None):
    provider = provider or getattr(settings, "DEFAULT_SMS_PROVIDER", "africastalking")
    if provider == "twilio":
        return send_sms_twilio(phone, message)
    else:
        return send_sms_africastalking(phone, message)
