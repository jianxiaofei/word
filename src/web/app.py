# -*- coding: utf-8 -*-
"""学习统计Web服务器 - Flask"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

HISTORY_FILE = 'word_history.json'
TOTAL_WORDS = 4537


def load_history():
    """加载学习历史"""
    if not os.path.exists(HISTORY_FILE):
        return {"words": {}, "used_indices": [], "last_update": None}
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_statistics():
    """计算统计数据"""
    history = load_history()
    words = history.get('words', {})
    
    # 基础统计
    total_learned = len(words)
    total_reviews = sum(w.get('review_count', 0) for w in words.values())
    
    # 掌握度统计
    mastery_counts = defaultdict(int)
    for word_data in words.values():
        level = word_data.get('mastery_level', 0)
        mastery_counts[level] += 1
    
    # 计算掌握率（完成3次以上复习算掌握）
    mastered = sum(count for level, count in mastery_counts.items() if level >= 3)
    mastery_rate = (mastered / total_learned * 100) if total_learned > 0 else 0
    
    # 学习进度
    progress = (total_learned / TOTAL_WORDS * 100) if TOTAL_WORDS > 0 else 0
    
    # 连续学习天数
    streak_days = calculate_streak(words)
    
    # 今日待复习
    today = datetime.now().strftime('%Y-%m-%d')
    today_review = [
        w for w in words.values() 
        if w.get('next_review') == today
    ]
    
    # 最近学习的单词
    recent_words = sorted(
        words.items(),
        key=lambda x: x[1].get('last_review', '1970-01-01'),
        reverse=True
    )[:10]
    
    # 按日期统计学习量
    daily_stats = calculate_daily_stats(words)
    
    return {
        'total_learned': total_learned,
        'total_reviews': total_reviews,
        'mastery_rate': round(mastery_rate, 1),
        'progress': round(progress, 2),
        'streak_days': streak_days,
        'today_review_count': len(today_review),
        'mastery_distribution': dict(mastery_counts),
        'recent_words': recent_words[:5],
        'daily_stats': daily_stats,
        'last_update': history.get('last_update', 'N/A')
    }


def calculate_streak(words):
    """计算连续学习天数"""
    if not words:
        return 0
    
    # 获取所有学习日期
    dates = set()
    for word_data in words.values():
        first_learned = word_data.get('first_learned')
        if first_learned:
            dates.add(first_learned)
        last_review = word_data.get('last_review')
        if last_review:
            dates.add(last_review)
    
    if not dates:
        return 0
    
    # 排序日期
    sorted_dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in dates], reverse=True)
    
    # 从最近日期开始计算连续天数
    today = datetime.now().date()
    streak = 0
    
    for i, date in enumerate(sorted_dates):
        expected_date = today - timedelta(days=i)
        if date.date() == expected_date:
            streak += 1
        else:
            break
    
    return streak


def calculate_daily_stats(words):
    """按日期统计学习量"""
    daily_counts = defaultdict(int)
    
    for word_data in words.values():
        first_learned = word_data.get('first_learned')
        if first_learned:
            daily_counts[first_learned] += 1
    
    # 最近30天
    today = datetime.now()
    result = []
    for i in range(29, -1, -1):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        result.append({
            'date': date,
            'count': daily_counts.get(date, 0)
        })
    
    return result


@app.route('/')
def index():
    """主页 - 统计面板"""
    stats = calculate_statistics()
    return render_template('statistics.html', stats=stats)


@app.route('/api/stats')
def api_stats():
    """API接口 - 返回统计数据JSON"""
    stats = calculate_statistics()
    return jsonify(stats)


@app.route('/api/words')
def api_words():
    """API接口 - 返回所有单词详情"""
    history = load_history()
    words = history.get('words', {})
    
    # 转换为列表格式
    word_list = []
    for idx, word_data in words.items():
        word_list.append({
            'index': idx,
            **word_data
        })
    
    # 按最后复习时间排序
    word_list.sort(key=lambda x: x.get('last_review', '1970-01-01'), reverse=True)
    
    return jsonify({
        'total': len(word_list),
        'words': word_list
    })


if __name__ == '__main__':
    print("=" * 60)
    print("单词学习统计系统")
    print("=" * 60)
    print("访问地址: http://localhost:8080")
    print("API接口: http://localhost:8080/api/stats")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=True)
