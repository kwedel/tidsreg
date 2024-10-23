import datetime
from dataclasses import dataclass
from itertools import pairwise
from typing import TextIO

from playwright.sync_api import Page

from .bulk import read_registration_file
from .exceptions import InvalidBulkRegistration


@dataclass
class Registration:
    project: str
    start_time: datetime.time
    end_time: datetime.time
    comment: str = ""

    @property
    def start_time_str(self):
        return self._format_time(self.start_time)

    @property
    def end_time_str(self):
        return self._format_time(self.end_time)

    def _format_time(self, time):
        """Format datetime as a string in the form HH:MM"""
        return f"{time.hour:02}:{time.minute:02}"

    def __lt__(self, other):
        return self.start_time < other.start_time


class RegistrationDialog:
    """Pop-up registration dialog"""

    def __init__(self, page: Page):
        self.dialog = page.frame_locator("#dialog-body")
        self.start = self.dialog.locator(
            "#NormalContainer_NormalTimePnl_NormalTimeStart"
        )
        self.slut = self.dialog.locator("#NormalContainer_NormalTimePnl_NormalTimeEnd")
        self.kommentar = self.dialog.get_by_role("textbox", name="Til personligt notat")
        self.ok_button = self.dialog.get_by_role("button", name="Ok")
        self.annullere_button = self.dialog.get_by_role("button", name="Annullere")
        self.slet_button = self.dialog.get_by_role("button", name="Slet")


class BulkRegistration:
    """Many registrations at the same time"""

    def __init__(self, registrations: list[Registration]) -> None:
        self.registrations = sorted(registrations)
        if not self._is_valid_plan():
            raise InvalidBulkRegistration("overlapping registrations")

    def _is_valid_plan(self) -> bool:
        return [
            reg2.start_time >= reg1.end_time
            for reg1, reg2 in pairwise(self.registrations)
        ].any()

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
