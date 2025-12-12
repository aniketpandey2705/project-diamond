# Environment Variables Template

Copy the content below to create your `.env` file in the `project-diamond` directory.

## Quick Copy-Paste Template

```env
# ============================================
# PRAHARI - Grievance Management System
# Environment Variables Configuration
# ============================================
# Copy this content to .env file and fill in your actual values
# NEVER commit .env to version control!

# ============================================
# FLASK APPLICATION SETTINGS
# ============================================
# Secret key for Flask sessions (change in production!)
# Generate a secure key: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=prahari-secret-key-change-in-production

# ============================================
# ADMIN CREDENTIALS
# ============================================
# Admin dashboard login credentials
# ⚠️ CHANGE THESE IN PRODUCTION!
ADMIN_USERNAME=admin
ADMIN_PASSWORD=prahari@2024

# ============================================
# GOOGLE GEMINI AI API
# ============================================
# Required for AI audio analysis and transcription
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_gemini_api_key_here

# ============================================
# TWILIO VOICE API (IVR System)
# ============================================
# Required for voice call handling and audio recording
# Get credentials from: https://console.twilio.com/
account_sid=your_twilio_account_sid_here
auth_token=your_twilio_auth_token_here
twilio_number=+1234567890
my_mobile_number=+1234567890

# ============================================
# ETHEREUM BLOCKCHAIN CONFIGURATION
# ============================================
# Ethereum RPC endpoint (Cloudflare is free, no API key needed)
# Mainnet: https://cloudflare-eth.com
# Sepolia Testnet: https://rpc.sepolia.org
ETH_RPC_URL=https://cloudflare-eth.com

# Smart contract address (leave empty until contract is deployed)
# Get this after deploying GrievanceRegistry.sol contract
# See README_ETHEREUM.md for deployment instructions
CONTRACT_ADDRESS=

# Ethereum private key (OPTIONAL - only needed for writing to blockchain)
# ⚠️ SECURITY WARNING: Never commit this to git!
# Only needed if you want to register grievances on Ethereum
# For read-only operations, leave this empty
# Format: 0x followed by 64 hex characters (no spaces)
ETH_PRIVATE_KEY=
```

## Required vs Optional Variables

### ✅ REQUIRED Variables (App won't work without these)

1. **SECRET_KEY** - Flask session secret (has default but should be changed)
2. **ADMIN_USERNAME** - Admin login username (has default)
3. **ADMIN_PASSWORD** - Admin login password (has default)
4. **GOOGLE_API_KEY** - Required for AI analysis (no default, must be set)
5. **account_sid** - Twilio account SID (required for voice calls)
6. **auth_token** - Twilio auth token (required for voice calls)
7. **twilio_number** - Your Twilio phone number (required)
8. **my_mobile_number** - Your mobile number for testing (required)

### ⚙️ OPTIONAL Variables (App works without these)

1. **ETH_RPC_URL** - Defaults to Cloudflare if not set
2. **CONTRACT_ADDRESS** - Empty = uses local blockchain
3. **ETH_PRIVATE_KEY** - Empty = read-only mode (can't write to Ethereum)

## Setup Instructions

1. **Create .env file:**
   ```bash
   cd project-diamond
   cp ENV_TEMPLATE.md .env
   # Or manually create .env and copy the template above
   ```

2. **Fill in required values:**
   - Get Google API key: https://makersuite.google.com/app/apikey
   - Get Twilio credentials: https://console.twilio.com/
   - Generate secure SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`

3. **For Ethereum (optional):**
   - Leave CONTRACT_ADDRESS empty to use local blockchain
   - Set CONTRACT_ADDRESS after deploying contract (see README_ETHEREUM.md)
   - Set ETH_PRIVATE_KEY only if you want to write to Ethereum

## Security Notes

- ⚠️ **Never commit .env file to git** (already in .gitignore)
- ⚠️ **Change default passwords** in production
- ⚠️ **Keep ETH_PRIVATE_KEY secure** - never share or commit
- ⚠️ **Use strong SECRET_KEY** in production

## Example .env File (Minimal Setup)

```env
SECRET_KEY=your-secret-key-here-change-this
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
account_sid=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
auth_token=your_twilio_auth_token
twilio_number=+1234567890
my_mobile_number=+1234567890
ETH_RPC_URL=https://cloudflare-eth.com
```

This minimal setup will work with local blockchain (no Ethereum contract needed).

