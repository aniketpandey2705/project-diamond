# PRAHARI - Blockchain-Based Grievance Management System

A secure, transparent, and accessible grievance management system that combines blockchain technology, AI analysis, and voice-based IVR for seamless complaint registration and verification.

## Overview

PRAHARI is a citizen-centric platform that enables people to register complaints via phone calls in their native language (Hinglish), with automatic AI-powered analysis and immutable blockchain storage for transparency and accountability.

## Key Features

### 📱 SMS Notifications
- **Registration Confirmation**: Instant SMS with tracking ID and verification link
- **Resolution Updates**: Automatic SMS when admin resolves complaint
- No need for citizens to repeatedly call back
- Works on any phone - no smartphone required

### 🎙️ Voice-Based IVR System
- Twilio-powered voice interface with Hinglish prompts
- No app or internet required - just a phone call
- Speech recognition for location and complaint details
- Time-based greetings for personalized experience
- 60-second audio recording for detailed complaints
- **SMS acknowledgment** with tracking ID sent immediately after registration
- **SMS notification** when grievance is resolved by admin

### 🤖 AI-Powered Analysis
- Google Gemini AI for automatic transcription
- Intelligent categorization (Water/Road/Electricity/Medical/Corruption/Other)
- Sentiment analysis (Urgent/Calm/Angry)
- Priority detection (High/Medium/Low)
- Automated summary generation

### 🔗 Blockchain Security
- Dual blockchain support: Ethereum + Local fallback
- Immutable record storage with SHA-256 hashing
- Smart contract integration for public verification
- Tamper-proof audit trail
- Transparent verification without login

### 📊 Admin Dashboard
- Clean, minimal interface for grievance management
- Real-time status updates (Pending/Resolved)
- Analytics with category breakdown
- Audio playback and AI report viewing
- Complete blockchain verification

### 🔍 Public Verification
- Citizens can verify complaints using 6-digit ticket ID
- No login required for transparency
- Blockchain-backed proof of registration
- Transaction hash and timestamp verification

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask (Python 3.8+) |
| AI/ML | Google Gemini AI |
| Voice/IVR | Twilio Voice API |
| Blockchain | Ethereum (Sepolia/Mainnet) + Custom Local Chain |
| Smart Contracts | Solidity 0.8.20 |
| Web3 | Web3.py |
| Frontend | Vanilla JavaScript, CSS |
| Database | In-memory (Python dict) |

## Installation

### Prerequisites

- Python 3.8 or higher
- Twilio account with phone number
- Google AI API key (Gemini)
- MetaMask wallet (for Ethereum deployment)
- Git

### Quick Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd prahari
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the root directory:

```env
# Twilio Configuration
account_sid=your_twilio_account_sid
auth_token=your_twilio_auth_token
twilio_number=+1234567890
my_mobile_number=+1234567890

# Google AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=prahari@2024
SECRET_KEY=your_secret_session_key

# Ethereum Configuration (Optional - see BLOCKCHAIN.md)
ETH_RPC_URL=https://ethereum-sepolia.publicnode.com
CONTRACT_ADDRESS=0xYourContractAddressHere
ETH_PRIVATE_KEY=your_private_key_here
```

4. **Run the application**
```bash
python app.py
```

5. **Set up ngrok for Twilio (Development)**
```bash
# In a new terminal
ngrok http 5000
```
Copy the HTTPS URL and configure it in Twilio (see Configuration section below)

6. **Access the system**
- Admin Dashboard: http://localhost:5000/login
- Public Verification: http://localhost:5000/verify_blockchain
- IVR: Call your Twilio number
- ngrok Dashboard: http://localhost:4040

## Project Structure

```
prahari/
├── app.py                      # Main Flask application
├── blockchain.py               # Blockchain implementation (Ethereum + Local)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
├── BLOCKCHAIN.md               # Blockchain integration guide
├── SETUP.md                    # Detailed setup instructions
├── contracts/
│   ├── GrievanceRegistry.sol  # Smart contract source
│   └── GrievanceRegistry.json # Contract ABI
├── templates/
│   ├── admin.html             # Admin dashboard
│   ├── login.html             # Login page
│   └── verify.html            # Public verification page
└── static/
    ├── style.css              # Styles
    ├── script.js              # Client-side logic
    └── recordings/            # Audio files storage (auto-created)
```

