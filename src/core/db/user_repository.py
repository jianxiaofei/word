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
            'SELECT id, username, password_hash, is_active, is_admin, created_at, last_login_at FROM users WHERE username = ? LIMIT 1',
            ((username or "").strip(),),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        cols = ['id', 'username', 'password_hash', 'is_active', 'is_admin', 'created_at', 'last_login_at']
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
    
    def get_all_users(self):
        """获取所有用户列表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, is_active, is_admin, created_at, last_login_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'username', 'is_active', 'is_admin', 'created_at', 'last_login_at']
        return [dict(zip(cols, row)) for row in rows]
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, is_active, is_admin, created_at, last_login_at 
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        cols = ['id', 'username', 'is_active', 'is_admin', 'created_at', 'last_login_at']
        return dict(zip(cols, row))
    
    def update_user(self, user_id: int, username: str = None, password: str = None, is_active: bool = None, is_admin: bool = None) -> Tuple[bool, str]:
        """更新用户信息"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if username is not None:
                username = username.strip()
                if not username:
                    return False, "用户名不能为空"
                if len(username) < 3:
                    return False, "用户名至少 3 个字符"
                updates.append("username = ?")
                params.append(username)
            
            if password is not None and password:
                if len(password) < 6:
                    return False, "密码至少 6 个字符"
                password_hash = generate_password_hash(password, method="pbkdf2:sha256")
                updates.append("password_hash = ?")
                params.append(password_hash)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if is_admin is not None:
                updates.append("is_admin = ?")
                params.append(1 if is_admin else 0)
            
            if not updates:
                return False, "没有要更新的内容"
            
            params.append(user_id)
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
            conn.commit()
            
            if cursor.rowcount == 0:
                return False, "用户不存在"
            
            return True, "更新成功"
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """删除用户"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            # 检查用户是否存在
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return False, "用户不存在"
            
            # 删除用户
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return True, "删除成功"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
