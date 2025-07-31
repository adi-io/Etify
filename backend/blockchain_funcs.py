import os
import json
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY_ADMIN = os.getenv("PRIVATE_KEY_ADMIN")
WALLET_ADDRESS_ADMIN = os.getenv("WALLET_ADDRESS_ADMIN")
WALLET_ADDRESS_TEST_USER = os.getenv("WALLET_ADDRESS_TEST_USER")
TRANSACTIONGATEWAY_ADDRESS = os.getenv("TRANSACTIONGATEWAY_ADDRESS")
TOKEN_ISSUER_ADDRESS = os.getenv("DSPY_ADDRESS")
CHAIN_ID = os.getenv("CHAIN_ID")
USDC_ADDRESS = os.getenv("USDC_ADDRESS")

with open("abi/TokenIssuerABI.json") as TokenIssuerABI_file:
    TOKEN_ISSUER_ABI = json.load(TokenIssuerABI_file)

with open("abi/TransactionGatewayABI.json", "r") as TransactionGatewayABI_file:
    GATEWAY_ABI = json.load(TransactionGatewayABI_file)

with open("abi/USDCABI.json", "r") as USDCABI_file:
    USDC_ABI = json.load(USDCABI_file)

def mint(user_address, token_amount, frontend_hash):
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
        'chainId': CHAIN_ID,
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

def burn(admin_address, token_amount, frontend_hash):
    if not admin_address:
        print("[ERROR] No admin address provided.")
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
    burn_txn = token_issuer.functions.burn(
        admin_address,
        token_amount,
        frontend_hash
    ).build_transaction({
        'chainId': CHAIN_ID,
        'gas': 150000,
        'gasPrice': w3.to_wei('1', 'gwei'),
        'nonce': nonce
    })

    signed_txn = w3.eth.account.sign_transaction(burn_txn, private_key=PRIVATE_KEY_ADMIN)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f"✅ Burn tx sent: {w3.to_hex(tx_hash)}")
    print("⏳ Waiting for receipt...")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("🎉 Burn executed successfully!" if receipt['status'] == 1 else "❌ Transaction failed.")

    return receipt

def transfer_usdc(user_address, token_amount):
	if not user_address:
		print("[ERROR] No user address provided.")
		return

	if not token_amount or token_amount <= 0:
		print("[ERROR] Invalid token amount.")
		return

	w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))

	usdc = w3.eth.contract(address=USDC_ADDRESS, abi=USDC_ABI)

	sender_balance = usdc.functions.balanceOf(WALLET_ADDRESS_ADMIN).call()
	print(f"Sender balance: {sender_balance}")

	if sender_balance < token_amount:
		print(f"[ERROR] Insufficient balance. Required: {token_amount}, Available: {sender_balance}")
		return

	nonce = w3.eth.get_transaction_count(WALLET_ADDRESS_ADMIN)
	transfer_txn = usdc.functions.transfer(
		user_address,
		token_amount
	).build_transaction({
		'chainId': CHAIN_ID,
		'gas': 150000,
		'gasPrice': w3.to_wei('1', 'gwei'),
		'nonce': nonce
	})

	signed_txn = w3.eth.account.sign_transaction(transfer_txn, private_key=PRIVATE_KEY_ADMIN)
	tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

	print(f"✅ Transfer tx sent: {w3.to_hex(tx_hash)}")
	print(f"⏳ Transferring {token_amount} USDC to {user_address}...")

	receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

	if receipt['status'] == 1:
		print("🎉 Transfer successful!")
		# Check new balances
		new_sender_balance = usdc.functions.balanceOf(WALLET_ADDRESS_ADMIN).call()
		recipient_balance = usdc.functions.balanceOf(user_address).call()
		print(f"Sender balance now: {new_sender_balance}")
		print(f"Recipient balance now: {recipient_balance}")
	else:
		print("❌ Transfer failed.")
		# Try to get error reason
		tx = w3.eth.get_transaction(tx_hash)
		try:
			w3.eth.call({
				'to': tx['to'],
				'from': tx['from'],
				'data': tx['input'],
				'value': tx['value'],
				'gas': tx['gas']
			}, block_identifier=tx['blockNumber'])
		except web3.exceptions.ContractLogicError as e:
			print(f"Revert reason: {e}")

	return receipt
