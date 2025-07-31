import requests
import json
import os
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.historical import StockHistoricalDataClient
from dotenv import load_dotenv

load_dotenv()

def get_approx_spy_value(usdc):
    spy = get_latest_spy_ask()
    return round(usdc/spy, 9)

def get_approx_spy_sale_value(dspy):
    spy = get_latest_spy_ask()
    return round(dspy*spy, 6)

def get_latest_spy_ask():
    try:
        #start = time.perf_counter()
        price_client = StockHistoricalDataClient(os.getenv('API_KEY'), os.getenv('SECRET_KEY'))
        request_params = StockLatestQuoteRequest(symbol_or_symbols="SPY")
        latest_spy_price = price_client.get_stock_latest_quote(request_params)
        ask_price = latest_spy_price['SPY'].ask_price

        #end = time.perf_counter()
        #time_taken = end - start
        #print(f"Request took {end - start:.4f} seconds")

        return (ask_price)
    except Exception as e:
        print(f"An error occurred: {e}")
        return (None)

def is_market_open():
    url = "https://paper-api.alpaca.markets/v2/clock"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": os.getenv('API_KEY'),
        "APCA-API-SECRET-KEY": os.getenv('SECRET_KEY')
    }
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    return (response)
