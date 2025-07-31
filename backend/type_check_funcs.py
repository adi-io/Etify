from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID


class WalletAddress(BaseModel):
    erc20_address: str

class UserSignIn(BaseModel):
    email: str
    password: str

class UserSignUp(BaseModel):
    email: str
    password: str

class BuySpyPayload(BaseModel):
    frontend_hash: UUID
    amount_of_usdc_sent: Decimal

class SellSpyPayload(BaseModel):
    frontend_hash: UUID
    amount_of_dspy_sent: Decimal

def usdc_type_check(usdc_market_order_amount):

    if not isinstance(usdc_market_order_amount, Decimal):
        return False

    if usdc_market_order_amount < Decimal('10'):
        return False

    exponent = usdc_market_order_amount.as_tuple().exponent
    if exponent < -6: # If exponent is less than -6, it means more than 6 decimal places (e.g., -7 for 0.0000001)
        return False

    return True

def dspy_type_check(dspy_market_order_amount):

    if not isinstance(dspy_market_order_amount, Decimal):
        return False

    if dspy_market_order_amount < Decimal('0.01'):
        return False

    exponent = dspy_market_order_amount.as_tuple().exponent
    if exponent < -9:
        return False

    return True
