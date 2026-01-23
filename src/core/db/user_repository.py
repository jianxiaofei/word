# -*- coding: utf-8 -*-
"""用户数据访问层"""

import sqlite3
from typing import Optional, Dict, Tuple, Callable
from werkzeug.security import generate_password_hash, check_password_hash


class UserRepository:
    """用户相关数据库操作"""
    
    def __init__(self, get_conn_func: Callable[[], sqlite3.Connection]):
        self._get_conn = get_conn_func
    
    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        """创建新用户"""
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
        """根据用户名获取用户信息"""
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
        """验证用户名和密码"""
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
