from typing import List, Optional
from collections import defaultdict
from backtest.broker.order import OrderSide, Order


class Position:
    def __init__(self, symbol: str, side: OrderSide, quantity: int, price: float):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.avg_price = round(price, 3)
        self.realized_profit = 0
        self.unrealized_profit = 0

    def __str__(self):
        return f"{self.position_type.name} {self.quantity} shares of {self.symbol} at {self.price:.2f}"

    def get_value(self, current_price: float) -> float:
        return self.quantity * current_price

    def get_realized_profit(self) -> float:
        return self.realized_profit
    
    def get_unrealized_profit(self) -> float:
        return self.unrealized_profit
    
    def get_avg_price(self) -> float:
        return self.avg_price
    
    def get_symbol(self) -> str:
        return self.symbol
    
    def get_quantity(self) -> int:
        return self.quantity
    
    def get_side(self) -> OrderSide:
        return self.side
    
    def update_quantity(self, quantity: int) -> None:
        self.quantity += quantity
    
    def update_avg_price(self, price: float, quantity: int) -> None:
        # quantity could be negative. need to take abs value
        current_total = self.quantity * self.avg_price
        total_delta = abs(quantity) * price
        self.avg_price = round((current_total + total_delta) / (self.quantity + quantity), 3)
    
    def update_realized_profit(self, delta: float) -> None:
        self.realized_profit += round(delta, 3)


class Account:
    def __init__(self, initial_balance: float):
        self.balance = initial_balance
        self.buying_power = initial_balance # Used to withold buying power when order is placed but not executed.
        self.open_positions = defaultdict() # Key is (symbol, side)
        self.closed_positions = defaultdict() # Key is (symbol, side)

    def get_open_position(self, symbol: str, side: OrderSide) -> Optional[Position]:
        if (symbol, side) not in self.open_positions:
            return None
        return self.open_positions[(symbol, side)]

    def get_closed_position(self, symbol: str, side: OrderSide) -> Optional[Position]:
        if (symbol, side) not in self.closed_positions:
            return None
        return self.closed_positions[(symbol, side)]
    
    def list_open_positions(self) -> List[Position]:
        return self.open_positions.values()

    def list_closed_positions(self) -> List[Position]:
        return self.closed_positions.values()

    def update_position(self, price: float, order: Order):
        symbol = order.get_symbol()
        side = order.get_side()
        quantity = order.get_quantity()
        # Update position should also update account balance and buying power
        open_position = self.get_open_position(symbol=symbol, side=side)
        if not open_position:
            new_position = Position(symbol=symbol, side=side, quantity=quantity, price=price)
            # We don't need to worry about negative quantity case.
            # If there's no open position, order system won't accept order with negative quantity
            cost = quantity * price
            self.update_balance(-cost)
            # reduce actual amount from buying power
            self.update_buying_power(-cost)
            # Credit back the witholding amount
            self.update_buying_power(order.get_quantity() * order.get_price())
            self.open_positions[(symbol, side)] = new_position
        else:
            # In this case, we have an open position already
                    
            if quantity < 0:
            # We are either selling on a LONG order or buying on a SHORT order
                if order.get_side() == OrderSide.SHORT:
                    realized_profit = abs(quantity) * (open_position.get_avg_price() - price)
                    net_proceeding = (open_position.get_avg_price() * abs(quantity)) + realized_profit
                # We do not need to update average price for the open order
                else:
                    realized_profit = abs(quantity) * (price - open_position.get_avg_price())
                    net_proceeding = abs(quantity) * price
                self.update_buying_power(net_proceeding)
                self.update_balance(net_proceeding)
                open_position.update_quantity(quantity)
                
                # Update closed position entry
                closed_position = self.get_closed_position(symbol=symbol, side=side)
                if not closed_position:
                    new_closed_position = Position(symbol=symbol, side=side, quantity=abs(quantity), price=0)
                    new_closed_position.update_realized_profit(realized_profit)
                    self.closed_positions[(symbol, side)] = new_closed_position
                else:
                    closed_position.update_quantity(abs(quantity))
                    closed_position.update_realized_profit(realized_profit)
                    
                # If we are selling all shares. We need to remove the position from open positions
                if not open_position.get_quantity():
                    del self.open_positions[(symbol, side)]
                    
            else:
                # We are adding to the current position. In this case, quantity is for sure a positive int
                cost = quantity * price
                self.update_balance(-cost)
                # reduce actual amount from buying power
                self.update_buying_power(-cost)
                # Credit back the witholding amount
                self.update_buying_power(order.get_quantity() * order.get_price())
                open_position.update_avg_price(price=price, quantity=quantity)
                open_position.update_quantity(quantity)
            
    def get_balance(self) -> float:
        return self.balance
    
    def update_balance(self, delta) -> float:
        self.balance += delta
    
    def update_buying_power(self, delta) -> None:
        self.buying_power += delta
        
    def get_buying_power(self) -> float:
        return self.buying_power
     
    def __str__(self) -> str:
        # TODO: implement this function
        pass