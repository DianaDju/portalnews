import os
import django
import logging
from django.conf import settings

# --- Настройка Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_news.settings')
django.setup()

# Временная настройка email для проверки
settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- Логгеры ---
logger = logging.getLogger('django')          # основной логгер
sec_logger = logging.getLogger('django.security')  # логгер безопасности

# --- Проверка консоли (DEBUG+) ---
logger.debug("TEST DEBUG message in console")
logger.info("TEST INFO message in console")
logger.warning("TEST WARNING message in console")
logger.error("TEST ERROR message in console")

# --- Проверка general.log (INFO+) ---
logger.info("TEST INFO message in general.log")
logger.warning("TEST WARNING message in general.log")

# --- Проверка errors.log (ERROR+) ---
try:
    1 / 0
except ZeroDivisionError:
    logger.error("TEST ERROR message in errors.log", exc_info=True)

# --- Проверка security.log ---
sec_logger.info("TEST SECURITY message in security.log")

# --- Проверка email (через консольный backend) ---
logger.error("TEST ERROR message for email")

# --- Вывод последних записей из файлов логов ---
log_dir = os.path.join(settings.BASE_DIR, 'logs')
files_to_check = ['general.log', 'errors.log', 'security.log']

for file in files_to_check:
    path = os.path.join(log_dir, file)
    print(f"\nСодержимое {file} (последние 5 записей):")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(line.strip())
    else:
        print("Файл не найден")