from django.apps import AppConfig
from django.conf import settings

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        print(">>> AppConfig ready() executed")

        # Подключаем сигналы
        from . import signals

        # Запуск APScheduler
        from portal_news.scheduler import start_scheduler

        if settings.DEBUG:
            print(">>> Starting APScheduler in DEBUG mode (every 2 minutes for testing)...")
            start_scheduler(debug=True)
        else:
            print(">>> Starting APScheduler in PRODUCTION mode (once per week)...")
            start_scheduler(debug=False)

