# pages/payment_page.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage
from logger_utils import log_step


class PaymentPage(BasePage):
    # --------- Primary controls ----------
    NEW_PAYMENT_BTN = [
        (By.ID, "new_payment"),
        (By.XPATH, "//button[@id='new_payment']"),
        (By.XPATH, "//button[contains(.,'New Payment') or contains(.,'Submit a Payment')]"),
    ]
    PAYMENT_TYPE = [
        (By.ID, "payment_type"),
        (By.XPATH, "//select[@id='payment_type']"),
    ]
    AMOUNT = [
        (By.ID, "paymentAmount"),
        (By.XPATH, "//input[@id='paymentAmount']"),
    ]
    PAYEE_EMAIL = [
        (By.ID, "payee_email"),
        (By.XPATH, "//input[@id='payee_email']"),
    ]
    SUBMIT = [
        (By.ID, "submitPayment"),
        (By.XPATH, "//button[@id='submitPayment']"),
        (By.XPATH, "//button[contains(.,'Submit Payment') or @name='submitPayment']"),
    ]

    # --------- Modals / feedback ----------
    MODAL_VISIBLE = [
        (By.XPATH, "//div[contains(@class,'modal') and contains(@class,'show')]"),
    ]
    CONFIRM_AFTER_SUBMIT = [
        (By.XPATH, "(//div[contains(@class,'modal') and contains(@class,'show')]//button[normalize-space()='Confirm'])[1]"),
        (By.XPATH, "(//button[normalize-space()='Confirm'])[1]"),
        (By.XPATH, "(//button[normalize-space()='Cancel']/following::button[1])[1]"),
    ]
    CLOSE_MODAL = [
        (By.ID, "close_modal"),
        (By.XPATH, "//button[@id='close_modal']"),
    ]

    # SweetAlert / SweetAlert2 / generic “Payment submitted” dialog
    PAYMENT_OK_ANY = [
        # SweetAlert (classic)
        (By.CSS_SELECTOR, ".sweet-alert .confirm"),
        (By.CSS_SELECTOR, ".confirm"),
        # SweetAlert2
        (By.CSS_SELECTOR, ".swal2-popup button.swal2-confirm"),
        (By.XPATH, "//div[contains(@class,'swal2-popup')]//button[normalize-space()='OK']"),
        # Generic text fallback
        (By.XPATH, "//button[normalize-space()='OK']"),
        (By.XPATH, "(//button[normalize-space()='OK'])[1]"),
    ]
    PAYMENT_DIALOG_ANY = [
        (By.CSS_SELECTOR, ".sweet-alert"),
        (By.CSS_SELECTOR, ".swal2-container"),
        (By.CSS_SELECTOR, ".swal2-popup"),
        (By.XPATH, "//div[contains(@class,'modal') and contains(., 'Payment submitted')]"),
    ]

    # Success markers if no modal path happens
    SUCCESS_MARKERS = [
        (By.XPATH, "//*[contains(@class,'alert') and contains(.,'Payment')]"),
        (By.XPATH, "//*[contains(@class,'toast') and contains(.,'Payment')]"),
        (By.XPATH, "//*[contains(@class,'alert-success')]"),
    ]

    # --------- Payments table (right panel) ----------
    # Be permissive: any table in the payment panel column
    PAYMENTS_TABLE = [
        (By.CSS_SELECTOR, "div#payment_panel table"),
        (By.XPATH, "//div[@id='payment_panel']//table"),
        (By.XPATH, "//table"),
    ]

    def _payment_row_by_email_amount(self, email: str, amount: str):
        # looks for a <tr> that contains both email and amount in descendant <td>
        return [
            (By.XPATH, f"//table//tr[.//td[contains(normalize-space(), '{email}')] and .//td[contains(normalize-space(), '{amount}')]]")
        ]

    # --------- Void controls on the Payment panel ----------
    VOID_BUTTONS = [
        (By.CSS_SELECTOR, "button.void_payment_button"),
        (By.XPATH, "//button[contains(@class,'void_payment_button')]"),
        (By.XPATH, "//button[normalize-space()='x']"),
        (By.XPATH, "//button[starts-with(@id,'ticket_id_')]"),
    ]
    VOID_REASON = [(By.ID, "void_payment_reason"), (By.XPATH, "//input[@id='void_payment_reason']")]
    CONFIRM_VOID = [(By.ID, "confirm_void_payment"), (By.XPATH, "//button[@id='confirm_void_payment'])")]

    # ===================== Actions =====================

    @log_step("Open New Payment modal")
    def open_new_payment(self):
        self.safe_click(self.NEW_PAYMENT_BTN)

    @log_step("Fill payment form")
    def fill_payment(self, payment_type_text: str, amount: str, email: str):
        # Select payment type
        sel_el = self.try_find_any(self.PAYMENT_TYPE, timeout=15)
        Select(sel_el).select_by_visible_text(payment_type_text)

        # Amount + email
        self.safe_type(self.AMOUNT, amount)
        self.safe_type(self.PAYEE_EMAIL, email)

    @log_step("Submit payment")
    def submit_payment(self):
        """
        Click Submit.
        If a confirm modal appears → click Confirm and wait for it to close.
        Otherwise, wait for a success marker or submit button to disable/disappear.
        """
        self.safe_click(self.SUBMIT)

        modal = None
        # Try to detect a Bootstrap-like confirm modal
        try:
            modal = self.try_find_any(self.MODAL_VISIBLE, timeout=4)
            self._scroll_into_view(modal)
        except Exception:
            modal = None  # likely SweetAlert or auto-submit

        if modal:
            # Modal path: click Confirm (with JS fallback) and wait to close
            try:
                btn = self.try_find_any(self.CONFIRM_AFTER_SUBMIT, timeout=6)
            except Exception:
                btn = self.try_find_in_any_iframe(self.CONFIRM_AFTER_SUBMIT, timeout_per_iframe=3)
            self._scroll_into_view(btn)
            try:
                btn.click()
            except Exception:
                self._js_click(btn)

            try:
                self.wait.until(EC.invisibility_of_element(modal))
            except Exception:
                pass
            # Sometimes there's an explicit close button afterward
            try:
                close = self.try_find_any(self.CLOSE_MODAL, timeout=3)
                self._scroll_into_view(close)
                try:
                    close.click()
                except Exception:
                    self._js_click(close)
            except Exception:
                pass
        else:
            # No modal path: wait for success signal or the submit button to change
            # Try a few different success indicators
            try:
                for loc in self.SUCCESS_MARKERS:
                    try:
                        self.try_find_any([loc], timeout=3)
                        break
                    except Exception:
                        continue
            except Exception:
                pass
            # Also accept that the submit button becomes disabled or hidden
            try:
                submit_el = self.try_find_any(self.SUBMIT, timeout=2)
                self.wait.until(lambda d: not submit_el.is_enabled() or not submit_el.is_displayed())
            except Exception:
                pass

    @log_step("Close 'Payment submitted' dialog")
    def handle_payment_submitted_ok(self, timeout: int = 12):
        """
        Wait for the 'Payment submitted' dialog and click its OK/Confirm button.
        Supports SweetAlert / SweetAlert2 / Bootstrap variants.
        """
        dlg = None
        end = time.time() + timeout
        while time.time() < end and dlg is None:
            # default content
            for loc in self.PAYMENT_DIALOG_ANY:
                try:
                    dlg = self.try_find_any([loc], timeout=2)
                    break
                except Exception:
                    pass
            # any iframe
            if dlg is None:
                for loc in self.PAYMENT_DIALOG_ANY:
                    try:
                        dlg = self.try_find_in_any_iframe([loc], timeout_per_iframe=2)
                        break
                    except Exception:
                        pass
            if dlg is None:
                time.sleep(0.2)

        if dlg is None:
            # Some environments auto-dismiss; don't fail the flow
            return

        self._scroll_into_view(dlg)

        ok_btn = None
        for loc in self.PAYMENT_OK_ANY:
            try:
                ok_btn = self.try_find_any([loc], timeout=2)
                break
            except Exception:
                pass
            try:
                ok_btn = self.try_find_in_any_iframe([loc], timeout_per_iframe=2)
                break
            except Exception:
                pass

        if ok_btn is None:
            return  # tolerate missing explicit OK

        self._scroll_into_view(ok_btn)
        try:
            ok_btn.click()
        except Exception:
            try:
                self._js_click(ok_btn)
            except Exception:
                pass

        # Wait for dialog to go away
        try:
            self.wait.until(lambda d: not dlg.is_displayed())
        except Exception:
            # try common containers
            try:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".swal2-container")))
            except Exception:
                try:
                    self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".sweet-alert")))
                except Exception:
                    pass


    @log_step("Void latest payment on Payment page")
    def void_latest_payment(self, reason: str = "VOID"):
        """
        Scrolls to payments table, clicks the visible Void (x) button for latest row,
        fills reason, confirms.
        """
        # ensure the panel is in view
        self.scroll_to_bottom()

        # Click any visible 'void' candidate (default content first)
        clicked = False
        for by, sel in self.VOID_BUTTONS:
            try:
                btn = self.try_find_any([(by, sel)], timeout=3)
                self._scroll_into_view(btn)
                try:
                    btn.click()
                except Exception:
                    self._js_click(btn)
                clicked = True
                break
            except Exception:
                continue

        # Try inside iframes if needed
        if not clicked:
            for by, sel in self.VOID_BUTTONS:
                try:
                    btn = self.try_find_in_any_iframe([(by, sel)], timeout_per_iframe=2)
                    self._scroll_into_view(btn)
                    try:
                        btn.click()
                    except Exception:
                        self._js_click(btn)
                    clicked = True
                    break
                except Exception:
                    continue

        if not clicked:
            raise AssertionError("Void button not found on Payment page")

        # now the reason input and confirm should be visible (often in a modal)
        # give the UI a tiny beat to render
        time.sleep(0.25)

        # type reason (allow JS fallback if not interactable)
        try:
            self.safe_type(self.VOID_REASON, reason)
        except Exception:
            # locate raw element and set value via JS as last resort
            try:
                el = self.try_find_any(self.VOID_REASON, timeout=2)
            except Exception:
                el = self.try_find_in_any_iframe(self.VOID_REASON, timeout_per_iframe=2)
            self._js_set_value(el, reason)

        # click confirm
        try:
            self.safe_click(self.CONFIRM_VOID)
        except Exception:
            try:
                el = self.try_find_any(self.CONFIRM_VOID, timeout=2)
            except Exception:
                el = self.try_find_in_any_iframe(self.CONFIRM_VOID, timeout_per_iframe=2)
            self._js_click(el)

        # small wait so the row updates/vanishes
        time.sleep(0.5)
