# Prahari Blockchain Verification Guide

## How Blockchain Ensures Immutability

### 1. **Cryptographic Hashing (SHA-256)**
Every block contains:
- Block data (grievance ID, audio hash, status)
- Timestamp
- Previous block's hash
- Current block's hash

When you hash a block, even changing a single character changes the entire hash completely.

### 2. **Chain Linking**
```
Block 1 (Genesis)
├─ Hash: abc123...
└─ Previous: 0

Block 2
├─ Hash: def456...
└─ Previous: abc123... ← Links to Block 1

Block 3
├─ Hash: ghi789...
└─ Previous: def456... ← Links to Block 2
```

### 3. **Tamper Detection**
If someone tries to modify Block 2:
- Block 2's hash changes
- Block 3's "previous hash" no longer matches
- **Chain breaks** → Tampering detected!

## Verification Features in Prahari

### 1. **Full Chain Verification**
Visit: `http://localhost:5000/verify_blockchain`

Shows:
- ✅ Total blocks mined
- ✅ Genesis block hash
- ✅ Latest block hash
- ✅ Complete chain with all hashes
- ✅ Verification status (VERIFIED/COMPROMISED)

### 2. **Individual Grievance Verification**
API: `GET /verify_grievance/<grievance_id>`

Returns:
```json
{
  "found": true,
  "block_index": 5,
  "block_hash": "abc123...",
  "timestamp": "2025-12-09 15:30:45"
}
```

### 3. **Real-time Verification Badge**
Each grievance card shows:
- 🛡️ **Verified** badge (green, pulsing)
- Full SHA-256 hash
- Copy-to-clipboard functionality

## How to Prove Immutability

### Method 1: Visual Verification
1. Go to Admin Dashboard
2. Click **"Verify Chain"** button (top right)
3. See complete blockchain with all hashes
4. Status shows: **VERIFIED** ✅

### Method 2: API Verification
```bash
curl http://localhost:5000/api/verify
```

Returns JSON with full verification report.

### Method 3: Manual Hash Verification
1. Copy any block's hash from verification page
2. Copy the previous block's data
3. Generate SHA-256 hash yourself
4. Compare - they must match!

## Why This Proves Immutability

### ❌ **What Attackers CANNOT Do:**
1. **Modify a grievance** - Changes the block hash
2. **Delete a grievance** - Breaks the chain
3. **Fake a grievance** - No matching previous hash
4. **Reorder blocks** - Hash sequence breaks

### ✅ **What the System GUARANTEES:**
1. **Tamper-proof records** - Any change is detected
2. **Chronological order** - Timestamps are locked
3. **Audit trail** - Complete history preserved
4. **Transparency** - Anyone can verify

## Technical Implementation

### Blockchain Class Methods:
```python
# Add grievance to blockchain
prahari_chain.add_data(grievance_id, audio_hash, status)

# Create new block
prahari_chain.create_block(proof, previous_hash)

# Verify entire chain
is_valid, message = prahari_chain.is_chain_valid()

# Get verification report
report = prahari_chain.get_verification_report()

# Find grievance in chain
result = prahari_chain.find_grievance_in_chain(grievance_id)
```

### Hash Generation:
```python
def hash(self, block):
    encoded_block = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(encoded_block).hexdigest()
```

## Real-World Example

### Scenario: Someone tries to change a grievance status

**Before Attack:**
```
Block 5: Hash = abc123...
├─ Grievance: #123456
├─ Status: Pending
└─ Previous: xyz789...

Block 6: Hash = def456...
└─ Previous: abc123... ✅ MATCHES
```

**After Attack (Status changed to "Resolved"):**
```
Block 5: Hash = CHANGED999... ❌
├─ Grievance: #123456
├─ Status: Resolved (TAMPERED!)
└─ Previous: xyz789...

Block 6: Hash = def456...
└─ Previous: abc123... ❌ DOESN'T MATCH!
```

**Result:** Verification fails! Tampering detected immediately.

## Verification Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/verify_blockchain` | GET | Full verification page (HTML) |
| `/api/verify` | GET | Verification report (JSON) |
| `/verify_grievance/<id>` | GET | Individual grievance verification |

## Security Features

1. **SHA-256 Hashing** - Industry standard, collision-resistant
2. **Chain Linking** - Each block references previous
3. **Timestamps** - Chronological proof
4. **Immutable Storage** - Cannot be altered retroactively
5. **Public Verification** - Anyone can verify integrity

## Conclusion

Prahari's blockchain implementation provides **cryptographic proof** that grievance records are:
- ✅ **Authentic** - Not forged
- ✅ **Unaltered** - Not modified
- ✅ **Complete** - Not deleted
- ✅ **Chronological** - Correct order

This makes it ideal for government accountability and transparent grievance redressal.
