# -*- coding: utf-8 -*-
"""用户-单词绑定数据访问层"""

import sqlite3
from typing import Set, List, Dict, Optional, Tuple, Callable


class BindingRepository:
    """用户-单词绑定关系数据库操作"""
    
    def __init__(self, get_conn_func: Callable[[], sqlite3.Connection]):
        self._get_conn = get_conn_func
    
    def bind_word_to_user(self, user_id: int, word_id: int) -> bool:
        """绑定单词到用户"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO user_word_bindings (user_id, word_id) VALUES (?, ?)',
                (int(user_id), int(word_id)),
            )
            conn.commit()
            return True
        finally:
            conn.close()
    
    def unbind_word_from_user(self, user_id: int, word_id: int) -> bool:
        """解绑用户的单词"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'DELETE FROM user_word_bindings WHERE user_id = ? AND word_id = ?',
                (int(user_id), int(word_id)),
            )
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_user_bound_word_ids(self, user_id: int, word_ids: Optional[List[int]] = None) -> Set[int]:
        """获取用户绑定的单词ID集合"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            if word_ids:
                placeholders = ",".join(["?"] * len(word_ids))
                cursor.execute(
                    f'SELECT word_id FROM user_word_bindings WHERE user_id = ? AND word_id IN ({placeholders})',
                    [int(user_id)] + [int(w) for w in word_ids],
                )
            else:
                cursor.execute('SELECT word_id FROM user_word_bindings WHERE user_id = ?', (int(user_id),))

            rows = cursor.fetchall()
            return {int(r[0]) for r in rows}
        finally:
            conn.close()
    
    def list_user_bound_words(self, user_id: int, page: int = 1, page_size: int = 20, query: str = None) -> Tuple[List[Dict], int]:
        """分页获取用户绑定的单词列表"""
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
            FROM user_word_bindings b
            JOIN words w ON w.id = b.word_id
            WHERE b.user_id = ?{where_extra}
            ''',
            params,
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            f'''
            SELECT w.*
            FROM user_word_bindings b
            JOIN words w ON w.id = b.word_id
            WHERE b.user_id = ?{where_extra}
            ORDER BY b.created_at DESC
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
        """获取用户绑定的全部单词"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                SELECT w.*
                FROM user_word_bindings b
                JOIN words w ON w.id = b.word_id
                WHERE b.user_id = ?
                ORDER BY b.created_at DESC
                ''',
                (int(user_id),),
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 'first_learned', 'last_review', 'next_review', 'review_count', 'mastery_level', 'created_at', 'updated_at']
        return [dict(zip(cols, row)) for row in rows]
