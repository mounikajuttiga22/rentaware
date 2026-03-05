from twilio.rest import Client

ACCOUNT_SID = "AC5b89d46f37ed2e5e91e1f6af9f12bd2b"
AUTH_TOKEN = "5e7310423ddb28b4fb9e107fc9e7ab6f"

FROM_NUMBER = "+13202335382"   # your Twilio number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(phone, message):
    try:
        message = client.messages.create(
            body=message,
            from_=FROM_NUMBER,
            to=phone
        )

        print("SMS sent successfully:", message.sid)

    except Exception as e:
        print("Error sending SMS:", e)