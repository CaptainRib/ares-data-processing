import sys
sys.path.append('/home/jeffreydhy/workspace/project-ares/ares-finance')

import pandas as pd
from utils.time_utils import Utility
from utils.data_utils import DataUtils

from data.fetcher.polygon_data_fetcher import PolygonDataFetcher
from train.pattern_recognition.segementation_generation import SegmentImageGenerator



def read_data(start_time, end_time):
    fetcher = PolygonDataFetcher()
    
    symbol = 'AMD'
    start_time_nano = Utility.datetime_str_to_nanoseconds(start_time)
    end_time_nano = Utility.datetime_str_to_nanoseconds(end_time)
    trade_data = fetcher.fetch_trades(symbol, start_time_nano, end_time_nano)
    df = DataUtils.import_data_from_iter(trade_data, symbol)
    return df

def load_data():
    for date in dates:
        start_time = '{}T09:30:00'.format(date)
        end_time = '{}T16:00:00'.format(date)
        data = read_data(start_time=start_time, end_time=end_time)
        data.to_csv('~/data/projects/ares-finance/raw/trade/amd/{}.csv'.format(date), index=False)
        df1 = DataUtils.resample_xmin_bars(data, 1)
        df1.to_csv('~/data/projects/ares-finance/generated/bar/amd/{}_1_min.csv'.format(date), index=False)
        
#load_data()
def generate_img():
    for date in dates:
        data = pd.read_csv('~/data/projects/ares-finance/generated/bar/amd/{}_1_min.csv'.format(date), parse_dates=['timestamp'])
        segment_sizes = [30]
        seggen = SegmentImageGenerator(data)
        seggen.generate_segmented_images(segment_sizes, 'AMD', date)
    

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
