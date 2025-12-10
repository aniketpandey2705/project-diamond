import os
import requests
import hashlib
import random
import datetime
from flask import Flask, request, render_template, redirect, url_for, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import google.generativeai as genai
from blockchain import Blockchain

load_dotenv()

app = Flask(__name__)
prahari_chain = Blockchain()
grievance_db = {}

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# Generate time-based greeting in Hinglish
def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Namaste. Aap ka swagat hai Prahari mein."
    elif hour < 18:
        return "Namaste. Prahari helpline mein aapka swagat hai."
    else:
        return "Namaste. Prahari mein aapka swagat hai."

# Send audio to Gemini for transcription and analysis
def analyze_audio_with_ai(file_path):
    try:
        if not os.path.exists(file_path):
            return f"Error: Audio file not found"
        
        audio_file = genai.upload_file(file_path)
        
        prompt = """
        Listen to this audio grievance complaint and analyze it. Return a summary in this format:
        
        Transcription: [What the person said]
        Category: [Water/Road/Electricity/Medical/Corruption/Other]
        Summary: [1 sentence summary of the complaint]
        Sentiment: [Urgent/Calm/Angry]
        Priority: [High/Medium/Low]
        """
        
        gemini_response = gemini_model.generate_content([prompt, audio_file])
        return gemini_response.text
        
    except Exception as e:
        return f"AI Analysis Failed: {str(e)}"

# IVR entry point - greet caller and show menu
@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()
    greeting = get_greeting()
    full_message = f"{greeting} Apni shikayat register karne ke liye 1 dabayein. Status check karne ke liye 2 dabayein."
    
    gather = Gather(num_digits=1, action='/gather', method='POST')
    gather.say(full_message, voice='Polly.Aditi', language='en-IN')
    resp.append(gather)
    resp.redirect('/voice')
    return str(resp)

# Handle menu selection (1 for register, 2 for status)
@app.route("/gather", methods=['GET', 'POST'])
def gather():
    digit = request.values.get('Digits', None)
    resp = VoiceResponse()

    if digit == '1':
        resp.redirect('/ask_state')
    elif digit == '2':
        gather = Gather(num_digits=6, action='/status_result', method='POST')
        gather.say("Apna 6 digit tracking number enter karein.", voice='Polly.Aditi', language='en-IN')
        resp.append(gather)
    else:
        resp.say("Galat option. Dobara try karein.", voice='Polly.Aditi', language='en-IN')
        resp.redirect('/voice')

    return str(resp)

# Ask caller for their state
@app.route("/ask_state", methods=['GET', 'POST'])
def ask_state():
    resp = VoiceResponse()
    gather = Gather(input='speech', timeout=5, action='/save_state', method='POST', language='en-IN', speechTimeout='auto')
    gather.say("Pehle batayein, aap kis state se bol rahe hain?", voice='Polly.Aditi', language='en-IN')
    resp.append(gather)
    resp.say("Koi jawab nahi mila. Dobara try karein.", voice='Polly.Aditi', language='en-IN')
    resp.redirect('/ask_state')
    return str(resp)

# Save state and ask for city
@app.route("/save_state", methods=['GET', 'POST'])
def save_state():
    state = request.values.get('SpeechResult', None)
    if not state:
        return redirect('/ask_state')
    
    session_id = request.values.get('CallSid')
    if session_id not in grievance_db:
        grievance_db[session_id] = {}
    grievance_db[session_id]['state'] = state
    
    resp = VoiceResponse()
    gather = Gather(input='speech', timeout=5, action='/save_city', method='POST', language='en-IN', speechTimeout='auto')
    gather.say("Theek hai. Ab batayein aapka city ya district kya hai?", voice='Polly.Aditi', language='en-IN')
    resp.append(gather)
    resp.say("Koi jawab nahi mila. Dobara try karein.", voice='Polly.Aditi', language='en-IN')
    resp.redirect('/ask_city')
    return str(resp)

# Ask for city (retry route)
@app.route("/ask_city", methods=['GET', 'POST'])
def ask_city():
    resp = VoiceResponse()
    gather = Gather(input='speech', timeout=5, action='/save_city', method='POST', language='en-IN', speechTimeout='auto')
    gather.say("Aapka city ya district kya hai?", voice='Polly.Aditi', language='en-IN')
    resp.append(gather)
    resp.say("Koi jawab nahi mila. Dobara try karein.", voice='Polly.Aditi', language='en-IN')
    resp.redirect('/ask_city')
    return str(resp)

# Save city and ask for area
@app.route("/save_city", methods=['GET', 'POST'])
def save_city():
    city = request.values.get('SpeechResult', None)
    if not city:
        return redirect('/ask_city')
    
    session_id = request.values.get('CallSid')
    if session_id in grievance_db:
        grievance_db[session_id]['city'] = city
    
    resp = VoiceResponse()
    gather = Gather(input='speech', timeout=5, action='/save_location', method='POST', language='en-IN', speechTimeout='auto')
    gather.say("Aur aapka area ya mohalla kya hai?", voice='Polly.Aditi', language='en-IN')
    resp.append(gather)
    resp.say("Koi jawab nahi mila. Dobara try karein.", voice='Polly.Aditi', language='en-IN')
    resp.redirect('/ask_location')
    return str(resp)

