from ..fetcher.polygon_data_model import Trade
from typing import Iterator
from polygon.rest.models import Trade as PTrade
import pandas as pd

class DataUtils:

    @staticmethod
    def import_data_from_iter(_iter: Iterator[PTrade], symbol: str) -> pd.DataFrame:
        '''Import data from Polygon iter to Panda DataFrame.

        Args:
            _iter (Iterator[PTrade]): _description_
            symbol (str): _description_

        Returns:
            pd.DataFrame: Data Frame that contains trade data
        '''
        datas = []
        for trade in _iter:
            d = Trade(symbol, trade.sip_timestamp, trade.price, trade.size)
            datas.append(d)
        return pd.DataFrame.from_records([s.to_dict() for s in datas])

    @staticmethod
    def resample_xmin_bars(df: pd.DataFrame, multiplier: int) -> pd.DataFrame:
        df = df.copy()
        # Convert the timestamp from nanoseconds to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')

        # Set the timestamp as the index
        df.set_index('timestamp', inplace=True)

        # Convert the timezone to New York
        df.index = df.index.tz_localize('UTC').tz_convert('America/New_York')

        # Resample and calculate open, high, low, and close prices
        open_prices = df['price'].resample('{}min'.format(multiplier)).first()
        high_prices = df['price'].resample('{}min'.format(multiplier)).max()
        low_prices = df['price'].resample('{}min'.format(multiplier)).min()
        close_prices = df['price'].resample('{}min'.format(multiplier)).last()
        
        # Resample and calculate the total quantity
        total_quantity = df['quantity'].resample('{}min'.format(multiplier)).sum()

        # Calculate the volume-weighted price
        df['price_quantity'] = df['price'] * df['quantity']
        volume_weighted_price_sum = df['price_quantity'].resample('{}min'.format(multiplier)).sum()
        volume_weighted_price = volume_weighted_price_sum / total_quantity

        # Combine the results into a new DataFrame
        result = pd.DataFrame({
            'open': open_prices,
            'close': close_prices,
            'high': high_prices,
            'low': low_prices,
            'v': total_quantity,
            'vw': volume_weighted_price
        })

        # Reset the index to convert the DateTimeIndex back to a column
        result.reset_index(inplace=True)

        return result