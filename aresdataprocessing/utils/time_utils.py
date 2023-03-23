import datetime
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
            dt = parser.parse(date_time_str)
            dt_utc = dt.astimezone(datetime.timezone.utc)
            nanoseconds = int(dt_utc.timestamp() * 1e9)
            return nanoseconds
        except ValueError as e:
            raise ValueError("Invalid date_time_str format. Use 'YYYY-MM-DDTHH:MM:SS±hh:mm'.") from e