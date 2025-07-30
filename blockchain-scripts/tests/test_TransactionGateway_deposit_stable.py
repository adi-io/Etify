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
USDC_ADDRESS = os.getenv("USDC_ADDRESS")
TRANSACTIONGATEWAY_ADDRESS = os.getenv("TRANSACTIONGATEWAY_ADDRESS") 
BASE_CHAIN_ID = int(os.getenv("BASE_CHAIN_ID"))
USDC_abi_path = os.path.join(contracts_dir, "abi", "USDCABI.json")
TransactionGateway_abi_path = os.path.join(contracts_dir, "abi", "TransactionGatewayABI.json")

# Load ABIs

with open(TransactionGateway_abi_path, "r") as TransactionGatewayABI_file:
    GATEWAY_ABI = json.load(TransactionGatewayABI_file)

with open(USDC_abi_path) as USDCABI_file:
	USDC_ABI = json.load(USDCABI_file)


def test_deposit_stable(amount, frontendHash):
	if not amount or amount <= 0:
		print("[ERROR] Wrong amount.")
	if not frontendHash:
		print("[ERROR] No hash provided.")

	w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))

	usdc = w3.eth.contract(address=USDC_ADDRESS, abi=USDC_ABI)

	nonce = w3.eth.get_transaction_count(WALLET_ADDRESS_TEST_USER)
	txn = usdc.functions.approve(TRANSACTIONGATEWAY_ADDRESS, amount).build_transaction({
		'chainId': BASE_CHAIN_ID,
		'gas': 70000,
		'gasPrice': w3.to_wei('1', 'gwei'),
		'nonce': nonce
	})

	signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY_TEST_USER)
	tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
	print(f"✅ Approve tx sent: {w3.to_hex(tx_hash)}")
	print("⏳ Waiting for receipt...")

	receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
	print("🎉 Approved successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")

	gateway = w3.eth.contract(address=TRANSACTIONGATEWAY_ADDRESS, abi=GATEWAY_ABI)
	deposit_txn = gateway.functions.depositUSDC(amount, frontendHash).build_transaction({
		'chainId': BASE_CHAIN_ID,
		'gas': 150000,
			'gasPrice': w3.to_wei('1', 'gwei'),
			'nonce': nonce + 1,
	})
	signed_deposit = w3.eth.account.sign_transaction(deposit_txn, PRIVATE_KEY_TEST_USER)
	deposit_tx_hash = w3.eth.send_raw_transaction(signed_deposit.raw_transaction)

	print(f"✅ Deposit tx sent: {w3.to_hex(deposit_tx_hash)}")
	print("⏳ Waiting for receipt...")

	receipt = w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
	print("🎉 Executed successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")

	if receipt['status'] != 1:
		tx = w3.eth.get_transaction(tx_hash)

		try:
				w3.eth.call({
					'to': tx['to'],
					'from': tx['from'],
					'data': tx['input'],
					'value': tx['value'],
					'gas': tx['gas']
				}, tx.blockNumber)
		except Exception as e:
				print("🔍 Revert reason:", e)

	tx = w3.eth.get_transaction(tx_hash)
	try:
		w3.eth.call({
			'to': tx['to'],
			'from': tx['from'],
			'data': tx['input'],
			'value': tx['value'],
			'gas': tx['gas']
		}, block_identifier=tx['blockNumber'])
	except ContractLogicError as e:
		print("Revert reason:", e)
	except Exception as e:
		print("Other error:", e)


test_deposit_stable(2*10**6, "0x1234567890abcdef8234567890abcdef1234567890abcdef1234567890abcd17")
