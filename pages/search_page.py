# pages/search_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from logger_utils import log_step

class SearchPage(BasePage):
    DATE_RANGE = [(By.ID, "filter-date_range")]
    SERIAL_INPUT = [(By.ID, "filter-serial_number")]
    PRIMARY_SEARCH_BTN = [(By.ID, "btn-search-primary")]

    def _row_by_ticket(self, ticket_id: str):
        # Your table row id is the ticket id itself: <tr id="P4003300">
        return [(By.XPATH, f"//tr[@id='{ticket_id}']")]

    def _row_action_dropdown(self, ticket_id: str):
        # From your XPath: //tr[@id='P4003300']/td[8]/div/div[2]/span
        return [(By.XPATH, f"//tr[@id='{ticket_id}']/td[8]//div/div[2]/span")]

    PAYMENT_LINK = [
        (By.LINK_TEXT, "Payment"),
        (By.XPATH, "//a[normalize-space()='Payment']"),
    ]

    @log_step("Apply filters and search")
    def apply_filters_and_search(self, serial_number: str = "", press_enter_if_no_button: bool = False):
        try:
            self.safe_click(self.DATE_RANGE)  # open calendar; not setting a range yet
        except Exception:
            self.debug_log.debug("Date range not clickable; continuing.")

        # Type serial if provided; else just click search
        if serial_number:
            self.safe_type(self.SERIAL_INPUT, serial_number)

        try:
            self.safe_click(self.PRIMARY_SEARCH_BTN)
        except Exception:
            if press_enter_if_no_button:
                el = self.try_find_any(self.SERIAL_INPUT, timeout=4)
                el.send_keys(Keys.ENTER)
            else:
                raise

    @log_step("Open ticket row")
    def open_ticket_actions(self, ticket_id: str):
        # Wait for row to be present
        self.try_find_any(self._row_by_ticket(ticket_id), timeout=20)
        # Open row action dropdown
        self.safe_click(self._row_action_dropdown(ticket_id))

    @log_step("Choose Payment from row actions")
    def choose_payment(self):
        self.safe_click(self.PAYMENT_LINK)
        # Navigates into Payment modal/page
    # ADD these locators (class attributes)
    PAID_BY_CASH_PREF = [
        (By.XPATH, "(//span[@class='label label-primary'][normalize-space()='paid by cash'])[1]"),
    ]
    PAID_BY_CASH_ABS = [
        (By.XPATH, "/html/body/div[2]/div/div[2]/div/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[8]/div/div[2]/span[1]"),
    ]

    # ADD this method (inside the class)
    @log_step("Refresh and re-check paid-by-cash")
    def refresh_and_verify_paid_by_cash(self) -> bool:
        self.safe_refresh()
        if self.element_exists(self.PAID_BY_CASH_PREF, timeout=5):
            return True
        return self.element_exists(self.PAID_BY_CASH_ABS, timeout=5)

    # ADD this method (inside the class)
    @log_step("Go back to Search page")
    def back_to_search(self):
        # lightweight reload of current listing
        self.driver.get(self.driver.current_url)
    # ADD: row-scoped locators builder (inside SearchPage)
    # REPLACE this method in SearchPage
    def _row_paid_by_cash_locators(self, ticket_id: str):
        return [
            #  Your Rel XPath (scoped to the ticket row)
            (By.XPATH, f"//tr[@id='{ticket_id}']//span[@class='label label-primary' and normalize-space()='paid by cash']"),

            #  Your Rel CSS (scoped to the ticket row)
            (By.CSS_SELECTOR, f"tr[id='{ticket_id}'] div.col-xs-12.res-table-fine-status.text-important span.label.label-primary"),

            #  Your index XPath (page-level fallback)
            (By.XPATH, "(//span[@class='label label-primary'][normalize-space()='paid by cash'])[1]"),

            #  Your Abs XPath (last resort; brittle)
            (By.XPATH, "/html/body/div[2]/div/div[2]/div/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[8]/div/div[2]/span[1]"),
        ]


    # ADD: refresh results helper (inside SearchPage)
    @log_step("Refresh search results")
    def refresh_results(self):
        try:
            self.safe_click(self.PRIMARY_SEARCH_BTN)
        except Exception:
            # fallback: hit Enter in serial field if button absent
            try:
                el = self.try_find_any(self.SERIAL_INPUT, timeout=2)
                el.send_keys(Keys.ENTER)
            except Exception:
                self.safe_refresh()
