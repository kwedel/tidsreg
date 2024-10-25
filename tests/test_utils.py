import datetime

from tidsreg.models import Registration
from tidsreg.utils import registration_length, str_to_time, truncate_string


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


def test_truncation():
    text = "This is a long text"  # length 19

    assert truncate_string(text, None) == text
    assert truncate_string(text, 100) == text
    assert truncate_string(text, 19) == text
    assert truncate_string(text, 18) == "This is a long ..."
    assert truncate_string(text, 6) == "Thi..."


def test_registration_length():
    reg1 = Registration(
        "project", start_time=datetime.time(10), end_time=datetime.time(11)
    )
    assert registration_length(reg1) == datetime.timedelta(hours=1)
    reg2 = Registration(
        "project", start_time=datetime.time(10), end_time=datetime.time(10, 30)
    )
    assert registration_length(reg2) == datetime.timedelta(minutes=30)

    total_time = registration_length(reg1) + registration_length(reg2)

    assert total_time == datetime.timedelta(hours=1.5)
