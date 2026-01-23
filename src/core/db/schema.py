# -*- coding: utf-8 -*-
"""数据库表结构初始化"""

import sqlite3


def init_database_schema(conn: sqlite3.Connection):
    """初始化所有数据库表"""
    cursor = conn.cursor()
    
    # V2 表: 系统设置
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # V2 表: 词书管理
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        total_words INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # V2 表: 单词表 (合并了学习记录)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        word TEXT NOT NULL,
        phonetic TEXT,
        definition TEXT,
        
        -- 学习记录字段
        status INTEGER DEFAULT 0,
        first_learned DATE,
        last_review DATE,
        next_review DATE,
        review_count INTEGER DEFAULT 0,
        mastery_level INTEGER DEFAULT 0,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
    ''')

    # --- Auth: Users ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login_at TIMESTAMP
    )
    ''')
    
    # 添加 is_admin 列（如果不存在）
    cursor.execute('PRAGMA table_info(users)')
    user_cols = {row[1] for row in cursor.fetchall()}
    if 'is_admin' not in user_cols:
        cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')

    # --- User <-> Word learning records ---
    cursor.execute('PRAGMA table_info(learning_records)')
    learning_cols = {row[1] for row in cursor.fetchall()}

    if not learning_cols:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            status INTEGER DEFAULT 0,
            first_learned DATE,
            last_review DATE,
            next_review DATE,
            review_count INTEGER DEFAULT 0,
            mastery_level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, word_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
        )
        ''')
    elif 'user_id' not in learning_cols or 'word_id' not in learning_cols:
        cursor.execute('ALTER TABLE learning_records RENAME TO learning_records_old')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            status INTEGER DEFAULT 0,
            first_learned DATE,
            last_review DATE,
            next_review DATE,
            review_count INTEGER DEFAULT 0,
            mastery_level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, word_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('SELECT id FROM users ORDER BY id LIMIT 1')
        default_user_row = cursor.fetchone()
        default_user_id = default_user_row[0] if default_user_row else None

        if default_user_id is not None:
            cursor.execute('PRAGMA table_info(learning_records_old)')
            old_cols = {row[1] for row in cursor.fetchall()}
            if 'word' in old_cols:
                cursor.execute('''
                INSERT OR IGNORE INTO learning_records (
                    user_id, word_id, status,
                    first_learned, last_review, next_review,
                    review_count, mastery_level, created_at, updated_at
                )
                SELECT ?, w.id, 1,
                       lr.first_learned, lr.last_review, lr.next_review,
                       lr.review_count, lr.mastery_level, lr.created_at, lr.updated_at
                FROM learning_records_old lr
                JOIN words w ON w.word = lr.word
                ''', (default_user_id,))

        cursor.execute('DROP TABLE learning_records_old')

    # --- Deprecated table cleanup ---
    cursor.execute('DROP TABLE IF EXISTS user_word_bindings')

    # --- Email logs ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sent_date DATE UNIQUE,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'success',
        to_email TEXT,
        from_email TEXT,
        duration_ms INTEGER,
        user_id INTEGER,
        provider TEXT DEFAULT 'smtp',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # 兼容旧表：补充缺失字段
    cursor.execute('PRAGMA table_info(email_logs)')
    existing_cols = {row[1] for row in cursor.fetchall()}

    def add_col_if_missing(column_def: str, column_name: str):
        if column_name not in existing_cols:
            cursor.execute(f'ALTER TABLE email_logs ADD COLUMN {column_def}')

    add_col_if_missing("sent_at TIMESTAMP", "sent_at")
    add_col_if_missing("status TEXT DEFAULT 'success'", "status")
    add_col_if_missing("to_email TEXT", "to_email")
    add_col_if_missing("from_email TEXT", "from_email")
    add_col_if_missing("duration_ms INTEGER", "duration_ms")
    add_col_if_missing("user_id INTEGER", "user_id")
    add_col_if_missing("provider TEXT DEFAULT 'smtp'", "provider")
    add_col_if_missing("created_at TIMESTAMP", "created_at")

    # 兼容旧数据：补齐时间字段
    cursor.execute("UPDATE email_logs SET sent_at = COALESCE(sent_at, created_at, CURRENT_TIMESTAMP)")
    cursor.execute("UPDATE email_logs SET created_at = COALESCE(created_at, sent_at, CURRENT_TIMESTAMP)")
    
    # --- 登录历史记录表 ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        user_agent TEXT,
        login_method TEXT DEFAULT 'password',
        status TEXT DEFAULT 'success',
        failure_reason TEXT,
        session_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # 为登录历史表创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time DESC)')
    
    # --- 用户操作日志表 ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        resource_type TEXT,
        resource_id INTEGER,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # 为操作日志表创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON user_activity_logs(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON user_activity_logs(created_at DESC)')
    
    conn.commit()
