"""
Ethereum Blockchain Integration using Cloudflare RPC
Connects to Ethereum mainnet via Cloudflare's free public RPC
"""
import os
import json
import hashlib
from datetime import datetime
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()

# Cloudflare Ethereum RPC (free, no API key)
RPC_URL = os.getenv('ETH_RPC_URL', 'https://cloudflare-eth.com')

# Contract address (set after deployment)
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')

# Private key for transactions (optional - only needed for writing)
PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY', '')

# Contract ABI
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_grievanceId", "type": "string"},
            {"internalType": "bytes32", "name": "_audioHash", "type": "bytes32"}
        ],
        "name": "registerGrievance",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "_grievanceId", "type": "string"}],
        "name": "getGrievance",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "grievanceId", "type": "string"},
                    {"internalType": "bytes32", "name": "audioHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "address", "name": "registeredBy", "type": "address"}
                ],
                "internalType": "struct GrievanceRegistry.Grievance",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "_grievanceId", "type": "string"}],
        "name": "grievanceExists",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getTotalGrievances",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_grievanceId", "type": "string"},
            {"internalType": "bytes32", "name": "_audioHash", "type": "bytes32"}
        ],
        "name": "verifyHash",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "grievanceId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "audioHash", "type": "bytes32"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "registeredBy", "type": "address"}
        ],
        "name": "GrievanceRegistered",
        "type": "event"
    }
]


