"""Email configuration smoke test for CampusSlot (does not send a message)."""
import os
from dotenv import load_dotenv
load_dotenv()
required = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "MAIL_FROM")
missing = [key for key in required if not os.getenv(key)]
if missing:
    print("[SKIP] Email is not configured. Missing: " + ", ".join(missing))
    print("Set these values in .env. This test does not send email.")
else:
    print("[OK] Email settings are present. Use the app's admin notification test to verify SMTP delivery.")
