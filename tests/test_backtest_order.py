import unittest
from backtest.broker.broker import Broker, OrderStatus
from backtest.broker.order import Order, OrderType, OrderSide
from backtest.exceptions.broker_exception import BrokerException


class TestOrder(unittest.TestCase):

    def test_order_creation(self):
        order1 = Order('AAPL', 10, OrderType.MARKET, OrderSide.LONG, market_price=100.0)
        self.assertEqual(order1.get_symbol(), 'AAPL')
        self.assertEqual(order1.get_quantity(), 10)
        self.assertEqual(order1.get_order_type(), OrderType.MARKET)
        self.assertEqual(order1.get_side(), OrderSide.LONG)
        self.assertIsNone(order1.get_order_id())

        order2 = Order('AAPL', 10, OrderType.LIMIT, OrderSide.SHORT, limit_price=100.0)
        self.assertEqual(order2.get_symbol(), 'AAPL')
        self.assertEqual(order2.get_quantity(), 10)
        self.assertEqual(order2.get_order_type(), OrderType.LIMIT)
        self.assertEqual(order2.get_side(), OrderSide.SHORT)
        self.assertIsNone(order2.get_order_id())
        self.assertEqual(order2.get_price(), 100.0)

    def test_order_creation_with_exception(self):
        with self.assertRaisesRegex(BrokerException, "You must and only can specify market price for a market order"):
            Order('AAPL', 10, OrderType.MARKET, OrderSide.SHORT, limit_price=100.0)

        with self.assertRaisesRegex(BrokerException, "You must and only can specify limit price for a limit order"):
            Order('AAPL', 10, OrderType.LIMIT, OrderSide.LONG, stop_price=100.0)

        with self.assertRaisesRegex(BrokerException, "You must and only can specify stop price for a stop order"):
            Order('AAPL', 10, OrderType.STOP, OrderSide.SHORT, limit_price=100.0)