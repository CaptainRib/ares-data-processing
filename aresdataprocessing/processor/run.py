import pandas as pd
from .segementation_generation import SegGen
from ..utils.time_utils import Utility
from ..utils.data_utils import DataUtils
from ..fetcher.polygon_data_fetcher import PolygonDataFetcher

import sys
sys.path.append('/Users/captainrib/workspace/project-ares/ares-data-processing/aresdataprocessing')

def read_data():
    fetcher = PolygonDataFetcher()
    start_time = '2023-03-20T09:30:00-04:00'
    end_time = '2023-03-20T16:00:00-04:00'
    symbol = 'AMD'
    start_time_nano = Utility.datetime_str_to_nanoseconds(start_time)
    end_time_nano = Utility.datetime_str_to_nanoseconds(end_time)
    trade_data = fetcher.fetch_trades(symbol, start_time_nano, end_time_nano)
    df = DataUtils.import_data_from_iter(trade_data, symbol)
    df1 = DataUtils.resample_xmin_bars(df, 1)
    return df1

data = pd.read_csv('data/raw/amd.csv', parse_dates=['timestamp'])

segment_sizes = [30]
seggen = SegGen(data)
seggen.generate_segmented_images(segment_sizes)