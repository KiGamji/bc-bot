import re
from datetime import timedelta, datetime


def parse_time(timestr):
    regex = r"(?:(\d+)[MМ])?(?:(\d+)[wWнН])?(?:(\d+)[dDдД])?(?:(\d+)[hHчЧ])?(?:(\d+)[mм])?(?:(\d+)[sSсС])?"
    match = re.search(regex, timestr)

    months, weeks, days, hours, minutes, seconds = (
        int(x) if x else 0 for x in match.groups()
    )

    delta = timedelta(
        days=months*30 + weeks*7 + days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )
    return delta
