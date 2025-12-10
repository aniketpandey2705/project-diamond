import os
import requests
import hashlib
import random
import datetime
from flask import Flask, request, render_template, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import google.generativeai as genai
import whisper
from blockchain import Blockchain

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
app = Flask(__name__)
prahari_chain = Blockchain()
grievance_db = {}

# Configure Gemini from environment variable
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")
genai.configure(api_key=GOOGLE_API_KEY)

# Try different model names based on API availability
try:
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
except:
    try:
        gemini_model = genai.GenerativeModel('models/gemini-1.5-pro')
    except:
        gemini_model = genai.GenerativeModel('models/gemini-pro')

# Load Whisper model (runs locally, completely free)
whisper_model = whisper.load_model("base")  # Options: tiny, base, small, medium, large

# --- HELPER FUNCTIONS ---

def get_greeting():
    """Generate time-based greeting."""
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning. Namaste."
    elif hour < 18:
        return "Good afternoon. Namaste."
    else:
        return "Good evening. Namaste."

def analyze_audio_with_ai(file_path):
    """Step 1: Whisper transcribes audio. Step 2: Gemini analyzes the text."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: Audio file not found at {file_path}"
        
        print(f"[DEBUG] Transcribing audio: {file_path}")
        
        # Step 1: Transcribe audio using Whisper (free, local)
        result = whisper_model.transcribe(file_path, language="en", fp16=False)
        transcribed_text = result["text"]
        
        print(f"[DEBUG] Transcription: {transcribed_text}")
        
        # Step 2: Send transcription to Gemini for analysis
        prompt = f"""
        Analyze this grievance complaint and return a summary in this format:
        
        Transcription: {transcribed_text}
        
        Category: [Water/Road/Electricity/Medical/Corruption/Other]
        Summary: [1 sentence summary of the complaint]
        Sentiment: [Urgent/Calm/Angry]
        Priority: [High/Medium/Low]
        """
        
        gemini_response = gemini_model.generate_content(prompt)
        return gemini_response.text
        
    except FileNotFoundError as e:
        return f"Error: ffmpeg not found. Install it with: winget install ffmpeg"
    except Exception as e:
        print(f"[DEBUG] Analysis error: {str(e)}")
        return f"AI Analysis Failed: {str(e)}"

# --- ROUTES ---

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """The Start of the Call"""
    resp = VoiceResponse()
    
    greeting = get_greeting()
    full_message = f"{greeting} Welcome to Prahari, your grievance helpline. To register a grievance, press 1. To check status, press 2."
    
    gather = Gather(num_digits=1, action='/gather', method='POST')
    gather.say(full_message, voice='Polly.Aditi', language='en-IN')
    
    resp.append(gather)
    resp.redirect('/voice')
    return str(resp)

@app.route("/gather", methods=['GET', 'POST'])
def gather():
    """Handle Button Press"""
    digit = request.values.get('Digits', None)
    resp = VoiceResponse()

    if digit == '1':
        resp.say("Please speak your complaint clearly after the beep.", voice='Polly.Aditi', language='en-IN')
        resp.record(maxLength=60, finishOnKey='#', playBeep=True, action='/handle_recording')
    
    elif digit == '2':
        gather = Gather(num_digits=6, action='/status_result', method='POST')
        gather.say("Please enter your 6 digit tracking I D.", voice='Polly.Aditi', language='en-IN')
        resp.append(gather)
    
    else:
        resp.say("Invalid choice.", voice='Polly.Aditi', language='en-IN')
        resp.redirect('/voice')

    return str(resp)

@app.route("/handle_recording", methods=['GET', 'POST'])
def handle_recording():
    """The Core Logic: AI Analysis + Blockchain + Database"""
    recording_url = request.values.get("RecordingUrl")
    g_id = str(random.randint(100000, 999999))
    
    ai_analysis = "Pending Analysis"
    file_hash = "No Audio"
    local_audio_path = None

    if recording_url:
        # Create recordings directory if it doesn't exist
        os.makedirs('static/recordings', exist_ok=True)
        
        saved_filename = f"static/recordings/{g_id}.wav"
        temp_filename = f"temp_{g_id}.wav"
        
        try:
            # 1. Download audio file from Twilio
            print(f"[DEBUG] Downloading from: {recording_url}")
            
            # Get Twilio credentials from env
            account_sid = os.getenv('account_sid')
            auth_token = os.getenv('auth_token')
            
            # Download with authentication
            response = requests.get(
                recording_url + ".wav",
                auth=(account_sid, auth_token),
                timeout=30
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                # Save to temp file for processing
                with open(temp_filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"[DEBUG] Downloaded {len(response.content)} bytes")
                
                # 2. Transcribe and analyze with AI
                ai_analysis = analyze_audio_with_ai(temp_filename)
                
                # 3. Create Hash for Blockchain
                with open(temp_filename, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                # 4. Save permanently for admin panel
                with open(temp_filename, 'rb') as src:
                    with open(saved_filename, 'wb') as dst:
                        dst.write(src.read())
                
                local_audio_path = f"/static/recordings/{g_id}.wav"
                
                # Cleanup temp file
                os.remove(temp_filename)
            else:
                print(f"[DEBUG] Download failed: {response.status_code}")
                ai_analysis = "Audio download failed - file too small or unavailable"
                
        except Exception as e:
            print(f"[DEBUG] Recording processing error: {str(e)}")
            ai_analysis = f"Processing error: {str(e)}"

    # 4. Save everything to Mock Database
    grievance_db[g_id] = {
        'url': local_audio_path if local_audio_path else "No audio",
        'hash': file_hash,
        'status': 'Pending',
        'ai_report': ai_analysis
    }

    # 5. Add to Blockchain
    prahari_chain.add_data(g_id, file_hash, 'Pending')
    previous_block = prahari_chain.get_last_block()
    previous_hash = prahari_chain.hash(previous_block)
    prahari_chain.create_block(proof=len(grievance_db), previous_hash=previous_hash) 

    resp = VoiceResponse()
    formatted_id = " ".join(g_id)
    resp.say("I have analyzed your complaint and secured it on the blockchain.", voice='Polly.Aditi', language='en-IN')
    resp.say(f"Your tracking I D is {formatted_id}.", voice='Polly.Aditi', language='en-IN')
    
    return str(resp)

@app.route("/status_result", methods=['GET', 'POST'])
def status_result():
    entered_id = request.values.get('Digits', None)
    resp = VoiceResponse()

    if entered_id in grievance_db:
        status = grievance_db[entered_id]['status']
        resp.say(f"The status is {status}.", voice='Polly.Aditi', language='en-IN')
    else:
        resp.say("I D not found.", voice='Polly.Aditi', language='en-IN')

    return str(resp)

# --- ADMIN PANEL ROUTES ---
@app.route("/admin")
def admin():
    chain_length = len(prahari_chain.chain) if hasattr(prahari_chain, 'chain') else 0
    return render_template('admin.html', db=grievance_db, chain_len=chain_length)

@app.route("/update_status", methods=['POST'])
def update_status():
    g_id = request.form.get('g_id')
    new_status = request.form.get('new_status')
    if g_id in grievance_db:
        grievance_db[g_id]['status'] = new_status
    return redirect(url_for('admin'))

@app.route("/verify_blockchain")
def verify_blockchain():
    """API endpoint to verify blockchain integrity"""
    report = prahari_chain.get_verification_report()
    return render_template('verify.html', report=report)

@app.route("/api/verify", methods=['GET'])
def api_verify():
    """JSON API for blockchain verification"""
    from flask import jsonify
    report = prahari_chain.get_verification_report()
    return jsonify(report)

@app.route("/verify_grievance/<grievance_id>")
def verify_grievance(grievance_id):
    """Verify a specific grievance in the blockchain"""
    from flask import jsonify
    result = prahari_chain.find_grievance_in_chain(grievance_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)