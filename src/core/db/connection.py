# -*- coding: utf-8 -*-
"""数据库连接管理"""

import sqlite3
from pathlib import Path


def configure_sqlite_connection(conn: sqlite3.Connection) -> None:
    """配置 SQLite 连接优化参数"""
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA foreign_keys=ON')


def get_default_db_path() -> str:
    """获取默认数据库路径"""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    return str(base_dir / 'src' / 'data' / 'word.db')


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """获取数据库连接"""
    if db_path is None:
        db_path = get_default_db_path()
    
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    configure_sqlite_connection(conn)
    return conn
