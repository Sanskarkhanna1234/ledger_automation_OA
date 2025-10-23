# pages/navbar_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from logger_utils import log_step

class NavBar(BasePage):
    NAV_TOGGLE = [(By.XPATH, "//a[@id='navbar_toggle_anchor']/i")]
    DATA_MENU_ANCHOR = [(By.XPATH, "//li[@id='data_nav']/a")]
    DATA_MENU_SPAN   = [(By.XPATH, "//li[@id='data_nav']/a/span")]  # fallback
    SEARCH_LINK = [(By.LINK_TEXT, "Search"), (By.PARTIAL_LINK_TEXT, "Search")]

    def open_data_search(self):
        self.switch_to_default_content()

        # If collapsed navbar exists, open it (ignore if already open)
        try:
            self.safe_click(self.NAV_TOGGLE)
        except Exception:
            self.debug_log.debug("Navbar toggle not visible or not needed.")

        # Click the anchor (more reliable than span). If that fails, click span.
        try:
            self.safe_click(self.DATA_MENU_ANCHOR)
        except Exception:
            self.safe_click(self.DATA_MENU_SPAN)

        # Now click "Search"
        self.safe_click(self.SEARCH_LINK)

        # Wait for data page to load or key controls to appear
        try:
            self.wait.until(EC.url_contains("/data"))
        except Exception:
            # Stay tolerant; page might be routed inside same URL, so just continue
            pass
    # ADD these locators (class attributes)
    FINANCE_SPAN_INDEX = [(By.XPATH, "(//span[normalize-space()='Finance'])[1]")]
    FINANCE_SPAN_REL   = [(By.XPATH, "//span[normalize-space()='Finance']")]
    FINANCE_LINK_REL   = [(By.XPATH, "//a[contains(text(),'Finance')]")]

    NOT_FOUND_404 = [
        (By.XPATH, "//*[contains(text(),'404') and contains(text(),'Not Found')]"),
        (By.XPATH, "//*[contains(text(),'404 Not Found')]"),
    ]
    # ADD (class attributes)
    FINANCE_ANCHOR_ANY = [
        (By.XPATH, "//li[.//span[normalize-space()='Finance']]//a"),
        (By.XPATH, "//a[contains(@href,'finance') and (normalize-space()='Finance' or .//span[normalize-space()='Finance'])]"),
        (By.CSS_SELECTOR, "a[href*='finance']"),
    ]

    @log_step("Go back to Data → Search from Finance")
    def go_to_data_search_from_finance(self):
        try:
            self.safe_click([(By.XPATH, "//span[normalize-space()='Data']")])
        except Exception:
            pass
        self.safe_click([(By.XPATH, "//a[normalize-space()='Search']")])
        self.wait.until(EC.url_contains("/data"))

    # ADD this method
# ADD (new robust method)
    @log_step("Open Finance (robust, with URL fallback)")
    def go_to_finance_with_fallback(self, base_url: str) -> bool:
        self.switch_to_default_content()

        # Try to expand navbar
        try:
            self.safe_click(self.NAV_TOGGLE)
        except Exception:
            self.debug_log.debug("Toggle not needed/visible.")

        # 1) menu clicks in default content
        clicked = self.smart_click_many(
            [self.FINANCE_SPAN_INDEX, self.FINANCE_SPAN_REL, self.FINANCE_LINK_REL, self.FINANCE_ANCHOR_ANY],
            timeout_each=5
        )

        # 2) if not, try inside iframes
        if not clicked:
            try:
                el = self.try_find_in_any_iframe(self.FINANCE_SPAN_INDEX, timeout_per_iframe=3)
                self._js_click(el); clicked = True
            except Exception:
                try:
                    el = self.try_find_in_any_iframe(self.FINANCE_ANCHOR_ANY, timeout_per_iframe=3)
                    self._js_click(el); clicked = True
                except Exception:
                    clicked = False

        # 3) wait for route or 404 marker
        try:
            self.wait.until(EC.any_of(
                EC.url_contains("/finance"),
                EC.presence_of_element_located(self.NOT_FOUND_404[0]),
                EC.presence_of_element_located(self.NOT_FOUND_404[1]),
            ))
        except Exception:
            pass

        if self.element_exists(self.NOT_FOUND_404, timeout=1):
            clicked = False

        # 4) direct URL candidates
        if not clicked or "/finance" not in (self.driver.current_url or "").lower():
            for path in ["/finance/index", "/finance/home", "/finance", "/finance/transactions"]:
                target = base_url.rstrip("/") + path
                self.step_log.info("[DEBUG] Direct URL fallback: %s", target)
                self.driver.get(target)

                # stop on not authorized (if you added detector on BasePage)
                if hasattr(self, "is_not_authorized") and self.is_not_authorized():
                    return False

                if self.element_exists(self.NOT_FOUND_404, timeout=1):
                    continue

                if "/finance" in (self.driver.current_url or "").lower():
                    return True
            return False

        if hasattr(self, "is_not_authorized") and self.is_not_authorized():
            return False

        return True
    

    

