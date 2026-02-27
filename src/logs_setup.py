from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now()
now_local = now.astimezone(ZoneInfo(key="America/Bogota"))
time_stamp = now.strftime("[ %d-%m-%Y %H:%M ]")


def get_time_stamp() -> str:
    now = datetime.now()
    now_local = now.astimezone(ZoneInfo(key="America/Bogota"))

    return now_local.strftime("[ %d-%m-%Y %I:%M %p ]")
