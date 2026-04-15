import smtplib
from email.mime.text import MIMEText
import os
from backend.db import get_connection


def process_alert_queue():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, sneaker_id, old_price, new_price, drop_pct FROM alert_queue WHERE sent = FALSE")
    alerts = cur.fetchall()

    print("Alerts to send:", alerts)

    for alert in alerts:
        try:
            _send_email(alert)

            cur.execute("UPDATE alert_queue SET sent = TRUE WHERE id = %s", (alert[0],))
            conn.commit()

        except Exception as e:
            print("Email failed:", e)

    cur.close()
    conn.close()


def _send_email(alert):
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    msg = MIMEText(f"""
Sneaker {alert[1]} dropped!

Old: ₹{alert[2]}
New: ₹{alert[3]}
Drop: {alert[4]}%
""")

    msg["Subject"] = "🔥 Price Drop Alert"
    msg["From"] = SMTP_USER
    msg["To"] = SMTP_USER

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("✅ Email sent")