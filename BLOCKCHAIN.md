# PRAHARI - Blockchain Integration Guide

Complete guide for integrating Ethereum blockchain with PRAHARI grievance management system.

## Overview

PRAHARI uses a hybrid blockchain approach:
- **Ethereum blockchain** for immutable, public verification
- **Local blockchain** as automatic fallback
- **Smart contracts** for transparent data storage
- **Free RPC endpoint** (Sepolia Public Node) - no API key needed

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRAHARI Application                      │
│                        (Flask/Python)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    blockchain.py Module                      │
│              (Hybrid Ethereum + Local Chain)                 │
└───────────┬─────────────────────────────┬───────────────────┘
            │                             │
            ▼                             ▼
┌───────────────────────┐     ┌──────────────────────────────┐
│   Ethereum Network    │     │    Local Blockchain          │
│   (via Web3.py)       │     │    (Python Implementation)   │
│                       │     │                              │
│ • Sepolia Testnet     │     │ • In-memory chain            │
│ • Ethereum Mainnet    │     │ • Automatic fallback         │
│ • Smart Contract      │     │ • No external dependencies   │
└───────────────────────┘     └──────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────┐
│           Sepolia Public RPC Endpoint (Free)               │
│       https://ethereum-sepolia.publicnode.com              │
└───────────────────────────────────────────────────────────┘
```

## What Gets Stored Where

### On Ethereum Blockchain (Immutable)
- **Grievance ID**: 6-digit ticket number
- **Audio Hash**: SHA-256 hash of audio file
- **Timestamp**: Block timestamp
- **Registered By**: Ethereum address
- **Transaction Hash**: Unique transaction identifier

### In Application Database (Mutable)
- Full audio recording file
- AI analysis report
- Location data (state, city, area)
- Status updates (Pending/Resolved)
- All other metadata

### Why This Approach?
- **Cost-effective**: Only store hash on-chain (cheap)
- **Scalable**: Large files stored off-chain
- **Verifiable**: Anyone can verify hash matches
- **Immutable**: Blockchain prevents tampering
- **Transparent**: Public verification without login

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `web3>=6.0.0` - Ethereum interaction
- `eth-account>=0.8.0` - Account management

**Note**: If you encounter build errors with `lru-dict` or `ckzg`, these are optional. The core functionality will work without them.

### 2. Test Connection

```bash
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia.publicnode.com')); print('✅ Connected!' if w3.is_connected() else '❌ Failed')"
```

Expected output: `✅ Connected!`

## Smart Contract Deployment

### Option A: Remix IDE (Recommended for Beginners)

1. **Open Remix**
   - Go to https://remix.ethereum.org/

2. **Create Contract File**
   - Create new file: `GrievanceRegistry.sol`
   - Copy content from `contracts/GrievanceRegistry.sol`

3. **Compile**
   - Select Solidity compiler version: `0.8.20`
   - Click "Compile GrievanceRegistry.sol"
   - Ensure no errors

4. **Deploy to Testnet (Sepolia)**
   - Install MetaMask browser extension
   - Switch MetaMask to Sepolia testnet
   - Get free testnet ETH from https://sepoliafaucet.com/
   - In Remix, go to "Deploy & Run Transactions"
   - Select "Injected Provider - MetaMask"
   - Click "Deploy"
   - Confirm transaction in MetaMask
   - Copy deployed contract address

5. **Deploy to Mainnet** (Production)
   - Switch MetaMask to Ethereum Mainnet
   - Ensure you have real ETH for gas fees
   - Follow same steps as testnet
   - **⚠️ Warning**: Mainnet deployment costs real money!

### Option B: Hardhat (Advanced)

```bash
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers
npx hardhat init
# Copy contract to contracts/ folder
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

### Option C: Python Web3 Deployment

