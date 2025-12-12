# news/tests/test_logging.py
import logging
import os
from django.test import TestCase, override_settings
from django.conf import settings
from django.core import mail

LOG_DIR = settings.BASE_DIR / 'logs'

@override_settings(DEBUG=True)
class LoggingDebugModeTest(TestCase):
    """Тесты логирования при DEBUG=True (консоль)"""

    def test_debug_message_in_console(self):
        logger = logging.getLogger('django')
        with self.assertLogs(logger, level='DEBUG') as cm:
            logger.debug("DEBUG test message")
        # Проверяем, что DEBUG-сообщение поймано
        self.assertTrue(any("DEBUG test message" in m for m in cm.output))

    def test_warning_message_in_console(self):
        logger = logging.getLogger('django')
        with self.assertLogs(logger, level='WARNING') as cm:
            logger.warning("WARNING test message")
        self.assertTrue(any("WARNING test message" in m for m in cm.output))

    def test_error_message_in_console(self):
        logger = logging.getLogger('django')
        with self.assertLogs(logger, level='ERROR') as cm:
            logger.error("ERROR test message")
        self.assertTrue(any("ERROR test message" in m for m in cm.output))


@override_settings(DEBUG=False)
class LoggingProductionModeTest(TestCase):
    """Тесты логирования при DEBUG=False (файлы и email)"""

    def test_info_written_to_general_log(self):
        logger = logging.getLogger('django')
        test_msg = "INFO test message for general.log"
        logger.info(test_msg)

        general_log_path = LOG_DIR / 'general.log'
        with open(general_log_path, 'r') as f:
            log_content = f.read()
        self.assertIn(test_msg, log_content)

    def test_error_written_to_errors_log(self):
        logger = logging.getLogger('django.request')
        test_msg = "ERROR test message for errors.log"
        logger.error(test_msg, exc_info=True)

        errors_log_path = LOG_DIR / 'errors.log'
        with open(errors_log_path, 'r') as f:
            log_content = f.read()
        self.assertIn(test_msg, log_content)

    def test_security_info_written_to_security_log(self):
        logger = logging.getLogger('django.security')
        test_msg = "SECURITY test message"
        logger.info(test_msg)

        security_log_path = LOG_DIR / 'security.log'
        with open(security_log_path, 'r') as f:
            log_content = f.read()
        self.assertIn(test_msg, log_content)


LOG_DIR = settings.BASE_DIR / 'logs'


class LoggingEmailTest(TestCase):

    @override_settings(DEBUG=False)  # Эмулируем production
    def test_error_triggers_email(self):
        # Получаем логгер django.request, чтобы сгенерировать ERROR
        logger = logging.getLogger('django.request')

        # Логируем сообщение ERROR
        logger.error('ERROR test message for email')

        # Проверяем, что письмо добавлено в outbox
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        # Проверяем, что тема письма содержит текст уровня и сообщение
        self.assertIn('ERROR', email.subject)
        self.assertIn('ERROR test message for email', email.subject)

        # Проверяем, что тело письма содержит сообщение
        self.assertIn('ERROR test message for email', email.body)







