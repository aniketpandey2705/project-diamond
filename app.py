import hashlib
import random
from flask import Flask, request, render_template, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse
from blockchain import Blockchain

app = Flask(__name__)

prahari_chain = Blockchain()
grievance_db = {}

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()
    gather = resp.gather(num_digits=1, action='/menu', method='POST')
    gather.say("Welcome to Project Prahari. Press 1 to register a grievance. Press 2 to check status.")
    resp.say("No input received. Goodbye.")
    return str(resp)

@app.route("/menu", methods=['GET', 'POST'])
def menu():
    digit_pressed = request.values.get('Digits', None)
    resp = VoiceResponse()

    if digit_pressed == '1':
        resp.say("Please state your grievance after the beep. Press hash when finished.")
        resp.record(maxLength=30, finishOnKey='#', action='/handle_recording')
    elif digit_pressed == '2':
        gather = resp.gather(num_digits=6, action='/check_status', method='POST')
        gather.say("Please enter your 6-digit grievance ID.")
    else:
        resp.say("Invalid option.")
        resp.redirect('/voice')

    return str(resp)

@app.route("/handle_recording", methods=['GET', 'POST'])
@app.route("/handle_recording", methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get('RecordingUrl', None)
    
    # FIX: Append .mp3 to the URL to make it playable in browser
    if recording_url:
        recording_url = recording_url + ".mp3"
    
    grievance_id = str(random.randint(100000, 999999))
    grievance_hash = hashlib.sha256(recording_url.encode()).hexdigest()
    
    # Store in the dictionary
    grievance_db[grievance_id] = {
        'status': 'Pending',
        'hash': grievance_hash,
        'url': recording_url 
    }
    
    # Add to blockchain (Simulation)
    previous_block = prahari_chain.get_last_block()
    previous_hash = prahari_chain.hash(previous_block)
    prahari_chain.create_block(len(grievance_db), previous_hash)

    resp = VoiceResponse()
    formatted_id = " ".join(grievance_id)
    resp.say("Grievance recorded on the blockchain.")
    resp.say(f"Your tracking ID is {formatted_id}. I repeat your tracking id is {formatted_id}")
    
    return str(resp)

@app.route("/check_status", methods=['GET', 'POST'])
def check_status():
    entered_id = request.values.get('Digits', None)
    resp = VoiceResponse()
    
    record = grievance_db.get(entered_id)

    if record:
        resp.say(f"The status of grievance {entered_id} is {record['status']}.")
    else:
        resp.say("ID not found.")
        
    return str(resp)

@app.route("/admin")
def admin_panel():
    return render_template('admin.html', db=grievance_db, chain_len=len(prahari_chain.chain))

@app.route("/update_status", methods=['POST'])
def update_status():
    g_id = request.form.get('g_id')
    new_status = request.form.get('new_status')
    
    if g_id in grievance_db:
        grievance_db[g_id]['status'] = new_status
        
    return redirect(url_for('admin_panel'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)