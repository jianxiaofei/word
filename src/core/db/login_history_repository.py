# -*- coding: utf-8 -*-
"""登录历史和用户活动日志数据访问层"""

import sqlite3
from typing import Optional, List, Dict, Callable


class LoginHistoryRepository:
    """登录历史和用户活动日志相关数据库操作"""
    
    def __init__(self, get_conn_func: Callable[[], sqlite3.Connection]):
        self._get_conn = get_conn_func
    
    def record_login(self, user_id: int, username: str, ip_address: str = None, 
                    user_agent: str = None, login_method: str = 'password', 
                    status: str = 'success', failure_reason: str = None, 
                    session_id: str = None) -> int:
        """记录登录历史"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO login_history 
                (user_id, username, ip_address, user_agent, login_method, status, failure_reason, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, ip_address, user_agent, login_method, status, failure_reason, session_id))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_user_login_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """获取用户的登录历史"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, username, login_time, ip_address, user_agent, 
                   login_method, status, failure_reason
            FROM login_history
            WHERE user_id = ?
            ORDER BY login_time DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'user_id', 'username', 'login_time', 'ip_address', 
                'user_agent', 'login_method', 'status', 'failure_reason']
        return [dict(zip(cols, row)) for row in rows]
    
    def get_recent_login_history(self, limit: int = 50) -> List[Dict]:
        """获取最近的登录历史（所有用户）"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, username, login_time, ip_address, user_agent, 
                   login_method, status, failure_reason
            FROM login_history
            ORDER BY login_time DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'user_id', 'username', 'login_time', 'ip_address', 
                'user_agent', 'login_method', 'status', 'failure_reason']
        return [dict(zip(cols, row)) for row in rows]
    
    def get_failed_login_attempts(self, username: str = None, hours: int = 24) -> List[Dict]:
        """获取失败的登录尝试"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if username:
            cursor.execute('''
                SELECT id, user_id, username, login_time, ip_address, user_agent, 
                       login_method, status, failure_reason
                FROM login_history
                WHERE status = 'failure' 
                  AND username = ?
                  AND login_time > datetime('now', '-' || ? || ' hours')
                ORDER BY login_time DESC
            ''', (username, hours))
        else:
            cursor.execute('''
                SELECT id, user_id, username, login_time, ip_address, user_agent, 
                       login_method, status, failure_reason
                FROM login_history
                WHERE status = 'failure'
                  AND login_time > datetime('now', '-' || ? || ' hours')
                ORDER BY login_time DESC
            ''', (hours,))
        
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'user_id', 'username', 'login_time', 'ip_address', 
                'user_agent', 'login_method', 'status', 'failure_reason']
        return [dict(zip(cols, row)) for row in rows]
    
    def log_user_activity(self, user_id: int, username: str, action: str, 
                         resource_type: str = None, resource_id: int = None, 
                         details: str = None, ip_address: str = None) -> int:
        """记录用户操作日志"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_activity_logs 
                (user_id, username, action, resource_type, resource_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, action, resource_type, resource_id, details, ip_address))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_user_activities(self, user_id: int = None, limit: int = 50) -> List[Dict]:
        """获取用户活动日志"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT id, user_id, username, action, resource_type, resource_id, 
                       details, ip_address, created_at
                FROM user_activity_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT id, user_id, username, action, resource_type, resource_id, 
                       details, ip_address, created_at
                FROM user_activity_logs
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        cols = ['id', 'user_id', 'username', 'action', 'resource_type', 
                'resource_id', 'details', 'ip_address', 'created_at']
        return [dict(zip(cols, row)) for row in rows]
    
    def get_user_stats(self, user_id: int) -> Dict:
        """获取用户的统计信息"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 总登录次数
        cursor.execute('SELECT COUNT(*) FROM login_history WHERE user_id = ? AND status = "success"', (user_id,))
        total_logins = cursor.fetchone()[0]
        
        # 最后登录时间
        cursor.execute('SELECT login_time FROM login_history WHERE user_id = ? AND status = "success" ORDER BY login_time DESC LIMIT 1', (user_id,))
        row = cursor.fetchone()
        last_login = row[0] if row else None
        
        # 失败登录次数（最近24小时）
        cursor.execute('''
            SELECT COUNT(*) FROM login_history 
            WHERE user_id = ? AND status = "failure" 
            AND login_time > datetime('now', '-24 hours')
        ''', (user_id,))
        failed_logins_24h = cursor.fetchone()[0]
        
        # 活动次数
        cursor.execute('SELECT COUNT(*) FROM user_activity_logs WHERE user_id = ?', (user_id,))
        total_activities = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_logins': total_logins,
            'last_login': last_login,
            'failed_logins_24h': failed_logins_24h,
            'total_activities': total_activities
        }
