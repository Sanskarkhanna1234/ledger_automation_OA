# conftest.py
import os
import json
import logging
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from logger_utils import setup_loggers


@pytest.fixture(scope="session", autouse=True)
def _configure_logging():
    """Console shows ONLY lines containing [DEBUG], [SUCCESS], or [FAIL]."""
    os.makedirs("logs", exist_ok=True)
    setup_loggers()

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))

    class OnlyTagged(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            msg = record.getMessage()
            return any(tag in msg for tag in ("[DEBUG]", "[SUCCESS]", "[FAIL]"))

    # show only our tagged lines on console
    console.addFilter(OnlyTagged())

    root = logging.getLogger()

    # remove existing stream handlers to avoid duplicates
    for h in list(root.handlers):
        if isinstance(h, logging.StreamHandler):
            root.removeHandler(h)

    root.setLevel(logging.INFO)
    root.addHandler(console)

    # silence noisy libs completely
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("WDM").setLevel(logging.CRITICAL)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    yield


@pytest.fixture(scope="session")
def clients_data():
    """Load clients from data/ledger_client_data.json"""
    data_path = os.path.join("data", "ledger_client_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["clients"]


@pytest.fixture(scope="function")
def driver():
    """Visible Chrome (no headless), auto-driver via webdriver-manager."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)  # keep window for debugging

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    drv.set_page_load_timeout(90)
    drv.delete_all_cookies()

    yield drv

    try:
        drv.quit()
    except Exception:
        pass
# --- ADD THIS FIXTURE (keeps other logic untouched) -------------------------

@pytest.fixture(scope="session")
def finance_client():
    """
    Return a single client dict for finance-table tests.
    Prefers data/adjustment_data.json (has base_url/username/password/ticket).
    Falls back to data/ledger_client_data.json if needed.
    """
    # Preferred file (used in your recent flows)
    pref_path = os.path.join("data", "adjustment_data.json")
    alt_path  = os.path.join("data", "ledger_client_data.json")

    path = pref_path if os.path.exists(pref_path) else alt_path
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Both files store under "clients"
    clients = data.get("clients", [])
    if not clients:
        raise RuntimeError(f"No clients found in {path}")

    return clients[0]  # single client dict with base_url/username/password/etc.
