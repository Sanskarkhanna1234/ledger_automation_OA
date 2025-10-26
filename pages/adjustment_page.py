# pages/adjustment_page.py
import os
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage
from logger_utils import log_step
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class AdjustmentPage(BasePage):
    # ==== Search/Data page ====
    DATA_ICON            = [(By.XPATH, "//i[@class='fa fa-database']")]
    SEARCH_LINK          = [(By.XPATH, "//a[normalize-space()='Search']")]
    DATE_RANGE           = [(By.XPATH, "//input[@id='filter-date_range']")]
    DATE_CLEAR_BTN       = [(By.XPATH, "//button[normalize-space()='Clear']")]
    TABLE_SEARCH_INPUT   = [(By.XPATH, "//input[@type='search']")]
    PRIMARY_SEARCH_BTN   = [(By.XPATH, "//button[@id='btn-search-primary']")]
    ROW_OFFICER_CELL     = [(By.XPATH, "//div[@class='col-xs-12 res-table-officer-name text-important']")]

    # Row action: Payment
    PAYMENT_LINK         = [(By.XPATH, "//a[normalize-space()='Payment']")]

    # ==== Adjustment modal ====
    ADD_ADJUSTMENT_BTN   = [(By.XPATH, "//button[@id='add_adjustment']")]
    ADJUST_AMOUNT_INPUT  = [(By.XPATH, "//input[@id='adjustment_amount']")]
    ADJUST_REASON_INPUT  = [(By.XPATH, "//input[@id='adjustment_reason']")]
    ADJUST_CONFIRM_BTN   = [(By.XPATH, "//button[@id='confirm_adjustment']")]

    SWEET_ALERT          = [(By.CSS_SELECTOR, ".sweet-alert")]
    SWEET_OK             = [
        (By.XPATH, "//button[normalize-space()='OK']"),
        (By.XPATH, "(//button[normalize-space()='OK'])[1]"),
        (By.CSS_SELECTOR, ".sweet-alert .confirm"),
        (By.XPATH, "//button[@class='confirm']"),
    ]

    CLOSE_TICKET_BTN     = [(By.XPATH, "//button[@id='ticket_view_close_top']")]

    # ==== Finance page ====
    FINANCE_ICON         = [(By.XPATH, "//i[@class='fa fa-money']")]
    FINANCE_LINK         = [(By.XPATH, "//a[contains(text(),'Finance')]")]
    FINANCE_LOCAL_CHECK  = [(By.XPATH, "//input[@value='local']")]
    FINANCE_SEARCH_INPUT = [(By.XPATH, "//input[@type='search']")]
    FINANCE_SEARCH_BTN   = [(By.XPATH, "//button[@id='searchCitation']")]

    # Finance results: first row, status/label
    FINANCE_STATUS_CELL  = [
        (By.XPATH, "//tbody/tr[1]/td[11]/span[1]"),
        (By.XPATH, "(//span[@class='label label-primary'][normalize-space()='adjustment'])[1]"),
    ]

    def _ensure_dirs(self):
        os.makedirs("logs/adjustment_logs", exist_ok=True)
        os.makedirs("logs/adjustment_screenshots", exist_ok=True)

    @log_step("Open Data → Search page")
    def open_data_search(self):
        self.safe_click(self.DATA_ICON)
        self.safe_click(self.SEARCH_LINK)

    @log_step("Search ticket on Data → Search")
    def search_ticket(self, ticket_id: str):
        # Clear date range (ensures results show)
        try:
            self.safe_click(self.DATE_RANGE)
            self.safe_click(self.DATE_CLEAR_BTN)
        except Exception:
            # If either control is missing, continue gracefully
            self.debug_log.debug("Date controls not clickable; continuing.")

        # Type in table search
        box = self.try_find_any(self.TABLE_SEARCH_INPUT, timeout=10)
        box.clear()
        box.send_keys(ticket_id)

        self.safe_click(self.PRIMARY_SEARCH_BTN)
        self.try_find_any(self.ROW_OFFICER_CELL, timeout=10)

    @log_step("Open Payment panel from row actions")
    def open_payment_from_row(self):
        self.safe_click(self.PAYMENT_LINK)
    # @log_step("Add adjustment")
    # def add_adjustment(self, amount: str, reason: str):

    #     print("\n[DEBUG] STEP 1: Open 'Add Adjustment' modal…")
    #     self.safe_click(self.ADD_ADJUSTMENT_BTN)

    #     # Wait for modal inputs to be interactable
    #     try:
    #         self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_amount")))
    #         self.wait.until(EC.element_to_be_clickable((By.ID, "adjustment_amount")))
    #         self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_reason")))
    #         print("[DEBUG] Modal inputs ready.")
    #     except Exception as e:
    #         print(f"[WARN] Modal readiness wait failed: {e}")

    #     # Fill fields
    #     print(f"[DEBUG] STEP 2: Typing amount = {amount}")
    #     self.safe_type([(By.ID, "adjustment_amount")], amount)

    #     print(f"[DEBUG] STEP 3: Typing reason = {reason}")
    #     reason_el = self.try_find_any([(By.ID, "adjustment_reason")], timeout=10)
    #     try:
    #         reason_el.clear()
    #     except Exception:
    #         pass
    #     reason_el.send_keys(reason)

    #     # Fire input/change/blur to satisfy any validators
    #     try:
    #         print("[DEBUG] Fire input/change/blur on both fields.")
    #         amt = self.try_find_any([(By.ID, "adjustment_amount")], timeout=2)
    #         for el in (amt, reason_el):
    #             self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", el)
    #             self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", el)
    #             self.driver.execute_script("arguments[0].blur();", el)
    #         time.sleep(0.35)
    #     except Exception:
    #         print("[WARN] Could not fire validation events; continuing.")

    #     # Confirm button candidates
    #     confirm_sets = [
    #         [(By.ID, "confirm_adjustment")],
    #         [(By.XPATH, "(//button[@id='confirm_adjustment'])[1]")],
    #         [(By.XPATH, "//button[normalize-space()='Confirm']")],
    #         [(By.XPATH, "//button[contains(@class,'btn') and contains(normalize-space(.),'Confirm')]")],
    #         [(By.XPATH, "/html[1]/body[1]/div[14]/div[1]/div[1]/div[3]/button[1]")],
    #     ]

    #     def _focus(el):
    #         try:
    #             self.driver.execute_script("arguments[0].focus();", el)
    #             self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    #         except Exception:
    #             pass

    #     def _send_keys_to(el, seq):
    #         try:
    #             _focus(el)
    #             el.send_keys(seq)
    #             return True
    #         except Exception:
    #             return False

    #     def _dispatch_key(el, keycode):
    #         try:
    #             self.driver.execute_script("""
    #                 var el=arguments[0], code=arguments[1];
    #                 ['keydown','keyup'].forEach(t=>{
    #                 el.dispatchEvent(new KeyboardEvent(t,{bubbles:true,cancelable:true,key:code,code:code}));
    #                 });
    #             """, el, keycode)
    #             return True
    #         except Exception:
    #             return False

    #     # STEP 4: Keyboard-first approach (TAB → ENTER)
    #     print("[DEBUG] STEP 4: Try keyboard submit (TAB → ENTER).")
    #     try:
    #         actions = ActionChains(self.driver)
    #         # from reason → TAB to Confirm → ENTER
    #         _focus(reason_el)
    #         actions.send_keys(Keys.TAB).pause(0.15).send_keys(Keys.ENTER).perform()
    #         time.sleep(0.3)
    #     except Exception:
    #         print("[WARN] ActionChains TAB→ENTER failed; continuing.")

    #     # STEP 5: Try sending ENTER directly to visible Confirm
    #     print("[DEBUG] STEP 5: Try ENTER/SPACE directly on Confirm.")
    #     pressed = False
    #     for loc in confirm_sets:
    #         try:
    #             btn = self.try_find_any(loc, timeout=1)
    #             if _send_keys_to(btn, Keys.ENTER) or _send_keys_to(btn, Keys.SPACE):
    #                 pressed = True
    #                 print(f"[DEBUG] Sent ENTER/SPACE to Confirm via {loc}.")
    #                 break
    #         except Exception:
    #             continue

    #     # STEP 6: Programmatic focus + synthetic key events
    #     if not pressed:
    #         print("[DEBUG] STEP 6: Synthetic key events on Confirm.")
    #         for loc in confirm_sets:
    #             try:
    #                 btn = self.try_find_any(loc, timeout=1)
    #                 _focus(btn)
    #                 if _dispatch_key(btn, "Enter") or _dispatch_key(btn, "Space"):
    #                     pressed = True
    #                     print(f"[DEBUG] Dispatched KeyboardEvent to Confirm via {loc}.")
    #                     break
    #             except Exception:
    #                 continue

    #     # STEP 7: If still not fired, click attempts (normal → JS → dispatch MouseEvent)
    #     if not pressed:
    #         print("[DEBUG] STEP 7: Click attempts on Confirm.")
    #         for loc in confirm_sets:
    #             try:
    #                 btn = self.try_find_any(loc, timeout=1)
    #                 _focus(btn)
    #                 try:
    #                     btn.click()
    #                     pressed = True
    #                     print(f"[DEBUG] Native click worked on {loc}.")
    #                     break
    #                 except Exception:
    #                     pass
    #                 try:
    #                     self._js_click(btn)
    #                     pressed = True
    #                     print(f"[DEBUG] JS click worked on {loc}.")
    #                     break
    #                 except Exception:
    #                     pass
    #                 try:
    #                     self.driver.execute_script("""
    #                         const e=new MouseEvent('click',{bubbles:true,cancelable:true,view:window});
    #                         arguments[0].dispatchEvent(e);
    #                     """, btn)
    #                     pressed = True
    #                     print(f"[DEBUG] MouseEvent click worked on {loc}.")
    #                     break
    #                 except Exception:
    #                     continue
    #             except Exception:
    #                 continue

    #     # STEP 8: Try querySelector / jQuery as last resort
    #     if not pressed:
    #         print("[DEBUG] STEP 8: querySelector / jQuery fallbacks.")
    #         try:
    #             ok = self.driver.execute_script("""
    #                 var el=document.querySelector('#confirm_adjustment');
    #                 if(el){ el.focus(); el.click(); return true; }
    #                 return false;
    #             """)
    #             pressed = bool(ok)
    #         except Exception:
    #             pass
    #         if not pressed:
    #             try:
    #                 if self.driver.execute_script("return !!window.jQuery;"):
    #                     self.driver.execute_script("$('#confirm_adjustment').focus().click();")
    #                     pressed = True
    #             except Exception:
    #                 pass

    #     print(f"[DEBUG] Confirm fired? {pressed}. Waiting for result…")
    #     time.sleep(0.4)

    #     # STEP 9: Handle SweetAlert “Success” or silent save
    #     def _handle_success():
    #         try:
    #             if self.element_exists([(By.CSS_SELECTOR, ".sweet-alert")], timeout=5):
    #                 print("[DEBUG] SweetAlert detected → clicking OK.")
    #                 # common OK variants
    #                 ok_locs = [
    #                     (By.XPATH, "//button[normalize-space()='OK']"),
    #                     (By.CSS_SELECTOR, ".sweet-alert .confirm"),
    #                     (By.XPATH, "//button[@class='confirm']"),
    #                 ]
    #                 for by, sel in ok_locs:
    #                     try:
    #                         self.safe_click([(by, sel)])
    #                         break
    #                     except Exception:
    #                         continue
    #                 self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".sweet-alert")))
    #                 print("[DEBUG] SweetAlert closed.")
    #                 return True
    #         except Exception as e:
    #             print(f"[WARN] SweetAlert handling issue: {e}")
    #         return False

    #     if _handle_success():
    #         print("[DEBUG] Success confirmed via SweetAlert.")
    #         return

    #     # STEP 10: If modal still visible, try one more keyboard submit path
    #     try:
    #         if self.element_exists([(By.ID, "adjustment_reason")], timeout=1):
    #             print("[WARN] Modal still visible; one more TAB→ENTER attempt.")
    #             actions = ActionChains(self.driver)
    #             actions.send_keys(Keys.TAB).pause(0.15).send_keys(Keys.ENTER).perform()
    #             time.sleep(0.4)
    #             if _handle_success():
    #                 return
    #     except Exception:
    #         pass

    #     # Grace period for silent save
    #     print("[DEBUG] No SweetAlert detected; allowing silent save grace period.")
    #     time.sleep(1.2)
    #     print("[DEBUG] Adjustment flow finished.\n")
    @log_step("Add adjustment")
    def add_adjustment(self, amount: str, reason: str):
        print("\n[DEBUG] STEP 1: Open 'Add Adjustment' modal…")
        self.safe_click(self.ADD_ADJUSTMENT_BTN)

        # Wait until modal visible
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_amount")))
            self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_reason")))
            print("[DEBUG] Modal is ready for input.")
        except Exception as e:
            raise AssertionError(f"Modal didn't open properly: {e}")

        # Type in values
        print(f"[DEBUG] STEP 2: Entering amount = {amount}")
        self.safe_type([(By.ID, "adjustment_amount")], amount)

        print(f"[DEBUG] STEP 3: Entering reason = {reason}")
        reason_el = self.try_find_any([(By.ID, "adjustment_reason")], timeout=10)
        reason_el.clear()
        reason_el.send_keys(reason)

        # Trigger UI validation
        self.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
            arguments[0].blur();
        """, reason_el)

        # Locate Confirm and click
        print("[DEBUG] STEP 4: Clicking Confirm button…")
        try:
            confirm_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "confirm_adjustment"))
            )
            confirm_btn.click()
            print("[DEBUG] Confirm clicked.")
        except Exception as e:
            raise AssertionError(f"Confirm button not clickable: {e}")

        # Verify Success popup
        print("[DEBUG] STEP 5: Waiting for Success dialog…")
        try:
            success_popup = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(.,'Success') and contains(.,'Adjustment has been submitted')]"))
            )
            print("[DEBUG] Success dialog appeared — clicking OK.")
            ok_btn = self.try_find_any([
                (By.XPATH, "//button[normalize-space()='OK']"),
                (By.CSS_SELECTOR, ".sweet-alert .confirm"),
            ], timeout=5)
            ok_btn.click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".sweet-alert")))
            print("[DEBUG] Success popup closed — Adjustment completed successfully.")
        except Exception:
            raise AssertionError(" Adjustment failed: Success dialog not found after confirming.")

        print("[DEBUG] Adjustment process PASSED.\n")

    # @log_step("Add adjustment")
    # def add_adjustment(self, amount: str, reason: str):
    #     # local imports so this function is self-contained
    #     from selenium.webdriver.common.by import By
    #     from selenium.webdriver.common.keys import Keys
    #     from selenium.webdriver.common.action_chains import ActionChains
    #     from selenium.webdriver.support import expected_conditions as EC
    #     import time

    #     print("\n[DEBUG] STEP 1: Open 'Add Adjustment' modal…")
    #     self.safe_click(self.ADD_ADJUSTMENT_BTN)

    #     # Wait for the visible modal & inputs (animation/backdrop)
    #     try:
    #         self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal.show")))
    #         self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-backdrop.fade.in")))  # ok if not present
    #     except Exception:
    #         pass
    #     try:
    #         self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_amount")))
    #         self.wait.until(EC.element_to_be_clickable((By.ID, "adjustment_amount")))
    #         self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_reason")))
    #         print("[DEBUG] Modal inputs ready.")
    #     except Exception as e:
    #         print(f"[WARN] Modal readiness wait failed: {e}")

    #     # Fill fields
    #     print(f"[DEBUG] STEP 2: Typing amount = {amount}")
    #     self.safe_type([(By.ID, "adjustment_amount")], amount)

    #     print(f"[DEBUG] STEP 3: Typing reason = {reason}")
    #     reason_el = self.try_find_any([(By.ID, "adjustment_reason")], timeout=10)
    #     try:
    #         reason_el.clear()
    #     except Exception:
    #         pass
    #     reason_el.send_keys(reason)

    #     # Fire validators & blur so Confirm can enable
    #     try:
    #         print("[DEBUG] Fire input/change/blur on both fields.")
    #         amt = self.try_find_any([(By.ID, "adjustment_amount")], timeout=2)
    #         for el in (amt, reason_el):
    #             self.driver.execute_script("arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", el)
    #             self.driver.execute_script("arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", el)
    #             self.driver.execute_script("arguments[0].blur();", el)
    #         time.sleep(0.35)
    #     except Exception:
    #         print("[WARN] Could not fire validation events; continuing.")

    #     # --- SCOPED Confirm locators: only inside the visible modal ---
    #     CONFIRM_LOCATORS = [
    #         (By.CSS_SELECTOR, "div.modal.show #confirm_adjustment"),
    #         (By.CSS_SELECTOR, "div.modal.in #confirm_adjustment"),
    #         (By.XPATH, "(//div[contains(@class,'modal') and (contains(@class,'show') or contains(@class,'in'))]//button[@id='confirm_adjustment'])[1]"),
    #         (By.XPATH, "//div[contains(@class,'modal') and (contains(@class,'show') or contains(@class,'in'))]//button[normalize-space()='Confirm']"),
    #         (By.XPATH, "//div[contains(@class,'modal') and (contains(@class,'show') or contains(@class,'in'))]//button[contains(@class,'btn') and contains(normalize-space(.),'Confirm')]"),
    #     ]
    #     def _refind_confirm(timeout=4):
    #         for by, sel in CONFIRM_LOCATORS:
    #             try:
    #                 return self.wait.until(EC.element_to_be_clickable((by, sel)))
    #             except Exception:
    #                 continue
    #         # last-chance direct querySelector (scoped to .modal.show)
    #         try:
    #             el = self.driver.execute_script("return document.querySelector('div.modal.show #confirm_adjustment');")
    #             if el:
    #                 return el
    #         except Exception:
    #             pass
    #         raise Exception("Confirm button not found/clickable in visible modal.")

    #     def _focus(el):
    #         try:
    #             self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    #             self.driver.execute_script("arguments[0].focus();", el)
    #         except Exception:
    #             pass

    #     # Re-find after typing (modal can re-render)
    #     print("[DEBUG] STEP 4: Locate Confirm in visible modal…")
    #     try:
    #         confirm_btn = _refind_confirm()
    #         print("[DEBUG] Confirm located & clickable.")
    #     except Exception as e:
    #         print(f"[ERROR] Cannot locate Confirm: {e}")
    #         raise

    #     # Keyboard first: TAB→ENTER from reason (matches manual flow)
    #     print("[DEBUG] STEP 5: Try keyboard submit (TAB → ENTER).")
    #     try:
    #         _focus(reason_el)
    #         ActionChains(self.driver).send_keys(Keys.TAB).pause(0.15).send_keys(Keys.ENTER).perform()
    #         time.sleep(0.3)
    #     except Exception:
    #         print("[WARN] TAB→ENTER failed; will try direct click.")

    #     # If still visible, try native click on the *scoped* button
    #     try:
    #         if confirm_btn.is_displayed():
    #             print("[DEBUG] STEP 6: Native click on Confirm…")
    #             _focus(confirm_btn)
    #             confirm_btn.click()
    #             print("[DEBUG] Native click sent.")
    #     except Exception:
    #         print("[WARN] Native click failed; attempting JS click.")
    #         try:
    #             _focus(confirm_btn)
    #             self._js_click(confirm_btn)
    #             print("[DEBUG] JS click sent.")
    #         except Exception:
    #             print("[WARN] JS click failed; dispatch MouseEvent.")
    #             try:
    #                 self.driver.execute_script(
    #                     "arguments[0].dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));",
    #                     confirm_btn
    #                 )
    #                 print("[DEBUG] MouseEvent click sent.")
    #             except Exception as e:
    #                 print(f"[ERROR] All click attempts failed: {e}")
    #                 raise

    #     # Wait for success SweetAlert, otherwise allow silent save
    #     print("[DEBUG] STEP 7: Await success alert or silent save…")
    #     try:
    #         if self.element_exists([(By.CSS_SELECTOR, ".sweet-alert")], timeout=5):
    #             print("[DEBUG] SweetAlert detected → clicking OK.")
    #             # common OKs
    #             for loc in [
    #                 (By.XPATH, "//button[normalize-space()='OK']"),
    #                 (By.CSS_SELECTOR, ".sweet-alert .confirm"),
    #                 (By.XPATH, "//button[@class='confirm']"),
    #             ]:
    #                 try:
    #                     self.safe_click([loc])
    #                     break
    #                 except Exception:
    #                     continue
    #             self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".sweet-alert")))
    #             print("[DEBUG] SweetAlert closed.")
    #         else:
    #             print("[DEBUG] No SweetAlert — assuming silent success. Waiting briefly…")
    #             time.sleep(1.0)
    #     except Exception as e:
    #         print(f"[WARN] SweetAlert handling issue: {e}")

    #     # Final sanity: ensure modal closed (or at least confirm not clickable)
    #     try:
    #         self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.modal.show")))
    #     except Exception:
    #         print("[WARN] Modal still visible; backend may still complete. Proceeding.\n")
    #     else:
    #         print("[DEBUG] Adjustment complete; modal closed.\n")   


    # @log_step("Add adjustment")
    # def add_adjustment(self, amount: str, reason: str):
    #     from selenium.webdriver.common.by import By
    #     from selenium.webdriver.support import expected_conditions as EC
    #     import time

    #     print("\n[DEBUG] STEP 1: Open 'Add Adjustment' modal...")
    #     self.safe_click(self.ADD_ADJUSTMENT_BTN)

    #     # Wait for the modal fields to be usable
    #     try:
    #         self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_amount")))
    #         self.wait.until(EC.element_to_be_clickable((By.ID, "adjustment_amount")))
    #         self.wait.until(EC.visibility_of_element_located((By.ID, "adjustment_reason")))
    #         print("[DEBUG] Modal ready.")
    #     except Exception as e:
    #         print(f"[WARN] Modal readiness wait failed: {e}")

    #     # Fill fields
    #     print(f"[DEBUG] STEP 2: Typing amount = {amount}")
    #     self.safe_type(self.ADJUST_AMOUNT_INPUT, amount)

    #     print(f"[DEBUG] STEP 3: Typing reason = {reason}")
    #     reason_el = self.try_find_any(self.ADJUST_REASON_INPUT, timeout=10)
    #     try:
    #         reason_el.clear()
    #     except Exception:
    #         pass
    #     reason_el.send_keys(reason)

    #     # Nudge validations
    #     try:
    #         print("[DEBUG] Trigger blur/tab + JS validations...")
    #         self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", reason_el)
    #         self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", reason_el)
    #         self.driver.execute_script("arguments[0].blur();", reason_el)
    #         time.sleep(0.5)
    #     except Exception:
    #         print("[WARN] Validation nudge skipped.")

    #     # All confirm locators (your list + usual fallbacks)
    #     confirm_variants = [
    #         self.ADJUST_CONFIRM_BTN,  # class attribute: //button[@id='confirm_adjustment']
    #         [(By.XPATH, "(//button[@id='confirm_adjustment'])[1]")],
    #         [(By.XPATH, "//button[normalize-space()='Confirm']")],
    #         [(By.XPATH, "//button[contains(@class,'btn') and contains(.,'Confirm')]")],
    #         [(By.XPATH, "/html[1]/body[1]/div[14]/div[1]/div[1]/div[3]/button[1]")],
    #     ]

    #     # Helper: try one click style on a found element
    #     def _try_click_element(el) -> bool:
    #         try:
    #             self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    #         except Exception:
    #             pass
    #         # 1) normal click
    #         try:
    #             el.click()
    #             return True
    #         except Exception:
    #             pass
    #         # 2) selenium safe_click wrapper
    #         try:
    #             self._js_click(el)
    #             return True
    #         except Exception:
    #             pass
    #         # 3) dispatch MouseEvent
    #         try:
    #             self.driver.execute_script("""
    #                 const e = new MouseEvent('click', {bubbles:true, cancelable:true, view:window});
    #                 arguments[0].dispatchEvent(e);
    #             """, el)
    #             return True
    #         except Exception:
    #             return False

    #     # Helper: detect success SweetAlert and close it
    #     def _await_success_and_close() -> bool:
    #         try:
    #             if self.element_exists(self.SWEET_ALERT, timeout=5):
    #                 print("[DEBUG] SweetAlert detected.")
    #                 try:
    #                     self.safe_click(self.SWEET_OK)
    #                 except Exception:
    #                     # try common OK variants
    #                     try:
    #                         self.safe_click([(By.XPATH, "//button[normalize-space()='OK']")])
    #                     except Exception:
    #                         pass
    #                 self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".sweet-alert")))
    #                 print("[DEBUG] SweetAlert closed.")
    #                 return True
    #         except Exception as e:
    #             print(f"[WARN] SweetAlert handling issue: {e}")
    #         return False

    #     print("[DEBUG] STEP 4: Ensuring confirm is visible/enabled (best effort)...")
    #     try:
    #         btn = self.try_find_any([(By.ID, "confirm_adjustment")], timeout=5)
    #         self.wait.until(lambda d: btn.is_displayed() and btn.is_enabled())
    #         print("[DEBUG] Confirm appears enabled.")
    #     except Exception:
    #         print("[WARN] Could not confirm enabled state; proceeding with attempts.")

    #     print("[DEBUG] STEP 5: Clicking Confirm via multiple strategies...")
    #     clicked = False

    #     # A) try clicking each locator (normal/js/dispatch)
    #     for locset in confirm_variants:
    #         try:
    #             el = self.try_find_any(locset, timeout=2)
    #             if _try_click_element(el):
    #                 print(f"[DEBUG] Clicked Confirm via locator {locset}.")
    #                 clicked = True
    #                 break
    #         except Exception:
    #             continue

    #     # B) querySelector direct
    #     if not clicked:
    #         try:
    #             print("[DEBUG] Trying document.querySelector('#confirm_adjustment').click() ...")
    #             self.driver.execute_script("var el=document.querySelector('#confirm_adjustment'); if(el){el.click(); return true}else{return false}")
    #             clicked = True
    #         except Exception:
    #             pass

    #     # C) jQuery if present
    #     if not clicked:
    #         try:
    #             has_jq = self.driver.execute_script("return !!window.jQuery;")
    #             if has_jq:
    #                 print("[DEBUG] Trying jQuery('#confirm_adjustment').click() ...")
    #                 self.driver.execute_script("$('#confirm_adjustment').click();")
    #                 clicked = True
    #         except Exception:
    #             pass

    #     # D) keyboard Enter from reason field
    #     if not clicked:
    #         try:
    #             print("[DEBUG] Sending ENTER from reason field...")
    #             reason_el.send_keys("\ue007")  # Keys.ENTER
    #             clicked = True
    #         except Exception:
    #             pass

    #     print(f"[DEBUG] Clicked? {clicked}. Waiting for result...")
    #     time.sleep(0.5)

    #     # STEP 6: success handling (SweetAlert or silent)
    #     if _await_success_and_close():
    #         print("[DEBUG] Success confirmed via SweetAlert.")
    #         return

    #     # STEP 7: If no SweetAlert, check if modal closed; if still open, try one last hard click
    #     try:
    #         still_open = self.driver.find_elements(By.ID, "adjustment_reason")
    #         if still_open:
    #             print("[WARN] Modal appears still open; retry hard click once.")
    #             try:
    #                 el = self.try_find_any([(By.ID, "confirm_adjustment")], timeout=2)
    #                 self._js_click(el)
    #                 time.sleep(0.3)
    #                 if _await_success_and_close():
    #                     print("[DEBUG] Success after hard retry.")
    #                     return
    #             except Exception:
    #                 pass
    #     except Exception:
    #         pass

    #     # Final grace period for silent save
    #     print("[DEBUG] No SweetAlert detected; giving backend a second...")
    #     time.sleep(1.5)
    #     print("[DEBUG] Adjustment flow finished (silent mode).")




    @log_step("Close ticket view")
    def close_ticket_view(self):
        self.safe_click(self.CLOSE_TICKET_BTN)

    @log_step("Open Finance and filter + search")
    def open_finance_and_search(self, ticket_id: str):
        # Navigate via icon → link
        self.safe_click(self.FINANCE_ICON)
        self.safe_click(self.FINANCE_LINK)

        # Ensure Local filter checked
        try:
            cb = self.try_find_any(self.FINANCE_LOCAL_CHECK, timeout=10)
            if not cb.is_selected():
                cb.click()
        except Exception:
            self.debug_log.debug("Local checkbox not found/selected; continuing.")

        # Search by ticket
        box = self.try_find_any(self.FINANCE_SEARCH_INPUT, timeout=10)
        box.clear()
        box.send_keys(ticket_id)
        self.safe_click(self.FINANCE_SEARCH_BTN)

    @log_step("Capture Finance evidence & log latest action")
    def capture_finance_evidence(self, ticket_id: str) -> str:
        self._ensure_dirs()
        time.sleep(2)  # small wait so the grid has data

        # Grab status cell text if present
        latest_text = ""
        try:
            cell = self.try_find_any(self.FINANCE_STATUS_CELL, timeout=5)
            latest_text = (cell.text or "").strip()
        except Exception:
            latest_text = ""

        # Screenshot
        path = f"logs/adjustment_screenshots/finance_{ticket_id}.png"
        self.driver.save_screenshot(path)
        self.step_log.info(f"[Adjustment] Finance screenshot: {path}")

        # Log file
        log_path = "logs/adjustment_logs/latest_action.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"Ticket {ticket_id} — Latest Finance action: {latest_text}\n")
        self.step_log.info(f"[Adjustment] Logged latest action: {latest_text}")

        return latest_text
