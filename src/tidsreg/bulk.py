import csv
from itertools import pairwise
from typing import TextIO

from .models import Registration
from .utils import str_to_time


def read_registration_file(f: TextIO) -> list[Registration]:
    """Read content from a registration file and return a list of Registrations"""
    registrations = []
    lines = list(
        csv.DictReader(f, delimiter="\t", fieldnames=("time", "project", "comment"))
    )
    for l1, l2 in pairwise(lines):
        if l1["project"] is not None:
            registrations.append(
                Registration(
                    project=l1["project"],
                    start_time=str_to_time(l1["time"]),
                    end_time=str_to_time(l2["time"]),
                    comment=l1["comment"],
                )
            )
    return registrations
