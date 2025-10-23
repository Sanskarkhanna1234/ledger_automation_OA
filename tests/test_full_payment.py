import os, traceback
from conftest import driver
from pages.finance_page import FinancePage
from pages.login_page import LoginPage
from pages.navbar_page import NavBar
from pages.search_page import SearchPage
from pages.payment_page import PaymentPage
from logger_utils import get_step_logger, get_result_logger

step_log = get_step_logger()
res_log = get_result_logger()

def test_full_payment_flow(driver, clients_data):
    client = clients_data[0]  # e.g., 'lyons'
    ticket = client['ticket_id']

    step_log.info('Start test for client: %s', client['client_name'])

    try:
        # 1) Login & enter app
        login = LoginPage(driver, client['base_url'])
        login.open_and_login(client['username'], client['password'])

        # 2) Open Data → Search
        nav = NavBar(driver)
        nav.open_data_search()

        # 3) Apply filters & search
        search = SearchPage(driver)
        search.apply_filters_and_search(serial_number="", press_enter_if_no_button=False)

        # 4) Open row actions for the ticket, then click Payment
        search.open_ticket_actions(ticket)
        search.choose_payment()

        # 5) New payment: Cash, ₹50, payee email = your email
        pay = PaymentPage(driver)
        pay.open_new_payment()
        pay.fill_payment("Cash", client['fine_amount'], client['username'])
        pay.submit_payment()

        # Close the "Payment submitted" dialog before touching anything else
        pay.handle_payment_submitted_ok()

        # Try Finance (do not fail the test if Finance UI differs / is slow / in iframe)
        # === NEW: Go to Finance, search ticket, take screenshot ===
        reached_finance = nav.go_to_finance_with_fallback(client['base_url'])
        if reached_finance:
            fin = FinancePage(driver)
            try:
                fin.open_finance_and_search(ticket)
            except Exception as e:
                step_log.warning("Finance flow failed: %s", e)
        else:
            step_log.warning("Finance page not reachable or 404, skipping Finance check.")

        # # === RETURN BACK to Data → Search ===
        # try:
        #     nav.go_to_data_search_from_finance()
        # except Exception as e:
        #     step_log.warning("Failed returning to Search: %s", e)

        # # === NOW void the latest payment ===
        # search.open_ticket_actions(ticket)
        # search.choose_payment()
        # pay.void_latest_payment("Void by officer")
        # === RETURN BACK to Data → Search ===
        try:
            nav.go_to_data_search_from_finance()
        except Exception as e:
            step_log.warning("Failed returning to Search: %s", e)

        # === RE-RUN SEARCH TO REPOPULATE RESULTS ===
        try:
            step_log.info("Re-running search after coming back from Finance page...")
            search.apply_filters_and_search(serial_number="", press_enter_if_no_button=False)
        except Exception as e:
            step_log.warning("Re-search failed; refreshing search results instead: %s", e)
            search.refresh_results()

        # === ENSURE THE TICKET ROW IS VISIBLE ===
        try:
            search.try_find_any(search._row_by_ticket(ticket), timeout=15)
        except Exception as e:
            step_log.warning("Ticket row not found after refresh: %s", e)
            raise

        # === NOW VOID THE LATEST PAYMENT ===
        search.open_ticket_actions(ticket)
        pay.void_latest_payment("Void by officer")



        res_log.info('TEST: Full payment flow — PASS')
    except Exception:
        name = 'test_full_payment_flow_failure.png'
        path = os.path.join('logs', name)
        driver.save_screenshot(path)
        res_log.error('TEST: Full payment flow — FAIL (screenshot: %s)', path)
        step_log.exception('Exception in test_full_payment_flow:\n%s', traceback.format_exc())
        raise

# # tests/test_full_payment.py
# import os, traceback
# import time
# from conftest import driver
# from pages.login_page import LoginPage
# from pages.navbar_page import NavBar
# from pages.search_page import SearchPage
# from pages.payment_page import PaymentPage
# from logger_utils import get_step_logger, get_result_logger

# step_log = get_step_logger()
# res_log = get_result_logger()

# def test_full_payment_flow(driver, clients_data):
#     client = clients_data[0]  # e.g., 'lyons'
#     ticket = client['ticket_id']

#     step_log.info('Start test for client: %s', client['client_name'])

#     try:
#         # 1) Login & enter app
#         login = LoginPage(driver, client['base_url'])
#         login.open_and_login(client['username'], client['password'])

#         # 2) Open Data → Search
#         nav = NavBar(driver)
#         nav.open_data_search()

#         # 3) Apply filters & search
#         search = SearchPage(driver)
#         search.apply_filters_and_search(serial_number="", press_enter_if_no_button=False)

#         # 4) Open row actions for the ticket, then click Payment
#         search.open_ticket_actions(ticket)
#         search.choose_payment()

#         # 5) New payment: Cash, ₹50, payee email = your email
#         pay = PaymentPage(driver)
#         pay.open_new_payment()
#         pay.fill_payment("Cash", client['fine_amount'], client['username'])
#         pay.submit_payment()
#         # time.sleep(2)
#         # Close the "Payment submitted" dialog before touching the table
#         pay.handle_payment_submitted_ok()

#         # Now void the latest payment on the Payment panel
#         pay.void_latest_payment("Void by officer")


#         # If Finance validation is out of testing scope, skip its check
#         step_log.info("Finance check skipped (out of scope)")

#         res_log.info('TEST: Full payment flow — PASS')

#     except Exception:
#         name = 'test_full_payment_flow_failure.png'
#         path = os.path.join('logs', name)
#         driver.save_screenshot(path)
#         res_log.error('TEST: Full payment flow — FAIL (screenshot: %s)', path)
#         step_log.exception('Exception in test_full_payment_flow:\n%s', traceback.format_exc())
#         raise

