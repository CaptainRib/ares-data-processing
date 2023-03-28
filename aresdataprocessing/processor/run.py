import pandas as pd
from .segementation_generation import SegGen
from ..utils.time_utils import Utility
from ..utils.data_utils import DataUtils
from ..fetcher.polygon_data_fetcher import PolygonDataFetcher

import sys
sys.path.append('/Users/captainrib/workspace/project-ares/ares-data-processing/aresdataprocessing')

def read_data(start_time, end_time):
    fetcher = PolygonDataFetcher()
    
    symbol = 'AMD'
    start_time_nano = Utility.datetime_str_to_nanoseconds(start_time)
    end_time_nano = Utility.datetime_str_to_nanoseconds(end_time)
    trade_data = fetcher.fetch_trades(symbol, start_time_nano, end_time_nano)
    df = DataUtils.import_data_from_iter(trade_data, symbol)
    df1 = DataUtils.resample_xmin_bars(df, 1)
    return df1

dates = [
        # '2023-01-03',
        # '2023-01-04',
        # '2023-01-05',
        # '2023-01-06',
        # '2023-01-09',
        # '2023-01-10',
        # '2023-01-11',
        # '2023-01-12',
        # '2023-01-13',
        # '2023-01-17',
        # '2023-01-18',
        # '2023-01-19',
        # '2023-01-20',
        # '2023-01-23',
        # '2023-01-24',
        # '2023-01-25',
        # '2023-01-26',
        # '2023-01-27',
        # '2023-01-30',
        # '2023-01-31',
        # '2023-02-01',
        # '2023-02-02',
        # '2023-02-03',
        # '2023-02-06',
        # '2023-02-07',
        # '2023-02-08',
        # '2023-02-09',
        # '2023-02-10',
        # '2023-02-13',
        # '2023-02-14',
        # '2023-02-15',
        # '2023-02-16',
        # '2023-02-17',
        # '2023-02-21',
        # '2023-02-22',
        # '2023-02-23',
        # '2023-02-24',
        # '2023-02-27',
        # '2023-02-28',
        # '2023-03-01',
        # '2023-03-02',
        # '2023-03-03',
        # '2023-03-06',
        # '2023-03-07',
        # '2023-03-08',
        # '2023-03-09',
        # '2023-03-10',
        # '2023-03-13',
        # '2023-03-14',
        # '2023-03-15',
        # '2023-03-16',
        # '2023-03-17',
        # '2023-03-20',
        # '2023-03-21',
        # '2023-03-22'
        '2023-03-23'
        ]


def load_data():
    for date in dates:
        start_time = '{}T09:30:00-04:00'.format(date)
        end_time = '{}T16:00:00-04:00'.format(date)
        data = read_data(start_time=start_time, end_time=end_time)
        data.to_csv('data/raw/amd_{}.csv'.format(date))
        
# load_data()
def generate_img():
    for date in dates:
        data = pd.read_csv('data/raw/amd_{}.csv'.format(date), parse_dates=['timestamp'])
        segment_sizes = [30]
        seggen = SegGen(data)
        seggen.generate_segmented_images(segment_sizes, date)
    
#load_data()
generate_img()

# import os
# import shutil

# xml_folder = '/Users/captainrib/workspace/project-ares/ares-data-processing/data/images/labeled'
# image_folder = '/Users/captainrib/workspace/project-ares/ares-data-processing/data/images/30min_segments'

# # Get all the XML file names
# xml_files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]

# # Move the corresponding images to the XML folder
# for xml_file in xml_files:
#     image_name = xml_file[:-4] + '.png'  # Replace .xml extension with .png
#     image_path = os.path.join(image_folder, image_name)
    
#     # Check if the image file exists in the image folder
#     if os.path.exists(image_path):
#         # Move the image to the XML folder
#         shutil.move(image_path, os.path.join(xml_folder, image_name))
#     else:
#         print(f"Image {image_name} not found in the image folder.")
