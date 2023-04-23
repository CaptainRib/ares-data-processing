from typing import Callable, List, Type
from data.fetcher.polygon_data_model import Trade
from backtest.broker.broker import Broker
from backtest.strategy.strategy import BaseStrategy
from loguru import logger

class Ares(object):
    '''
    Ares is the orchestrator method to trigger data replay and backtesting
    '''
    def __init__(self):
        self.broker_on_trade = None
        self.strategy_on_trade = None
        self.data = None
        self.symbol = None
        self.broker = None
        self.ending_cash = None
        
        self.logger = logger.bind(classname="Ares")
        
    def configure_backtest(self, broker_on_trade: Callable[[Trade], None],
                           strategy: Type[BaseStrategy],
                           symbol: str, starting_cash: float = 30000) -> None:
        self._register_broker_callback(broker_on_trade)
        self._register_strategy_callback(strategy.on_trade)
        self.symbol = symbol
        self.broker = Broker(starting_cash)
        strategy.register_broker(self.broker)
        
    def _register_broker_callback(self, on_trade: Callable[[Trade], None]) -> None:
        self.broker_on_trade = on_trade
    
    def _register_strategy_callback(self, on_trade: Callable[[Trade], None]) -> None:
        self.strategy_on_trade = on_trade
        
    def load_data(self, data: List[Trade]) -> None:
        self.data = data
    
    def bark(self):
        '''Main function to run the backtest
        '''
        logger.info("Starting replaying trade for {}".format(self.symbol))
        for trade in self.data:
            self.broker_on_trade(trade)
            self.strategy_on_trade(trade)
        
    def plot(self) -> None:
        pass
    
    def generate_summary(self) -> str:
        pass