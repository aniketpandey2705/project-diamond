import hashlib
import json
import time
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_data = []
        self.create_block(proof=1, previous_hash='0', data='Genesis Block')

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

    def add_data(self, grievance_id, audio_hash, status):
        data = {
            'grievance_id': grievance_id,
            'audio_hash': audio_hash,
            'status': status,
            'timestamp': time.time()
        }
        self.pending_data.append(data)
        return data

    def get_last_block(self):
        return self.chain[-1]

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self):
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
        is_valid, message, tampering_details = self.is_chain_valid()
        
        report = {
            'is_valid': is_valid,
            'message': message,
            'total_blocks': len(self.chain),
            'genesis_hash': self.hash(self.chain[0]),
            'latest_hash': self.hash(self.chain[-1]),
            'chain_integrity': 'VERIFIED' if is_valid else 'COMPROMISED',
            'tampering_detected': len(tampering_details) > 0,
            'tampering_details': tampering_details,
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
            
            # Extract grievance IDs from block data
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
        for block in self.chain:
            if isinstance(block['data'], list):
                for data in block['data']:
                    if isinstance(data, dict) and data.get('grievance_id') == grievance_id:
                        return {
                            'found': True,
                            'block_index': block['index'],
                            'block_hash': self.hash(block),
                            'timestamp': datetime.fromtimestamp(block['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                        }
        return {'found': False}