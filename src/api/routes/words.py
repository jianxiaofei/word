# -*- coding: utf-8 -*-
"""单词相关路由"""

from flask import Blueprint, render_template, request, jsonify, session
from services.word_service import WordService
from api.utils import login_required, get_db

words_bp = Blueprint('words', __name__, url_prefix='/words')

def get_word_service():
    """获取单词服务实例"""
    return WordService(get_db())


@words_bp.route('/')
@login_required
def word_list():
    """单词列表页面"""
    book_id = request.args.get('book_id', type=int)
    page = request.args.get('page', 1, type=int)
    user_id = session.get('user_id')
    
    word_service = get_word_service()
    
    if book_id:
        words = word_service.get_words_by_book(book_id)
        book = get_db().get_book(book_id)
        book_name = book['name'] if book else 'Unknown'
    else:
        words = word_service.get_user_words(user_id)
        book_name = '我的单词'
    
    # 简单分页
    page_size = 20
    total_pages = (len(words) + page_size - 1) // page_size if words else 1
    start = (page - 1) * page_size
    end = start + page_size
    paginated_words = words[start:end]
    
    return render_template('words.html', 
                         words=paginated_words, 
                         book_name=book_name,
                         current_page=page,
                         total_pages=total_pages)


@words_bp.route('/my')
@login_required
def my_words():
    """我的单词"""
    from datetime import datetime
    user_id = session.get('user_id')
    
    # 调试日志
    print(f'[MY_WORDS DEBUG] user_id={user_id}, type={type(user_id)}', flush=True)
    
    status_filter = request.args.get('status')
    filter_type = request.args.get('filter')  # 新增：筛选类型
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    
    word_service = get_word_service()
    all_words = word_service.get_user_words(user_id, status_filter)
    print(f'[MY_WORDS DEBUG] all_words count={len(all_words)}', flush=True)
    
    # 根据筛选类型过滤
    if filter_type == 'due_today':
        # 今日待复习
        today = datetime.now().date().isoformat()
        words = [w for w in all_words if w.get('next_review') == today and w.get('status') == 1]
        filter_title = '今日待复习'
    elif filter_type == 'learning':
        # 学习中的单词
        words = [w for w in all_words if w.get('status') == 1]
        filter_title = '学习中'
    elif filter_type == 'mastered':
        # 已掌握（掌握度>=5）
        words = [w for w in all_words if w.get('mastery_level', 0) >= 5]
        filter_title = '已掌握'
    else:
        words = all_words
        filter_title = '全部'
    
    # 搜索过滤
    if query:
        words = [w for w in words if query.lower() in w.get('word', '').lower() or query.lower() in w.get('definition', '').lower()]
    
    # 简单分页
    page_size = 20
    total_pages = (len(words) + page_size - 1) // page_size if words else 1
    start = (page - 1) * page_size
    end = start + page_size
    paginated_words = words[start:end]
    
    return render_template('my_words.html', 
                         words=paginated_words, 
                         status_filter=status_filter,
                         filter_type=filter_type,
                         filter_title=filter_title,
                         total_count=len(words),
                         current_page=page,
                         total_pages=total_pages)


@words_bp.route('/mark/<int:word_id>', methods=['POST'])
@login_required
def mark_word(word_id):
    """标记单词状态"""
    action = request.args.get('action', 'known')
    
    try:
        word_service = get_word_service()
        message = word_service.mark_word_status(word_id, action)
        
        # 如果是 AJAX 请求，返回 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': message})
        
        # 否则返回 HTML 页面
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>反馈成功</title>
            <style>
                body {{ font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f5f5f5; }}
                .card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }}
                .icon {{ font-size: 48px; color: #28a745; margin-bottom: 1rem; }}
                h1 {{ margin: 0 0 1rem; font-size: 24px; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="icon">✓</div>
                <h1>操作成功</h1>
                <p>{message}</p>
                <p><small>您可以关闭此页面</small></p>
            </div>
        </body>
        </html>
        """
    except ValueError as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        return str(e), 400
