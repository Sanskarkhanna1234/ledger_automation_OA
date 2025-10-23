# ledger_automation_oa

Selenium + Pytest + POM with DEBUG terminal logs and dual files:
- logs/result.log (PASS/FAIL per step)
- logs/steps.log + logs/debug.log (detailed)

## Run
```bash
pip install -r requirements.txt
python -m pytest -q tests/test_full_payment.py::test_full_payment_flow -s
```
'''

{
  "clients": [
    {
      "client_name": "lyons",
      "base_url": "https://testing.quicketsolutions.info/lyons/",
      "username": "skhanna@quicketsolutions.com",
      "password": "Q!q1q1q1q1",
      "ticket_id": "P4003300",
      "fine_amount": "50",
      "payment_reason": "full payment lyons"
    }
  ]
}
'''