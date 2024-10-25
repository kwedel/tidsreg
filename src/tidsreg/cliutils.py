from .models import Registration
from .utils import truncate_string


def format_registration_for_cli(reg: Registration):
    times = f"{reg.start_time_str}-{reg.end_time_str}"
    project = f"{truncate_string(reg.project, 50):<50}"
    comment = f"{truncate_string(reg.comment, 50):<50}"
    output = f"{times} | {project} | {comment}"
    return output
