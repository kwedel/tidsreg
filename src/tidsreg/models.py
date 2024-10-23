import datetime
from dataclasses import dataclass


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
