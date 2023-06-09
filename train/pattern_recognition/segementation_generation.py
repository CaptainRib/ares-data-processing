import matplotlib.dates as mdates
import plotly.graph_objects as go
import os
import pytz


class SegmentImageGenerator:
    def __init__(self, data):
        self.data = data

    def _generate_candlestick_image(self, start, segment_size, output_dir):
        """
        Generate and save a candlestick chart image from the given DataFrame.

        :param data: pd.DataFrame, containing columns: 'open', 'high', 'low', 'close', and indexed by timestamp
        :param start: int, the index at which to start the segment
        :param segment_size: int, the number of consecutive bars to include in the segment
        :param output_filename: str, the path to save the generated image
        """

        segment_data = self.data.iloc[start:start + segment_size].reset_index()
        segment_data['timestamp'] = mdates.date2num(segment_data['timestamp'].dt.to_pydatetime())
        timestamp_start = mdates.num2date(segment_data['timestamp'].iloc[0])
        timestamp_end = mdates.num2date(segment_data['timestamp'].iloc[-1])
        
        fig = go.Figure(data=[go.Candlestick(x=segment_data['timestamp'],
                    open=segment_data['open'],
                    high=segment_data['high'],
                    low=segment_data['low'],
                    close=segment_data['close'], increasing_line_color='red', decreasing_line_color='red')])
        
        # Remove slider, set background color to white and remove grid
        fig.update_layout(xaxis_rangeslider_visible=False, paper_bgcolor='white', xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False))
        fig.update_traces(line=dict(width=0))

        timestamp_start_utc = timestamp_start.replace(tzinfo=pytz.UTC)
        timestamp_end_utc = timestamp_end.replace(tzinfo=pytz.UTC)

        new_york_tz = pytz.timezone('America/New_York')

        timestamp_start_ny = timestamp_start_utc.astimezone(new_york_tz)
        timestamp_end_ny = timestamp_end_utc.astimezone(new_york_tz)

        timestamp_start_str = timestamp_start_ny.strftime('%Y%m%d%H%M%S')
        timestamp_end_str = timestamp_end_ny.strftime('%Y%m%d%H%M%S')
        output_filename = os.path.join(output_dir, '{}_{}.png'.format(timestamp_start_str, timestamp_end_str))
        fig.write_image(output_filename)
    

    def generate_segmented_images(self, segment_sizes, ticker, output_dir, step=1):
        """
        Generate and save candlestick chart images for multiple segment sizes and start indices.

        :param data: pd.DataFrame, containing columns: 'open', 'high', 'low', 'close', and indexed by timestamp
        :param segment_sizes: list of int, the segment sizes (in minutes) to generate images for
        :param step: int, the step size for iterating through the data (default: 1)
        """
        # Find the correct output directory

        for segment_size in segment_sizes:
            size_dir = os.path.join(output_dir, f"{ticker}_{segment_size}min_segments")
            os.makedirs(size_dir, exist_ok=True)

            for start in range(0, len(self.data) - segment_size, step):
                self._generate_candlestick_image(start, segment_size, size_dir)
