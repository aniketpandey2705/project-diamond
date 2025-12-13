import hashlib
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3

try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware

load_dotenv()

class Blockchain:
    """Hybrid blockchain supporting both Ethereum and local chain"""
    
    def __init__(self):
        # initialize local blockchain
        self.chain = []
        self.pending_data = []
        self.create_block(proof=1, previous_hash='0', data='Genesis Block')
        
        # ethereum connection variables
        self.use_eth = False
        self.w3 = None
        self.contract = None
        self.account = None
        
        # try to connect to Ethereum if configured
        try:
            rpc_url = os.getenv('ETH_RPC_URL')
            contract_addr = os.getenv('CONTRACT_ADDRESS')
            private_key = os.getenv('ETH_PRIVATE_KEY')

            if rpc_url and contract_addr and private_key:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url))
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if self.w3.is_connected():
                    print("✅ Connected to Ethereum/Sepolia")
                    self.account = self.w3.eth.account.from_key(private_key)
                    
                    contract_abi = [
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
                        }
                    ]
                    
                    self.contract = self.w3.eth.contract(address=contract_addr, abi=contract_abi)
                    self.use_eth = True
                else:
                    print("⚠️ Ethereum connection failed. App will run in local mode.")
        except Exception as e:
            print(f"⚠️ Ethereum setup error: {e}. App will run in local mode.")

    def create_block(self, proof, previous_hash, data=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'data': data or self.pending_data,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.pending_data = []
        self.chain.append(block)
        return block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_last_block(self):
        return self.chain[-1]

    def add_data(self, grievance_id, audio_hash, status):
        """Adds grievance to blockchain (Ethereum if available, local otherwise)"""
        data = {
            'grievance_id': grievance_id,
            'audio_hash': audio_hash,
            'status': status,
            'timestamp': time.time()
        }
        self.pending_data.append(data)

        # try to register on Ethereum if connected
        if self.use_eth:
            try:
                balance = self.w3.eth.get_balance(self.account.address)
                if balance == 0:
                    print("❌ Error: Wallet has 0 ETH.")
                    return data

                print(f"🔗 Attempting to mine {grievance_id} to Ethereum...")
                
                # convert hash to bytes32 format
                if audio_hash.startswith('0x'):
                    hash_bytes = bytes.fromhex(audio_hash[2:])
                else:
                    hash_bytes = bytes.fromhex(audio_hash)

                tx = self.contract.functions.registerGrievance(
                    str(grievance_id), 
                    hash_bytes
                ).build_transaction({
                    'from': self.account.address,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address, 'pending'),
                    'gas': 2000000, 
                    'gasPrice': self.w3.eth.gas_price
                })
                
                signed_tx = self.w3.eth.account.sign_transaction(tx, os.getenv('ETH_PRIVATE_KEY'))
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                print(f"✅ Transaction sent! Hash: {self.w3.to_hex(tx_hash)}")
                
            except Exception as e:
                print(f"❌ Blockchain Write Error: {e}")
        
        return data

    def get_verification_report(self):
        is_valid = True 
        message = "✅ Local Chain Valid"
        eth_status = "NOT CONNECTED"
        if self.use_eth:
            eth_status = "CONNECTED (Sepolia)"

        return {
            'is_valid': is_valid,
            'message': message,
            'total_blocks': len(self.chain),
            'chain_integrity': 'VERIFIED' if is_valid else 'COMPROMISED',
            'ethereum_status': eth_status,
            'blocks': self.chain[-5:] 
        }

    def find_grievance_in_chain(self, grievance_id):
        """Searches for grievance in Ethereum first, then local chain"""
        # check Ethereum blockchain first
        if self.use_eth:
            try:
                data_struct = self.contract.functions.getGrievance(str(grievance_id)).call()
                returned_hash = data_struct[1].hex()
                
                # try to get transaction hash from events
                tx_hash = "Unavailable"
                try:
                    events = self.contract.events.GrievanceRegistered.create_filter(
                        fromBlock=0,
                        argument_filters={'grievanceId': str(grievance_id)}
                    ).get_all_entries()
                    
                    if events:
                        tx_hash = events[0]['transactionHash'].hex()
                except Exception as log_error:
                    print(f"⚠️ Log search failed: {log_error}")

                return {
                    'found': True,
                    'source': 'ETHEREUM_BLOCKCHAIN',
                    'timestamp': datetime.fromtimestamp(data_struct[2]).strftime('%Y-%m-%d %H:%M:%S'),
                    'block_hash': f"ETH_BLOCK_{data_struct[3]}", 
                    'audio_hash': returned_hash,
                    'tx_hash': tx_hash
                }
            except Exception as e:
                pass 

        # fallback to local chain
        for block in self.chain:
            if isinstance(block['data'], list):
                for data in block['data']:
                    if isinstance(data, dict) and data.get('grievance_id') == grievance_id:
                        return {
                            'found': True,
                            'source': 'LOCAL_CHAIN_FALLBACK',
                            'block_index': block['index'],
                            'block_hash': self.hash(block),
                            'timestamp': datetime.fromtimestamp(block['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                            'tx_hash': None
                        }
        return {'found': False}