from abc import ABC, abstractmethod
from backtest.broker.broker import Broker

class BaseStrategy(ABC):
    def __init__(self):
        self.broker = None
        
    @abstractmethod
    def on_trade(self):
        """
        Main strategy runtime method, called as each new
        `backtesting.backtesting.Strategy.data`
        instance (row; full candlestick bar) becomes available.
        This is the main method where strategy decisions
        upon data precomputed in `backtesting.backtesting.Strategy.init`
        take place.
        If you extend composable strategies from `backtesting.lib`,
        make sure to call:
            super().next()
        """
    
    def register_broker(self, broker: Broker) -> None:
        self.broker = broker