# pages/base_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from typing import List, Tuple, Optional
from logger_utils import get_step_logger, get_debug_file_logger

class BasePage:
    def __init__(self, driver, wait: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait)
        self.step_log = get_step_logger()
        self.debug_log = get_debug_file_logger()

    def try_find_any(self, locators: List[Tuple[By, str]], timeout: int = 20):
        last_exc: Optional[Exception] = None
        for by, value in locators:
            try:
                self.debug_log.debug("try_find_any: trying %s = %s", by, value)
                el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
                return el
            except Exception as e:
                last_exc = e
                self.debug_log.debug("try_find_any: failed %s = %s (%s)", by, value, e)
                continue
        raise TimeoutException(f"None of the locators matched: {locators}") from last_exc

    def _scroll_into_view(self, el):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", el)
        except Exception:
            pass

    def _js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    def safe_click(self, locators: List[Tuple[By, str]], timeout: int = 20):
        el = self.try_find_any(locators, timeout)
        self._scroll_into_view(el)
        self.step_log.info("Clicking element %s", locators[0])
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, ".//ancestor-or-self::*[1]")))
            el.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.step_log.info("Native click failed; trying ActionChains → JS click fallback")
            try:
                ActionChains(self.driver).move_to_element(el).pause(0.1).click(el).perform()
            except Exception:
                self._js_click(el)
    # Add this method in BasePage class
    def wait_for_page_ready(self, timeout: int = 15):
        """
        Wait until the page's document.readyState == 'complete'
        and (if exists) jQuery AJAX calls are finished.
        """
        import time
        from selenium.webdriver.support.ui import WebDriverWait

        self.debug_log.debug("Waiting for page ready state...")

        def page_ready(driver):
            try:
                ready_state = driver.execute_script("return document.readyState")
                jquery_active = driver.execute_script("return window.jQuery ? jQuery.active : 0")
                return ready_state == "complete" and jquery_active == 0
            except Exception:
                # Even if jQuery not found or other errors, continue checking document.readyState
                try:
                    return driver.execute_script("return document.readyState") == "complete"
                except Exception:
                    return False

        WebDriverWait(self.driver, timeout).until(page_ready)
        time.sleep(1)  # small buffer to ensure stability
        self.debug_log.debug("Page ready state confirmed.")


    def safe_type(self, locators: List[Tuple[By, str]], text: str, timeout: int = 20, clear_first=True):
        el = self.try_find_any(locators, timeout)
        self._scroll_into_view(el)
        if clear_first:
            el.clear()
        self.step_log.info("Typing '%s' into %s", text, locators[0])
        el.send_keys(text)

    # ---------- window / iframe helpers ----------
    def switch_to_last_window(self, timeout: int = 15):
        self.step_log.info("Checking for new window/tab...")
        WebDriverWait(self.driver, timeout).until(lambda d: len(d.window_handles) >= 1)
        handles = self.driver.window_handles
        self.debug_log.debug("window handles: %s", handles)
        self.driver.switch_to.window(handles[-1])
        self.step_log.info("Now on window: %s | title=%s | url=%s", handles[-1], self.driver.title, self.driver.current_url)

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    def try_find_in_any_iframe(self, locators: List[Tuple[By, str]], timeout_per_iframe: int = 6):
        self.switch_to_default_content()
        try:
            return self.try_find_any(locators, timeout=3)
        except Exception:
            pass

        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        self.step_log.info("Scanning %s iframe(s) for target element", len(iframes))
        for idx, frame in enumerate(iframes):
            self.switch_to_default_content()
            try:
                self.driver.switch_to.frame(frame)
                self.debug_log.debug("Switched to iframe #%s", idx)
                el = self.try_find_any(locators, timeout=timeout_per_iframe)
                self.step_log.info("Found element inside iframe #%s", idx)
                return el
            except Exception as e:
                self.debug_log.debug("Not in iframe #%s (%s)", idx, e)
                continue

        self.switch_to_default_content()
        raise TimeoutException(f"Element not found in default content or any iframe: {locators}")
    # ADD to BasePage (inside the class)
    def safe_refresh(self, wait_seconds: int = 1):
        self.step_log.info("[DEBUG] Refreshing page")
        self.driver.refresh()
        try:
            WebDriverWait(self.driver, wait_seconds).until(lambda d: True)
        except Exception:
            pass

    def element_exists(self, locators: List[Tuple[By, str]], timeout: int = 3) -> bool:
        try:
            self.try_find_any(locators, timeout=timeout)
            return True
        except Exception:
            return False

    def scroll_to_bottom(self):
        self.step_log.info("[DEBUG] Scrolling to bottom")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def smart_click_many(self, locator_sets: List[List[Tuple[By, str]]], timeout_each: int = 4) -> bool:
        """
        Try groups of locators until one clicks. Returns True on first success.
        """
        for locs in locator_sets:
            try:
                el = self.try_find_any(locs, timeout=timeout_each)
                self._scroll_into_view(el)
                try:
                    el.click()
                except Exception:
                    self._js_click(el)
                return True
            except Exception:
                continue
        return False



