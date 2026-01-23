# -*- coding: utf-8 -*-
"""词书数据访问层"""

import sqlite3
from typing import List, Dict, Optional, Callable


class BookRepository:
    """词书数据库操作"""
    
    def __init__(self, get_conn_func: Callable[[], sqlite3.Connection]):
        self._get_conn = get_conn_func
    
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
        """获取当前激活的词书"""
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
        """激活指定词书"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE books SET is_active = 0')
            cursor.execute('UPDATE books SET is_active = 1 WHERE id = ?', (book_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
