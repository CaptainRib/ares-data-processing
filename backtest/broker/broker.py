from backtest.broker.account import Account
from backtest.broker.order import OrderType, Order, OrderSide
from backtest.exceptions.broker_exception import BrokerException
from data.fetcher.polygon_data_model import Trade
from typing import List, Union
from loguru import logger
from collections import defaultdict
from enum import Enum


class OrderStatus(Enum):
    '''Order status Enum

    Legit State transition:
    1 -> 3
    1 -> 4
    or initial value
    '''
    ACCEPTED = 1
    REJECTED = 2
    CANCELED = 3
    FILLED = 4


class OrderBook(object):
    '''
    Order book lists all order sent to broker. All orders are validated before entered in book
    Valid order will have status 1, 3 or 4. Invalid order will have status 2.
    '''
    def __init__(self):
        self.logger = logger.bind(classname="OrderBook")
        self.order_book = defaultdict()
    
    def add_order(self, order: Order, status: OrderStatus) -> None:
        logger.info('Added order {} to order book. Current status is {}'.format(order.get_order_id(), status.name))
        self.order_book[order.get_order_id()] = (order, status)
    
    def update_order(self, order_id: str, status: OrderStatus) -> None:
        order, current_status = self.order_book[order_id]
        if current_status == OrderStatus.ACCEPTED and (status is not OrderStatus.CANCELED and status is not OrderStatus.FILLED):
            raise BrokerException('Invliad argument. Order can only be transited from ACCEPTED to CANCELED or FILLED')
        self.order_book[order_id] = (order, status)
        logger.info('Updated order status of {} from {} to {}'.format(order_id, current_status.name, status.name))

    def get_order(self, order_id: str) -> Union[Order, OrderStatus]:
        return self.order_book[order_id]

    def list_orders(self, order_status: OrderStatus = None, symbol: str = None) -> List:
        '''List orders in order book.

        Args:
            order_status (str, optional): _description_. Defaults to None.
            symbol (str, optional): _description_. Defaults to None.

        Raises:
            BrokerException: _description_

        Returns:
            _type_: _description_
        '''
        symbol_result = set()
        status_result = set()
        total_result = []
        for order, status in self.order_book.values():
            if symbol and order.get_symbol() == symbol:
                symbol_result.add(order)
            if status and status == order_status:
                status_result.add(order)
            total_result.append(order)
        if symbol and order_status:
            return list(symbol_result & status_result)
        elif symbol:
            return list(symbol_result)
        elif order_status:
            return list(status_result)
        else:
            return total_result


