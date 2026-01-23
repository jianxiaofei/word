# -*- coding: utf-8 -*-
"""用户管理路由"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from api.utils import get_db, admin_required
from core.db.user_repository import UserRepository
from core.db.login_history_repository import LoginHistoryRepository

users_bp = Blueprint('users', __name__)


def get_user_repo():
    """获取用户仓储实例"""
    db = get_db()
    return UserRepository(db._get_conn)

def get_login_history_repo():
    """获取登录历史仓储实例"""
    db = get_db()
    return LoginHistoryRepository(db._get_conn)

def log_activity(action, resource_type=None, resource_id=None, details=None):
    """记录用户操作日志"""
    try:
        login_history_repo = get_login_history_repo()
        login_history_repo.log_user_activity(
            user_id=session.get('user_id'),
            username=session.get('username'),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr
        )
    except Exception:
        pass  # 日志记录失败不影响主流程


@users_bp.route('/users')
@admin_required
def user_list():
    """用户列表页面"""
    user_repo = get_user_repo()
    users = user_repo.get_all_users()
    return render_template('users.html', users=users)


@users_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """添加用户"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not username or not password:
        flash('用户名和密码不能为空', 'error')
        return redirect(url_for('users.user_list'))
    
    user_repo = get_user_repo()
    success, message = user_repo.create_user(username, password)
    
    if success:
        log_activity('create_user', 'user', None, f'创建用户: {username}')
        flash('用户添加成功', 'success')
    else:
        flash(f'添加失败: {message}', 'error')
    
    return redirect(url_for('users.user_list'))


@users_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    """编辑用户"""
    # 不允许修改自己
    if user_id == session.get('user_id'):
        flash('不能修改当前登录用户', 'error')
        return redirect(url_for('users.user_list'))
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    is_active = request.form.get('is_active') == '1'
    is_admin = request.form.get('is_admin') == '1'
    
    user_repo = get_user_repo()
    
    # 如果密码为空，则不更新密码
    update_password = password if password else None
    success, message = user_repo.update_user(
        user_id, 
        username=username, 
        password=update_password, 
        is_active=is_active,
        is_admin=is_admin
    )
    
    if success:
        log_activity('update_user', 'user', user_id, f'更新用户信息')
        flash('用户更新成功', 'success')
    else:
        flash(f'更新失败: {message}', 'error')
    
    return redirect(url_for('users.user_list'))


@users_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    # 不允许删除自己
    if user_id == session.get('user_id'):
        flash('不能删除当前登录用户', 'error')
        return redirect(url_for('users.user_list'))
    
    user_repo = get_user_repo()
    
    # 先获取用户信息用于日志
    user = user_repo.get_user_by_id(user_id)
    username_to_delete = user['username'] if user else str(user_id)
    
    success, message = user_repo.delete_user(user_id)
    
    if success:
        log_activity('delete_user', 'user', user_id, f'删除用户: {username_to_delete}')
        flash('用户删除成功', 'success')
    else:
        flash(f'删除失败: {message}', 'error')
    
    return redirect(url_for('users.user_list'))


@users_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """切换用户状态"""
    # 不允许修改自己
    if user_id == session.get('user_id'):
        return jsonify({'success': False, 'message': '不能修改当前登录用户状态'})
    
    user_repo = get_user_repo()
    user = user_repo.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'})
    
    new_status = not user['is_active']
    success, message = user_repo.update_user(user_id, is_active=new_status)
    
    return jsonify({
        'success': success,
        'message': message,
        'is_active': new_status
    })


@users_bp.route('/users/<int:user_id>/details')
@admin_required
def user_details(user_id):
    """用户详情页面（包括登录历史和活动日志）"""
    user_repo = get_user_repo()
    login_history_repo = get_login_history_repo()
    
    user = user_repo.get_user_by_id(user_id)
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('users.user_list'))
    
    # 获取用户统计
    stats = login_history_repo.get_user_stats(user_id)
    
    # 获取登录历史
    login_history = login_history_repo.get_user_login_history(user_id, limit=30)
    
    # 获取活动日志
    activities = login_history_repo.get_user_activities(user_id, limit=30)
    
    return render_template('user_details.html', 
                          user=user, 
                          stats=stats,
                          login_history=login_history,
                          activities=activities)


@users_bp.route('/login-history')
@admin_required
def login_history_list():
    """登录历史列表（所有用户）"""
    login_history_repo = get_login_history_repo()
    
    # 获取最近登录历史
    login_history = login_history_repo.get_recent_login_history(limit=100)
    
    # 获取失败的登录尝试
    failed_logins = login_history_repo.get_failed_login_attempts(hours=24)
    
    return render_template('login_history.html',
                          login_history=login_history,
                          failed_logins=failed_logins)


@users_bp.route('/activity-logs')
@admin_required
def activity_logs():
    """用户活动日志列表"""
    login_history_repo = get_login_history_repo()
    
    # 获取所有用户的活动日志
    activities = login_history_repo.get_user_activities(limit=100)
    
    return render_template('activity_logs.html', activities=activities)
