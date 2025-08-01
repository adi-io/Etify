import os
from dotenv import load_dotenv
from web3 import Web3
import json
from web3.exceptions import ContractLogicError

load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
contracts_dir = os.path.dirname(script_dir)

# Load environment variables
PRIVATE_KEY_ADMIN = os.getenv("PRIVATE_KEY_ADMIN")
WALLET_ADDRESS_ADMIN = os.getenv("WALLET_ADDRESS_ADMIN")
WALLET_ADDRESS_TEST_USER = os.getenv("WALLET_ADDRESS_TEST_USER")
TRANSACTIONGATEWAY_ADDRESS = os.getenv("TRANSACTIONGATEWAY_ADDRESS")
TOKEN_ISSUER_ADDRESS = os.getenv("ETFY_ADDRESS")
BASE_CHAIN_ID = int(os.getenv("BASE_CHAIN_ID"))
TokenIssuer_abi_path = os.path.join(contracts_dir, "abi", "TokenIssuerABI.json")
TransactionGateway_abi_path = os.path.join(contracts_dir, "abi", "TransactionGatewayABI.json")

# Load ABIs
with open(TokenIssuer_abi_path) as TokenIssuerABI_file:
    TOKEN_ISSUER_ABI = json.load(TokenIssuerABI_file)

with open(TransactionGateway_abi_path, "r") as TransactionGatewayABI_file:
    GATEWAY_ABI = json.load(TransactionGatewayABI_file)

def test_mint(user_address, token_amount, frontend_hash):
    if not user_address:
        print("[ERROR] No user address provided.")
        return
    
    if not token_amount or token_amount <= 0:
        print("[ERROR] Invalid token amount.")
        return
        
    if not frontend_hash:
        print("[ERROR] No frontend hash provided.")
        return
    
    w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
    
    token_issuer = w3.eth.contract(address=TOKEN_ISSUER_ADDRESS, abi=TOKEN_ISSUER_ABI)
    
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS_ADMIN)
    mint_txn = token_issuer.functions.mint(
        user_address, 
        token_amount, 
        frontend_hash
    ).build_transaction({
        'chainId': BASE_CHAIN_ID,
        'gas': 150000,
        'gasPrice': w3.to_wei('1', 'gwei'),
        'nonce': nonce
    })
    
    signed_txn = w3.eth.account.sign_transaction(mint_txn, private_key=PRIVATE_KEY_ADMIN)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"✅ Mint tx sent: {w3.to_hex(tx_hash)}")
    print("⏳ Waiting for receipt...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("🎉 Mint executed successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")
    
    return receipt


test_mint(WALLET_ADDRESS_TEST_USER, 1*10**9, "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd15")
