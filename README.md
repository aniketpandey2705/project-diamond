# PRAHARI - Blockchain-Based Grievance Management System

A secure, transparent grievance management system using blockchain technology, AI analysis, and IVR integration.

## Features

- **IVR System**: Twilio-powered voice interface for complaint registration
- **AI Analysis**: Gemini AI for automatic transcription and categorization
- **Blockchain Security**: Immutable record storage with SHA-256 hashing
- **Admin Dashboard**: Clean, minimal interface for grievance management
- **Public Verification**: Citizens can verify their complaints on blockchain
- **Multi-language Support**: Hinglish voice prompts for accessibility

## Installation

### Prerequisites

- Python 3.8 or higher
- Twilio account with phone number
- Google AI API key (Gemini)

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd prahari
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
Create a `.env` file with:
```
account_sid = 'your_twilio_account_sid'
auth_token = 'your_twilio_auth_token'
GOOGLE_API_KEY = 'your_google_ai_api_key'
twilio_number = 'your_twilio_phone_number'
my_mobile_number = 'your_verified_number'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'your_secure_password'
SECRET_KEY = 'your_secret_key_for_sessions'
```

4. Run the application
```bash
python app.py
```

5. Access the system
- Admin Dashboard: http://localhost:5000/login
- Public Verification: http://localhost:5000/verify_blockchain

## Default Credentials

- Username: `admin`
- Password: `prahari@2024`

**Important**: Change these credentials in production!

## Project Structure

```
prahari/
├── app.py                  # Main Flask application
├── blockchain.py           # Blockchain implementation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── templates/
│   ├── admin.html         # Admin dashboard
│   ├── login.html         # Login page
│   └── verify.html        # Public verification page
└── static/
    ├── style.css          # Styles
    ├── script.js          # Client-side logic
    └── recordings/        # Audio files storage
```

## Usage

### For Citizens

1. Call the Twilio number
2. Follow voice prompts to register complaint
3. Receive 6-digit ticket ID
4. Verify complaint at verification page using ticket ID

### For Administrators

1. Login at `/login`
2. View pending grievances on dashboard
3. Update status (Pending/Resolved)
4. View analytics and category breakdown
5. Access complete blockchain verification

## Security Features

- Session-based authentication
- Blockchain immutability
- Cryptographic hashing (SHA-256)
- Tamper detection
- Public verification without login

## Technology Stack

- **Backend**: Flask (Python)
- **AI**: Google Gemini AI
- **IVR**: Twilio Voice API
- **Blockchain**: Custom implementation
- **Frontend**: Vanilla JavaScript, CSS

## License

MIT License
