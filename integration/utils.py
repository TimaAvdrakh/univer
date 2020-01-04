from datetime import datetime
import pytz


def timestamp_to_local_datetime(timestamp):
    """timestamp - in UTC"""
    utc_date = datetime.fromtimestamp(timestamp,
                                      pytz.utc)
    local_date = utc_date.astimezone(pytz.timezone('Asia/Almaty'))
    return local_date

