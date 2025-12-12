# Setup Instructions

## ✅ Installation Steps

### 1. Install Python Dependencies

```bash
cd project-diamond
pip install -r requirements.txt
```

**Note:** If you encounter build errors with `lru-dict` or `ckzg`:
- These are optional dependencies
- The app will work without them for basic functionality
- You can install web3 dependencies manually:

```bash
pip install web3 eth-account eth-abi eth-hash eth-typing eth-utils hexbytes websockets pyunormalize bitarray eth-keyfile eth-keys eth-rlp rlp py_ecc pycryptodome
```

### 2. Test Ethereum Connection

```bash
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://cloudflare-eth.com')); print('✅ Connected!' if w3.is_connected() else '❌ Failed')"
```

### 3. Configure Environment Variables

Create or update `.env` file:

```env
# Existing variables
GOOGLE_API_KEY=your_google_api_key
account_sid=your_twilio_account_sid
auth_token=your_twilio_auth_token
twilio_number=your_twilio_number
my_mobile_number=your_mobile_number
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
SECRET_KEY=your_secret_key

# Ethereum Configuration (NEW)
ETH_RPC_URL=https://cloudflare-eth.com
CONTRACT_ADDRESS=  # Leave empty until contract is deployed
ETH_PRIVATE_KEY=   # Optional - only needed for writing to blockchain
```

### 4. Deploy Smart Contract

See `README_ETHEREUM.md` for detailed deployment instructions.

**Quick Start:**
1. Go to https://remix.ethereum.org/
2. Copy `contracts/GrievanceRegistry.sol`
3. Compile with Solidity 0.8.20
4. Deploy using MetaMask
5. Copy contract address to `.env` as `CONTRACT_ADDRESS`

### 5. Run the Application

```bash
python app.py
```

The app will:
- ✅ Work in **read-only mode** without contract (uses local blockchain)
- ✅ Work in **full mode** with contract deployed
- ✅ Automatically use Ethereum if contract address is configured

## 🎯 What's New

### Ethereum Integration
- Smart contract for storing grievance hashes
- Cloudflare free RPC endpoint (no API key needed)
- Automatic fallback to local blockchain if contract not deployed

### Files Added
- `contracts/GrievanceRegistry.sol` - Smart contract
- `contracts/GrievanceRegistry.json` - Contract ABI
- `deploy_contract.py` - Deployment helper script
- `README_ETHEREUM.md` - Detailed Ethereum guide
- Updated `blockchain.py` - Ethereum integration

### Files Modified
- `blockchain.py` - Now supports Ethereum + local fallback
- `app.py` - Updated to work with new blockchain module
- `requirements.txt` - Added web3 and eth-account

## 🔧 Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'web3'`:
```bash
pip install web3 eth-account
```

### Connection Issues
If Ethereum connection fails:
- Check internet connection
- Verify Cloudflare RPC is accessible: https://cloudflare-eth.com
- The app will fallback to local blockchain automatically

### Contract Not Working
If contract operations fail:
- Verify `CONTRACT_ADDRESS` in `.env` is correct
- Check contract is deployed on the network you're using
- Ensure `ETH_PRIVATE_KEY` is set if writing to blockchain

## 📝 Next Steps

1. ✅ Install dependencies
2. ✅ Test connection
3. ⏳ Deploy contract (optional - app works without it)
4. ⏳ Configure `.env` with contract address
5. ✅ Run and test!

For detailed Ethereum setup, see `README_ETHEREUM.md`

