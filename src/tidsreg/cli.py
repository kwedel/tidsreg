import datetime
from zoneinfo import ZoneInfo

import click
from playwright.sync_api import sync_playwright

from .api import TidsRegger
from .models import Registration
from .utils import str_to_time

START_OF_DAY = datetime.time(8, 30)


@click.group
def cli():
    pass


@cli.command(name="add")
@click.argument("project", required=True)
@click.option("-s", "--start", help="Start time of registration")
@click.option("-e", "--end", help="End time of registration")
@click.option("-m", "--comment", help="Message for registration")
@click.option(
    "--dry-run", help="Just output planned changes", is_flag=True, default=False
)
def add(project, start, end, comment, dry_run) -> None:
    with sync_playwright() as p:
        tr = TidsRegger(p)

        # Get last end time if no start time is provided
        if start is None:
            click.echo("Getting start time from previous registrations")
            previous_registrations = tr.get_registrations()
            if not previous_registrations:
                start_time = START_OF_DAY
            else:
                start_time = previous_registrations[-1].end_time
        else:
            start_time = str_to_time(start)

        end_time = (
            datetime.datetime.now(ZoneInfo("localtime")).time()
            if end is None
            else str_to_time(end)
        )

        registration = Registration(project, start_time, end_time, comment)
        click.echo(f"Creating registration {registration}")
        if dry_run:
            click.echo("Dry run - no changes made")
            return
        tr.register_hours(registration)