```python
from web3 import Web3
from eth_account import Account
import json

# Connect
w3 = Web3(Web3.HTTPProvider('https://rpc.sepolia.org'))
account = Account.from_key('YOUR_PRIVATE_KEY')

# Load contract
with open('contracts/GrievanceRegistry.json') as f:
    contract_json = json.load(f)
    
# Deploy
Contract = w3.eth.contract(abi=contract_json['abi'], bytecode=contract_json['bytecode'])
tx = Contract.constructor().build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price
})

signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Contract deployed at: {receipt.contractAddress}")
```

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Ethereum Configuration
ETH_RPC_URL=https://ethereum-sepolia.publicnode.com
CONTRACT_ADDRESS=0xYourContractAddressHere
ETH_PRIVATE_KEY=your_private_key_here
```

### Network Options

#### Sepolia Testnet (Recommended for Testing)
```env
ETH_RPC_URL=https://ethereum-sepolia.publicnode.com
# or
ETH_RPC_URL=https://rpc.sepolia.org
```

#### Ethereum Mainnet (Production)
```env
ETH_RPC_URL=https://ethereum.publicnode.com
# or
ETH_RPC_URL=https://cloudflare-eth.com
```

#### Other Networks
```env
# Polygon Mumbai Testnet
ETH_RPC_URL=https://rpc-mumbai.maticvigil.com

# Polygon Mainnet
ETH_RPC_URL=https://polygon-rpc.com

# Arbitrum
ETH_RPC_URL=https://arb1.arbitrum.io/rpc
```

### Security Best Practices

**⚠️ CRITICAL: Never commit private keys to Git!**

1. **Use Separate Account**
   - Create dedicated account for contract interactions
   - Keep minimal ETH in this account
   - Never use your main wallet

2. **Protect Private Key**
   - Store in `.env` file (already in `.gitignore`)
   - Use environment variables in production
   - Consider hardware wallet for mainnet

3. **Verify Contract**
   - Verify contract source on Etherscan
   - Review all transactions before signing
   - Test thoroughly on testnet first

## Smart Contract Functions

### registerGrievance
```solidity
function registerGrievance(string grievanceId, bytes32 audioHash)
```
**Purpose**: Register new grievance on blockchain  
**Gas Cost**: ~100,000 gas (~$2-10 depending on network)  
**Access**: Public (anyone can call)

**Example**:
```python
# In blockchain.py
prahari_chain.add_data('123456', 'abc123...', 'Pending')
```

### getGrievance
```solidity
function getGrievance(string grievanceId) returns (Grievance)
```
**Purpose**: Retrieve grievance details  
**Gas Cost**: Free (read-only)  
**Returns**: Struct with id, hash, timestamp, address

**Example**:
```python
result = prahari_chain.find_grievance_in_chain('123456')
```

### grievanceExists
```solidity
function grievanceExists(string grievanceId) returns (bool)
```
**Purpose**: Check if grievance is registered  
**Gas Cost**: Free (read-only)

### verifyHash
```solidity
function verifyHash(string grievanceId, bytes32 audioHash) returns (bool)
```
**Purpose**: Verify audio hash matches stored hash  
**Gas Cost**: Free (read-only)

### getTotalGrievances
```solidity
function getTotalGrievances() returns (uint256)
```
**Purpose**: Get total count of registered grievances  
**Gas Cost**: Free (read-only)

## Cost Estimation

### Testnet (Sepolia)
- **Deployment**: FREE (testnet ETH)
- **Register Grievance**: FREE (testnet ETH)
- **Read Operations**: FREE (always)

Get testnet ETH:
- https://sepoliafaucet.com/
- https://faucet.sepolia.dev/
- https://sepolia-faucet.pk910.de/

### Mainnet (Ethereum)
- **Deployment**: $50-200 (one-time, varies with gas price)
- **Register Grievance**: $2-10 per transaction
- **Read Operations**: FREE

### Gas Optimization Tips
1. Batch multiple registrations if possible
2. Register during low network activity (weekends)
3. Use Layer 2 solutions (Polygon, Arbitrum) for lower fees
4. Monitor gas prices: https://etherscan.io/gastracker

## How It Works

### Registration Flow

```
1. Citizen calls IVR → Records complaint
                ↓
