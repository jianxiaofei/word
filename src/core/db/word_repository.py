# -*- coding: utf-8 -*-
"""单词数据访问层"""

import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Callable


class WordRepository:
    """单词数据库操作"""
    
    def __init__(self, get_conn_func: Callable[[], sqlite3.Connection]):
        self._get_conn = get_conn_func
    
    def get_word_by_id(self, word_id: int) -> Optional[Dict]:
        """根据ID获取单词"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            cols = [d[0] for d in cursor.description]
            return dict(zip(cols, row))
        return None
    
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
        """获取待复习单词"""
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
        random.shuffle(results)
        return results
    
    def get_new_words(self, count: int) -> List[Dict]:
        """获取新单词"""
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
        return [dict(zip(cols, row)) for row in rows]
    
    def get_words(self, page: int = 1, page_size: int = 20, query: str = None, status: int = None, book_id: int = None) -> Tuple[List[Dict], int]:
        """获取单词列表（分页）"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        offset = (page - 1) * page_size
        params = []
        where_clauses = []
        
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
        
        cursor.execute(f"SELECT count(*) FROM words WHERE {where_str}", params)
        total = cursor.fetchone()[0]
        
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
    
    def get_all_records(self) -> List[Dict]:
        """获取所有学习记录"""
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
