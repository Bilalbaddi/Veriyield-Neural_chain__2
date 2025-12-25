import json
import os

DB_FILE = "mock_blockchain.json"

def save_certificate(cert_data):
    """Simulates writing to the Blockchain/Database"""
    # Load existing chain
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try:
                chain = json.load(f)
            except:
                chain = []
    else:
        chain = []
    
    # Append new block
    chain.append(cert_data)
    
    # Save
    with open(DB_FILE, 'w') as f:
        json.dump(chain, f, indent=4)

def get_latest_certificate():
    """Simulates scanning the most recent QR code"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            chain = json.load(f)
            if chain:
                return chain[-1] # Return the last minted cert
    return None