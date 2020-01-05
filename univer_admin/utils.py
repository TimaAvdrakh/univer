from datetime import datetime, timedelta
import pytz


def get_local_in_utc():
    """Получить местное время в UTC"""
    now_utc = datetime.now(tz=pytz.utc)
    local_in_utc = now_utc + timedelta(hours=6)

    return local_in_utc

