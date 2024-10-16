import datetime
import logging
import subprocess
from pathlib import Path
from random import choice
from zoneinfo import ZoneInfo

import click
from playwright.sync_api import sync_playwright

from .api import TidsRegger
from .exceptions import NotLoggedIn
from .inspiration import OPMUNTRINGER
from .models import Registration
from .utils import str_to_time

START_OF_DAY = datetime.time(8, 30)

APP_NAME = "tidsreg"


def user_dir() -> Path:
    path = Path(click.get_app_dir(APP_NAME))
    path.mkdir(exist_ok=True, parents=True)
    return path


BROWSER_STATE = user_dir() / "browser_state.json"


@click.group
@click.version_option()
@click.option("-v", "--verbose", count=True)
def cli(verbose):
    """
    Register time from the command line

    Run `tidsreg init` to make inital setup

    """
    loglevel = {1: logging.INFO, 2: logging.DEBUG}
    if verbose:
        logging.basicConfig(level=loglevel[verbose])


@cli.command(name="init")
def init() -> None:
    """
    Install a browser for playwright
    """
    click.echo("Installing chrome for playwright")
    try:
        subprocess.run(["playwright", "install", "chrome"], check=True)  # noqa: S603, S607
    except subprocess.CalledProcessError:
        click.echo("Chrome already installed")


@cli.command(name="login")
def login() -> None:
    """
    Interactively log in to tidsreg
    """
    with sync_playwright() as p:
        tr = TidsRegger(p, BROWSER_STATE)
        tr.log_in()


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
        tr = TidsRegger(p, BROWSER_STATE)

        # Get last end time if no start time is provided
        if start is None:
            click.echo("Getting start time from previous registrations")
            try:
                previous_registrations = tr.get_registrations()
            except NotLoggedIn:
                click.echo('Not logged in. Call "tidsreg login"')
                exit()
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
        try:
            tr.register_hours(registration)
        except NotLoggedIn:
            click.echo('Not logged in. Call "tidsreg login"')
            exit()


@cli.command(name="show")
def show():
    """
    Show all current registrations
    """
    with sync_playwright() as p:
        tr = TidsRegger(p, BROWSER_STATE)

        click.echo("Finding all registrations for today.\n")
        registrations = tr.get_registrations()
        if registrations:
            for reg in registrations:
                click.echo(reg)
        else:
            click.echo("No registrations for today")
            click.echo(choice(OPMUNTRINGER))  # noqa: S311


@cli.command(name="clear")
def clear():
    """
    Delete all registrations for the day
    """
    click.echo("Deleting all current registrations")
    with sync_playwright() as p:
        tr = TidsRegger(p, BROWSER_STATE)
        tr.clear_registrations()
