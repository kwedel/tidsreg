import datetime
from dataclasses import dataclass

from playwright.sync_api import Page


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
        return f"{time.hour:02}:{time.minute:02}"


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