## Usage Guide

### For Citizens

1. **Register a Complaint**
   - Call the Twilio number
   - Press 1 to register a new complaint
   - Provide your state, city, and area when prompted
   - Record your complaint after the beep (max 60 seconds)
   - Note down the 6-digit ticket ID announced
   - **Receive SMS confirmation** with tracking link

2. **Check Status**
   - Call the Twilio number
   - Press 2 to check status
   - Enter your 6-digit ticket ID
   - Or click the link in your SMS

3. **Verify on Blockchain**
   - Visit http://localhost:5000/verify_blockchain
   - Enter your 6-digit ticket ID
   - View blockchain verification details

4. **Get Resolution Updates**
   - **Automatic SMS notification** when admin resolves your complaint
   - No need to keep calling back

### For Administrators

1. **Login**
   - Navigate to http://localhost:5000/login
   - Enter credentials (default: admin/prahari@2024)

2. **Dashboard Views**
   - **Dashboard**: View pending grievances
   - **All Grievances**: View complete list
   - **Analytics**: View statistics and category breakdown

3. **Manage Grievances**
   - Click on any grievance to view details
   - Listen to audio recordings
   - Read AI analysis reports
   - Update status (Pending → Resolved)
   - **SMS automatically sent** to citizen when marked as Resolved

## Security Features

- **Session-based authentication** with secure cookies
- **Blockchain immutability** prevents data tampering
- **Cryptographic hashing (SHA-256)** for audio files
- **Smart contract verification** on Ethereum
- **Public verification** without exposing admin access
- **Environment variable protection** for sensitive keys

## Default Credentials

**⚠️ IMPORTANT: Change these in production!**

- Username: `admin`
- Password: `prahari@2024`

Update in `.env`:
```env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_secure_password
```

## API Endpoints

### Public Endpoints
- `GET /verify_blockchain?id=123456` - Verify grievance on blockchain
- `GET /verify_grievance/<id>` - Get grievance verification JSON
- `POST /voice` - Twilio IVR webhook

### Protected Endpoints (Login Required)
- `GET /admin` - Admin dashboard
- `GET /all_grievances` - View all grievances
- `GET /analytics` - View analytics
- `POST /update_status` - Update grievance status

## Blockchain Integration

PRAHARI supports two blockchain modes:

1. **Ethereum Mode** (Recommended for production)
   - Uses Sepolia testnet or Ethereum mainnet
   - Smart contract for immutable storage
   - Public verification via Etherscan
   - See [BLOCKCHAIN.md](BLOCKCHAIN.md) for setup

2. **Local Mode** (Automatic fallback)
   - Custom blockchain implementation
   - Works without Ethereum configuration
   - Suitable for development/testing

The system automatically uses Ethereum if configured, otherwise falls back to local blockchain.

## Configuration

### Twilio Setup
1. Create account at https://www.twilio.com
2. Get a phone number with voice capabilities
3. Configure webhook URL: `https://your-domain.com/voice`
4. Add credentials to `.env`

### Using ngrok for Local Development

Since Twilio needs a public URL to send webhooks, use ngrok to expose your local server:

1. **Install ngrok**
   - Download from https://ngrok.com/download
   - Or install via package manager:
   ```bash
   # Windows (Chocolatey)
   choco install ngrok
   
   # Mac
   brew install ngrok
   
   # Linux
   snap install ngrok
   ```

2. **Start your Flask app**
   ```bash
   python app.py
   ```
   Your app runs on `http://localhost:5000`

3. **Start ngrok in a new terminal**
   ```bash
   ngrok http 5000
   ```
   
   You'll see output like:
   ```
   Forwarding  https://abc123.ngrok.io -> http://localhost:5000
   ```

