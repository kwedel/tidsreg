import datetime
from zoneinfo import ZoneInfo

import click
from playwright.sync_api import sync_playwright

from .api import TidsRegger
from .models import Registration
from .utils import str_to_time

START_OF_DAY = datetime.time(8, 30)


@click.group
@click.version_option()
def cli():
    """
    Register time from the command line

    """


@cli.command(name="init")
def init() -> None:
    """
    Install a browser for playwright, and start log in flow
    """
    raise NotImplementedError


@cli.command(name="add")
@click.argument("project", required=True)
@click.option(
    "-s",
    "--start",
    help="Start time of registration, defaults to last end time or START_OF_DAY",
)
@click.option("-e", "--end", help="End time of registration, default to current time")
@click.option("-m", "--comment", help="Message for registration")
@click.option(
    "--dry-run", help="Just output planned changes", is_flag=True, default=False
)
def add(project, start, end, comment, dry_run) -> None:
    """
    Add a new registration to PROJECT

    Uses case-insensitive substring matching to find the right PROJECT from your list of favorites

    Times can be input as HH, HHMM or HH:MM

    Example usage:

        tidsreg add teammeeting --start 915 -m "Planning in small team"
        tidsreg add frokost --start 11:30 --end 12
    """
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


@cli.command(name="show")
def show():
    """
    Show all current registrations
    """
    with sync_playwright() as p:
        tr = TidsRegger(p)

        click.echo("Finding all registrations for today.\n")
        registrations = tr.get_registrations()
        for reg in registrations:
            click.echo(reg)
