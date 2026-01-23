# -*- coding: utf-8 -*-
"""单词数据访问层"""

import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Callable, Set


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
    
    def get_words_by_book(self, book_id: int) -> List[Dict]:
        """获取指定词书的所有单词"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM words 
        WHERE book_id = ?
        ORDER BY created_at DESC
        ''', (book_id,))
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'book_id', 'word', 'phonetic', 'definition', 'status', 
                'first_learned', 'last_review', 'next_review', 'review_count', 
                'mastery_level', 'created_at', 'updated_at']
        return [dict(zip(cols, row)) for row in rows]

    # === 用户-单词学习记录（learning_records） ===
    def bind_word_to_user(self, user_id: int, word_id: int) -> bool:
        """绑定单词到用户（创建学习记录）"""
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
        """解绑用户的单词（删除学习记录）"""
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
        """获取用户学习记录的单词ID集合"""
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
        """分页获取用户学习记录的单词列表"""
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
        """获取用户学习记录的全部单词"""
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
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            to_email TEXT,
            from_email TEXT,
            duration_ms INTEGER,
            user_id INTEGER,
            provider TEXT DEFAULT 'smtp',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        today = datetime.now().date().isoformat()
        cursor.execute('SELECT 1 FROM email_logs WHERE sent_date = ? AND status = ?', (today, 'success'))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        return row is not None
    
    def mark_email_sent_today(
        self,
        status: str = 'success',
        to_email: str = None,
        from_email: str = None,
        duration_ms: int = None,
        user_id: int = None,
        provider: str = 'smtp'
    ):
        """标记今天邮件已发送"""
        conn = self._get_conn()
        cursor = conn.cursor()
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        today = datetime.now().date().isoformat()
        cursor.execute(
            '''
            INSERT INTO email_logs
            (sent_date, sent_at, status, to_email, from_email, duration_ms, user_id, provider)
            VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sent_date) DO UPDATE SET
                sent_at = excluded.sent_at,
                status = excluded.status,
                to_email = excluded.to_email,
                from_email = excluded.from_email,
                duration_ms = excluded.duration_ms,
                user_id = excluded.user_id,
                provider = excluded.provider
            ''',
            (today, status, to_email, from_email, duration_ms, user_id, provider)
        )
        conn.commit()
        conn.close()

    def mark_words_sent(self, word_ids: List[int], sent_date: str):
        """标记单词已发送（用于24小时自动标记机制）"""
        if not word_ids:
            return
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(word_ids))
        cursor.execute(f'''
        UPDATE words 
        SET sent_date = ?
        WHERE id IN ({placeholders})
        ''', [sent_date] + word_ids)
        
        conn.commit()
        conn.close()
    
    def get_words_sent_before(self, before_date: str) -> List[Dict]:
        """获取在指定日期之前（包含当天）发送但未反馈的单词
        
        条件：sent_date <= before_date 且 last_review != sent_date
        这表示单词已发送但用户未标记反馈
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM words 
        WHERE sent_date IS NOT NULL 
        AND sent_date <= ?
        AND (last_review IS NULL OR last_review != sent_date)
        AND status = 1
        ''', (before_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    
    def clear_sent_date(self, word_id: int):
        """清除单词的发送日期标记"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE words SET sent_date = NULL WHERE id = ?', (word_id,))
        
        conn.commit()
        conn.close()
    
    def get_difficult_words(self, limit: int = 50, min_unknown_count: int = 2) -> List[Dict]:
        """
        获取易错单词（按错误次数降序）
        
        Args:
            limit: 返回数量限制
            min_unknown_count: 最小错误次数，默认至少错2次
            
        Returns:
            易错单词列表，包含完整单词信息和统计数据
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM words 
        WHERE status = 1 
        AND unknown_count >= ?
        ORDER BY unknown_count DESC, last_mistake_date DESC
        LIMIT ?
        ''', (min_unknown_count, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    
    def get_mistake_statistics(self) -> Dict:
        """
        获取学习效果统计数据
        
        Returns:
            统计信息字典，包括：
            - total_mistakes: 总错误次数
            - words_with_mistakes: 有错误记录的单词数
            - avg_mistakes: 平均错误次数
            - difficult_words_count: 困难单词数（错误≥3次）
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 统计总错误次数和单词数
        cursor.execute('''
        SELECT 
            COALESCE(SUM(unknown_count), 0) as total_mistakes,
            COUNT(CASE WHEN unknown_count > 0 THEN 1 END) as words_with_mistakes,
            COUNT(CASE WHEN unknown_count >= 3 THEN 1 END) as difficult_words_count
        FROM words 
        WHERE status = 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        total_mistakes, words_with_mistakes, difficult_words_count = result
        
        avg_mistakes = total_mistakes / words_with_mistakes if words_with_mistakes > 0 else 0
        
        return {
            'total_mistakes': total_mistakes,
            'words_with_mistakes': words_with_mistakes,
            'avg_mistakes': round(avg_mistakes, 2),
            'difficult_words_count': difficult_words_count
        }
