# Utility for sending WhatsApp/SMS using Twilio
from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to_number, message):
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', None)
    if not all([account_sid, auth_token, from_number]):
        return 'Twilio credentials not set.'
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=f'whatsapp:{from_number}',
            to=f'whatsapp:{to_number}'
        )
        return message.sid
    except Exception as e:
        return f'Twilio error: {e}'
