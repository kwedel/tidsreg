import datetime
from dataclasses import dataclass

from playwright.sync_api import Page

from .exceptions import InvalidRegistration


@dataclass
class Registration:
    project: str
    start_time: datetime.time
    end_time: datetime.time
    comment: str = ""

    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise InvalidRegistration(
                f"start_time ({self.start_time})  must come before end_time ({self.end_time})"
            )

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
