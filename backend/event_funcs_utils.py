from db_funcs import find_buy_order, find_sell_order, get_user_wallet_address, find_sold_order, find_bought_order
from decimal import Decimal, ROUND_HALF_UP

def user_wallet_details(dic):

    if (dic):
        temp = get_user_wallet_address(dic['user_id'])
        if (temp is None):
            return (None)
        dic['user_usdc_wallet_address'] = temp['usdc_wallet']
        dic['user_dspy_wallet_address'] = temp['dspy_wallet']
        return (dic)
    else:
        return (None)

def prefill_dspy_received_event(dspy_amount, frontend_hash, user_dspy_wallet_address):
    result = db_event_template
    try:
        temp = find_sell_order(frontend_hash, user_dspy_wallet_address)
    except Exception as e:
        print(f"Error in prefill_dspy_received_event: {e}")
        return (None)

    if temp is None:
        return (None)

    result = dir_copy(temp, result)
    result['event'] = "DSPY_RECEIVED"
    result['dspy_received_from_user'] = dspy_amount

    return (result)

def prefill_usdc_received_event(usdc_amount, frontend_hash, user_usdc_wallet_address):
    result = db_event_template
    try:
        temp = find_buy_order(frontend_hash, user_usdc_wallet_address)
    except Exception as e:
        print(f"Error in prefill_usdc_received_event: {e}")
        return (None)

    if temp is None:
        return (None)

    result = dir_copy(temp, result)
    result['event'] = "USDC_RECEIVED"
    result['usdc_received_from_user'] = usdc_amount
    result['user_spy_buy_order_fee'] = round(result['usdc_received_from_user'] * Decimal('0.005'), 2)
    result['user_spy_net_buy_order_value'] = result['usdc_received_from_user'] - result['user_spy_buy_order_fee']

    return (result)

def prefill_dspy_burn_event(frontend_hash):
    result = db_event_template
    try:
        temp = find_sold_order(frontend_hash)
    except Exception as e:
        print(f"Error in prefill_dspy_burn_event: {e}")
        return (None)

    if temp is None:
        return (None)

    result = dir_copy(temp, result)

    return (result)

def prefill_dspy_mint_event(frontend_hash, dspy_usdc_wallet_address):
    result = db_event_template
    try:
        temp = find_bought_order(frontend_hash, dspy_usdc_wallet_address)
    except Exception as e:
        print(f"Error in prefill_dspy_mint_event: {e}")
        return (None)

    if temp is None:
        return (None)

    result = dir_copy(temp, result)

    return (result)


def calculate_sell_order_values(alpaca_obj):
    result = {}
    filled_qty       = Decimal(alpaca_obj.filled_qty)
    filled_avg_price = Decimal(alpaca_obj.filled_avg_price)
    total_sell_order_value = filled_qty * filled_avg_price
    result['total_sell_order_value'] = total_sell_order_value.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP)
    result['total_sell_order_fee'] = total_sell_order_value * Decimal('0.01')
    result['total_net_sell_order_value'] = result['total_sell_order_value'] - result['total_sell_order_fee']

    return (result)

def dir_copy(source_dict, target_template):
    exclude_keys = {'event', 'created_at', 'id'}

    for key in target_template.keys():
        if key not in exclude_keys and key in source_dict and source_dict[key] is not None:
            target_template[key] = source_dict[key]

    return target_template

db_event_template = {
    'event': '',
    'user_usdc_wallet_address': '',
    'user_dspy_wallet_address': '',
    'frontend_hash': '',
    'smart_contract_one_transaction_hash': None,
    'order_amount_from_frontend': None,
    'user_spy_net_buy_order_value': None,
    'user_spy_buy_order_fee': None,
    'usdc_received_from_user': None,
    'dspy_received_from_user': None,
    'user_spy_sell_order_value_usd': None,
    'user_spy_sell_net_order_value_usd': None,
    'user_spy_sell_order_fee_usd': None,
    'redemption_usdc_sent_to_user': None,
    'gas_paid_for_sending_usdc': None,
    'gas_paid_for_sending_dspy_to_user': None,
    'gas_paid_for_sending_dspy_to_smart_contract': None,
    'dspy_average_minting_price': None,
    'dspy_average_burning_price': None,
    'dspy_mint_filled_quantity': None,
    'dspy_burning_filled_quantity': None,
    'user_id': '',
    'smart_contract_two_transaction_hash': None,
    'buy_order_alpaca_uuid': None,
    'sell_order_alpaca_uuid': None
}
