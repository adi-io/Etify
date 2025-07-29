import time, json
import requests
import os
from web3 import Web3
from decimal import Decimal
from dotenv import load_dotenv

from blockchain_utils import bytes32_to_string, cut_returned_hash, dspy_to_wei, wei_to_dspy, wei_to_usdc

load_dotenv()

INCH_API_BASE = "https://api.1inch.dev/history/v2.0"
API_KEY = os.getenv("1INCH_API")
TRANSACTIONGATEWAY_ADDRESS = os.getenv("TRANSACTIONGATEWAY_ADDRESS")
TOKEN_ISSUER_ADDRESS = os.getenv("DSPY_ADDRESS")
BASE_CHAIN_ID = os.getenv("BASE_CHAIN_ID")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


last_processed_timestamp = int(time.time() * 1000)  # Convert to milliseconds

def get_contract_events(contract_address, from_timestamp_ms, to_timestamp_ms):
    """Get events for a specific contract using 1inch history API"""
    url = f"{INCH_API_BASE}/history/{contract_address}/events"
    
    params = {
        "limit": 100,
        "chainId": BASE_CHAIN_ID,
        "fromTimestampMs": from_timestamp_ms,
        "toTimestampMs": to_timestamp_ms
    }
    
    # print(f"🔍 DEBUG - URL: {url}")
    # print(f"🔍 DEBUG - Params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        # print(f"🔍 DEBUG - Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"🔍 DEBUG - Response Text: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"🚫 1inch API request failed: {e}")
        return None

def decode_event_data(event_data_hex):
    """Decode event data hex string to get tokenAmount and frontendHash"""
    try:
        # Remove '0x' prefix if present
        if event_data_hex.startswith('0x'):
            event_data_hex = event_data_hex[2:]
        
        # Each parameter is 32 bytes (64 hex chars)
        # tokenAmount (uint256) - first 32 bytes
        token_amount_hex = event_data_hex[:64]
        token_amount = int(token_amount_hex, 16)
        
        # frontendHash (bytes32) - next 32 bytes
        frontend_hash_hex = event_data_hex[64:128]
        frontend_hash_bytes = bytes.fromhex(frontend_hash_hex)
        frontend_hash_string = cut_returned_hash(bytes32_to_string(frontend_hash_bytes))
        
        return token_amount, frontend_hash_string
    except Exception as e:
        print(f"Error decoding event data: {e}")
        return None, None

def process_events(events_data, contract_address):
    """Process events from 1inch API response"""
    if not events_data or 'items' not in events_data:
        print(f"No events found for {contract_address}")
        return
    
    print(f"📊 Found {len(events_data['items'])} events for {contract_address}")
    
    for event in events_data['items']:
        try:
            print(f"🔍 Processing event: {event}")
            
            event_name = event.get('eventName', '')
            
            if event_name in ['StableDeposited', 'ETFDeposited']:
                user = event['topics'][1] if len(event['topics']) > 1 else None
                
                if event_name == 'StableDeposited':
                    amount_wei, frontend_hash_string = decode_event_data(event['data'])
                    if amount_wei is not None:
                        amount = wei_to_usdc(amount_wei)
                        print(f"\n💰 StableDeposited (via 1inch API):")
                        print(f"  • user:      {user}")
                        print(f"  • amount:    {amount}")
                        print(f"  • frontendHash: {frontend_hash_string}")
                
                elif event_name == 'ETFDeposited':
                    token_amount_wei, frontend_hash_string = decode_event_data(event['data'])
                    if token_amount_wei is not None:
                        amount = wei_to_dspy(token_amount_wei)
                        print(f"\n🪙 ETFDeposited (via 1inch API):")
                        print(f"  • user:       {user}")
                        print(f"  • tokenAmount: {amount}")
                        print(f"  • frontendHash: {frontend_hash_string}")
            
            elif event_name in ['MintProcessed', 'BurnProcessed']:
                user = event['topics'][1] if len(event['topics']) > 1 else None
                
                if event_name == 'MintProcessed':
                    token_amount_wei, frontend_hash_string = decode_event_data(event['data'])
                    if token_amount_wei is not None:
                        amount = wei_to_dspy(token_amount_wei)
                        print(f"\n✨ MintProcessed (via 1inch API):")
                        print(f"  • user:       {user}")
                        print(f"  • tokenAmount: {amount}")
                        print(f"  • frontendHash: {frontend_hash_string}")
                
                elif event_name == 'BurnProcessed':
                    token_amount_wei, frontend_hash_string = decode_event_data(event['data'])
                    if token_amount_wei is not None:
                        amount = wei_to_dspy(token_amount_wei)
                        print(f"\n🔥 BurnProcessed (via 1inch API):")
                        print(f"  • admin:       {user}")
                        print(f"  • tokenAmount: {amount}")
                        print(f"  • frontendHash: {frontend_hash_string}")
                        
        except Exception as e:
            print(f"Error processing event: {e}")

print(f"🚀 Starting 1inch API polling from timestamp {last_processed_timestamp}")


while True:
    try:
        current_timestamp = int(time.time() * 1000)
        
        if current_timestamp > last_processed_timestamp + 30000:  # Check every 30 seconds
            print(f"📡 Checking events from {last_processed_timestamp} to {current_timestamp} via 1inch API...")
            
            # Check TransactionGateway events
            gateway_events = get_contract_events(
                TRANSACTIONGATEWAY_ADDRESS, 
                last_processed_timestamp, 
                current_timestamp
            )
            if gateway_events:
                process_events(gateway_events, TRANSACTIONGATEWAY_ADDRESS)
            
            # Check TokenIssuer events  
            issuer_events = get_contract_events(
                TOKEN_ISSUER_ADDRESS,
                last_processed_timestamp,
                current_timestamp
            )
            if issuer_events:
                process_events(issuer_events, TOKEN_ISSUER_ADDRESS)
            
            last_processed_timestamp = current_timestamp
        
        time.sleep(5)  # Poll every 5 seconds
        
    except Exception as e:
        print(f"‼️ Unexpected error: {type(e).__name__}: {e}")
        time.sleep(5)
