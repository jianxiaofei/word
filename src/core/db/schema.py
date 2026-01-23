# -*- coding: utf-8 -*-
"""数据库表结构初始化"""

import sqlite3


def init_database_schema(conn: sqlite3.Connection):
    """初始化所有数据库表"""
    cursor = conn.cursor()
    
    # V1 表: 学习记录表 (保留用于迁移)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learning_records (
        id INTEGER PRIMARY KEY,
        word TEXT NOT NULL,
        first_learned DATE,
        last_review DATE,
        next_review DATE,
        review_count INTEGER DEFAULT 0,
        mastery_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login_at TIMESTAMP
    )
    ''')

    # --- User <-> Word bindings ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_word_bindings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        word_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, word_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
