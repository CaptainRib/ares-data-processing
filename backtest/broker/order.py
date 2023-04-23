from enum import Enum
from backtest.exceptions.broker_exception import BrokerException


class OrderType(Enum):
    MARKET = 1
    LIMIT = 2
    STOP = 3


class OrderSide(Enum):
    LONG = 1
    SHORT = 2


class Order:
    def __init__(self, symbol: str, quantity: int, order_type: OrderType, side: OrderSide, 
                 time_in_force: str = "GTC", stop_price: float = None, limit_price: float = None, market_price: float = None):
        self.symbol = symbol
        self.quantity = quantity
        self.order_type = order_type
        self.time_in_force = time_in_force
        self.side = side
        self.id = None
        if order_type == OrderType.MARKET and ((limit_price or stop_price) or not market_price):
            raise BrokerException("You must and only can specify market price for a market order")
            # We still want to use market price to check account balance, though it will not be used in trade
        if order_type == OrderType.LIMIT and ((stop_price or market_price) or not limit_price):
            raise BrokerException("You must and only can specify limit price for a limit order")
        if order_type == OrderType.STOP and ((limit_price or market_price) or not stop_price):
            raise BrokerException("You must and only can specify stop price for a stop order")
        if stop_price:
            self.price = stop_price
        elif limit_price:
            self.price = limit_price
        else:
            self.price = market_price
    
    def __str__(self):
        if self.order_type == OrderType.MARKET:
            return f"{self.quantity} {self.side.name} {self.order_type.name} order of {self.symbol}"
        else:
            return f"{self.quantity} {self.side.name} {self.order_type.name} order of {self.symbol} at {self.price}"
        
    def set_order_id(self, id: str) -> None:
        self.id = id
    
    def get_order_id(self) -> str:
        return self.id
    
    def get_quantity(self) -> int:
        return self.quantity

    def get_price(self) -> float:
        return self.price

    def get_side(self) -> OrderSide:
        return self.side

    def get_symbol(self) -> str:
        return self.symbol
    
    def get_order_type(self) -> OrderType:
        return self.order_type