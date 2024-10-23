import csv
from itertools import pairwise
from typing import TextIO

from .exceptions import InvalidBulkRegistration
from .models import Registration
from .utils import str_to_time


class BulkRegistration:
    """Many registrations at the same time"""

    def __init__(self, registrations: list[Registration]) -> None:
        self.registrations = sorted(registrations)
        if not self._is_valid_plan():
            raise InvalidBulkRegistration("overlapping registrations")

    def _is_valid_plan(self) -> bool:
        return any(
            reg2.start_time >= reg1.end_time
            for reg1, reg2 in pairwise(self.registrations)
        )

    @classmethod
    def from_file(cls, f: TextIO):
        registrations = read_registration_file(f)
        return cls(registrations)

    def __iter__(self):
        for reg in self.registrations:
            yield reg

    def __len__(self):
        return len(self.registrations)

    def __repr__(self):
        return f"BulkRegistration[<{len(self.registrations)} Registrations>]"


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
