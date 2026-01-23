# -*- coding: utf-8 -*-
"""数据库模块 - 重构后的结构"""

from .manager import DatabaseManager
from .connection import get_connection, configure_sqlite_connection, get_default_db_path
from .user_repository import UserRepository
from .word_repository import WordRepository
from .book_repository import BookRepository
from .settings_repository import SettingsRepository
from .binding_repository import BindingRepository

__all__ = [
    'DatabaseManager',
    'get_connection',
    'configure_sqlite_connection',
    'get_default_db_path',
    'UserRepository',
    'WordRepository',
    'BookRepository',
    'SettingsRepository',
    'BindingRepository',
]
