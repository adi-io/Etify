from db_funcs import get_qualified_bids, get_qualified_asks, get_qualified_mints, get_qualified_burns, get_qualified_redemptions
from order_execution_funcs import spy_market_buy_order, spy_market_sell_order
from event_funcs_utils import dir_copy, db_event_template
from event_funcs import send_buy_order_to_exchange_event, spy_etf_purchase_event, spy_etf_sell_event, send_sell_order_to_exchange_event, dspy_token_minting_init_event, dspy_token_burning_init_event, usdc_redemption_transfer_initiated, sell_order_filled_usdc_sent
from blockchain_utils import bytes32_to_string, string_to_bytes32, wei_to_usdc, usdc_to_wei, dspy_to_wei
from dotenv import load_dotenv
import os
import asyncio
import blockchain_funcs

load_dotenv()

async def process_single_buy_order(dic):
    if (dic is None or dic['user_spy_net_buy_order_value'] is None or dic['user_spy_net_buy_order_value'] <= 0):
        return (None)
    try:
        dic['buy_order_alpaca_uuid'] = spy_market_buy_order(dic['user_spy_net_buy_order_value'])
    except Exception as e:
        print(f"Error processing order: {e}")
        return None

    try:
        result = send_buy_order_to_exchange_event(dic)

    except Exception as e:
        print(f"Event error (send_buy_order_to_exchange_event): {e}")
        return None

    try:
        result = spy_etf_purchase_event(dic)
        return (result)

    except Exception as e:
        print(f"Event error (spy_etf_purchase_event): {e}")
        return None

async def execute_buy_orders():

    while True:
        try:
            usdt_events = get_qualified_bids()
            if usdt_events:
                for event in usdt_events:
                    event_copy = dir_copy(event, db_event_template.copy())
                    asyncio.create_task(process_single_buy_order(event_copy))

        except Exception as e:
            print(f"An error occurred in the buy orders execution loop: {e}")

        await asyncio.sleep(2.5)


async def process_single_sell_order(dic):
    if (dic is None or dic['dspy_received_from_user'] is None or dic['dspy_received_from_user'] <= 0):
        return (None)
    try:
       dic['sell_order_alpaca_uuid'] = spy_market_sell_order(dic['dspy_received_from_user'])
    except Exception as e:
        print(f"Error processing order: {e}")
        return None

    try:
        result = send_sell_order_to_exchange_event(dic)

    except Exception as e:
        print(f"Event error (send_sell_order_to_exchange_event): {e}")
        return None

    try:
        result = spy_etf_sell_event(dic)
        return (result)

    except Exception as e:
        print(f"Event error (spy_etf_sell_event): {e}")
        return None

async def execute_sell_orders():

    while True:
        try:
            dspy_events = get_qualified_asks()
            if dspy_events:
                for event in dspy_events:
                    event_copy = dir_copy(event, db_event_template.copy())
                    asyncio.create_task(process_single_sell_order(event_copy))

        except Exception as e:
            print(f"An error occurred in the sell orders execution loop: {e}")

        await asyncio.sleep(2.5)

async def process_single_mint_action(dic):
    if (dic is None or dic['dspy_mint_filled_quantity'] is None):
        return (None)

    user_address = dic["user_dspy_wallet_address"]
    token_amount = dspy_to_wei(dic["dspy_mint_filled_quantity"])
    frontend_hash = str(dic["frontend_hash"])

    try:
        print("Processing mint action...")
        result = blockchain_funcs.mint(user_address, int(token_amount), string_to_bytes32(frontend_hash))
    except Exception as e:
        print(f"Error processing order: {e}")
        return None

    try:
        result = dspy_token_minting_init_event(dic)

    except Exception as e:
        print(f"Event error (dspy minting db entry event): {e}")
        return None

async def execute_mint_actions():

    while True:
        try:
            mint_events = get_qualified_mints()
            if mint_events:
                for event in mint_events:
                    event_copy = dir_copy(event, db_event_template.copy())
                    asyncio.create_task(process_single_mint_action(event_copy))

        except Exception as e:
            print(f"An error occurred in the mint actions execution loop: {e}")

        await asyncio.sleep(2.5)

async def process_single_burn_action(dic):
    if (dic is None or dic['dspy_burning_filled_quantity'] is None):
        return (None)

    admin_address = os.getenv("WALLET_ADDRESS_ADMIN")
    token_amount = dspy_to_wei(dic["dspy_received_from_user"])
    frontend_hash = str(dic["frontend_hash"])

    try:
        print("Processing burn action...")
        result = blockchain_funcs.burn(admin_address, int(token_amount), string_to_bytes32(frontend_hash))
    except Exception as e:
        print(f"Error processing order: {e}")
        return None

    try:
        result = dspy_token_burning_init_event(dic)

    except Exception as e:
        print(f"Event error (dspy burning db event): {e}")
        return None

async def execute_burn_actions():

    while True:
        try:
            burn_events = get_qualified_burns()
            if burn_events:
                for event in burn_events:
                    event_copy = dir_copy(event, db_event_template.copy())
                    asyncio.create_task(process_single_burn_action(event_copy))

        except Exception as e:
            print(f"An error occurred in the burn actions execution loop: {e}")

        await asyncio.sleep(2.5)

async def process_single_redemption_action(dic):

    if (dic is None or dic['user_spy_sell_net_order_value_usd'] is None):
        return (None)

    user_address = dic["user_usdc_wallet_address"]
    token_amount = usdc_to_wei(dic["user_spy_sell_net_order_value_usd"])

    try:
        result = usdc_redemption_transfer_initiated(dic)
    except Exception as e:
        print(f"Event error (usdc redemption db event): {e}")
        return None

    try:
        result = blockchain_funcs.transfer_usdc(user_address, token_amount)

        if (result is None):
            print("Blockchain Transfer failed")
            return (None)

        if result['status'] == 1:
            dic["redemption_usdc_sent_to_user"] = dic["user_spy_sell_net_order_value_usd"]
            sell_order_filled_usdc_sent(dic)

    except Exception as e:
        print(f"Error processing order: {e}")
        return None


async def execute_redemption_actions():

    while True:
        try:
            redemption_events = get_qualified_redemptions()
            if redemption_events:
                for event in redemption_events:
                    event_copy = dir_copy(event, db_event_template.copy())
                    asyncio.create_task(process_single_redemption_action(event_copy))

        except Exception as e:
            print(f"An error occurred in the redemptions actions execution loop: {e}")

        await asyncio.sleep(2.5)


async def run_buy_sell_loops():
    await asyncio.gather(
        execute_sell_orders(),
        execute_buy_orders(),
        execute_mint_actions(),
        execute_burn_actions(),
        execute_redemption_actions(),
    )
