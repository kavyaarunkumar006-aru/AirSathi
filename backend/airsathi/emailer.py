"""Send a plain-text e-mail (used for password-reset codes).

Set these environment variables to enable it (e.g. a Gmail address with an App Password):
  SMTP_HOST=smtp.gmail.com  SMTP_PORT=587  SMTP_USER=you@gmail.com  SMTP_PASSWORD=<16-letter app password>
Without them, the e-mail is printed in the server log instead (fine for testing on your laptop).
"""
import os
import smtplib
from email.message import EmailMessage


def send(to, subject, body):
    host, user, pw = os.environ.get("SMTP_HOST"), os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD")
    if not (host and user and pw):
        print(f"[email not configured] to={to} subject={subject!r}\n{body}", flush=True)
        return False
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = f"AirSathi <{user}>", to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", "587")), timeout=20) as s:
            s.starttls()
            s.login(user, pw)
            s.send_message(msg)
        return True
    except Exception as e:  # never crash the API because e-mail failed
        print("[email failed]", type(e).__name__, flush=True)
        return False
