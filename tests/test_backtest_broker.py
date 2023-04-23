import unittest
from backtest.broker.broker import Broker, OrderStatus
from backtest.broker.order import Order, OrderType, OrderSide
from backtest.exceptions.broker_exception import BrokerException
from data.fetcher.polygon_data_model import Trade


class TestBroker(unittest.TestCase):

    def setUp(self):
        self.broker = Broker(initial_balance=10000.0)

    def test_submit_order(self):
        order = Order(symbol="AAPL", side=OrderSide.LONG, order_type=OrderType.MARKET, quantity=100, market_price=99)
        order_id = self.broker.submit_order(order)
        self.assertIsNotNone(order_id)
        self.assertEqual(order_id, "X100001")
        self.assertEqual(self.broker.account.get_buying_power(), 100.0)
        _, order_status = self.broker.order_book.get_order(order_id)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
    
    def test_failure_in_submit_order(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        self.assertIsNotNone(order_id1)
        self.assertEqual(order_id1, 'X100001')
        self.assertEqual(self.broker.account.get_buying_power(), 8770)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        order2 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.MARKET, quantity=200, market_price=11.2)
        order_id2 = self.broker.submit_order(order2)
        self.assertIsNotNone(order_id2)
        self.assertEqual(self.broker.account.get_buying_power(), 8770) # Since this is a rejected order, we shouldn't update BP
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.REJECTED)
        order3 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id3 = self.broker.submit_order(order3)
        self.assertIsNotNone(order_id3)
        self.assertEqual(order_id3, 'X100003')
        self.assertEqual(self.broker.account.get_buying_power(), 7540)
        _, order_status = self.broker.order_book.get_order(order_id3)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        self.broker.account.update_position(12.2, order1)
        self.broker.account.update_position(12.2, order3)
        self.assertEqual(self.broker.account.get_buying_power(), 7560)
        order4 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.MARKET, quantity=200, market_price=11.2)
        order_id4 = self.broker.submit_order(order4)
        self.assertEqual(order_id4, 'X100004')
        self.assertIsNotNone(order_id4)
        self.assertEqual(self.broker.account.get_buying_power(), 7560) # Since this is a rejected order, we shouldn't update BP
        _, order_status = self.broker.order_book.get_order(order_id4)
        self.assertEqual(order_status, OrderStatus.REJECTED)
        order5 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.MARKET, quantity=-200, market_price=11.2)
        order_id5 = self.broker.submit_order(order5)
        self.assertIsNotNone(order_id5)
        self.assertEqual(order_id5, 'X100005')
        self.assertEqual(self.broker.account.get_buying_power(), 7560)
        _, order_status = self.broker.order_book.get_order(order_id5)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        self.broker.account.update_position(13, order5)
        self.assertEqual(self.broker.account.get_buying_power(), 10160)

    def test_cancel_order(self):
        order = Order(symbol="AAPL", side=OrderSide.LONG, order_type=OrderType.MARKET, quantity=100, market_price=99)
        order_id = self.broker.submit_order(order)
        self.assertIsNotNone(order_id)
        self.assertEqual(order_id, "X100001")
        self.broker.cancel_order(order_id)
        self.assertEqual(self.broker.account.get_buying_power(), 10000.0)
        _, order_status = self.broker.order_book.get_order(order_id)
        self.assertEqual(order_status, OrderStatus.CANCELED)
        
    def test_cancel_order_wrong_status(self):
        with self.assertRaises(BrokerException):
            order = Order(symbol="AAPL", side=OrderSide.LONG, order_type=OrderType.MARKET, quantity=100)
            order_id = self.broker.submit_order(order)
            self.broker.order_book.update_order(order_id, OrderStatus.FILLED)
            self.broker.cancel_order(order_id)

    def test_generate_order_id(self):
        order_id_1 = self.broker._generate_order_id()
        self.assertEqual(order_id_1, "X100001")
        order_id_2 = self.broker._generate_order_id()
        self.assertEqual(order_id_2, "X100002")
        
    def test_list_orders(self):
        order1 = Order(symbol="AAPL", quantity=1, side=OrderSide.LONG, order_type=OrderType.LIMIT, limit_price=192.2)
        order2 = Order(symbol="AAPL", quantity=1, side=OrderSide.SHORT, order_type=OrderType.LIMIT, limit_price=192.2)
        order3 = Order(symbol="AMZN", quantity=1, side=OrderSide.SHORT, order_type=OrderType.LIMIT, limit_price=192.2)
        order4 = Order(symbol="TSLA", quantity=1, side=OrderSide.SHORT, order_type=OrderType.LIMIT, limit_price=192.2)
        order5 = Order(symbol="TSLA", quantity=1, side=OrderSide.SHORT, order_type=OrderType.LIMIT, limit_price=1920000.2)
        order6 = Order(symbol="TSLA", quantity=1, side=OrderSide.LONG, order_type=OrderType.MARKET, market_price=190.0)
        self.broker.submit_order(order1)
        self.broker.submit_order(order2)
        self.broker.submit_order(order3)
        self.broker.submit_order(order4)
        self.broker.submit_order(order5)
        self.broker.cancel_order('X100004')
        self.assertEqual(set(['X100001', 'X100003']), set([order.get_order_id() for order in self.broker.list_orders(OrderStatus.ACCEPTED)]))
        self.assertEqual(set(['X100005', 'X100002']), set([order.get_order_id() for order in self.broker.list_orders(OrderStatus.REJECTED)]))
        self.assertEqual(set(['X100004']), set([order.get_order_id() for order in self.broker.list_orders(OrderStatus.CANCELED)]))
        self.assertEqual(set(['X100002', 'X100001']), set([order.get_order_id() for order in self.broker.list_orders(symbol='AAPL')]))
        self.assertEqual(set(['X100005', 'X100002', 'X100003', 'X100004', 'X100001']), set([order.get_order_id() for order in self.broker.list_orders()]))
        self.assertEqual([], self.broker.list_orders(OrderStatus.ACCEPTED, 'AMC'))
        self.broker.submit_order(order6)
        self.assertEqual(set(['X100006']), set([order.get_order_id() for order in self.broker.list_orders(OrderStatus.ACCEPTED, 'TSLA')]))
    
    def test_order_execution(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        self.assertIsNotNone(order_id1)
        self.assertEqual(order_id1, 'X100001')
        self.assertEqual(self.broker.account.get_buying_power(), 8770)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        trade1 = Trade('AAPL', 123456, 12.4, 100)
        
        # Trade 1 should not fill the order
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order('X100001')
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        self.assertEqual(self.broker.account.get_balance(), 10000)
        
        trade2 = Trade('AAPL', 123457, 12.3, 100)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order('X100001')
        self.assertEqual(order_status, OrderStatus.FILLED)
        self.assertEqual(self.broker.account.get_balance(), 8770)
        
        order2 = Order(symbol='AMZN', side=OrderSide.SHORT, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id2 = self.broker.submit_order(order2)
        self.assertIsNotNone(order_id2)
        self.assertEqual(order_id2, 'X100002')
        self.assertEqual(self.broker.account.get_buying_power(), 7540)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        trade3 = Trade('AAPL', 123458, 12.2, 1000)
        self.broker.on_trade(trade3)
        _, order_status = self.broker.order_book.get_order('X100002')
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        self.assertEqual(self.broker.account.get_balance(), 8770)
        self.assertEqual(len(self.broker.account.list_open_positions()), 1)
        self.assertEqual(len(self.broker.account.list_closed_positions()), 0)
        
        trade4 = Trade('AMZN', 123459, 12.4, 1000)
        self.broker.on_trade(trade4)
        _, order_status = self.broker.order_book.get_order('X100002')
        self.assertEqual(order_status, OrderStatus.FILLED)
        self.assertEqual(self.broker.account.get_balance(), 7530)
        self.assertEqual(self.broker.account.get_buying_power(), 7530)
        self.assertEqual(len(self.broker.account.list_open_positions()), 2)
        self.assertEqual(len(self.broker.account.list_closed_positions()), 0)
        
        order3 = Order(symbol='AMZN', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id3 = self.broker.submit_order(order3)
        self.assertIsNotNone(order_id3)
        self.assertEqual(order_id3, 'X100003')
        self.assertEqual(self.broker.account.get_buying_power(), 7530)
        _, order_status = self.broker.order_book.get_order(order_id3)
        self.assertEqual(order_status, OrderStatus.REJECTED)
        
        order4 = Order(symbol='AMZN', side=OrderSide.SHORT, order_type=OrderType.MARKET, quantity=-100, market_price=11.3)
        order_id4 = self.broker.submit_order(order4)
        self.assertIsNotNone(order_id4)
        self.assertEqual(order_id4, 'X100004')
        self.assertEqual(self.broker.account.get_buying_power(), 7530)
        _, order_status = self.broker.order_book.get_order(order_id4)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade5 = Trade('AMZN', 123452, 9.3, 1000)
        self.broker.on_trade(trade5)
        self.assertEqual(self.broker.account.get_balance(), 9080)
        _, order_status = self.broker.order_book.get_order(order_id4)
        self.assertEqual(order_status, OrderStatus.FILLED)
        self.assertEqual(len(self.broker.account.list_open_positions()), 1)
        self.assertEqual(len(self.broker.account.list_closed_positions()), 1)
        closed_amzn_short = self.broker.account.get_closed_position('AMZN', OrderSide.SHORT)
        self.assertEqual(closed_amzn_short.get_quantity(), 100)
        self.assertEqual(closed_amzn_short.get_realized_profit(), 310)

        order5 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=-50, limit_price=14.2)
        order_id5 = self.broker.submit_order(order5)
        self.assertIsNotNone(order_id5)
        self.assertEqual(order_id5, 'X100005')
        self.assertEqual(self.broker.account.get_buying_power(), 9080)
        _, order_status = self.broker.order_book.get_order(order_id5)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        self.assertEqual(self.broker.account.get_buying_power(), 9080)
        
        trade6 = Trade('AAPL', 1235321, 14.5, 200)
        self.broker.on_trade(trade6)
        _, order_status = self.broker.order_book.get_order(order_id5)
        self.assertEqual(order_status, OrderStatus.FILLED)
        self.assertEqual(len(self.broker.account.list_open_positions()), 1)
        self.assertEqual(len(self.broker.account.list_closed_positions()), 2)
        self.assertEqual(self.broker.account.get_balance(), 9805)
        
        order6 = Order(symbol='AMZN', side=OrderSide.SHORT, order_type=OrderType.MARKET, quantity=100, market_price=11.3)
        order_id6 = self.broker.submit_order(order6)
        _, order_status = self.broker.order_book.get_order(order_id6)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        self.assertEqual(self.broker.account.get_buying_power(), 8675)

        trade7 = Trade('AMZN', 123423123, 11.9, 200)
        self.broker.on_trade(trade7)
        _, order_status = self.broker.order_book.get_order(order_id6)
        self.assertEqual(order_status, OrderStatus.FILLED)
        self.assertEqual(self.broker.account.get_balance(), 8615)
        self.assertEqual(self.broker.account.get_buying_power(), 8615)
        
        order8 = Order(symbol='AMZN', side=OrderSide.SHORT, order_type=OrderType.LIMIT, quantity=-100, limit_price=8.3)
        order_id8 = self.broker.submit_order(order8)
        _, order_status = self.broker.order_book.get_order(order_id8)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade8 = Trade('AMZN', 123123, 7.4, 200)
        self.broker.on_trade(trade8)
        _, order_status = self.broker.order_book.get_order(order_id8)
        self.assertEqual(order_status, OrderStatus.FILLED)
        closed_amzn_short = self.broker.account.get_closed_position('AMZN', OrderSide.SHORT)
        self.assertEqual(closed_amzn_short.get_realized_profit(), 760)
        self.assertEqual(self.broker.account.get_balance(), 10255)

        order9 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=-50, limit_price=10.2)
        self.broker.submit_order(order9)
        trade9 = Trade('AAPL', 123123, 11.2, 200)
        self.broker.on_trade(trade9)
        self.assertEqual(len(self.broker.account.list_open_positions()), 0)
        self.assertEqual(len(self.broker.account.list_closed_positions()), 2)
        self.assertEqual(self.broker.account.get_balance(), 10815)
        
    def test_multiple_close_order(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        self.assertIsNotNone(order_id1)
        self.assertEqual(order_id1, 'X100001')
        self.assertEqual(self.broker.account.get_buying_power(), 8770)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade1 = Trade('AAPL', 123457, 12.3, 100)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order('X100001')
        self.assertEqual(order_status, OrderStatus.FILLED)
        self.assertEqual(self.broker.account.get_balance(), 8770)
        
        order2 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=-80, limit_price=12.3)
        order3 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=-80, limit_price=12.3)
        order_id2 = self.broker.submit_order(order2)
        order_id3 = self.broker.submit_order(order3)
        _, order_status2 = self.broker.order_book.get_order(order_id2)
        _, order_status3 = self.broker.order_book.get_order(order_id3)
        self.assertEqual(order_status2, OrderStatus.ACCEPTED)
        self.assertEqual(order_status3, OrderStatus.REJECTED)
    
        order4 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=-20, limit_price=12.3)
        order_id4 = self.broker.submit_order(order4)
        _, order_status4 = self.broker.order_book.get_order(order_id4)
        self.assertEqual(order_status4, OrderStatus.ACCEPTED)
    
    def test_multiple_open_order(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        self.assertIsNotNone(order_id1)
        self.assertEqual(order_id1, 'X100001')
        self.assertEqual(self.broker.account.get_buying_power(), 8770)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        order2 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id2 = self.broker.submit_order(order2)
        self.assertIsNotNone(order_id2)
        self.assertEqual(order_id2, 'X100002')
        self.assertEqual(self.broker.account.get_buying_power(), 7540)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
    
    def test_can_execute_order_with_limit_order_to_open_long(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # if limit_price < trade.price, should not succeed
        trade1 = Trade('AAPL', 123, 12.4, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        # if limit_price >= trade.price, should not succeed
        trade2 = Trade('AAPL', 123, 12.3, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    def test_can_execute_order_with_limit_order_to_open_short(self):
        order1 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # if limit_price > trade.price, should not succeed
        trade1 = Trade('AAPL', 123, 12.2, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # if limit_price <= trade.price, should succeed
        trade2 = Trade('AAPL', 123, 12.4, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    def test_can_execute_order_with_limit_order_to_close_long(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade1 = Trade('AAPL', 123, 12.3, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
        
        order2 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.LIMIT, quantity=-100, limit_price=12.5)
        order_id2 = self.broker.submit_order(order2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # when limit_price > trade.price, should not close
        trade2 = Trade('AAPL', 123, 12.3, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        # when limit_price <= trade.price, should close
        trade3 = Trade('AAPL', 123, 12.5, 1000)
        self.broker.on_trade(trade3)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    def test_can_execute_order_with_limit_order_to_close_short(self):
        order1 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade1 = Trade('AAPL', 123, 12.4, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
        
        order2 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.LIMIT, quantity=-100, limit_price=11.6)
        order_id2 = self.broker.submit_order(order2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # when limit_price < trade.price, should not close
        trade2 = Trade('AAPL', 123, 11.8, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        # when limit_price >= trade.price, should close
        trade3 = Trade('AAPL', 123, 11.2, 1000)
        self.broker.on_trade(trade3)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    # Testing Stop orders
    def test_can_execute_order_with_stop_order_to_open_long(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.STOP, quantity=100, stop_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # if stop_price > trade.price, should not succeed
        trade1 = Trade('AAPL', 123, 12.2, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        # if stop_price <= trade.price, should not succeed
        trade2 = Trade('AAPL', 123, 12.3, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    def test_can_execute_order_with_stop_order_to_open_short(self):
        order1 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.STOP, quantity=100, stop_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # if stop_price < trade.price, should not succeed
        trade1 = Trade('AAPL', 123, 12.4, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # if stop_price >= trade.price, should succeed
        trade2 = Trade('AAPL', 123, 12.2, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    def test_can_execute_order_with_stop_order_to_close_long(self):
        order1 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.STOP, quantity=100, stop_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade1 = Trade('AAPL', 123, 12.3, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
        
        order2 = Order(symbol='AAPL', side=OrderSide.LONG, order_type=OrderType.STOP, quantity=-100, stop_price=12.5)
        order_id2 = self.broker.submit_order(order2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # when stop_price < trade.price, should not close
        trade2 = Trade('AAPL', 123, 12.6, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        # when stop_price >= trade.price, should close
        trade3 = Trade('AAPL', 123, 12.5, 1000)
        self.broker.on_trade(trade3)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.FILLED)
    
    def test_can_execute_order_with_stop_order_to_close_short(self):
        order1 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.LIMIT, quantity=100, limit_price=12.3)
        order_id1 = self.broker.submit_order(order1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        trade1 = Trade('AAPL', 123, 12.4, 1000)
        self.broker.on_trade(trade1)
        _, order_status = self.broker.order_book.get_order(order_id1)
        self.assertEqual(order_status, OrderStatus.FILLED)
        
        order2 = Order(symbol='AAPL', side=OrderSide.SHORT, order_type=OrderType.STOP, quantity=-100, stop_price=11.6)
        order_id2 = self.broker.submit_order(order2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)
        
        # when stop_price > trade.price, should not close
        trade2 = Trade('AAPL', 123, 11.2, 1000)
        self.broker.on_trade(trade2)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.ACCEPTED)

        # when stop_price <= trade.price, should close
        trade3 = Trade('AAPL', 123, 11.6, 1000)
        self.broker.on_trade(trade3)
        _, order_status = self.broker.order_book.get_order(order_id2)
        self.assertEqual(order_status, OrderStatus.FILLED)