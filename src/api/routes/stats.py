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


@stats_bp.route('/api/mistakes')
@login_required
def api_difficult_words():
    """API: 获取易错单词分析"""
    from flask import request
    
    limit = request.args.get('limit', 50, type=int)
    
    stats_service = StatsService(get_db())
    analysis = stats_service.get_difficult_words_analysis(limit=limit)
    
    return jsonify(analysis)


@stats_bp.route('/api/efficiency')
@login_required
def api_learning_efficiency():
    """API: 获取学习效率报告"""
    stats_service = StatsService(get_db())
    report = stats_service.get_learning_efficiency_report()
    
    return jsonify(report)


@stats_bp.route('/mistakes')
@login_required
def mistakes_page():
    """易错单词页面"""
    stats_service = StatsService(get_db())
    
    # 获取易错单词分析
    analysis = stats_service.get_difficult_words_analysis(limit=50)
    efficiency_report = stats_service.get_learning_efficiency_report()
    
    return render_template('mistakes.html',
                         analysis=analysis,
                         efficiency=efficiency_report)
