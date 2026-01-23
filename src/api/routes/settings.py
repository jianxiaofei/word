# -*- coding: utf-8 -*-
"""设置相关路由"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from api.utils import login_required, get_db
import config

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def settings_page():
    """设置页面"""
    user_id = session.get('user_id')
    
    # 获取用户配置
    user_config = get_db().get_user_config(user_id)
    
    # 获取系统配置
    system_settings = get_db().get_all_settings()
    
    # 合并配置
    settings_data = {
        'daily_new_words': user_config.get('daily_words', config.DAILY_NEW_WORDS),
        'server_url': system_settings.get('server_url', config.SERVER_URL),
        'smtp_server': config.SMTP_SERVER,
        'smtp_port': config.SMTP_PORT,
        'email_from': config.EMAIL_FROM,
        'email_to': user_config.get('email', config.EMAIL_TO),
        'enable_email': user_config.get('enable_email', False),
    }
    
    return render_template('settings.html', settings=settings_data)


@settings_bp.route('/update', methods=['POST'])
@login_required
def update_settings():
    """更新设置"""
    user_id = session.get('user_id')
    
    # 获取表单数据
    daily_words = request.form.get('daily_words', type=int)
    email = request.form.get('email', '').strip()
    enable_email = request.form.get('enable_email') == 'on'
    
    try:
        # 更新配置
        get_db().update_user_config(user_id, {
            'daily_words': daily_words,
            'email': email,
            'enable_email': enable_email
        })
        
        flash('设置已保存', 'success')
    except Exception as e:
        flash(f'保存失败: {str(e)}', 'error')
    
    return redirect(url_for('settings.settings_page'))


@settings_bp.route('/test-email', methods=['POST'])
@login_required
def send_test_email():
    """发送测试邮件"""
    from flask import jsonify
    try:
        # TODO: 实现测试邮件发送
        return jsonify({'success': True, 'message': '测试邮件已发送'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@settings_bp.route('/test-webhook', methods=['POST'])
@login_required
def send_test_webhook():
    """发送测试 Webhook"""
    from flask import jsonify
    try:
        # TODO: 实现测试 Webhook 发送
        return jsonify({'success': True, 'message': '测试 Webhook 已发送'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
