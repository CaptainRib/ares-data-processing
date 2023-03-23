from polygon import RESTClient
from dotenv import load_dotenv
import os

class PolygonDataFetcher:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('POLYGON_API_KEY')
        self.client = RESTClient(self.api_key)
    
    def fetch_bars(self, ticker, from_timestamp, to_timestamp, limit=50000, timespan='minute', multiplier=1):
        return self.client.list_aggs(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_=from_timestamp,
            to=to_timestamp,
            adjusted=False,
            sort='asc',
            limit=limit,
        )
    
    def fetch_trades(self, ticker, from_timestamp, to_timestamp, limit=50000):
        return self.client.list_trades(
            ticker=ticker,
            timestamp_gte=from_timestamp,
            timestamp_lte= to_timestamp,
            limit=limit,
        )