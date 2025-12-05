try:
    from apscheduler.schedulers.background import BackgroundScheduler
    print("OK: APScheduler импортируется")
except Exception as e:
    print("ERROR:", e)

