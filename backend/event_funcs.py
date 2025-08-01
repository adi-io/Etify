from event_funcs_utils import db_event_template, user_wallet_details, prefill_usdc_received_event, prefill_dspy_received_event, calculate_sell_order_values
from db_funcs import insert_event
from order_execution_funcs import order_details

#BUY SIDE EVENTS

def new_buy_order_event(user_id, usdc_market_order_amount, frontend_hash):
    create_buy_order_event = db_event_template
    create_buy_order_event['event'] = "BUY_ORDER_CREATED"
    create_buy_order_event['user_id'] = user_id
    create_buy_order_event['order_amount_from_frontend'] = usdc_market_order_amount
    create_buy_order_event['frontend_hash'] = frontend_hash
    create_buy_order_event = user_wallet_details(create_buy_order_event)

    if create_buy_order_event is None:
        return None

    try:
        new_event = insert_event(
            user_id=create_buy_order_event['user_id'],
            event=create_buy_order_event['event'],
            user_usdc_wallet_address=create_buy_order_event['user_usdc_wallet_address'],
            user_dspy_wallet_address=create_buy_order_event['user_dspy_wallet_address'],
            frontend_hash=create_buy_order_event['frontend_hash'],
            order_amount_from_frontend=create_buy_order_event['order_amount_from_frontend']
        )
        return (new_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def usdc_received_event(user_usdc_wallet_address, usdc_amount, frontend_hash):
    result = prefill_usdc_received_event(usdc_amount, frontend_hash, user_usdc_wallet_address)

    if (result is None):
        return(None)

    try:
        usdc_received_event = insert_event(
            user_id=result['user_id'],
            event=result['event'],
            user_usdc_wallet_address=result['user_usdc_wallet_address'],
            user_dspy_wallet_address=result['user_dspy_wallet_address'],
            frontend_hash=result['frontend_hash'],
            order_amount_from_frontend=result['order_amount_from_frontend'],
            usdc_received_from_user=result['usdc_received_from_user'],
            user_spy_buy_order_fee=result['user_spy_buy_order_fee'],
            user_spy_net_buy_order_value=result['user_spy_net_buy_order_value'],
        )
        return (usdc_received_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def send_buy_order_to_exchange_event(order):

    if (order is None):
        return(None)

    try:
        spy_buy_order_event = insert_event(
            user_id=order['user_id'],
            event='SPY_BUY_ORDER_CREATED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            usdc_received_from_user=order['usdc_received_from_user'],
            user_spy_buy_order_fee=order['user_spy_buy_order_fee'],
            user_spy_net_buy_order_value=order['user_spy_net_buy_order_value'],
            buy_order_alpaca_uuid=order['buy_order_alpaca_uuid']
        )
        return (spy_buy_order_event )
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def spy_etf_purchase_event(order):

    if (order is None):
        return(None)


    try:
        alpaca_obj = order_details(order['buy_order_alpaca_uuid'])
        print(alpaca_obj)

        if alpaca_obj is None:
            raise ValueError("Alpaca order not found")

        spy_etf_purchase_event = insert_event(
            user_id=order['user_id'],
            event='SPY_ETF_PURCHASED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            usdc_received_from_user=order['usdc_received_from_user'],
            user_spy_buy_order_fee=order['user_spy_buy_order_fee'],
            user_spy_net_buy_order_value=order['user_spy_net_buy_order_value'],
            buy_order_alpaca_uuid=order['buy_order_alpaca_uuid'],
            dspy_average_minting_price=alpaca_obj.filled_avg_price,
            dspy_mint_filled_quantity=alpaca_obj.filled_qty,
        )
        return (spy_etf_purchase_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def dspy_token_minting_init_event(order):

    if (order is None):
        return(None)

    try:
        dspy_token_minting_init_event = insert_event(
            user_id=order['user_id'],
            event='DSPY_TOKEN_MINTING_INITIATED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            usdc_received_from_user=order['usdc_received_from_user'],
            user_spy_buy_order_fee=order['user_spy_buy_order_fee'],
            user_spy_net_buy_order_value=order['user_spy_net_buy_order_value'],
            buy_order_alpaca_uuid=order['buy_order_alpaca_uuid'],
            dspy_average_minting_price=order['dspy_average_minting_price'],
            dspy_mint_filled_quantity=order['dspy_mint_filled_quantity'],
            gas_paid_for_sending_dspy_to_user=order['gas_paid_for_sending_dspy_to_user'],
        )
        return (dspy_token_minting_init_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def dspy_order_filled_token_minted_event(order):

    if (order is None):
        return(None)

    try:
        dspy_order_filled_token_minted_event = insert_event(
            user_id=order['user_id'],
            event='BUY_ORDER_FILLED_TOKEN_MINTED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            usdc_received_from_user=order['usdc_received_from_user'],
            user_spy_buy_order_fee=order['user_spy_buy_order_fee'],
            user_spy_net_buy_order_value=order['user_spy_net_buy_order_value'],
            buy_order_alpaca_uuid=order['buy_order_alpaca_uuid'],
            dspy_average_minting_price=order['dspy_average_minting_price'],
            dspy_mint_filled_quantity=order['dspy_mint_filled_quantity'],
            gas_paid_for_sending_dspy_to_user=order['gas_paid_for_sending_dspy_to_user'],
            smart_contract_two_transaction_hash=order['smart_contract_two_transaction_hash'],
        )
        return (dspy_order_filled_token_minted_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)


#SELL SIDE EVENTS

def new_sell_order_event(user_id, dspy_market_order_amount, frontend_hash):
    create_sell_order_event = db_event_template
    create_sell_order_event['event'] = "SELL_ORDER_CREATED"
    create_sell_order_event['user_id'] = user_id
    create_sell_order_event['order_amount_from_frontend'] = dspy_market_order_amount
    create_sell_order_event['frontend_hash'] = frontend_hash
    create_sell_order_event = user_wallet_details(create_sell_order_event)

    if create_sell_order_event is None:
        return None

    try:
        new_event = insert_event(
            user_id=create_sell_order_event['user_id'],
            event=create_sell_order_event['event'],
            user_usdc_wallet_address=create_sell_order_event['user_usdc_wallet_address'],
            user_dspy_wallet_address=create_sell_order_event['user_dspy_wallet_address'],
            frontend_hash=create_sell_order_event['frontend_hash'],
            order_amount_from_frontend=create_sell_order_event['order_amount_from_frontend']
        )
        return (new_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def dspy_received_event(user_dspy_wallet_address, dspy_amount, frontend_hash):
    result = prefill_dspy_received_event(dspy_amount, frontend_hash, user_dspy_wallet_address)

    if (result is None):
        print("Prefill failed, Error occurred")
        return(None)

    try:
        dspy_received_event = insert_event(
            user_id=result['user_id'],
            event=result['event'],
            user_usdc_wallet_address=result['user_usdc_wallet_address'],
            user_dspy_wallet_address=result['user_dspy_wallet_address'],
            frontend_hash=result['frontend_hash'],
            order_amount_from_frontend=result['order_amount_from_frontend'],
            dspy_received_from_user=result['dspy_received_from_user'],
        )
        return (dspy_received_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def send_sell_order_to_exchange_event(order):

    if (order is None):
        return(None)

    try:
        spy_sell_order_event = insert_event(
            user_id=order['user_id'],
            event='SPY_SELL_ORDER_CREATED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            dspy_received_from_user=order['dspy_received_from_user'],
            sell_order_alpaca_uuid=order['sell_order_alpaca_uuid']
        )
        return (spy_sell_order_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)


def spy_etf_sell_event(order):

    if (order is None):
        return(None)

    try:
        alpaca_obj = order_details(order['sell_order_alpaca_uuid'])

        cal_sell_order_value = calculate_sell_order_values(alpaca_obj)

        if alpaca_obj is None:
            raise ValueError("Alpaca order not found")

        spy_etf_sell_event = insert_event(
            user_id=order['user_id'],
            event='SPY_ETF_SOLD',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            dspy_received_from_user=order['dspy_received_from_user'],
            dspy_average_burning_price=alpaca_obj.filled_avg_price,
            dspy_burning_filled_quantity=alpaca_obj.filled_qty,
            user_spy_sell_order_value_usd=cal_sell_order_value['total_sell_order_value'],
            user_spy_sell_net_order_value_usd=cal_sell_order_value['total_net_sell_order_value'],
            user_spy_sell_order_fee_usd=cal_sell_order_value['total_sell_order_fee']
        )
        return (spy_etf_sell_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def dspy_token_burning_init_event(order):

    if (order is None):
        return(None)

    try:
        dspy_token_burning_init_event = insert_event(
            user_id=order['user_id'],
            event='DSPY_TOKEN_BURNING_INITIATED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            dspy_received_from_user=order['dspy_received_from_user'],
            dspy_average_burning_price=order['dspy_average_burning_price'],
            dspy_burning_filled_quantity=order['dspy_burning_filled_quantity'],
            user_spy_sell_order_value_usd=order['user_spy_sell_order_value_usd'],
            user_spy_sell_net_order_value_usd=order['user_spy_sell_net_order_value_usd'],
            user_spy_sell_order_fee_usd=order['user_spy_sell_order_fee_usd'],
            gas_paid_for_sending_dspy_to_smart_contract=order['gas_paid_for_sending_dspy_to_smart_contract'], #The gas we paid for initiating the burn function

        )
        return (dspy_token_burning_init_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def dspy_token_burned_event(order):

    if (order is None):
        print("order is None")
        return(None)

    try:
        dspy_token_burning_init_event = insert_event(
            user_id=order['user_id'],
            event='DSPY_TOKEN_BURNED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            dspy_received_from_user=order['dspy_received_from_user'],
            dspy_average_burning_price=order['dspy_average_burning_price'],
            dspy_burning_filled_quantity=order['dspy_burning_filled_quantity'],
            user_spy_sell_order_value_usd=order['user_spy_sell_order_value_usd'],
            user_spy_sell_net_order_value_usd=order['user_spy_sell_net_order_value_usd'],
            user_spy_sell_order_fee_usd=order['user_spy_sell_order_fee_usd'],
            gas_paid_for_sending_dspy_to_smart_contract=order['gas_paid_for_sending_dspy_to_smart_contract'], #The gas we paid for initiating the burn function
            smart_contract_two_transaction_hash=order['smart_contract_two_transaction_hash'],

        )
        return (dspy_token_burning_init_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def usdc_redemption_transfer_initiated(order):

    if (order is None):
        return(None)

    try:
        usdc_redemption_transfer_event = insert_event(
            user_id=order['user_id'],
            event='REDEMPTION_USDC_TRANSFER_INITIATED',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            dspy_received_from_user=order['dspy_received_from_user'],
            dspy_average_burning_price=order['dspy_average_burning_price'],
            dspy_burning_filled_quantity=order['dspy_burning_filled_quantity'],
            user_spy_sell_order_value_usd=order['user_spy_sell_order_value_usd'],
            user_spy_sell_net_order_value_usd=order['user_spy_sell_net_order_value_usd'],
            user_spy_sell_order_fee_usd=order['user_spy_sell_order_fee_usd'],
            gas_paid_for_sending_dspy_to_smart_contract=order['gas_paid_for_sending_dspy_to_smart_contract'], #The gas we paid for initiating the burn function
            smart_contract_two_transaction_hash=order['smart_contract_two_transaction_hash'],
            gas_paid_for_sending_usdc=order['gas_paid_for_sending_usdc'],

        )
        return (usdc_redemption_transfer_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)

def sell_order_filled_usdc_sent(order):

    if (order is None):
        return(None)

    try:
        sell_order_filled_usdc_sent_event = insert_event(
            user_id=order['user_id'],
            event='SELL_ORDER_FILLED_REDEMPTION_USDC_SENT',
            user_usdc_wallet_address=order['user_usdc_wallet_address'],
            user_dspy_wallet_address=order['user_dspy_wallet_address'],
            frontend_hash=order['frontend_hash'],
            order_amount_from_frontend=order['order_amount_from_frontend'],
            dspy_received_from_user=order['dspy_received_from_user'],
            dspy_average_burning_price=order['dspy_average_burning_price'],
            dspy_burning_filled_quantity=order['dspy_burning_filled_quantity'],
            user_spy_sell_order_value_usd=order['user_spy_sell_order_value_usd'],
            user_spy_sell_net_order_value_usd=order['user_spy_sell_net_order_value_usd'],
            user_spy_sell_order_fee_usd=order['user_spy_sell_order_fee_usd'],
            gas_paid_for_sending_dspy_to_smart_contract=order['gas_paid_for_sending_dspy_to_smart_contract'], #The gas we paid for initiating the burn function
            smart_contract_two_transaction_hash=order['smart_contract_two_transaction_hash'],
            gas_paid_for_sending_usdc=order['gas_paid_for_sending_usdc'],
            redemption_usdc_sent_to_user=order['redemption_usdc_sent_to_user'],

        )
        return (sell_order_filled_usdc_sent_event)
    except Exception as e:
        print(f"Error occurred: {e}")
        return(None)
