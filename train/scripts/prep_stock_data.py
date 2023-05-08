import sys
sys.path.append('/home/jeffreydhy/workspace/project-ares/ares-finance')

from utils.time_utils import Utility
from utils.data_utils import DataUtils

from data.fetcher.polygon_data_fetcher import PolygonDataFetcher

import datetime


def read_data_from_polygon(start_time, end_time, symbol):
    fetcher = PolygonDataFetcher()
    start_time_nano = Utility.datetime_str_to_nanoseconds(start_time)
    end_time_nano = Utility.datetime_str_to_nanoseconds(end_time)
    trade_data = fetcher.fetch_trades(symbol, start_time_nano, end_time_nano)
    df = DataUtils.import_data_from_iter(trade_data, symbol)
    return df

def aggregate_and_save_data(dates, symbol):
    for date in dates:
        start_time = '{}T09:30:00'.format(date)
        end_time = '{}T16:00:00'.format(date)
        data = read_data_from_polygon(start_time=start_time, end_time=end_time, symbol=symbol)
        data.to_csv('~/data/projects/ares-finance/raw/trade/amd/{}.csv'.format(date), index=False)
        df1 = DataUtils.resample_xmin_bars(data, 1)
        df1.to_csv('~/data/projects/ares-finance/generated/bar/amd/{}_1_min.csv'.format(date), index=False)

SYMBOL = 'AMD'
DATE_START = '2023-04-01'
DATE_END = '2023-04-30'
dates = Utility.list_trading_days(DATE_START, DATE_END)
print(dates)
#aggregate_and_save_data(dates, SYMBOL)