import unittest
from datetime import datetime, timezone
from aresdataprocessing.fetcher.polygon_data_fetcher import PolygonDataFetcher

class TestPolygonDataFetcher(unittest.TestCase):
    def setUp(self):
        self.ticker = 'AAPL'
        self.start_date = datetime(2022, 1, 1, tzinfo=timezone.utc)
        self.end_date = datetime(2022, 1, 2, tzinfo=timezone.utc)
        self.start_timestamp = 1675117801000000000
        self.end_timestamp = 1675117830000000000
        self.fetcher = PolygonDataFetcher()

    def test_fetch_bars(self):
        bar_data = self.fetcher.fetch_bars(self.ticker, self.start_date, self.end_date)
        self.assertIsNotNone(bar_data)

    def test_fetch_trades(self):
        trade_data = self.fetcher.fetch_trades(self.ticker, self.start_timestamp, self.end_timestamp)
        self.assertIsNotNone(trade_data)

if __name__ == '__main__':
    unittest.main()