import sys
sys.path.append('/home/jeffreydhy/workspace/project-ares/ares-finance')

import pandas as pd
from utils.time_utils import Utility
from train.pattern_recognition.segementation_generation import SegmentImageGenerator

def generate_img(dates, output_dir):
    for date in dates:
        data = pd.read_csv('~/data/projects/ares-finance/generated/bar/amd/{}_1_min.csv'.format(date), parse_dates=['timestamp'])
        segment_sizes = [30]
        seggen = SegmentImageGenerator(data)
        seggen.generate_segmented_images(segment_sizes, 'AMD', output_dir)
        

output_base_directory = '/home/jeffreydhy/data/projects/ares-finance/generated/images/inference'
SYMBOL = 'AMD'
DATE_START = '2023-01-01'
DATE_END = '2023-04-28'
dates = Utility.list_trading_days(DATE_START, DATE_END)
generate_img(dates, output_base_directory)