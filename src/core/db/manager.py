# -*- coding: utf-8 -*-
"""数据库管理器 - 统一接口（向后兼容）"""

import sqlite3
from typing import List, Dict, Optional, Tuple, Set

from .connection import get_connection, get_default_db_path
from .schema import init_database_schema
from .user_repository import UserRepository
from .settings_repository import SettingsRepository
from .book_repository import BookRepository
from .word_repository import WordRepository


class DatabaseManager:
    """数据库管理器 - 统一入口，保持向后兼容"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = get_default_db_path()
        self.db_path = db_path
        
        # 初始化数据库
        conn = get_connection(db_path)
        init_database_schema(conn)
        conn.close()
        
        # 创建各个 Repository
        get_conn_func = lambda: get_connection(db_path)
        self.users = UserRepository(get_conn_func)
        self.settings = SettingsRepository(get_conn_func)
        self.books = BookRepository(get_conn_func)
        self.words = WordRepository(get_conn_func)
        
        # 兼容旧接口
        self._get_conn = get_conn_func
    
    # === 用户相关方法（委托给 UserRepository） ===
    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        return self.users.create_user(username, password)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        return self.users.get_user_by_username(username)
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        return self.users.verify_user(username, password)
    
    # === 用户-单词学习记录方法（learning_records） ===
    def bind_word_to_user(self, user_id: int, word_id: int) -> bool:
        return self.words.bind_word_to_user(user_id, word_id)
    
    def unbind_word_from_user(self, user_id: int, word_id: int) -> bool:
        return self.words.unbind_word_from_user(user_id, word_id)
    
    def get_user_bound_word_ids(self, user_id: int, word_ids: Optional[List[int]] = None) -> Set[int]:
        return self.words.get_user_bound_word_ids(user_id, word_ids)
    
    def list_user_bound_words(self, user_id: int, page: int = 1, page_size: int = 20, query: str = None) -> Tuple[List[Dict], int]:
        return self.words.list_user_bound_words(user_id, page, page_size, query)
    
    def get_user_bound_words(self, user_id: int) -> List[Dict]:
        return self.words.get_user_bound_words(user_id)
    
    # === 设置方法（委托给 SettingsRepository） ===
    def get_setting(self, key: str, default: str = None) -> str:
        return self.settings.get_setting(key, default)
    
    def set_setting(self, key: str, value: str):
        return self.settings.set_setting(key, value)
    
    def get_all_settings(self) -> Dict[str, str]:
        return self.settings.get_all_settings()
    
    def get_user_config(self, user_id: int) -> Dict:
        return self.settings.get_user_config(user_id)
    
    def update_user_config(self, user_id: int, config: Dict):
        return self.settings.update_user_config(user_id, config)
    
    # === 词书方法（委托给 BookRepository） ===
    def get_all_books(self) -> List[Dict]:
        return self.books.get_all_books()
    
    def get_active_book(self) -> Optional[Dict]:
        return self.books.get_active_book()
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        return self.books.get_book_by_id(book_id)
    
    def get_book(self, book_id: int) -> Optional[Dict]:
        """get_book_by_id 的别名，向后兼容"""
        return self.books.get_book_by_id(book_id)
    
    def create_book(self, book_name: str) -> int:
        return self.books.create_book(book_name)
    
    def activate_book(self, book_id: int) -> bool:
        return self.books.activate_book(book_id)
    
    # === 单词方法（委托给 WordRepository） ===
    def get_word_by_id(self, word_id: int) -> Optional[Dict]:
        return self.words.get_word_by_id(word_id)
    
    def add_word(self, word: str, phonetic: str, definition: str, book_id: int) -> int:
        return self.words.add_word(word, phonetic, definition, book_id)
    
    def update_word_progress(self, word_id: int, progress_data: Dict):
        return self.words.update_word_progress(word_id, progress_data)
    
    def get_words_for_review(self, due_date: str) -> List[Dict]:
        return self.words.get_words_for_review(due_date)
    
    def get_new_words(self, count: int) -> List[Dict]:
        return self.words.get_new_words(count)
    
    def get_words(self, page: int = 1, page_size: int = 20, query: str = None, status: int = None, book_id: int = None) -> Tuple[List[Dict], int]:
        return self.words.get_words(page, page_size, query, status, book_id)
    
    def get_words_by_book(self, book_id: int) -> List[Dict]:
        return self.words.get_words_by_book(book_id)
    
    def get_all_records(self) -> List[Dict]:
        return self.words.get_all_records()
    
    def update_review_status(self, word_index: int, last_review: str, next_review: str, review_count: int, mastery_level: int):
        return self.words.update_review_status(word_index, last_review, next_review, review_count, mastery_level)
    
    def has_sent_email_today(self) -> bool:
        return self.words.has_sent_email_today()
    
    def mark_email_sent_today(
        self,
        status: str = 'success',
        to_email: str = None,
        from_email: str = None,
        duration_ms: int = None,
        user_id: int = None,
        provider: str = 'smtp'
    ):
        return self.words.mark_email_sent_today(
            status=status,
            to_email=to_email,
            from_email=from_email,
            duration_ms=duration_ms,
            user_id=user_id,
            provider=provider
        )
    
    # === 迁移方法 ===
    def migrate_v1_to_v2(self, default_words: List[Dict]):
        """从V1迁移到V2结构"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT count(*) FROM books')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        print("开始迁移数据库到 V2 版本...")

        cursor.execute('INSERT INTO books (name, total_words, is_active) VALUES (?, ?, ?)', 
                      ('默认词书 (CET4)', len(default_words), 1))
        book_id = cursor.lastrowid

        print(f"正在导入 {len(default_words)} 个单词...")
        word_map = {}
        for w in default_words:
            cursor.execute('''
            INSERT INTO words (book_id, word, phonetic, definition) 
            VALUES (?, ?, ?, ?)
            ''', (book_id, w['word'], w.get('phonetic', ''), w.get('definition', '')))
            word_map[w['word']] = cursor.lastrowid

        print("正在迁移学习记录...")
        cursor.execute('SELECT * FROM learning_records')
        records = cursor.fetchall()
        
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
