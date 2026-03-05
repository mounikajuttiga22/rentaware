from twilio.rest import Client

# Twilio credentials (hardcoded)
ACCOUNT_SID = "AC5b89d46f37ed2e5e91e1f6af9f12bd2b"
AUTH_TOKEN = "b023dc262d781dc53636fd75f322f7d7"

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