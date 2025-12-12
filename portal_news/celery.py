import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portal_news.settings")

app = Celery("portal_news")

REDIS_PASSWORD = "XWnqRwXqjhJ4Ge82xL6tI7OmHzDXBQD8"
REDIS_HOST = "redis-16282.c61.us-east-1-3.ec2.cloud.redislabs.com"
REDIS_PORT = "16282"

app.conf.broker_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
app.conf.result_backend = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "weekly_digest": {
        "task": "news.tasks.send_weekly_news",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Пн 08:00
    },
}