4. **Configure Twilio Dashboard**
   
   This is where you tell the phone number to use your code:
   
   - Log in to your [Twilio Console](https://console.twilio.com/)
   - Go to **Phone Numbers** → **Manage** → **Active Numbers**
   - Click on your **Trial Number** (e.g., +1 555...)
   - Scroll down to the **"Voice & Fax"** section
   - Find the field labeled **"A Call Comes In"**
   - Ensure the dropdown is set to **Webhook**
   - Paste your ngrok URL and add `/voice` at the end
     - Format: `[YOUR_NGROK_URL]/voice`
     - Example: `https://a1b2-c3d4.ngrok-free.app/voice`
   - Make sure **HTTP Method** is set to **POST**
   - Click **Save** (usually at the bottom of the page)

5. **Test the system**
   - Call your Twilio number
   - The call will be forwarded to your local Flask app via ngrok
   - Check ngrok dashboard at `http://localhost:4040` to see requests

**Important Notes:**
- Free ngrok URLs change every time you restart ngrok
- Update Twilio webhook URL each time you restart ngrok
- For production, use a permanent domain (Heroku, AWS, etc.)
- Keep ngrok running while testing

### Google AI Setup
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env` as `GOOGLE_API_KEY`

### Ethereum Setup (Optional)
See [BLOCKCHAIN.md](BLOCKCHAIN.md) for detailed instructions on:
- Deploying smart contract
- Configuring Web3 connection
- Using testnet vs mainnet
- Gas cost estimation

## Troubleshooting

### Audio Not Recording
- Check Twilio webhook configuration
- Verify `account_sid` and `auth_token` in `.env`
- Ensure recordings folder has write permissions
- **Check ngrok is running** and URL is updated in Twilio

### SMS Not Sending
- Verify `twilio_number` is set correctly in `.env`
- Check Twilio account has SMS capabilities enabled
- For trial accounts, verify recipient number is verified in Twilio
- Check console logs for SMS error messages

### ngrok Issues
- **URL changed**: Restart ngrok and update Twilio webhook URL
- **Connection refused**: Make sure Flask app is running on port 5000
- **Timeout errors**: Check firewall settings
- **View requests**: Open `http://localhost:4040` to see ngrok dashboard

### AI Analysis Failing
- Verify `GOOGLE_API_KEY` is valid
- Check audio file size (should be > 1KB)
- Review console logs for API errors

### Blockchain Connection Issues
- For Ethereum: Check `ETH_RPC_URL` and `CONTRACT_ADDRESS`
- System will automatically fallback to local blockchain
- See [BLOCKCHAIN.md](BLOCKCHAIN.md) for detailed troubleshooting

### Login Issues
- Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`
- Clear browser cookies and try again
- Check `SECRET_KEY` is set

## Development

### Running in Debug Mode
```bash
python app.py
```
Flask debug mode is enabled by default in `app.py`.

### Testing Ethereum Connection
```bash
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia.publicnode.com')); print('Connected!' if w3.is_connected() else 'Failed')"
```

### Viewing Logs
Check console output for:
- ✅ Successful operations
- ⚠️ Warnings and fallbacks
- ❌ Errors and failures

## Deployment

### Production Checklist
- [ ] Change default admin credentials
- [ ] Use strong `SECRET_KEY`
- [ ] Deploy smart contract to mainnet
- [ ] Configure production Twilio number
- [ ] Set up HTTPS with SSL certificate
- [ ] Use production-grade database (PostgreSQL/MongoDB)
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Review security best practices

### Recommended Hosting
- **Backend**: Heroku, AWS, DigitalOcean, Railway
- **Blockchain**: Ethereum mainnet or Polygon
- **Storage**: AWS S3 for audio files
- **Database**: PostgreSQL or MongoDB
- **No ngrok needed**: Use permanent domain with HTTPS

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check [BLOCKCHAIN.md](BLOCKCHAIN.md) for blockchain-specific help
- Check [SETUP.md](SETUP.md) for installation help
- Review console logs for error messages
- Open an issue on GitHub

## Acknowledgments

- Twilio for voice infrastructure
- Google for Gemini AI
- Ethereum community for blockchain technology
- Cloudflare for free RPC endpoint

---

**Built with ❤️ for transparent governance and citizen empowerment**
