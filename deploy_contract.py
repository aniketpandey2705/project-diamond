"""
Deploy GrievanceRegistry contract to Ethereum using Cloudflare RPC
This script deploys the contract and saves the contract address to .env
"""
import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import json

load_dotenv()

# Cloudflare Ethereum RPC (free, no API key needed)
RPC_URL = "https://cloudflare-eth.com"

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum network")

print(f"✅ Connected to Ethereum network")
print(f"📡 Network: Mainnet")
print(f"🔗 Latest block: {w3.eth.block_number}")

# Get deployer account from environment
PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("ETH_PRIVATE_KEY not found in .env file")

account = Account.from_key(PRIVATE_KEY)
print(f"📝 Deployer address: {account.address}")

# Check balance
balance = w3.eth.get_balance(account.address)
balance_eth = w3.from_wei(balance, 'ether')
print(f"💰 Balance: {balance_eth} ETH")

if balance == 0:
    print("\n⚠️  WARNING: Account has 0 ETH. You need ETH to deploy contracts!")
    print("   For mainnet, you need real ETH.")
    print("   For testing, use Sepolia testnet: https://rpc.sepolia.org")
    print("   Get free testnet ETH from: https://sepoliafaucet.com/")
    exit(1)

# Contract bytecode (you'll need to compile the contract first)
# For now, this is a placeholder - you'll need to compile with solc or use Remix
print("\n📄 Note: You need to compile the contract first!")
print("   Options:")
print("   1. Use Remix IDE: https://remix.ethereum.org/")
print("   2. Use solc compiler: solc --bin --abi contracts/GrievanceRegistry.sol")
print("   3. Use Brownie or Hardhat")
print("\n   After compilation, update this script with the bytecode and ABI")

# Example of how to deploy (uncomment after getting bytecode)
"""
# Load compiled contract
with open('contracts/GrievanceRegistry.json', 'r') as f:
    contract_data = json.load(f)

bytecode = contract_data['bytecode']
abi = contract_data['abi']

# Create contract instance
GrievanceRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get nonce
nonce = w3.eth.get_transaction_count(account.address)

# Build transaction
transaction = GrievanceRegistry.constructor().build_transaction({
    'from': account.address,
    'nonce': nonce,
    'gas': 2000000,  # Adjust based on contract size
    'gasPrice': w3.eth.gas_price,
    'chainId': 1  # Mainnet
})

# Sign transaction
signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

# Send transaction
print("\n🚀 Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print(f"📤 Transaction hash: {tx_hash.hex()}")

# Wait for receipt
print("⏳ Waiting for confirmation...")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ Contract deployed at: {receipt.contractAddress}")

# Save to .env
with open('.env', 'a') as f:
    f.write(f"\nCONTRACT_ADDRESS={receipt.contractAddress}\n")

print(f"\n✅ Contract address saved to .env")
"""

print("\n💡 Quick Start Guide:")
print("   1. Go to https://remix.ethereum.org/")
print("   2. Create new file: GrievanceRegistry.sol")
print("   3. Paste the contract code from contracts/GrievanceRegistry.sol")
print("   4. Compile with Solidity 0.8.20")
print("   5. Deploy using Injected Web3 (MetaMask)")
print("   6. Copy the contract address to .env as CONTRACT_ADDRESS")

