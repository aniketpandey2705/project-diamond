# Ethereum Integration Guide

This project now supports Ethereum blockchain integration using Cloudflare's free public RPC endpoint.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with `lru-dict` (requires C++ build tools), you can skip it - it's optional for web3.

### 2. Deploy Smart Contract

#### Option A: Using Remix IDE (Recommended for beginners)

1. Go to [Remix IDE](https://remix.ethereum.org/)
2. Create a new file: `GrievanceRegistry.sol`
3. Copy the contract code from `contracts/GrievanceRegistry.sol`
4. Select Solidity compiler version 0.8.20
5. Compile the contract
6. Go to "Deploy & Run Transactions"
7. Connect your MetaMask wallet
8. Select "Injected Web3" as environment
9. Deploy the contract
10. Copy the contract address

#### Option B: Using Hardhat/Brownie (Advanced)

See deployment scripts in `deploy_contract.py` for reference.

### 3. Configure Environment Variables

Add these to your `.env` file:

```env
# Ethereum Configuration
ETH_RPC_URL=https://cloudflare-eth.com
CONTRACT_ADDRESS=0xYourContractAddressHere
ETH_PRIVATE_KEY=your_private_key_here

# Note: ETH_PRIVATE_KEY is only needed if you want to write to blockchain
# For read-only operations, you don't need it
```

**⚠️ Security Warning:**
- Never commit your private key to git
- Use a separate account with minimal ETH for contract interactions
- For production, use a hardware wallet or secure key management service

### 4. Get ETH (for Mainnet)

**For Mainnet:**
- You need real ETH to deploy contracts and register grievances
- Each transaction costs gas fees (varies, typically $1-50 depending on network congestion)

**For Testing (Recommended):**
- Use Sepolia testnet: `https://rpc.sepolia.org`
- Get free testnet ETH from: https://sepoliafaucet.com/
- Update `ETH_RPC_URL` to `https://rpc.sepolia.org`
- Update `chainId` in `blockchain.py` to `11155111` (Sepolia)

## 📋 How It Works

### What Gets Stored on Ethereum

**On Blockchain (Immutable):**
- Grievance ID (6-digit ticket)
- Audio file hash (SHA-256)
- Timestamp
- Block number

**In Database (Mutable):**
- Full audio file
- AI analysis report
- Location data
- Status updates
- All other metadata

### Architecture

```
┌─────────────────┐
│   Flask App     │
│   (app.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  blockchain.py  │
│  (Ethereum API) │
└────────┬────────┘
         │
         ├──► Cloudflare RPC (Free)
         │    https://cloudflare-eth.com
         │
         ▼
┌─────────────────┐
│ Smart Contract  │
│ (Ethereum)      │
└─────────────────┘
```

## 🔧 Features

### Current Implementation

- ✅ **Read Operations**: Free, no gas needed
  - Verify grievance exists
  - Get grievance details
  - Check hash integrity

- ✅ **Write Operations**: Requires ETH for gas
  - Register new grievances
  - Store hash on-chain

- ✅ **Fallback Mode**: Works without contract
  - Uses local blockchain if contract not deployed
  - Graceful degradation

### Smart Contract Functions

```solidity
// Register a new grievance
registerGrievance(string grievanceId, bytes32 audioHash)

// Check if grievance exists
grievanceExists(string grievanceId) returns (bool)

// Get grievance details
getGrievance(string grievanceId) returns (Grievance)

// Verify hash matches
verifyHash(string grievanceId, bytes32 audioHash) returns (bool)

// Get total count
getTotalGrievances() returns (uint256)
```

## 💰 Cost Estimation

### Mainnet Costs (Approximate)

- **Contract Deployment**: ~$50-200 (one-time)
- **Register Grievance**: ~$2-10 per grievance (gas fees vary)

### Testnet Costs

- **Free!** Use Sepolia testnet for development/testing

## 🛠️ Troubleshooting

### Connection Issues

```python
# Test connection
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://cloudflare-eth.com'))
print(w3.is_connected())  # Should be True
```

### Contract Not Found

- Verify `CONTRACT_ADDRESS` in `.env` is correct
- Check contract is deployed on the network you're using
- Ensure RPC URL matches the network (mainnet vs testnet)

### Transaction Failures

- Check account has sufficient ETH for gas
- Verify gas price is reasonable
- Check network congestion

### Private Key Issues

- Never share your private key
- Use environment variables, never hardcode
- Consider using a dedicated account with minimal funds

## 📚 Resources

- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Remix IDE](https://remix.ethereum.org/)
- [Ethereum Gas Tracker](https://etherscan.io/gastracker)
- [Sepolia Faucet](https://sepoliafaucet.com/)

## 🔐 Security Best Practices

1. **Never commit private keys** to version control
2. **Use testnet** for development
3. **Separate accounts** for different purposes
4. **Monitor gas prices** before transactions
5. **Verify contract code** before deployment
6. **Use hardware wallets** for production

## 🎯 Next Steps

1. Deploy contract to testnet (Sepolia)
2. Test with testnet ETH
3. Verify all functions work
4. Deploy to mainnet when ready
5. Monitor gas costs and optimize if needed

