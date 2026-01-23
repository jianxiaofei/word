# -*- coding: utf-8 -*-
"""用户认证服务"""

from typing import Optional, Dict
from core.database import DatabaseManager
from werkzeug.security import check_password_hash
import os


class AuthService:
    """用户认证业务逻辑"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码（使用 werkzeug）"""
        return check_password_hash(password_hash, password)
    
    def register_user(self, username: str, password: str, email: str = '') -> Dict:
        """注册新用户"""
        # 检查用户名是否已存在
        existing = self.db.get_user_by_username(username)
        if existing:
            raise ValueError("用户名已存在")
        
        # 创建用户（使用 DatabaseManager 的方法，它会自动哈希密码）
        created, message = self.db.create_user(
            username=username,
            password=password
        )
        if not created:
            raise ValueError(message or "注册失败")

        user = self.db.get_user_by_username(username)
        if not user:
            raise ValueError("注册失败")

        return {
            'user_id': user['id'],
            'username': user['username'],
            'email': email
        }
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """用户登录"""
        # 1. 先检查环境变量中的管理员账号
        admin_user = os.getenv('WEB_ADMIN_USER', '')
        admin_password = os.getenv('WEB_ADMIN_PASSWORD', '')
        
        if admin_user and admin_password and username == admin_user and password == admin_password:
            # 环境变量管理员登录 - 确保数据库中有对应用户
            user = self.db.get_user_by_username(admin_user)
            if user:
                # 数据库中已有该用户，返回数据库用户信息
                return {
                    'user_id': user['id'],
                    'username': user['username'],
                    'email': user.get('email', ''),
                    'is_admin': True
                }
            else:
                # 数据库中没有该用户，创建一个
                created, _ = self.db.create_user(username=admin_user, password=admin_password)
                if created:
                    user = self.db.get_user_by_username(admin_user)
                    if user:
                        return {
                            'user_id': user['id'],
                            'username': user['username'],
                            'email': '',
                            'is_admin': True
                        }
                # 创建失败，返回特殊ID（向后兼容）
                return {
                    'user_id': -1,
                    'username': admin_user,
                    'email': '',
                    'is_admin': True
                }
        
        # 2. 检查数据库用户
        user = self.db.verify_user(username, password)
        if not user:
            return None

        return {
            'user_id': user['id'],
            'username': user['username'],
            'email': user.get('email', ''),
            'is_admin': bool(user.get('is_admin', False))
        }
