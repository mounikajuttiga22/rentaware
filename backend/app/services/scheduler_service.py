from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.services.sms_service import send_sms

alerts = []
sent_alerts = set()

def update_alerts(new_alerts):
    global alerts
    alerts = new_alerts

def check_deadlines():
    print("Checking deadlines...")

    today = datetime.now()

    for alert in alerts:
        deadline = alert["deadline"]

        if deadline - today <= timedelta(days=3) and alert["type"] not in sent_alerts:

            send_sms(
                "+919177177822",
                "Reminder: Your rental agreement deadline is approaching."
            )

            sent_alerts.add(alert["type"])


scheduler = BackgroundScheduler()

scheduler.add_job(check_deadlines, "interval", minutes=1)

scheduler.start()