class Broker(object):
    def __init__(self, initial_balance=30000.0) -> None:
        self.logger = logger.bind(classname="Broker")
        self.account = Account(initial_balance)
        self.order_count = 0 # This is used to generate order ID
        self.order_book = OrderBook()
    
    def on_trade(self, trade: Trade) -> None:
        '''
        Passed as a callback function to data feed and 
        will react accordingly when trade happens.
        
        Operations inclueds:
        1. Check order book and try to execute any pending order
        2. Update account position information
        '''
        trade_symbol = trade.symbol
        eligible_orders = self.order_book.list_orders(order_status=OrderStatus.ACCEPTED, symbol=trade_symbol)
        for order in eligible_orders:
            if self._can_execute(order=order, trade=trade):
                self.logger.info("Executing order {} at price {}".format(order.get_order_id(), trade.price))
                self._exec_order(order=order, trade=trade)
        # TODO should periodically send trade data to account so that we can have a P&L history.
        # https://app.asana.com/0/1204114474228984/1204114397988410/f

    def submit_order(self, order: Order) -> str:
        '''Submit an order. Order will be put in order book for execution.

        Args:
            order (Order): Order object

        Returns:
            str: order ID
        '''
        order_id = self._generate_order_id()
        order.set_order_id(order_id)
        valid_order, trading_amount = self._valid_order(order)
        if not valid_order:
            self.order_book.add_order(order, OrderStatus.REJECTED)
            self.logger.info("Rejected {} because account has insufficient balance".format(str(order)))
        else:
            self.order_book.add_order(order, OrderStatus.ACCEPTED)
            self.account.update_buying_power(-1 * trading_amount) # Witholding account balance for trade
            self.logger.info('Received {} with order ID {}'.format(str(order), order.get_order_id()))
        return order_id
    
    def cancel_order(self, order_id: str) -> None:
        order, order_status = self.order_book.get_order(order_id)
        if order_status != OrderStatus.ACCEPTED:
            raise BrokerException('Invalid Status. Current order stauts must be ACCPETED before it can be canceld')
        trading_amount = order.get_quantity() * order.get_price()
        self.account.update_buying_power(trading_amount) # Credit witholding back to account
        self.order_book.update_order(order_id, OrderStatus.CANCELED)
    
    def _can_execute(self, order: Order, trade: Trade) -> bool:
        executed = False
        order_type = order.get_order_type()
        side = order.get_side()
        order_price = order.get_price()
        quantity = order.get_quantity()
        
        # If trade is not relevant to the order, directly return false
        if order.get_symbol() != trade.symbol:
            return False
        
        # Check if this order can be executed
        # Check https://app.asana.com/0/1204114474228984/1204114474228987/f for execution logic
        # It's ugly but it's easier to read
        if order_type == OrderType.MARKET:
            executed = True
        else:
            if side == OrderSide.LONG:
                if quantity > 0: # We are trying to OPEN a position
                    if order_type == OrderType.LIMIT:
                        if order_price >= trade.price:
                            return True
                        else:
                            return False
                    if order_type == OrderType.STOP:
                        if order_price > trade.price:
                            return False
                        else:
                            return True
                elif quantity < 0:
                    if order_type == OrderType.LIMIT:
                        if order_price > trade.price:
                            return False
                        else:
                            return True
                    if order_type == OrderType.STOP:
                        if order_price >= trade.price:
                            return True
                        else:
                            return False
            else:
                if quantity > 0:
                    if order_type == OrderType.LIMIT:
                        if order_price > trade.price:
                            return False
                        else:
                            return True
                    if order_type == OrderType.STOP:
                        if order_price >= trade.price:
                            return True
                        else:
                            return False
                elif quantity < 0:
                    if order_type == OrderType.LIMIT:
                        if order_price >= trade.price:
                            return True
                        else:
                            return False
                    if order_type == OrderType.STOP:
                        if order_price > trade.price:
                            return False
                        else:
                            return True
        return executed
    
    def _exec_order(self, order: Order, trade: Trade) -> None:
        trade_price = trade.price
        # Update account position and balance
        self.account.update_position(price=trade_price, order=order)
        # Change order book status
        self.order_book.update_order(order.get_order_id(), OrderStatus.FILLED)

    def list_orders(self, order_status: OrderStatus = None, symbol: str = None) -> List:
        return self.order_book.list_orders(order_status, symbol)
    
    def _valid_order(self, order: Order) -> Union[bool, float]:
        '''Check if order is a valid order. Valid order means the account has
        enough balance to fill the order at the given price.

        Args:
            order (Order): an order object
        '''
        buying_power = self.account.get_buying_power()
        symbol = order.get_symbol()
        quantity = order.get_quantity()
        price = order.get_price()
        amount = quantity * price
        side = order.get_side()
        if side == OrderSide.LONG:
            opposite_side = OrderSide.SHORT
        else:
            opposite_side = OrderSide.LONG
            
        if quantity < 0:
            # We are closing position. No need to reserve buying power
            open_position = self.account.get_open_position(symbol=symbol, side=side)
            open_orders = self.order_book.list_orders(order_status=OrderStatus.ACCEPTED, symbol=symbol)
            current_quantity = 0
            for open_order in open_orders:
                if open_order and side == open_order.get_side() and open_order.get_quantity() < 0:
                    current_quantity += abs(open_order.get_quantity())
            if not open_position or open_position.get_quantity() - current_quantity < abs(quantity):
                self.logger.info("Invalid order. We don't have enough open position to sell for {}".format(symbol))
                return False, 0
            
            return True, 0
        
        else: # In this case, we are open position or adding to existing position
            opposite_open_position = self.account.get_open_position(symbol=symbol, side=opposite_side)
            if opposite_open_position: # We don't allow open position in a opposite direction
                return False, 0
            unfilled_order = self.order_book.list_orders(order_status=OrderStatus.ACCEPTED, symbol=symbol)
            for o in unfilled_order:
                if o.get_side() == opposite_side:
                    return False, 0
            return amount <= buying_power, amount
    
    def _generate_order_id(self) -> str:
        self.order_count += 1
        return 'X{}'.format(str(100000+self.order_count))