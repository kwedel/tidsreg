import datetime
import logging
import subprocess
from pathlib import Path
from random import choice
from zoneinfo import ZoneInfo

import click
from playwright.sync_api import sync_playwright

from .api import TidsRegger
from .bulk import BulkRegistration, InvalidBulkRegistration
from .cliutils import format_registration_for_cli
from .exceptions import NotLoggedIn
from .inspiration import OPMUNTRINGER
from .models import Registration
from .utils import registration_length, str_to_time, today

START_OF_DAY = datetime.time(8, 30)
AVG_WORKDAY_HOURS = 7.4

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
@click.option("--headless", help="Login without openeing the browser GUI", is_flag=True)
def login(headless) -> None:
    """
    Interactively log in to tidsreg
    """
    try:
        with sync_playwright() as p:
            tr = TidsRegger(p, BROWSER_STATE)
            tr.log_in(headless=headless)
    except NotLoggedIn:
        click.echo("Login failed.")


@cli.command(name="add")
@click.argument("project", required=True)
@click.option(
    "-s",
    "--start",
    help="Start time of registration, defaults to last end time or START_OF_DAY",
)
@click.option("-e", "--end", help="End time of registration, default to current time")
@click.option("-m", "--comment", help="Message for registration", default="")
@click.option(
    "-d",
    "--date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(today()),
)
@click.option(
    "--dry-run", help="Just output planned changes", is_flag=True, default=False
)
def add(project, start, end, comment, date, dry_run) -> None:
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
        tr.goto_date(date.date())
        # Get last end time if no start time is provided
        if start is None:
            click.secho("Getting start time from previous registrations", dim=True)
            try:
                previous_registrations = tr.get_registrations()
            except NotLoggedIn:
                click.secho('Not logged in. Call "tidsreg login"', fg="red")
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
        click.echo("Creating registration:")
        click.echo(format_registration_for_cli(registration))
        if dry_run:
            click.echo("Dry run - no changes made")
            return
        try:
            tr.register_hours(registration)
        except NotLoggedIn:
            click.echo('Not logged in. Call "tidsreg login"')
            exit()


@cli.command(name="show")
@click.option(
    "-d",
    "--date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(today()),
)
def show(date):
    """
    Show all current registrations
    """
    name_of_date = "today" if date.date() == today() else date.date()
    with sync_playwright() as p:
        tr = TidsRegger(p, BROWSER_STATE)
        tr.goto_date(date.date())
        click.secho(f"Finding all registrations for {name_of_date}...\n", dim=True)
        try:
            registrations = tr.get_registrations()
        except NotLoggedIn:
            click.echo('Not logged in. Call "tidsreg login"')
            exit()

        if not registrations:
            if name_of_date != "today":
                click.echo(f"No registrations for {date.date()}")
                return
            click.echo("No registrations for today")
            click.echo(choice(OPMUNTRINGER))  # noqa: S311
            return

        click.secho(f'{"Time":<14}{"Project":<53}Comment')
        click.echo("-" * 115)
        for reg in registrations:
            click.echo(format_registration_for_cli(reg))
        click.echo("-" * 115)

        # Find total registered time
        registered_worktime = sum(
            (registration_length(reg) for reg in registrations),
            start=datetime.timedelta(0),
        )
        worktime_color = (
            "green"
            if registered_worktime >= datetime.timedelta(hours=AVG_WORKDAY_HOURS)
            else "red"
        )
        hours, remainder = divmod(registered_worktime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        click.echo()
        click.secho(
            f"You currently have {len(registrations)} registration(s) today totalling ",
            nl=False,
            dim=True,
        )
        click.secho(f"{hours} hours and {minutes} minutes", fg=worktime_color, dim=True)


@cli.command(name="clear")
@click.option(
    "-d",
    "--date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(today()),
)
@click.option(
    "-y",
    "--yes",
    help="Delete without asking for confirmation",
    is_flag=True,
    default=False,
)
def clear(date, yes):
    """
    Delete all registrations for the day
    """
    with sync_playwright() as p:
        tr = TidsRegger(p, BROWSER_STATE)
        tr.goto_date(date.date())
        regs = tr.get_registrations()
        if not regs:
            click.echo("You don't have any registrations for {date.date()}.")
            return
        click.echo(f"Deleting {len(regs)} registrations for {date.date()}.")
        if yes:
            tr.clear_registrations()
            return
        while True:
            click.echo("Continue? (y or n) ", nl=False)
            c = click.getchar()
            click.echo()
            if c == "y":
                tr.clear_registrations()
                click.echo("Registrations deleted.")
                return
            elif c == "n":
                click.echo("Abort!")
                return
            else:
                click.echo("Invalid input - try again.")


@cli.command(name="bulk")
@click.option("-f", "--filename", type=click.File("r"), required=True)
@click.option(
    "-d",
    "--date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(today()),
)
def bulk(filename, date):
    """
    Register multiple items in one go
    """
    try:
        bulk_reg = BulkRegistration.from_file(filename)
    except InvalidBulkRegistration:
        click.secho("Bulk registration file is not valid.", fg="red")
        return
    with sync_playwright() as p:
        tr = TidsRegger(p, BROWSER_STATE)
        tr.goto_date(date.date())
        click.echo(f"Creating {len(bulk_reg)} registrations")
        with click.progressbar(bulk_reg) as bar:
            for reg in bar:
                tr.register_hours(reg)
