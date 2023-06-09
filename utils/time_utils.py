import datetime
from dateutil import tz
from dateutil import parser

class Utility:

    @staticmethod
    def datetime_str_to_nanoseconds(date_time_str: str) -> int:
        """
        Convert a date and time string to nanoseconds.

        Args:
            date_time_str (str): Date and time string in the format: 'YYYY-MM-DDTHH:MM:SS±hh:mm'.
            
        Example:
            start_time = '2023-03-20T09:30:00-04:00' This is New York time
            start_time_nano = Utility.datetime_str_to_nanoseconds(start_time)

        Returns:
            int: Date and time in nanoseconds since the epoch.
        """
        try:
            new_york = tz.gettz('America/New_York')
            dt = parser.parse(date_time_str).replace(tzinfo=new_york)
            if dt.dst() != datetime.timedelta(0):  # Check if within Daylight Saving Time
                tz_offset = "-04:00"
            else:
                tz_offset = "-05:00"
            date_time_str += tz_offset
            dt = parser.parse(date_time_str)
            dt_utc = dt.astimezone(datetime.timezone.utc)
            nanoseconds = int(dt_utc.timestamp() * 1e9)
            return nanoseconds
        except ValueError as e:
            raise ValueError("Invalid date_time_str format. Use 'YYYY-MM-DDTHH:MM:SS±hh:mm'.") from e
        
    @staticmethod
    def list_trading_days(date_start: str, date_end: str):
        date_start = datetime.datetime.strptime(date_start, "%Y-%m-%d")
        date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d")
        result = []
        while date_start <= date_end:
            if date_start.weekday() <=4: # Sat and Sunday is 5 and 6
                result.append(date_start.strftime("%Y-%m-%d")) 
            date_start += datetime.timedelta(days=1)
            
        market_holidays = ['2021-01-01', '2021-01-18', '2021-02-15', '2021-04-02', '2021-05-31', '2021-07-05', '2021-09-06', '2021-11-25', '2021-11-26', '2021-12-24', '2022-01-17', '2022-02-21', '2022-04-15', '2022-05-30', '2022-06-20', '2022-07-04', '2022-09-05', '2022-11-24', '2022-11-25', '2022-12-26', '2023-01-02', '2023-01-16', '2023-02-20', '2023-03-24', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04', '2023-11-23', '2023-12-25']

        return list(set(result) - set(market_holidays))