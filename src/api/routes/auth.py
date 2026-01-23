# -*- coding: utf-8 -*-
"""认证相关路由 - 登录、注册、登出"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.auth_service import AuthService
from api.utils import get_db
import os

auth_bp = Blueprint('auth', __name__)

def get_auth_service():
    """获取认证服务实例"""
    return AuthService(get_db())


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
        user = auth_service.login(username, password)
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            # 设置管理员标识
            session['is_admin'] = user.get('is_admin', False)
            
            next_page = request.args.get('next', '/')
            return redirect(next_page)
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    # 检查是否允许注册
    allow_register = os.getenv('WEB_ALLOW_REGISTER', 'true').lower() == 'true'
    if not allow_register:
        flash('注册功能已关闭', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        email = request.form.get('email', '').strip()
        
        # 验证
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('register.html')
        
        if password != password2:
            flash('两次密码输入不一致', 'error')
            return render_template('register.html')
        
        try:
            auth_service = get_auth_service()
            user = auth_service.register_user(username, password, email)
            
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    return redirect(url_for('auth.login'))
