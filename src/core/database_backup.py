# -*- coding: utf-8 -*-
"""数据库管理模块 - SQLite"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple

from werkzeug.security import generate_password_hash, check_password_hash


def _configure_sqlite_connection(conn: sqlite3.Connection) -> None:
    # Better concurrency and fewer 'database is locked' errors.
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA foreign_keys=ON')

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认在 data 目录下
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = str(base_dir / 'src' / 'data' / 'word.db')
        else:
            self.db_path = db_path
            
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        _configure_sqlite_connection(conn)
        return conn

    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_conn()
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
            status INTEGER DEFAULT 0, -- 0:未学, 1:学习中
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
        
        conn.commit()
        conn.close()

    # --- Auth API ---
    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        username = (username or "").strip()
        if not username:
            return False, "用户名不能为空"
        if len(username) < 3:
            return False, "用户名至少 3 个字符"
        if not password or len(password) < 6:
            return False, "密码至少 6 个字符"

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash),
            )
            conn.commit()
            return True, "ok"
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, password_hash, is_active, created_at, last_login_at FROM users WHERE username = ? LIMIT 1',
            ((username or "").strip(),),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        cols = ['id', 'username', 'password_hash', 'is_active', 'created_at', 'last_login_at']
        return dict(zip(cols, row))

    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not user.get('is_active'):
            return None
        if not check_password_hash(user['password_hash'], password or ""):
            return None

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        conn.commit()
        conn.close()
        return user

    # --- User-Word learning_records API ---
    def bind_word_to_user(self, user_id: int, word_id: int) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO learning_records (user_id, word_id) VALUES (?, ?)',
                (int(user_id), int(word_id)),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def unbind_word_from_user(self, user_id: int, word_id: int) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'DELETE FROM learning_records WHERE user_id = ? AND word_id = ?',
                (int(user_id), int(word_id)),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_user_bound_word_ids(self, user_id: int, word_ids: Optional[List[int]] = None) -> Set[int]:
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            if word_ids:
                placeholders = ",".join(["?"] * len(word_ids))
                cursor.execute(
                    f'SELECT word_id FROM learning_records WHERE user_id = ? AND word_id IN ({placeholders})',
                    [int(user_id)] + [int(w) for w in word_ids],
                )
            else:
                cursor.execute('SELECT word_id FROM learning_records WHERE user_id = ?', (int(user_id),))

            rows = cursor.fetchall()
            return {int(r[0]) for r in rows}
        finally:
            conn.close()

    def list_user_bound_words(self, user_id: int, page: int = 1, page_size: int = 20, query: str = None) -> Tuple[List[Dict], int]:
        conn = self._get_conn()
        cursor = conn.cursor()
        offset = (page - 1) * page_size

        params: List[object] = [int(user_id)]
        where_extra = ""
        if query:
            where_extra = " AND (w.word LIKE ? OR w.definition LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        cursor.execute(
            f'''
            SELECT COUNT(*)
            FROM learning_records lr
            JOIN words w ON w.id = lr.word_id
            WHERE lr.user_id = ?{where_extra}
            ''',
            params,
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            f'''
            SELECT w.id, w.book_id, w.word, w.phonetic, w.definition,
                   lr.status, lr.first_learned, lr.last_review, lr.next_review,
                   lr.review_count, lr.mastery_level, lr.created_at, lr.updated_at
            FROM learning_records lr
            JOIN words w ON w.id = lr.word_id
            WHERE lr.user_id = ?{where_extra}
            ORDER BY lr.created_at DESC
            LIMIT ? OFFSET ?
            ''',
            params + [page_size, offset],
        )
        rows = cursor.fetchall()
        conn.close()
        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        words = [dict(zip(cols, row)) for row in rows]
        return words, total

    def get_user_bound_words(self, user_id: int) -> List[Dict]:
        """获取用户绑定的全部单词（用于统计等场景）。"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                SELECT w.id, w.book_id, w.word, w.phonetic, w.definition,
                       lr.status, lr.first_learned, lr.last_review, lr.next_review,
                       lr.review_count, lr.mastery_level, lr.created_at, lr.updated_at
                FROM learning_records lr
                JOIN words w ON w.id = lr.word_id
                WHERE lr.user_id = ?
                ORDER BY lr.created_at DESC
                ''',
                (int(user_id),),
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        return [dict(zip(cols, row)) for row in rows]

    def migrate_v1_to_v2(self, default_words: List[Dict]):
        """从V1迁移到V2结构"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 检查是否已经有书了
        cursor.execute('SELECT count(*) FROM books')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return # 已经迁移过了

        print("开始迁移数据库到 V2 版本...")

        # 1. 创建默认词书
        cursor.execute('INSERT INTO books (name, total_words, is_active) VALUES (?, ?, ?)', 
                      ('默认词书 (CET4)', len(default_words), 1))
        book_id = cursor.lastrowid

        # 2. 插入所有单词
        print(f"正在导入 {len(default_words)} 个单词...")
        word_map = {} # word -> id
        for w in default_words:
            cursor.execute('''
            INSERT INTO words (book_id, word, phonetic, definition) 
            VALUES (?, ?, ?, ?)
            ''', (book_id, w['word'], w.get('phonetic', ''), w.get('definition', '')))
            word_map[w['word']] = cursor.lastrowid

        # 3. 迁移学习记录
        print("正在迁移学习记录...")
        cursor.execute('SELECT * FROM learning_records')
        records = cursor.fetchall()
        
        # 获取列名
        col_names = [description[0] for description in cursor.description]
        
        migrated_count = 0
        for row in records:
            record = dict(zip(col_names, row))
            word_text = record['word']
            
            if word_text in word_map:
                word_id = word_map[word_text]
                cursor.execute('''
                UPDATE words SET 
                    status = 1,
                    first_learned = ?,
                    last_review = ?,
                    next_review = ?,
                    review_count = ?,
                    mastery_level = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (
                    record['first_learned'],
                    record['last_review'],
                    record['next_review'],
                    record['review_count'],
                    record['mastery_level'],
                    word_id
                ))
                migrated_count += 1

        print(f"迁移完成: 导入 {len(default_words)} 个单词, 恢复 {migrated_count} 条学习记录")
        conn.commit()
        conn.close()

    # --- Settings API ---
    def get_setting(self, key: str, default: str = None) -> str:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default

    def set_setting(self, key: str, value: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', (key, str(value)))
        conn.commit()
        conn.close()
        
    def get_all_settings(self) -> Dict[str, str]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}
    
    def get_user_config(self, user_id: int) -> Dict:
        """获取用户配置（使用 settings 表，key 格式为 user_{user_id}_*）"""
        prefix = f"user_{user_id}_"
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings WHERE key LIKE ?', (f"{prefix}%",))
        rows = cursor.fetchall()
        conn.close()
        
        config = {}
        for key, value in rows:
            # 去掉前缀
            config_key = key[len(prefix):]
            config[config_key] = value
        
        # 设置默认值
        return {
            'daily_words': int(config.get('daily_words', 5)),
            'email': config.get('email', ''),
            'enable_email': config.get('enable_email', 'false') == 'true'
        }
    
    def update_user_config(self, user_id: int, config: Dict):
        """更新用户配置"""
        prefix = f"user_{user_id}_"
        conn = self._get_conn()
        cursor = conn.cursor()
        
        for key, value in config.items():
            setting_key = f"{prefix}{key}"
            # 将布尔值转为字符串
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
                (setting_key, str(value))
            )
        
        conn.commit()
        conn.close()

    # --- Book API ---
    def get_all_books(self) -> List[Dict]:
        """获取所有词书列表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, total_words, is_active, created_at FROM books ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'id': row[0],
                'name': row[1],
                'total_words': row[2],
                'is_active': bool(row[3]),
                'created_at': row[4]
            }
            for row in rows
        ]
    
    def get_active_book(self) -> Optional[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE is_active = 1 LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'total_words': row[2]}
        return None
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """根据ID获取词书信息"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'total_words': row[2], 'is_active': bool(row[3])}
        return None
    
    def create_book(self, book_name: str) -> int:
        """创建新词书"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO books (name, total_words, is_active) VALUES (?, 0, 0)',
            (book_name,)
        )
        book_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return book_id
    
    def activate_book(self, book_id: int) -> bool:
        """激活指定词书（同时取消其他词书的激活状态）"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            # 取消所有词书的激活状态
            cursor.execute('UPDATE books SET is_active = 0')
            # 激活指定词书
            cursor.execute('UPDATE books SET is_active = 1 WHERE id = ?', (book_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def add_word(self, word: str, phonetic: str, definition: str, book_id: int) -> int:
        """添加单词到指定词书"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO words (book_id, word, phonetic, definition) 
               VALUES (?, ?, ?, ?)''',
            (book_id, word, phonetic, definition)
        )
        word_id = cursor.lastrowid
        
        # 更新词书的单词总数
        cursor.execute(
            'UPDATE books SET total_words = total_words + 1 WHERE id = ?',
            (book_id,)
        )
        
        conn.commit()
        conn.close()
        return word_id

    # --- Word API (V2) ---
    def get_word_by_id(self, word_id: int) -> Optional[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            # 简单的 row 转 dict，实际可能需要更严谨的映射
            cols = [d[0] for d in cursor.description]
            return dict(zip(cols, row))
        return None

    def update_word_progress(self, word_id: int, progress_data: Dict):
        """更新单词学习进度"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE words SET 
            status = 1,
            first_learned = COALESCE(first_learned, ?),
            last_review = ?,
            next_review = ?,
            review_count = ?,
            mastery_level = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            progress_data.get('first_learned'),
            progress_data.get('last_review'),
            progress_data.get('next_review'),
            progress_data.get('review_count'),
            progress_data.get('mastery_level'),
            word_id
        ))
        conn.commit()
        conn.close()

    def get_words_for_review(self, due_date: str) -> List[Dict]:
        """获取待复习单词 (V2)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM words 
        WHERE status = 1 
        AND next_review <= ?
        AND book_id = (SELECT id FROM books WHERE is_active = 1)
        ''', (due_date,))
        rows = cursor.fetchall()
        conn.close()
        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        results = [dict(zip(cols, row)) for row in rows]
        # 为了避免总是按相同顺序复习，这里做一次随机打乱
        import random
        random.shuffle(results)
        return results

    def get_new_words(self, count: int) -> List[Dict]:
        """获取新单词 (V2) - 随机选择"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM words 
        WHERE status = 0 
        AND book_id = (SELECT id FROM books WHERE is_active = 1)
        ORDER BY RANDOM()
        LIMIT ?
        ''', (count,))
        rows = cursor.fetchall()
        conn.close()
        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        results = [dict(zip(cols, row)) for row in rows]
        return results

    # --- Daily email log ---
    def has_sent_email_today(self) -> bool:
        """检查今天是否已经发送过学习邮件"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_date DATE UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        today = datetime.now().date().isoformat()
        cursor.execute('SELECT 1 FROM email_logs WHERE sent_date = ?', (today,))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        return row is not None

    def mark_email_sent_today(self):
        """标记今天邮件已发送"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_date DATE UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        today = datetime.now().date().isoformat()
        cursor.execute('INSERT OR IGNORE INTO email_logs (sent_date) VALUES (?)', (today,))
        conn.commit()
        conn.close()

    def get_all_records(self) -> List[Dict]:
        """获取所有学习记录 (兼容 V1 接口，但从 words 表读)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM words WHERE status = 1')
        rows = cursor.fetchall()
        conn.close()
        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        return [dict(zip(cols, row)) for row in rows]



    def update_review_status(self, word_index: int, last_review: str, next_review: str, review_count: int, mastery_level: int):
        """更新复习状态"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE learning_records 
        SET last_review = ?, next_review = ?, review_count = ?, mastery_level = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (last_review, next_review, review_count, mastery_level, word_index))
        
        conn.commit()
        conn.close()

    # 注意: get_all_records 已在上面定义，从 words 表读取 status=1 的记录
    # 旧的 learning_records 表已废弃
    
    def get_words(self, page: int = 1, page_size: int = 20, query: str = None, status: int = None, book_id: int = None) -> Tuple[List[Dict], int]:
        """获取单词列表（分页）"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        offset = (page - 1) * page_size
        params = []
        where_clauses = []
        
        # 如果指定了 book_id，使用指定的；否则使用激活的词书
        if book_id:
            where_clauses.append("book_id = ?")
            params.append(book_id)
        else:
            where_clauses.append("book_id = (SELECT id FROM books WHERE is_active = 1)")
        
        if query:
            where_clauses.append("(word LIKE ? OR definition LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
            
        if status is not None:
            where_clauses.append("status = ?")
            params.append(status)
            
        where_str = " AND ".join(where_clauses)
        
        # Get total count
        cursor.execute(f"SELECT count(*) FROM words WHERE {where_str}", params)
        total = cursor.fetchone()[0]
        
        # Get data
        cursor.execute(f'''
        SELECT * FROM words 
        WHERE {where_str}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        ''', params + [page_size, offset])
        
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        words = [dict(zip(cols, row)) for row in rows]
        
        return words, total

    def add_word(self, word_data: Dict) -> bool:
        """添加新单词"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            # Get active book
            cursor.execute("SELECT id FROM books WHERE is_active = 1")
            book_row = cursor.fetchone()
            if not book_row:
                return False
            book_id = book_row[0]
            
            cursor.execute('''
            INSERT INTO words (book_id, word, phonetic, definition, status)
            VALUES (?, ?, ?, ?, 0)
            ''', (book_id, word_data['word'], word_data.get('phonetic'), word_data['definition']))
            
            # Update book total words
            cursor.execute('UPDATE books SET total_words = total_words + 1 WHERE id = ?', (book_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding word: {e}")
            return False
        finally:
            conn.close()
