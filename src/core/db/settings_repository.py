# -*- coding: utf-8 -*-
"""设置数据访问层"""

import sqlite3
from typing import Dict, Callable


class SettingsRepository:
    """系统设置数据库操作"""
    
    def __init__(self, get_conn_func: Callable[[], sqlite3.Connection]):
        self._get_conn = get_conn_func
    
    def get_setting(self, key: str, default: str = None) -> str:
        """获取单个设置"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str):
        """设置单个配置"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', (key, str(value)))
        conn.commit()
        conn.close()
    
    def get_all_settings(self) -> Dict[str, str]:
        """获取所有设置"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}
    
    def get_user_config(self, user_id: int) -> Dict:
        """获取用户配置"""
        prefix = f"user_{user_id}_"
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings WHERE key LIKE ?', (f"{prefix}%",))
        rows = cursor.fetchall()
        conn.close()
        
        config = {}
        for key, value in rows:
            config_key = key[len(prefix):]
            config[config_key] = value
        
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
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
                (setting_key, str(value))
            )
        
        conn.commit()
        conn.close()
