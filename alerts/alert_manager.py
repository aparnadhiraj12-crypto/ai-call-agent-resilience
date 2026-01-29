# alerts/alert_manager.py

from logs.log_manager import log_event
from config import EMAIL_ENABLED, TELEGRAM_ENABLED, WEBHOOK_ENABLED


def send_email_alert(service, message):
    if EMAIL_ENABLED:
        print(f"📧 Email sent → {service}: {message}")


def send_telegram_alert(service, message):
    if TELEGRAM_ENABLED:
        print(f"📲 Telegram sent → {service}: {message}")


def send_webhook_alert(service, message):
    if WEBHOOK_ENABLED:
        print(f"🌐 Webhook sent → {service}: {message}")


def send_alert(service, message):
    """
    Unified alert dispatcher
    """
    log_event("CRITICAL", service, f"ALERT TRIGGERED: {message}")

    send_email_alert(service, message)
    send_telegram_alert(service, message)
    send_webhook_alert(service, message)
