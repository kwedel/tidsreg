import datetime

from tidsreg.utils import str_to_time


def test_str_to_time():
    cases = [
        ("8", datetime.time(8)),
        ("09", datetime.time(9)),
        ("12", datetime.time(12)),
        ("830", datetime.time(8, 30)),
        ("915", datetime.time(9, 15)),
        ("1259", datetime.time(12, 59)),
        ("8:20", datetime.time(8, 20)),
        ("15:10", datetime.time(15, 10)),
    ]
    for input_string, result in cases:
        assert str_to_time(input_string) == result