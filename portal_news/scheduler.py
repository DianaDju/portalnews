from apscheduler.schedulers.background import BackgroundScheduler
from news.tasks import weekly_digest
from django.conf import settings

def start_scheduler(debug=False):
    scheduler = BackgroundScheduler()
    print(">>> BackgroundScheduler created")

    if debug:
        # Для разработки: каждые 2 минуты
        scheduler.add_job(
            weekly_digest,
            'interval',
            minutes=2,
            id='weekly_digest',
            replace_existing=True
        )
        print(">>> Job weekly_digest registered (every 2 minutes for debug)")
    else:
        # Раз в неделю, понедельник в 09:00
        scheduler.add_job(
            weekly_digest,
            'cron',
            day_of_week='mon',
            hour=9,
            minute=0,
            id='weekly_digest',
            replace_existing=True
        )
        print(">>> Job weekly_digest registered (weekly on Monday at 09:00)")

    scheduler.start()
    print(">>> Scheduler started!")