class Blockchain:
    """
    Ethereum-based blockchain integration for grievance registry
    Uses Cloudflare's free public RPC endpoint
    """
    
    def __init__(self):
        """Initialize connection to Ethereum network"""
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum network")
        
        # Initialize contract if address is provided
        self.contract = None
        if CONTRACT_ADDRESS:
            try:
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                    abi=CONTRACT_ABI
                )
                print(f"✅ Connected to contract at {CONTRACT_ADDRESS}")
            except Exception as e:
                print(f"⚠️  Warning: Could not connect to contract: {e}")
                print("   Contract operations will be disabled until CONTRACT_ADDRESS is set")
        
        # Fallback: maintain local chain for compatibility
        self.chain = []
        self.pending_data = []
        self.create_block(proof=1, previous_hash='0', data='Genesis Block')
    
    def create_block(self, proof=1, previous_hash='0', data=None):
        """Create a local block (for compatibility/fallback)"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now().timestamp(),
            'data': data or self.pending_data,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.pending_data = []
        self.chain.append(block)
        return block
    
    def add_data(self, grievance_id, audio_hash, status='Pending'):
        """
        Add grievance data to blockchain
        
        Args:
            grievance_id: 6-digit ticket ID
            audio_hash: SHA-256 hash of audio file (hex string)
            status: Status of grievance (for local storage only)
        
        Returns:
            dict: Transaction receipt or local data
        """
        # Convert hex hash to bytes32
        if isinstance(audio_hash, str):
            # Remove '0x' prefix if present
            audio_hash = audio_hash.replace('0x', '')
            # Convert to bytes32
            audio_hash_bytes = bytes.fromhex(audio_hash)
            if len(audio_hash_bytes) != 32:
                raise ValueError(f"Hash must be 32 bytes (64 hex chars), got {len(audio_hash_bytes)}")
            audio_hash_bytes32 = _to_bytes32(audio_hash_bytes)
        else:
            audio_hash_bytes32 = _to_bytes32(audio_hash) if len(audio_hash) != 32 else audio_hash
        
        # Store locally for compatibility
        data = {
            'grievance_id': grievance_id,
            'audio_hash': audio_hash,
            'status': status,
            'timestamp': datetime.now().timestamp()
        }
        self.pending_data.append(data)
        
        # If contract is available and private key is set, register on Ethereum
        if self.contract and PRIVATE_KEY:
            try:
                account = Account.from_key(PRIVATE_KEY)
                nonce = self.w3.eth.get_transaction_count(account.address)
                
                # Estimate gas
                gas_estimate = self.contract.functions.registerGrievance(
                    grievance_id,
                    audio_hash_bytes32
                ).estimate_gas({'from': account.address})
                
                # Build transaction
                transaction = self.contract.functions.registerGrievance(
                    grievance_id,
                    audio_hash_bytes32
                ).build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gas': int(gas_estimate * 1.2),  # Add 20% buffer
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': 1  # Mainnet
                })
                
                # Sign and send
                signed_txn = self.w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                # Wait for receipt
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                print(f"✅ Grievance {grievance_id} registered on Ethereum")
                print(f"   Transaction: {tx_hash.hex()}")
                print(f"   Block: {receipt.blockNumber}")
                
                return {
                    'tx_hash': tx_hash.hex(),
                    'block_number': receipt.blockNumber,
                    'status': 'success'
                }
            except Exception as e:
                print(f"⚠️  Failed to register on Ethereum: {e}")
                print("   Storing locally only")
                return data
        else:
            if not self.contract:
                print("⚠️  Contract not deployed. Storing locally only.")
            if not PRIVATE_KEY:
                print("⚠️  ETH_PRIVATE_KEY not set. Storing locally only.")
            return data
    
    def get_last_block(self):
        """Get the last block from local chain"""
        return self.chain[-1] if self.chain else None
    
    def hash(self, block):
        """Hash a block (for local chain compatibility)"""
        encoded_block = json.dumps(block, sort_keys=True, default=str).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self):
        """Validate local chain integrity"""
        if len(self.chain) <= 1:
            return True, "✅ Blockchain is valid", []
        
        previous_block = self.chain[0]
        block_index = 1
        tampering_details = []
        
        while block_index < len(self.chain):
            block = self.chain[block_index]
            expected_previous_hash = self.hash(previous_block)
            actual_previous_hash = block['previous_hash']
            
            if actual_previous_hash != expected_previous_hash:
                tampering_details.append({
                    'block_index': block_index,
                    'error_type': 'HASH_MISMATCH',
                    'expected_hash': expected_previous_hash,
                    'actual_hash': actual_previous_hash,
                    'message': f"Block {block_index} references incorrect previous hash"
                })
                return False, f"⚠️ TAMPERING DETECTED at Block {block_index}", tampering_details
            
            previous_block = block
            block_index += 1
        
        return True, "✅ Blockchain is valid and immutable", []
    
    def get_verification_report(self):
        """Get verification report for local chain"""
        is_valid, message, tampering_details = self.is_chain_valid()
        
        # Get Ethereum network info
        try:
            latest_block = self.w3.eth.block_number
            network_name = "Ethereum Mainnet"
        except:
            latest_block = 0
            network_name = "Not Connected"
        
        report = {
            'is_valid': is_valid,
            'message': message,
            'total_blocks': len(self.chain),
            'genesis_hash': self.hash(self.chain[0]) if self.chain else None,
            'latest_hash': self.hash(self.chain[-1]) if self.chain else None,
            'chain_integrity': 'VERIFIED' if is_valid else 'COMPROMISED',
            'tampering_detected': len(tampering_details) > 0,
            'tampering_details': tampering_details,
            'ethereum_network': network_name,
            'ethereum_latest_block': latest_block,
            'contract_address': CONTRACT_ADDRESS if CONTRACT_ADDRESS else 'Not Deployed',
            'blocks': []
        }
        
        previous_block = None
        for block in self.chain:
            block_hash = self.hash(block)
            is_block_valid = True
            error_message = None
            
            if previous_block:
                expected_prev_hash = self.hash(previous_block)
                if block['previous_hash'] != expected_prev_hash:
                    is_block_valid = False
                    error_message = "Hash chain broken - data may have been altered"
            
            grievance_ids = []
            if isinstance(block['data'], list):
                for data in block['data']:
                    if isinstance(data, dict) and 'grievance_id' in data:
                        grievance_ids.append(data['grievance_id'])
            
            report['blocks'].append({
                'index': block['index'],
                'hash': block_hash,
                'previous_hash': block['previous_hash'],
                'timestamp': datetime.fromtimestamp(block['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                'data_count': len(block['data']) if isinstance(block['data'], list) else 1,
                'grievance_ids': grievance_ids,
                'is_valid': is_block_valid,
                'error_message': error_message
            })
            
            previous_block = block
        
        return report
    
    def find_grievance_in_chain(self, grievance_id):
        """
        Find grievance in blockchain (checks both Ethereum and local chain)
        
        Args:
            grievance_id: The 6-digit ticket ID
        
        Returns:
            dict: Grievance information if found
        """
        # First check Ethereum contract if available
        if self.contract:
            try:
                exists = self.contract.functions.grievanceExists(grievance_id).call()
                if exists:
                    grievance = self.contract.functions.getGrievance(grievance_id).call()
                    return {
                        'found': True,
                        'blockchain': 'Ethereum',
                        'grievance_id': grievance[0],
                        'audio_hash': grievance[1].hex(),
                        'timestamp': datetime.fromtimestamp(grievance[2]).strftime('%Y-%m-%d %H:%M:%S'),
                        'registered_by': grievance[3]
                    }
            except Exception as e:
                print(f"⚠️  Error checking Ethereum: {e}")
        
        # Fallback to local chain
        for block in self.chain:
            if isinstance(block['data'], list):
                for data in block['data']:
                    if isinstance(data, dict) and data.get('grievance_id') == grievance_id:
                        return {
                            'found': True,
                            'blockchain': 'Local',
                            'block_index': block['index'],
                            'block_hash': self.hash(block),
                            'timestamp': datetime.fromtimestamp(data.get('timestamp', block['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                        }
        
        return {'found': False}


def _to_bytes32(data):
    """Convert bytes to bytes32 (pad or truncate to 32 bytes)"""
    if isinstance(data, str):
        data = bytes.fromhex(data.replace('0x', ''))
    if len(data) > 32:
        return data[:32]
    elif len(data) < 32:
        return data + b'\x00' * (32 - len(data))
    return data
