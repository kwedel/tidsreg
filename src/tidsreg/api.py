import datetime
import logging
import re
from pathlib import Path

from playwright.sync_api import Playwright, TimeoutError

from .exceptions import NotLoggedIn
from .models import Registration, RegistrationDialog

logger = logging.getLogger(__name__)

TIDSREG_URL = (
    "https://kktidsregistreringks-kksky.msappproxy.net/TimeManager.aspx?Elm=7470"
)
TIDSREG_TITLE = "Koncernservice Tidsregistrering Edge"


class TidsRegger:
    """Class to automate the tedious task of registering time on projects"""

    def __init__(
        self, playwright: Playwright, state: Path | str = "state.json"
    ) -> None:
        self.playwright = playwright
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False
        self.state = Path(state)

    def log_in(self) -> None:
        """Log in interactively"""
        logger.info("Starting browser for log in.")
        browser = self.playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(TIDSREG_URL)
        page.get_by_placeholder("someone@example.com").click()
        input("Log in to the browser and press enter in the terminal.")
        if page.title() != TIDSREG_TITLE:
            context.close()
            browser.close()
            raise NotLoggedIn("log in failed")
        logger.info(f"Succesful log in. Saving state to {self.state}.")
        context.storage_state(path=self.state)
        context.close()
        browser.close()

    def close(self) -> None:
        if self.browser is None:
            logger.info("Browser already closed.")
            return
        logger.info("Closing browser and context.")
        self.context.close()
        self.browser.close()
        self.page = None
        self.context = None
        self.browser = None

    def register_hours(self, registration: Registration) -> None:
        """Make a new registration"""
        self._ensure_browser()
        logger.info(f"Registrering {registration}.")
        logger.debug("Clicking project.")
        self.page.get_by_role("link", name=registration.project).click()
        logger.debug("Filling start time.")
        dialog = self.page.frame_locator("#dialog-body")
        dialog.locator("#NormalContainer_NormalTimePnl_NormalTimeStart").fill(
            registration.start_time_str
        )
        logger.debug("Filling end time.")
        dialog.locator("#NormalContainer_NormalTimePnl_NormalTimeEnd").fill(
            registration.end_time_str
        )

        if registration.comment:
            logger.debug("Filling comment.")
            dialog.get_by_role("textbox", name="Til personligt notat").fill(
                registration.comment
            )
        logger.debug("Clicking OK.")
        dialog.get_by_role("button", name="Ok").click()

    def clear_registrations(self):
        """Delete all current registrations"""
        self._ensure_browser()
        logger.info("Deleting all registrations.")
        registration_rows = self._get_registration_rows()
        while True:
            row = registration_rows.first
            logger.debug(f"Trying to click {row}")
            try:
                row.click(timeout=2000)
                self.page.frame_locator("#dialog-body").get_by_role(
                    "button", name="Slet"
                ).click()
                logger.debug("Row clicked")
            except (AttributeError, TimeoutError):
                logger.debug("No more rows to click.")
                break

    def get_registrations(self) -> list[Registration]:
        """Get all current registrations"""
        self._ensure_browser()
        registrations = []
        logger.info("Fetching all current registrations")
        registration_rows = self._get_registration_rows()
        logger.debug(f"Number of registration rows={len(registration_rows.all())}")
        for i, row in enumerate(registration_rows.all(), 1):
            logger.debug(f"Row {i}")
            registration = self._get_registration_from_row(row)
            logger.debug(registration)
            registrations.append(registration)

        return registrations

    def _get_registration_rows(self):
        return self.page.locator("#Splitter1_RightP_Content").locator(".ListElm")

    def _get_registration_from_row(self, row):
        logger.debug(f"Getting registration from row {row}")
        project = re.search(
            r"[^0-9YDXA\s-]{2}.*", row.locator("td").first.text_content()
        ).group()
        row.click()
        dialog = RegistrationDialog(self.page)
        start_time = datetime.time.fromisoformat(dialog.start.get_attribute("value"))
        end_time = datetime.time.fromisoformat(dialog.slut.get_attribute("value"))
        comment = dialog.kommentar.text_content()
        dialog.annullere_button.click()
        return Registration(project, start_time, end_time, comment)

    def _logged_in(self) -> None:
        self._ensure_browser()
        logger.debug(f"{self.page.title() = !r}")
        return self.page.title() == TIDSREG_TITLE

    def _ensure_browser(self) -> None:
        if self.browser is None:
            self._start_browser()

    def _start_browser(self) -> None:
        if not self.state.exists():
            self.close()
            raise NotLoggedIn("no state is saved from log in. Run .log_in()")

        if self.browser is not None:
            logger.info("Using existing browser.")
            return

        logging.info("Starting browser.")
        self.browser = self.playwright.chromium.launch()
        self.context = self.browser.new_context(storage_state=self.state)
        if not self.context.pages:
            self.page = self.context.new_page()
        else:
            self.page = self.context.pages[0]
        self.page.goto(TIDSREG_URL)
        if not self._logged_in():
            self.close()
            raise NotLoggedIn("browser not logged in. run .log_in()")
