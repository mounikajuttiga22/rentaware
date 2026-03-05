from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.services.sms_service import send_sms

alerts = []
sent_alerts = set()

scheduler = BackgroundScheduler()


def update_alerts(new_alerts):
    global alerts
    alerts = new_alerts


def check_deadlines():
    print("Checking deadlines...")

    today = datetime.now()

    for alert in alerts:

        # Convert string deadline to datetime
        deadline = datetime.fromisoformat(alert["deadline"])

        if deadline - today <= timedelta(days=3) and alert["type"] not in sent_alerts:

            print("SMS condition met!")

            send_sms(
                "+919032921673",
                f"Reminder: Your rental agreement {alert['type']} deadline is approaching."
            )

            sent_alerts.add(alert["type"])


def start_scheduler():
    scheduler.add_job(check_deadlines, "interval", seconds=10)
    scheduler.start()