import os
import sys
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Load environment variables
load_dotenv()

def debug_connection():
    print("🔍 STARTING DIAGNOSTIC...")
    
    # 1. Check Credentials
    rpc = os.getenv('ETH_RPC_URL')
    addr = os.getenv('CONTRACT_ADDRESS')
    key = os.getenv('ETH_PRIVATE_KEY')
    
    if not all([rpc, addr, key]):
        print("❌ MISSING .env variables! Check ETH_RPC_URL, CONTRACT_ADDRESS, ETH_PRIVATE_KEY")
        return

    print(f"📡 Connecting to: {rpc}")
    w3 = Web3(Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    if not w3.is_connected():
        print("❌ FAILED to connect to RPC. Try a different ETH_RPC_URL.")
        return
    print(f"✅ Connected to network. Chain ID: {w3.eth.chain_id}")

    # 2. Check Account
    try:
        account = w3.eth.account.from_key(key)
        balance = w3.eth.get_balance(account.address)
        eth_balance = w3.from_wei(balance, 'ether')
        print(f"👤 Account: {account.address}")
        print(f"💰 Balance: {eth_balance} ETH")
        
        if balance == 0:
            print("❌ ABORTING: You have 0 ETH. You cannot write to blockchain.")
            print("👉 Go to https://sepoliafaucet.com/ to get free ETH.")
            return
    except Exception as e:
        print(f"❌ Private Key Error: {e}")
        return

    # 3. Check Contract
    print(f"📜 Contract Address: {addr}")
    code = w3.eth.get_code(addr)
    if code == b'' or code == '0x':
        print("❌ CRITICAL ERROR: No contract found at this address!")
        print("👉 Did you deploy it? Did you copy the address correctly to .env?")
        print("👉 Are you on the right network (Sepolia)?")
        return
    else:
        print("✅ Contract code found.")

    # 4. Attempt a Test Write (The moment of truth)
    print("\n⚡ Attempting a TEST Transaction...")
    try:
        # Dummy data
        test_id = "999999"
        # Valid 32-byte hash
        test_hash = bytes.fromhex("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        
        # Manually build transaction with EIP-1559 values (More robust)
        # We define the function signature manually to ensure it matches your Solidity
        # Function: registerGrievance(string,bytes32) -> signature hash 8933b432
        
        # Simple contract wrapper
        abi = [{
            "inputs": [
                {"internalType": "string", "name": "_id", "type": "string"},
                {"internalType": "bytes32", "name": "_hash", "type": "bytes32"}
            ],
            "name": "registerGrievance",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        
        contract = w3.eth.contract(address=addr, abi=abi)
        
        # Estimate Gas (This usually reveals the specific revert reason)
        try:
            gas_estimate = contract.functions.registerGrievance(test_id, test_hash).estimate_gas({
                'from': account.address
            })
            print(f"✅ Gas Estimate successful: {gas_estimate}")
        except Exception as e:
            print(f"\n❌ TRANSACTION REVERTED DURING ESTIMATION!")
            print(f"This usually means the contract logic failed.")
            print(f"Possible reason: 'Grievance ID already exists'?")
            print(f"Full Error: {e}")
            return

        # Build & Send
        tx = contract.functions.registerGrievance(test_id, test_hash).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'maxFeePerGas': w3.to_wei('20', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('2', 'gwei'),
        })
        
        signed = w3.eth.account.sign_transaction(tx, key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"\n🎉 SUCCESS! Transaction sent.")
        print(f"🔗 Hash: {w3.to_hex(tx_hash)}")
        
    except Exception as e:
        print(f"\n❌ WRITE FAILED: {e}")

if __name__ == "__main__":
    debug_connection()