2. Flask app processes audio → Generates hash
                ↓
3. blockchain.py receives data
                ↓
4. Checks if Ethereum configured
                ↓
        ┌───────┴───────┐
        ▼               ▼
   Ethereum         Local Chain
   Available        (Fallback)
        │               │
        ▼               ▼
5. Calls smart    Stores in
   contract       memory
        │               │
        ▼               ▼
6. Transaction    Block created
   mined          locally
        │               │
        └───────┬───────┘
                ▼
7. Returns success + transaction hash
                ↓
8. Citizen receives 6-digit ticket ID
```

### Verification Flow

```
1. Citizen enters ticket ID on website
                ↓
2. blockchain.py searches for ID
                ↓
        ┌───────┴───────┐
        ▼               ▼
   Ethereum         Local Chain
   (Primary)        (Fallback)
        │               │
        ▼               ▼
3. Calls           Searches
   getGrievance    in-memory
                    blocks
        │               │
        └───────┬───────┘
                ▼
4. Returns: ID, Hash, Timestamp, TX Hash
                ↓
5. Displays verification details to citizen
```

## Troubleshooting

### Connection Issues

**Problem**: `❌ Ethereum connection failed`

**Solutions**:
```bash
# Test connection
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia.publicnode.com')); print(w3.is_connected())"

# Try alternative RPC
ETH_RPC_URL=https://rpc.sepolia.org

# Check internet connection
ping ethereum-sepolia.publicnode.com
```

### Contract Not Found

**Problem**: `Contract not found` or `Invalid address`

**Solutions**:
- Verify `CONTRACT_ADDRESS` in `.env` is correct (starts with `0x`)
- Ensure contract is deployed on the network you're using
- Check contract on Etherscan: `https://sepolia.etherscan.io/address/YOUR_ADDRESS`

### Transaction Failures

**Problem**: Transaction reverts or fails

**Solutions**:
```python
# Check account balance
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")

# Check gas price
gas_price = w3.eth.gas_price
print(f"Gas Price: {w3.from_wei(gas_price, 'gwei')} Gwei")

# Increase gas limit
tx = contract.functions.registerGrievance(...).build_transaction({
    'gas': 3000000,  # Increase from 2000000
    'gasPrice': w3.eth.gas_price * 2  # Double gas price
})
```

### Private Key Issues

**Problem**: `Invalid private key` or `Account not found`

**Solutions**:
- Ensure private key starts with `0x`
- Remove any spaces or newlines
- Verify key is 64 hex characters (+ `0x` prefix)
- Test key:
```python
from eth_account import Account
account = Account.from_key('YOUR_PRIVATE_KEY')
print(f"Address: {account.address}")
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'web3'`

**Solutions**:
```bash
# Reinstall dependencies
pip install --upgrade web3 eth-account

# If build errors occur
pip install web3 --no-deps
pip install eth-account eth-abi eth-hash eth-typing eth-utils hexbytes
```

## Monitoring & Verification

### View Transactions on Etherscan

**Sepolia Testnet**:
```
https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS
```

**Mainnet**:
```
https://etherscan.io/address/YOUR_CONTRACT_ADDRESS
```

### Check Contract State

```python
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('ETH_RPC_URL')))

# Load contract
contract_address = os.getenv('CONTRACT_ADDRESS')
contract_abi = [...]  # From GrievanceRegistry.json
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Get total grievances
total = contract.functions.getTotalGrievances().call()
print(f"Total Grievances: {total}")

# Check specific grievance
exists = contract.functions.grievanceExists('123456').call()
print(f"Grievance 123456 exists: {exists}")
```

### Monitor Gas Costs

