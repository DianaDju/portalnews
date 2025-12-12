import os
import io
import logging
from django.test import TestCase, override_settings
from django.core import mail
from django.conf import settings

class LoggingFullTest(TestCase):

    @override_settings(DEBUG=True)
    def test_console_logging(self):
        """Проверяем вывод в консоль"""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(pathname)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('django')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Генерируем логи
        logger.debug("DEBUG message")
        logger.info("INFO message")
        logger.warning("WARNING message")
        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("ERROR message", exc_info=True)

        output = stream.getvalue()
        logger.removeHandler(handler)

        self.assertIn("DEBUG message", output)
        self.assertIn("INFO message", output)
        self.assertIn("WARNING message", output)
        self.assertIn("ERROR message", output)
        self.assertIn("Traceback", output)

    @override_settings(DEBUG=False)
    def test_general_log(self):
        """Проверяем general.log (INFO+)"""
        log_file = os.path.join(settings.BASE_DIR, 'logs', 'general.log')
        logger = logging.getLogger('django')
        logger.info("INFO for general.log")
        logger.warning("WARNING for general.log")

        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.assertTrue(any("INFO for general.log" in l for l in lines))
        self.assertTrue(any("WARNING for general.log" in l for l in lines))

    @override_settings(DEBUG=False)
    def test_errors_log(self):
        """Проверяем errors.log (ERROR/CRITICAL)"""
        log_file = os.path.join(settings.BASE_DIR, 'logs', 'errors.log')
        logger = logging.getLogger('django.request')
        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("ERROR for errors.log", exc_info=True)

        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.assertTrue(any("ERROR for errors.log" in l for l in lines))
        self.assertTrue(any("Traceback" in l for l in lines))

    def test_security_log(self):
        """Проверяем security.log (django.security)"""
        log_file = os.path.join(settings.BASE_DIR, 'logs', 'security.log')
        sec_logger = logging.getLogger('django.security')
        sec_logger.info("SECURITY test message")

        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.assertTrue(any("SECURITY test message" in l for l in lines))

    @override_settings(DEBUG=False, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_on_error(self):
        """Проверяем отправку email при ERROR+"""
        mail.outbox = []
        logger = logging.getLogger('django.request')

        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("ERROR for email")

        self.assertTrue(len(mail.outbox) > 0)
        self.assertIn("ERROR for email", mail.outbox[0].subject + mail.outbox[0].body)
