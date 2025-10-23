from selenium.webdriver.common.by import By
from .base_page import BasePage
from logger_utils import log_step
import time


class FinancePage(BasePage):
    # FINANCE_TAB = [
    #     (By.XPATH, "//a[@id='financeTab']"),
    #     (By.XPATH, "//a[normalize-space()='Finance']"),
    #     (By.CSS_SELECTOR, "a[href*='finance']")
    # ]
    # LAST_PAYMENT_ROW = [
    #     (By.XPATH, "//table[@id='paymentsTable']//tr[1]"),
    #     (By.CSS_SELECTOR, "#paymentsTable tbody tr:first-child"),
    #     (By.XPATH, "//table[contains(@id,'payment')]/tbody/tr[1]")
    # ]

    # @log_step('Verify payment appears in finance ledger')
    # def verify_last_payment(self, expected_amount: str):
    #     self.safe_click(self.FINANCE_TAB)
    #     row = self.try_find_any(self.LAST_PAYMENT_ROW, timeout=20)
    #     text = row.text
    #     assert expected_amount in text, f"Expected amount '{expected_amount}' not found in row: {text}"
    # Add to FinancePage

    FINANCE_CONTAINER = [
        (By.CSS_SELECTOR, "div#finance_panel"),
        (By.XPATH, "//*[contains(@class,'finance') or contains(@id,'finance')]"),
    ]

    ANY_PAYMENTS_ROW = [
        (By.XPATH, "(//table[contains(@id,'payment') or contains(@class,'payment') or contains(@id,'ledger')])[1]//tbody/tr[1]"),
        (By.CSS_SELECTOR, "table tbody tr"),
    ]
    # ADD THESE IN FinancePage class

    FINANCE_SPAN = [(By.XPATH, "//span[normalize-space()='Finance']")]
    FINANCE_LINK = [(By.XPATH, "//a[contains(text(),'Finance')]")]
    LOCAL_CHECKBOX = [(By.XPATH, "//input[@value='local']")]
    PAID_BY_CASH_CHECKBOX = [(By.XPATH, "//input[@value='paid by cash']")]
    SEARCH_INPUT = [(By.XPATH, "//input[@type='search']")]
    SEARCH_BUTTON = [(By.XPATH, "//button[@id='searchCitation']")]

    @log_step("Open Finance and apply filters, search, and take screenshot")
    def open_finance_and_search(self, ticket_id: str):
        try:
            self.safe_click(self.FINANCE_SPAN)
        except Exception:
            self.safe_click(self.FINANCE_LINK)

        # Wait for Finance page UI
        self.wait_for_page_ready()

        # Apply checkboxes
        self.safe_click(self.LOCAL_CHECKBOX)
        self.safe_click(self.PAID_BY_CASH_CHECKBOX)

        # Search the ticket
        search_box = self.try_find_any(self.SEARCH_INPUT, timeout=10)
        search_box.clear()
        search_box.send_keys(ticket_id)

        self.safe_click(self.SEARCH_BUTTON)
        time.sleep(2)

        # Take screenshot for evidence
        screenshot_path = f"logs/screenshots/finance_{ticket_id}.png"
        self.driver.save_screenshot(screenshot_path)
        self.step_log.info(f"Finance screenshot saved: {screenshot_path}")


    @log_step('Verify payment appears in finance ledger (safe)')
    def verify_last_payment_safe(self, expected_amount: str, timeout: int = 20) -> bool:
        # Try to click a Finance tab if present (ignore failures)
        try:
            self.safe_click(self.FINANCE_TAB)
        except Exception:
            pass

        # Wait a bit for Finance container or any table
        found = False
        try:
            self.try_find_any(self.FINANCE_CONTAINER, timeout=timeout//2)
            found = True
        except Exception:
            pass

        # Try specific payments table first, then generic fallbacks
        loc_sets = [self.LAST_PAYMENT_ROW, self.ANY_PAYMENTS_ROW]
        for locs in loc_sets:
            try:
                row = self.try_find_any(locs, timeout=6)
                text = row.text
                if expected_amount in (text or ""):
                    return True
            except Exception:
                # Try inside iframes
                try:
                    row_if = self.try_find_in_any_iframe(locs, timeout_per_iframe=3)
                    text_if = row_if.text
                    if expected_amount in (text_if or ""):
                        return True
                except Exception:
                    continue

        return False

