# -*- coding: utf-8 -*-
"""认证相关路由 - 登录、注册、登出"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.auth_service import AuthService
from api.utils import get_db
from core.db.login_history_repository import LoginHistoryRepository
import os

auth_bp = Blueprint('auth', __name__)

def get_auth_service():
    """获取认证服务实例"""
    return AuthService(get_db())

def get_login_history_repo():
    """获取登录历史仓储实例"""
    db = get_db()
    return LoginHistoryRepository(db._get_conn)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        auth_service = get_auth_service()
        login_history_repo = get_login_history_repo()
        
        # 获取客户端信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        user = auth_service.login(username, password)
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)
            
            # 记录成功的登录
            login_history_repo.record_login(
                user_id=user['user_id'],
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_method='password',
                status='success',
                session_id=session.get('_id', '')
            )
            
            next_page = request.args.get('next', '/')
            return redirect(next_page)
        else:
            # 记录失败的登录尝试
            login_history_repo.record_login(
                user_id=-1,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_method='password',
                status='failure',
                failure_reason='用户名或密码错误'
            )
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册 - 已禁用"""
    flash('注册功能已关闭，请联系管理员创建账号', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    return redirect(url_for('auth.login'))
