from datetime import datetime, timedelta



def is_valid_time(d: datetime):
    return d.minute == 0 or d.minute == 30


def is_30_minutes(start: datetime, end: datetime):
    return (end-start).seconds == 1800

def is_date_aware(d: datetime):
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None

def is_date_passed(d: datetime):
    return datetime.now() > d
