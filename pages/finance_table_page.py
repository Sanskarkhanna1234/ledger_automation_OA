# pages/finance_table_page.py
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage
from logger_utils import log_step


class FinanceTablePage(BasePage):
    """
    Utilities for reading the Finance 'Payment History' table (UI only).
    This reads the FIRST ROW using the exact selectors you provided and
    appends a formatted line to logs/tabel_log/<log_name>.
    """

    # ---- (optional) quick filter controls on the Finance page ----
    _FILTER_LOCAL_CHECK = [(By.XPATH, "//input[@value='local']")]
    _FILTER_SEARCH_INPUT = [(By.XPATH, "//input[@type='search']")]
    _FILTER_SEARCH_BTN = [
        (By.ID, "searchCitation"),
        (By.XPATH, "//button[@id='searchCitation']"),
    ]

    # ---- FIRST ROW locators you provided (UI table only) ----
    _TICKET_NUMBER = [
        (By.CSS_SELECTOR, "body > div:nth-child(4) > div:nth-child(2) > div:nth-child(11) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > table:nth-child(4) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1)")
    ]
    _DATE = [
        (By.XPATH, "//body[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[2]")
    ]
    _TICKET_STATUS = [
        (By.XPATH, "//body[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]")
    ]
    _ORIGINAL_FINE = [
        (By.XPATH, "//body[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[6]")
    ]
    _AMOUNT_PAID = [
        (By.XPATH, "//body[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[7]")
    ]
    _AMOUNT_OWED = [
        (By.XPATH, "//tbody/tr[1]/td[8]")
    ]

    # Payment Status badges / cell (first that matches "wins")
    _STATUS_PAID_BY_CASH = [(By.XPATH, "//span[normalize-space()='paid by cash']")]
    _STATUS_UNPAID = [(By.XPATH, "//span[@class='label label-danger']")]
    _STATUS_GENERIC_COL11 = [(By.XPATH, "//tbody/tr[1]/td[11]/span[1]")]  # e.g. "void"

    # ---- helpers ----
    def _ensure_table_log_dir(self):
        os.makedirs(os.path.join("logs", "tabel_log"), exist_ok=True)

    def _text_or_blank(self, locs, timeout=5) -> str:
        try:
            el = self.try_find_any(locs, timeout=timeout)
            return (el.text or "").strip()
        except Exception:
            return ""

    def _read_payment_status(self) -> str:
        if self.element_exists(self._STATUS_PAID_BY_CASH, timeout=1):
            return "paid by cash"
        if self.element_exists(self._STATUS_UNPAID, timeout=1):
            return "unpaid"
        # Fallback: whatever label is in col 11 (often "void")
        val = self._text_or_blank(self._STATUS_GENERIC_COL11, timeout=1)
        return val or ""

    # ---- public API ----
    @log_step("Apply Finance table filter (optional)")
    def apply_filter(self, ticket_id: str, ensure_local: bool = True):
        """Type into the table's 'Search' box and click the Search button."""
        try:
            if ensure_local:
                cb = self.try_find_any(self._FILTER_LOCAL_CHECK, timeout=5)
                if not cb.is_selected():
                    cb.click()
        except Exception:
            # harmless if not present
            self.debug_log.debug("Local checkbox missing or already selected.")

        # Type ticket and search
        box = self.try_find_any(self._FILTER_SEARCH_INPUT, timeout=10)
        box.clear()
        box.send_keys(ticket_id)

        try:
            self.safe_click(self._FILTER_SEARCH_BTN)
        except Exception:
            # some UIs filter instantly without button
            self.debug_log.debug("Search button not clickable; relying on live filtering.")

        # small pause for table redraw
        time.sleep(0.7)

    @log_step("Read first row from Finance table and append log line")
    def log_first_row(self, log_name: str = "finance_table.log"):
        """
        Reads: ticket number | date | Ticket status | Original Fine |
               Amount Paid | Amount Owed | Payment Status

        Appends a single line to logs/tabel_log/<log_name>.
        Returns (line, file_path).
        """
        self._ensure_table_log_dir()

        ticket_number = self._text_or_blank(self._TICKET_NUMBER)
        date = self._text_or_blank(self._DATE)
        ticket_status = self._text_or_blank(self._TICKET_STATUS)
        original_fine = self._text_or_blank(self._ORIGINAL_FINE)
        amount_paid = self._text_or_blank(self._AMOUNT_PAID)
        amount_owed = self._text_or_blank(self._AMOUNT_OWED)
        payment_status = self._read_payment_status()

        line = f"{ticket_number} | {date} | {ticket_status} | {original_fine} | {amount_paid} | {amount_owed} | {payment_status}"

        path = os.path.join("logs", "tabel_log", log_name)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        # mirror to step logger for quick visibility
        self.step_log.info(f"[TABLE] {line}")

        return line, path
