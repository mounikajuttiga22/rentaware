from twilio.rest import Client
import os

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

FROM_NUMBER = "+13202335382"

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def send_sms(phone, message):

    try:
        sms = client.messages.create(
            body=message,
            from_=FROM_NUMBER,
            to=phone
        )

        print("SMS sent successfully:", sms.sid)

    except Exception as e:
        print("Error sending SMS:", e)