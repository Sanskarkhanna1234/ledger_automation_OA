# tests/test_adjustment.py
import json
import os
import pytest
from logger_utils import result_log as step_log
from pages.login_page import LoginPage
from pages.adjustment_page import AdjustmentPage


DATA_FILE = os.path.join("data", "adjustment_data.json")

@pytest.fixture(scope="session")
def adjustment_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["clients"][0]  # single client per your file

def test_adjustment_flow(driver, adjustment_data):
    """
    Flow:
    - Login
    - Data → Search → find ticket
    - Payment → Add Adjustment (amount & reason from JSON)
    - Confirm 'OK', close ticket view
    - Finance → Local → search same ticket
    - Wait 2s, screenshot, log latest action text
    """
    client = adjustment_data
    ticket = client["ticket_id"]

    step_log.info("Start Adjustment test for client: %s", client["client_name"])

    # 1) Login
    login = LoginPage(driver, client["base_url"])
    login.open_and_login(client["username"], client["password"])

    # 2) Data → Search → ticket
    adj = AdjustmentPage(driver)
    adj.open_data_search()
    adj.search_ticket(ticket)

    # 3) Payment → Add Adjustment
    adj.open_payment_from_row()
    adj.add_adjustment(client["amount"], client["reason"])

    # 4) Close ticket view
    adj.close_ticket_view()

    # 5) Finance → Local → search + evidence
    adj.open_finance_and_search(ticket)
    latest = adj.capture_finance_evidence(ticket)

    # 6) Basic sanity assertion (don’t make it brittle; just check we captured something)
    assert "adjustment" in (latest.lower() if latest else ""), \
        f"Expected 'adjustment' label in Finance first row; got: {latest!r}"
