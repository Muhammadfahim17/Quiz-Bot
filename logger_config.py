import logging
from datetime import datetime
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = f'logs/bot_log_{datetime.now().strftime("%Y%m%d")}.log'

file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('quiz_bot')
logger.setLevel(logging.INFO)

logger.handlers.clear()

try:
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"Не удалось создать файл лога: {e}")


def get_logger():
    return logger