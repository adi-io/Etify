import os
from dotenv import load_dotenv
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

load_dotenv()

trading_client = TradingClient(os.getenv('API_KEY'), os.getenv('SECRET_KEY'), paper=True)
price_client = StockHistoricalDataClient(os.getenv('API_KEY'), os.getenv('SECRET_KEY'))

def spy_limit_order(user_bid_price, quantity):
    try:
        limit_order_buy = LimitOrderRequest(
            symbol="SPY",
            limit_price=user_bid_price,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.IOC
        )
        order = trading_client.submit_order(order_data=limit_order_buy)
        return (order)

    except Exception as e:
        print(f"Failed to place to buy order on the exchange {e}")
        return None

def spy_market_buy_order(amount):
    try:
        market_order_buy = MarketOrderRequest(
            symbol="SPY",
            notional=amount,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        order = trading_client.submit_order(order_data=market_order_buy)
        return (order.id)

    except Exception as e:
        print(f"Failed to place to buy order on the exchange {e}")
        return None

def spy_market_sell_order(amount):
    try:
        market_order_sell = MarketOrderRequest(
            symbol="SPY",
            qty=amount,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        order = trading_client.submit_order(order_data=market_order_sell)
        return (order.id)

    except Exception as e:
        print(f"Failed to place to sell order on the exchange {e}")
        return None

def order_details(order_id):
    try:
        order = trading_client.get_order_by_id(order_id)
        if order:
            if order.status == OrderStatus.FILLED:
                return (order)
        return (None)

    except Exception as e:
        print(f"Failed to get order details on the exchange {e}")
        return None
