from twilio.rest import Client

# --- CONFIGURATION ---
# Find these on your Twilio Dashboard home screen
#account_sid = '' 
#auth_token = ''

# Your Twilio Phone Number (from the dashboard)
#twilio_number = '' 

# Your Personal Mobile Number (must be verified if on Trial)
#my_mobile_number = '' 

# Your Ngrok URL (Copy from terminal, make sure to add /voice)
#webhook_url = ''
# ---------------------

client = Client(account_sid, auth_token)

print(f"Calling {my_mobile_number}...")

call = client.calls.create(
    to=my_mobile_number,
    from_=twilio_number,
    url=webhook_url
)

print(f"Call initiated! SID: {call.sid}")