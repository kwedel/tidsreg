import datetime


def skip_n(it, n=1):
    """Skip n elements in iterator"""
    for i, element in enumerate(it):
        if i >= n:
            yield element


def str_to_time(time: str) -> datetime.time:
    if ":" in time:
        return datetime.time(*map(int, time.split(":")))
    if len(time) <= 2:  # '8, 09, 12'
        return datetime.time(int(time))
    if len(time) >= 3:  # '830, 915
        return datetime.time(int(time[:-2]), int(time[-2:]))


def truncate_string(text: str, length: int | None) -> str:
    if length is None or len(text) <= length:
        return text
    return text[: length - 3] + "..."
