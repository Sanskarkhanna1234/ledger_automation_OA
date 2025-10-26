# tests/test_finance_table_log.py
from pages.login_page import LoginPage
from pages.navbar_page import NavBar
from pages.finance_table_page import FinanceTablePage


def test_finance_table_log_first_row(driver, clients_data):
    """
    Open Finance, filter by the ticket, read the first row from the UI table,
    and append a formatted line to logs/tabel_log/finance_table.log.
    """
    client = clients_data[0]  # uses your existing fixture
    ticket = client["ticket_id"]

    # 1) Login
    LoginPage(driver, client["base_url"]).open_and_login(
        client["username"], client["password"]
    )

    # 2) Go to Finance
    NavBar(driver).go_to_finance_with_fallback(client["base_url"])

    # 3) Filter & read table
    table = FinanceTablePage(driver)
    table.apply_filter(ticket_id=ticket, ensure_local=True)
    line, path = table.log_first_row(log_name="finance_table.log")

    # 4) Simple sanity check
    assert ticket in line, f"Ticket '{ticket}' not found in logged line: {line}"