```python
# Get recent transaction
tx_hash = '0x...'
receipt = w3.eth.get_transaction_receipt(tx_hash)
gas_used = receipt['gasUsed']
gas_price = w3.eth.get_transaction(tx_hash)['gasPrice']
cost_wei = gas_used * gas_price
cost_eth = w3.from_wei(cost_wei, 'ether')
print(f"Transaction cost: {cost_eth} ETH")
```

## Advanced Features

### Event Listening

Monitor new grievances in real-time:

```python
def handle_event(event):
    print(f"New grievance: {event['args']['grievanceId']}")
    print(f"Hash: {event['args']['audioHash'].hex()}")

# Create filter
event_filter = contract.events.GrievanceRegistered.create_filter(fromBlock='latest')

# Poll for events
while True:
    for event in event_filter.get_new_entries():
        handle_event(event)
    time.sleep(2)
```

### Batch Verification

Verify multiple grievances at once:

```python
def batch_verify(grievance_ids):
    results = []
    for gid in grievance_ids:
        try:
            data = contract.functions.getGrievance(gid).call()
            results.append({
                'id': gid,
                'found': True,
                'hash': data[1].hex(),
                'timestamp': data[2]
            })
        except:
            results.append({'id': gid, 'found': False})
    return results
```

### Custom RPC Endpoints

For better reliability, use multiple RPC endpoints:

```python
from web3 import Web3
from web3.middleware import geth_poa_middleware

rpcs = [
    'https://ethereum-sepolia.publicnode.com',
    'https://rpc.sepolia.org',
    'https://ethereum-sepolia.blockpi.network/v1/rpc/public'
]

for rpc in rpcs:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc))
        if w3.is_connected():
            print(f"✅ Connected to {rpc}")
            break
    except:
        continue
```

## Production Deployment

### Checklist

- [ ] Deploy contract to mainnet
- [ ] Verify contract source on Etherscan
- [ ] Test all functions on testnet first
- [ ] Set up monitoring and alerts
- [ ] Configure backup RPC endpoints
- [ ] Implement gas price optimization
- [ ] Set up transaction retry logic
- [ ] Enable error logging
- [ ] Document contract address
- [ ] Create admin dashboard for blockchain stats

### Recommended Setup

```python
# Production configuration
ETH_RPC_URL=https://ethereum-sepolia.publicnode.com
CONTRACT_ADDRESS=0xYourSepoliaContractAddress
ETH_PRIVATE_KEY=your_production_private_key

# Backup RPC
ETH_RPC_URL_BACKUP=https://rpc.sepolia.org

# Gas settings
MAX_GAS_PRICE_GWEI=50
GAS_LIMIT=200000
```

## Resources

### Documentation
- [Web3.py Docs](https://web3py.readthedocs.io/)
- [Solidity Docs](https://docs.soliditylang.org/)
- [Ethereum.org](https://ethereum.org/en/developers/)

### Tools
- [Remix IDE](https://remix.ethereum.org/) - Smart contract development
- [Etherscan](https://etherscan.io/) - Blockchain explorer
- [MetaMask](https://metamask.io/) - Wallet
- [Hardhat](https://hardhat.org/) - Development framework

### Faucets (Testnet ETH)
- [Sepolia Faucet](https://sepoliafaucet.com/)
- [Alchemy Faucet](https://sepoliafaucet.com/)
- [Chainlink Faucet](https://faucets.chain.link/)

### Gas Trackers
- [Etherscan Gas Tracker](https://etherscan.io/gastracker)
- [ETH Gas Station](https://ethgasstation.info/)
- [Blocknative Gas Estimator](https://www.blocknative.com/gas-estimator)

## Support

For blockchain-specific issues:
1. Check console logs for error messages
2. Verify contract deployment on Etherscan
3. Test connection with provided scripts
4. Review troubleshooting section above
5. Open issue on GitHub with error details

---

**Remember**: The system works perfectly fine without Ethereum configuration. It will automatically use the local blockchain fallback. Ethereum integration is optional but recommended for production transparency.
