import os
from dotenv import load_dotenv
from web3 import Web3
import json
from time import sleep
from web3.exceptions import ContractLogicError


load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
contracts_dir = os.path.dirname(script_dir)

PRIVATE_KEY_TEST_USER = os.getenv("PRIVATE_KEY_TEST_USER")
WALLET_ADDRESS_TEST_USER = os.getenv("WALLET_ADDRESS_TEST_USER")
ETFY_ADDRESS = os.getenv("ETFY_ADDRESS")
TRANSACTIONGATEWAY_ADDRESS = os.getenv("TRANSACTIONGATEWAY_ADDRESS")
BASE_CHAIN_ID = int(os.getenv("BASE_CHAIN_ID"))
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


	etfy_balance = token.functions.balanceOf(WALLET_ADDRESS_TEST_USER).call()
	print(f"ETFY Balance: {etfy_balance / 10**9} ETFY")
	allowance = token.functions.allowance(WALLET_ADDRESS_TEST_USER, TRANSACTIONGATEWAY_ADDRESS).call()
	print(f"Allowance set: {allowance / 10**9} ETFY")

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

	# Check allowance after approval
	allowance_after = token.functions.allowance(WALLET_ADDRESS_TEST_USER, TRANSACTIONGATEWAY_ADDRESS).call()
	print(f"Allowance after approval: {allowance_after / 10**9} ETFY")
	print(f"Trying to deposit: {amount / 10**9} ETFY")

	if allowance_after < amount:
		print("❌ Insufficient allowance!")
		return

	# Let's also check if we can call transferFrom directly to see the error
	try:
		# This is just a simulation, not an actual transaction
		result = token.functions.transferFrom(
			WALLET_ADDRESS_TEST_USER, 
			TRANSACTIONGATEWAY_ADDRESS, 
			amount
		).call({'from': TRANSACTIONGATEWAY_ADDRESS})
		print("✅ transferFrom simulation successful")
	except Exception as e:
		print(f"❌ transferFrom simulation failed: {e}")

	# Deposit
	gateway = w3.eth.contract(address=TRANSACTIONGATEWAY_ADDRESS, abi=GATEWAY_ABI)

	# nonce = w3.eth.get_transaction_count(WALLET_ADDRESS_TEST_USER, block_identifier="pending")
	nonce += 1

	deposit_txn = gateway.functions.depositOurToken(amount, frontendHash).build_transaction({
		'chainId': BASE_CHAIN_ID,
		'gas': 170000,
		'gasPrice': w3.to_wei('1', 'gwei'),
		'nonce': nonce
	})

	signed_deposit = w3.eth.account.sign_transaction(deposit_txn, PRIVATE_KEY_TEST_USER)
	deposit_tx_hash = w3.eth.send_raw_transaction(signed_deposit.raw_transaction)
	print(f"✅ Deposit tx sent: {w3.to_hex(deposit_tx_hash)}")
	print("⏳ Waiting for receipt...")

	receipt = w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
	print("🎉 Executed successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")

	# Debug failed transaction
	if receipt['status'] != 1:
		try:
			# Try to simulate the transaction to get the revert reason
			tx = w3.eth.get_transaction(deposit_tx_hash)
			w3.eth.call({
				'to': tx['to'],
				'from': tx['from'],
				'data': tx['input'],
				'value': tx['value'],
				'gas': tx['gas']
			}, block_identifier='latest')
		except ContractLogicError as e:
			print("🔍 Revert reason:", e)
		except Exception as e:
			print("🔍 Error:", e)


test_deposit_ETFY(1*10**9, "0x7234567890abcdef8234567890abcdef1234567890abcdef1234567890abcd17")
