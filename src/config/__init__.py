# -*- coding: utf-8 -*-
"""配置模块初始化"""

from .config import *

__all__ = [
    'SMTP_SERVER',
    'SMTP_PORT',
    'SMTP_USE_TLS',
    'SMTP_USERNAME',
    'SMTP_PASSWORD',
    'EMAIL_FROM',
    'EMAIL_TO',
    'WORD_FILE',
    'HISTORY_FILE',
    'WORDS_PER_EMAIL',
    'LOG_FILE',
]
