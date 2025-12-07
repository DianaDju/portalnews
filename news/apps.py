from django.apps import AppConfig
from django.conf import settings


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # Импорт сигналов только здесь, после полной загрузки приложений
        import news.signals




