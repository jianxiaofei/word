# -*- coding: utf-8 -*-
"""工具函数和装饰器"""

from functools import wraps
from flask import session, redirect, url_for, request, g
from core.database import DatabaseManager


def login_required(f):
    """登录验证装饰器 - 统一版本"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    """获取数据库实例（单例模式）"""
    if 'db' not in g:
        g.db = DatabaseManager()
    return g.db


def close_db(e=None):
    """清理数据库实例"""
    g.pop('db', None)


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        
        # 检查是否是管理员
        user_id = session.get('user_id')
        db = get_db()
        user = db.get_user(user_id)
        
        if not user or not user.get('is_admin'):
            return "权限不足", 403
        
        return f(*args, **kwargs)
    return decorated_function


def api_response(success=True, data=None, message='', status_code=200):
    """统一 API 响应格式"""
    from flask import jsonify
    
    response = {
        'success': success,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code
