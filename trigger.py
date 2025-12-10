import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Get credentials from .env
account_sid = os.getenv('account_sid')
auth_token = os.getenv('auth_token')
twilio_number = os.getenv('twilio_number')
my_mobile_number = os.getenv('my_mobile_number')

# Your Ngrok URL (update this when ngrok restarts)
webhook_url = 'https://codi-interpressure-jacqui.ngrok-free.dev/voice'

# Validate credentials
if not all([account_sid, auth_token, twilio_number, my_mobile_number]):
    raise ValueError("Missing Twilio credentials in .env file")

client = Client(account_sid, auth_token)

print(f"Calling {my_mobile_number}...")

call = client.calls.create(
    to=my_mobile_number,
    from_=twilio_number,
    url=webhook_url
)

print(f"Call initiated! SID: {call.sid}")