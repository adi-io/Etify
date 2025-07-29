import os
from dotenv import load_dotenv
from web3 import Web3
import json
from web3.exceptions import ContractLogicError


load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
contracts_dir = os.path.dirname(script_dir)

PRIVATE_KEY_TEST_USER = os.getenv("PRIVATE_KEY_TEST_USER")
WALLET_ADDRESS_TEST_USER = os.getenv("WALLET_ADDRESS_TEST_USER")
ETFY_ADDRESS = os.getenv("ETFY_ADDRESS")
TRANSACTIONGATEWAY_ADDRESS = os.getenv("TRANSACTIONGATEWAY_ADDRESS")
BASE_CHAIN_ID = os.getenv("BASE_CHAIN_ID")
TokenIssuer_abi_path = os.path.join(contracts_dir, "abi", "TokenIssuerABI.json")
TransactionGateway_abi_path = os.path.join(contracts_dir, "abi", "TransactionGatewayABI.json")

# Load ABIs
with open(TokenIssuer_abi_path) as TokenIssuerABI_file:
    TOKEN_ISSUER_ABI = json.load(TokenIssuerABI_file)

with open(TransactionGateway_abi_path, "r") as TransactionGatewayABI_file:
    GATEWAY_ABI = json.load(TransactionGatewayABI_file)

# frontendHash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd71"

def test_deposit_ETFY(amount, frontendHash):
	if not amount or amount <= 0:
		print("[ERROR] Wrong amount.")
	if not frontendHash:
		print("[ERROR] No hash provided.")

	w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))

	# Approve
	token = w3.eth.contract(address=ETFY_ADDRESS, abi=TOKEN_ISSUER_ABI)
	nonce = w3.eth.get_transaction_count(WALLET_ADDRESS_TEST_USER, "pending")

	approve_txn = token.functions.approve(TRANSACTIONGATEWAY_ADDRESS, amount).build_transaction({
		'chainId': BASE_CHAIN_ID,
		'gas': 100000,
		'gasPrice': w3.to_wei('1', 'gwei'),
		'nonce': nonce
	})

	signed_approve = w3.eth.account.sign_transaction(approve_txn, PRIVATE_KEY_TEST_USER)
	tx_hash = w3.eth.send_raw_transaction(signed_approve.raw_transaction)
	print(f"✅ Approve tx sent: {w3.to_hex(tx_hash)}")
	print("⏳ Waiting for receipt...")

	receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
	print("🎉 Approved successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")

	# Deposit
	gateway = w3.eth.contract(address=TRANSACTIONGATEWAY_ADDRESS, abi=GATEWAY_ABI)
	nonce = w3.eth.get_transaction_count(WALLET_ADDRESS_TEST_USER, block_identifier="pending")

	deposit_txn = gateway.functions.depositDSPY(amount, frontendHash).build_transaction({
		'chainId': BASE_CHAIN_ID,
		'gas': 150000,
		'gasPrice': w3.to_wei('1', 'gwei'),
		'nonce': nonce
	})

	signed_deposit = w3.eth.account.sign_transaction(deposit_txn, PRIVATE_KEY_TEST_USER)
	deposit_tx_hash = w3.eth.send_raw_transaction(signed_deposit.raw_transaction)
	print(f"✅ Deposit tx sent: {w3.to_hex(deposit_tx_hash)}")
	print("⏳ Waiting for receipt...")

	receipt = w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
	print("🎉 Executed successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")


test_deposit_ETFY(1*10**9, "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd16")
