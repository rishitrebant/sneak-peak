import smtplib
from email.mime.text import MIMEText
import os

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


def _send_email(item: dict):
    msg = MIMEText(f"""
{item['name']} dropped from ₹{item['old_price']} → ₹{item['new_price']}
({item['drop_pct']}% off)

Buy now: {item['url']}
""")

    msg["Subject"] = f"Price Drop Alert 🚨"
    msg["From"] = SMTP_USER
    msg["To"] = item["email"]

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)