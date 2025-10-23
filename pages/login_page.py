from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver, base_url, wait: int = 20):
        self.driver = driver
        self.base_url = base_url.rstrip('/') + '/default/index'
        super().__init__(driver, wait)
        self.wait = WebDriverWait(driver, wait)

    def open_and_login(self, username: str, password: str):
        self.driver.get(self.base_url)

        username_locators = [
            (By.ID, 'username'),
            (By.XPATH, "//input[@id='username']"),
            (By.NAME, "username"),
        ]
        password_locators = [
            (By.ID, 'password'),
            (By.XPATH, "//input[@id='password']"),
            (By.NAME, "password"),
        ]
        login_button_locators = [
            (By.ID, 'loginButton'),
            (By.XPATH, "//input[@id='loginButton']"),
        ]
        db_icon_locators = [
            (By.XPATH, "//i[@class='fa fa-database']"),
            (By.CSS_SELECTOR, "i.fa-database"),
        ]

        self.safe_type(username_locators, username)
        self.safe_type(password_locators, password, clear_first=False)
        self.safe_click(login_button_locators)

        # Wait & click DB icon to enter app
        self.wait.until(EC.element_to_be_clickable(db_icon_locators[0]))
        self.safe_click(db_icon_locators)

        # If a new tab is opened, switch to it (safe even if not)
        try:
            self.switch_to_last_window(timeout=10)
        except Exception:
            self.debug_log.debug("No new window detected after DB icon.")
