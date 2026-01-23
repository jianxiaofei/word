# -*- coding: utf-8 -*-
"""统计相关路由"""

from flask import Blueprint, render_template, jsonify, session
from services.stats_service import StatsService
from api.utils import login_required, get_db

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')


@stats_bp.route('/')
@login_required
def statistics():
    """统计页面"""
    user_id = session.get('user_id')
    
    # 调试日志
    print(f'[STATS DEBUG] user_id={user_id}, type={type(user_id)}', flush=True)
    
    stats_service = StatsService(get_db())
    
    # 获取统计数据
    user_stats = stats_service.get_user_stats(user_id)
    print(f'[STATS DEBUG] total={user_stats.get("total")}, learned={user_stats.get("total_learned")}', flush=True)
    
    progress = stats_service.get_learning_progress(user_id, days=30)
    distribution = stats_service.get_word_distribution(user_id)
    
    return render_template('statistics.html', 
                         stats=user_stats,
                         progress=progress,
                         distribution=distribution)


@stats_bp.route('/api')
@login_required
def api_stats():
    """API: 获取统计数据"""
    user_id = session.get('user_id')
    
    stats_service = StatsService(get_db())
    
    return jsonify({
        'user_stats': stats_service.get_user_stats(user_id),
        'progress': stats_service.get_learning_progress(user_id, days=30),
        'distribution': stats_service.get_word_distribution(user_id)
    })