# Ask for location (retry route)
@app.route("/ask_location", methods=['GET', 'POST'])
def ask_location():
    resp = VoiceResponse()
    gather = Gather(input='speech', timeout=5, action='/save_location', method='POST', language='en-IN', speechTimeout='auto')
    gather.say("Aapka area ya mohalla kya hai?", voice='Polly.Aditi', language='en-IN')
    resp.append(gather)
    resp.say("Koi jawab nahi mila. Dobara try karein.", voice='Polly.Aditi', language='en-IN')
    resp.redirect('/ask_location')
    return str(resp)

# Save location and start recording complaint
@app.route("/save_location", methods=['GET', 'POST'])
def save_location():
    location = request.values.get('SpeechResult', None)
    if not location:
        return redirect('/ask_location')
    
    session_id = request.values.get('CallSid')
    if session_id in grievance_db:
        grievance_db[session_id]['location'] = location
    
    resp = VoiceResponse()
    resp.say("Dhanyavaad. Ab beep ke baad apni shikayat clearly bolein.", voice='Polly.Aditi', language='en-IN')
    resp.record(maxLength=60, finishOnKey='#', playBeep=True, action='/handle_recording')
    return str(resp)

# Process recorded complaint: download, analyze with AI, save to blockchain
@app.route("/handle_recording", methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get("RecordingUrl")
    g_id = str(random.randint(100000, 999999))
    ai_analysis = "Pending Analysis"
    file_hash = "No Audio"
    local_audio_path = None

    if recording_url:
        os.makedirs('static/recordings', exist_ok=True)
        saved_filename = f"static/recordings/{g_id}.wav"
        temp_filename = f"temp_{g_id}.wav"
        
        try:
            account_sid = os.getenv('account_sid')
            auth_token = os.getenv('auth_token')
            
            response = requests.get(recording_url + ".wav", auth=(account_sid, auth_token), timeout=30)
            
            if response.status_code == 200 and len(response.content) > 1000:
                with open(temp_filename, 'wb') as f:
                    f.write(response.content)
                
                ai_analysis = analyze_audio_with_ai(temp_filename)
                
                with open(temp_filename, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                with open(temp_filename, 'rb') as src:
                    with open(saved_filename, 'wb') as dst:
                        dst.write(src.read())
                
                local_audio_path = f"/static/recordings/{g_id}.wav"
                os.remove(temp_filename)
            else:
                ai_analysis = "Audio download failed"
                
        except Exception as e:
            ai_analysis = f"Processing error: {str(e)}"

    session_id = request.values.get('CallSid')
    location_data = grievance_db.get(session_id, {})
    state = location_data.get('state', 'Not provided')
    city = location_data.get('city', 'Not provided')
    location = location_data.get('location', 'Not provided')
    
    if session_id in grievance_db:
        del grievance_db[session_id]
    
    grievance_db[g_id] = {
        'url': local_audio_path if local_audio_path else "No audio",
        'hash': file_hash,
        'status': 'Pending',
        'ai_report': ai_analysis,
        'state': state,
        'city': city,
        'location': location
    }

    prahari_chain.add_data(g_id, file_hash, 'Pending')
    previous_block = prahari_chain.get_last_block()
    previous_hash = prahari_chain.hash(previous_block)
    prahari_chain.create_block(proof=len(grievance_db), previous_hash=previous_hash) 

    resp = VoiceResponse()
    formatted_id = " ".join(g_id)
    resp.say("Aapki shikayat register ho gayi hai aur blockchain par secure kar di gayi hai.", voice='Polly.Aditi', language='en-IN')
    resp.say(f"Aapka tracking number hai {formatted_id}. Ek baar phir, {formatted_id}.", voice='Polly.Aditi', language='en-IN')
    
    return str(resp)

# Check status of existing grievance
@app.route("/status_result", methods=['GET', 'POST'])
def status_result():
    entered_id = request.values.get('Digits', None)
    resp = VoiceResponse()

    if entered_id in grievance_db:
        status = grievance_db[entered_id]['status']
        resp.say(f"Aapki shikayat ka status hai {status}.", voice='Polly.Aditi', language='en-IN')
    else:
        resp.say("Yeh number nahi mila. Kripya dobara check karein.", voice='Polly.Aditi', language='en-IN')

    return str(resp)

# Show admin dashboard with all grievances
@app.route("/")
@app.route("/admin")
def admin():
    chain_length = len(prahari_chain.chain) if hasattr(prahari_chain, 'chain') else 0
    return render_template('admin.html', db=grievance_db, chain_len=chain_length)

# Update grievance status from admin panel
@app.route("/update_status", methods=['POST'])
def update_status():
    g_id = request.form.get('g_id')
    new_status = request.form.get('new_status')
    if g_id in grievance_db:
        grievance_db[g_id]['status'] = new_status
    return redirect(url_for('admin'))

# Show blockchain verification page
@app.route("/verify_blockchain")
def verify_blockchain():
    report = prahari_chain.get_verification_report()
    return render_template('verify.html', report=report)

# API endpoint for blockchain verification (JSON)
@app.route("/api/verify", methods=['GET'])
def api_verify():
    report = prahari_chain.get_verification_report()
    return jsonify(report)

# API endpoint to verify specific grievance in blockchain
@app.route("/verify_grievance/<grievance_id>")
def verify_grievance(grievance_id):
    result = prahari_chain.find_grievance_in_chain(grievance_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)