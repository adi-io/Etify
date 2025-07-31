from web3 import Web3
import uuid
from decimal import Decimal, getcontext
import math


# Set precision for Decimal calculations
getcontext().prec = 28

# Maximum value for uint256
MAX_UINT256 = 2**256 - 1

def string_to_bytes32(text):
    """
    Converts a string or UUID to bytes32 format for smart contracts.

    Args:
        text (str): String or UUID string to convert

    Returns:
        bytes: bytes32 representation for smart contract
    """
    # Remove hyphens if it's a UUID string
    clean_text = text.replace('-', '')

    # Ensure the string is not longer than 32 bytes (64 hex chars)
    if len(clean_text) > 64:
        clean_text = clean_text[:64]

    # Pad to 32 bytes (64 hex characters) with zeros
    padded_text = clean_text.ljust(64, '0')

    # Convert to bytes32
    return Web3.to_bytes(hexstr=padded_text)

def bytes32_to_string(bytes32_data):
    """
    Converts bytes32 data from a smart contract back to a string.

    Args:
        bytes32_data (bytes): bytes32 data from smart contract

    Returns:
        str: The original string (formatted as UUID if applicable)
    """
    # Convert bytes32 to hex string
    hex_str = Web3.to_hex(bytes32_data)[2:]  # Remove '0x' prefix

    # For UUIDs, we expect exactly 32 hex characters
    # Only remove trailing zeros if there are more than 32 characters
    if len(hex_str) > 32:
        # Remove padding zeros (but keep the original 32 characters)
        clean_str = hex_str[:32]
    else:
        # If it's already 32 or fewer characters, don't strip anything
        clean_str = hex_str.rstrip('0') if len(hex_str) < 32 else hex_str

    # If it's exactly 32 characters, format as UUID
    if len(clean_str) == 32:
        return f"{clean_str[:8]}-{clean_str[8:12]}-{clean_str[12:16]}-{clean_str[16:20]}-{clean_str[20:]}"
    elif len(clean_str) == 31:
        # If it's 31 characters, add back the missing zero and format
        clean_str = clean_str + "0"
        return f"{clean_str[:8]}-{clean_str[8:12]}-{clean_str[12:16]}-{clean_str[16:20]}-{clean_str[20:]}"

    return clean_str

def cut_returned_hash(hash):
	return hash[:36]

def generate_uuid_as_bytes32():
    """
    Generates a new random UUID and converts it directly to bytes32.

    Returns:
        bytes: bytes32 representation of a new UUID
    """
    new_uuid = uuid.uuid4()
    return string_to_bytes32(new_uuid.hex)

def generate_uuid():
	new_uuid = uuid.uuid4()
	return new_uuid.replace('-', '')

def dspy_to_wei(dspy_amount):
    """
    Convert DSPY amount from human-readable to blockchain format

    Args:
        dspy_amount (float): Amount in DSPY (e.g., 0.03)

    Returns:
        int: Amount in blockchain format (e.g., 30000000)
    """
    # Round to 9 decimal places to prevent precision errors
    rounded = round(dspy_amount * 10**9)
    return int(rounded)

def wei_to_dspy(wei_amount):
    """
    Convert DSPY amount from blockchain format to human-readable

    Args:
        wei_amount (int): Amount in blockchain format (e.g., 30000000)

    Returns:
        float: Amount in DSPY (e.g., 0.03)
    """
    return wei_amount / 10**9

def wei_to_usdc(wei_amount):
    """
    Convert blockchain format (wei) to USDC amount safely.

    Args:
        wei_amount: Amount in blockchain format

    Returns:
        Decimal: Amount in USDC with exactly 6 decimal places
    """
    result = Decimal(wei_amount) / Decimal(10**6)
    # Format to exactly 6 decimal places
    return result.quantize(Decimal('0.000001'))

def usdc_to_wei(usdc_amount):
    """
    Convert USDC amount to blockchain format (wei) safely.

    Args:
        usdc_amount: Amount in USDC as float, int, or string

    Returns:
        int: Amount in blockchain format with 6 decimal precision
    """
    # Convert to Decimal first for precise handling
    if isinstance(usdc_amount, str):
        amount_decimal = Decimal(usdc_amount)
    else:
        # Convert float/int to string then Decimal to avoid float precision issues
        amount_decimal = Decimal(str(usdc_amount))

    # Round to exactly 6 decimal places
    rounded = amount_decimal.quantize(Decimal('0.000001'))

    # Convert to blockchain format
    wei_amount = int(rounded * 10**6)

    # Check for uint256 overflow
    if wei_amount > MAX_UINT256:
        raise ValueError(f"Amount too large for uint256: {wei_amount}")

    return wei_amount
