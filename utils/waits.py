from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

DEFAULT_WAIT = 20

def wait_for_presence(driver, by: By, locator: str, timeout: int = DEFAULT_WAIT):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def wait_for_clickable(driver, by: By, locator: str, timeout: int = DEFAULT_WAIT):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))
