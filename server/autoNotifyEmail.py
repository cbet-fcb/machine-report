import smtplib
from email.message import EmailMessage
import os
import json

def send_email_alert(subject: str, body: str, to_emails: list[str]):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = ', '.join(to_emails)
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            smtp.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    send_email_alert(
        subject="🚨 Machine Report Mismatch Detected",
        body=f"Report ID has a mismatch and was added to monitoring.\n\nData: 'Nothing'\n",
        to_emails=["monitoring-team@example.com"]
    )