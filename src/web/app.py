# -*- coding: utf-8 -*-
"""学习统计Web服务器 - Flask"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sys
import re
import os
import secrets
import hmac
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import config

from werkzeug.middleware.proxy_fix import ProxyFix

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import DatabaseManager
from core.email_sender import EmailSender
from core.notifier import Notifier
from core.word_selector import WordSelectorV2
from core.word_parser import WordParser

class PrefixMiddleware:
    """支持把 Flask 挂在子路径下（例如 /word-web）。

    Nginx 需设置：proxy_set_header X-Script-Name /word-web;
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ.get("PATH_INFO", "")
            if path_info.startswith(script_name):
                new_path = path_info[len(script_name) :]
                environ["PATH_INFO"] = new_path if new_path else "/"
        return self.wsgi_app(environ, start_response)


app = Flask(__name__)

# 反代场景下修正 X-Forwarded-*，并支持 /word-web 这类子路径部署
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.wsgi_app = PrefixMiddleware(app.wsgi_app)


def _get_web_secret_key() -> str:
    configured = os.environ.get("WEB_SECRET_KEY")
    if configured:
        return configured
    generated = secrets.token_urlsafe(32)
    app.logger.warning(
        "WEB_SECRET_KEY 未设置，已临时生成随机值；重启会导致登录失效。建议在 .env 中设置 WEB_SECRET_KEY。"
    )
    return generated


def _get_admin_credentials() -> tuple[str, str]:
    username = os.environ.get("WEB_ADMIN_USER", "admin")
    password = os.environ.get("WEB_ADMIN_PASSWORD")
    if password:
        return username, password

    generated = secrets.token_urlsafe(16)
    app.logger.warning(
        "WEB_ADMIN_PASSWORD 未设置，已临时生成随机密码：%s （建议立刻在 .env 中设置 WEB_ADMIN_PASSWORD 并重启容器）",
        generated,
    )
    return username, generated


app.secret_key = _get_web_secret_key()
_ADMIN_USER, _ADMIN_PASS = _get_admin_credentials()


def _allow_register() -> bool:
    return os.environ.get("WEB_ALLOW_REGISTER", "true").lower() in ("true", "1", "yes")


def _is_logged_in() -> bool:
    return bool(session.get("is_admin") or session.get("user_id"))


def _is_admin() -> bool:
    return bool(session.get("is_admin"))


def _require_admin():
    if _is_admin():
        return None
    if request.path.startswith("/api/"):
        return jsonify({"error": "Forbidden"}), 403
    return "Forbidden", 403


@app.before_request
def require_login():
    # 邮件反馈接口需要匿名访问（从邮件按钮打开）
    if request.path.startswith("/api/feedback"):
        return None

    # 登录/登出/注册页放行
    if request.path in ("/login", "/logout", "/register"):
        return None

    # Flask 静态资源放行（本项目目前基本不用）
    if request.path.startswith("/static/"):
        return None

    if _is_logged_in():
        # 管理员才能访问敏感配置与词书管理
        admin_only_paths = (
            "/settings",
            "/books",
            "/api/settings",
            "/api/books",
            "/api/test-email",
            "/api/test-webhook",
        )
        if request.path.startswith(admin_only_paths):
            return _require_admin()
        return None

    # API 未登录返回 401，页面则跳转登录
    if request.path.startswith("/api/"):
        return jsonify({"error": "Unauthorized"}), 401

    return redirect(url_for("login", next=request.full_path))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        # 1) 管理员登录（兼容旧模式）
        if username == _ADMIN_USER and hmac.compare_digest(password, _ADMIN_PASS):
            session.clear()
            session["is_admin"] = True
            session["username"] = username
            next_url = request.args.get("next")
            return redirect(next_url or url_for("index"))

        # 2) 普通用户登录
        db = get_db()
        user = db.verify_user(username, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = False
            next_url = request.args.get("next")
            return redirect(next_url or url_for("words_page"))

        return render_template("login.html", error="用户名或密码错误", allow_register=_allow_register()), 401

    return render_template("login.html", allow_register=_allow_register())


@app.route("/register", methods=["GET", "POST"])
def register():
    if not _allow_register():
        return "Registration disabled", 403

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""

        if password != password2:
            return render_template("register.html", error="两次输入的密码不一致"), 400

        db = get_db()
        ok, msg = db.create_user(username, password)
        if not ok:
            return render_template("register.html", error=msg), 400

        user = db.verify_user(username, password)
        if not user:
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = False
        return redirect(url_for("words_page"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/api/me')
def api_me():
    if not _is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "is_admin": bool(session.get("is_admin")),
        "user_id": session.get("user_id"),
        "username": session.get("username"),
    })

def get_db():
    return DatabaseManager()

def calculate_statistics(user_id: int = None, is_admin: bool = False):
    """计算统计数据。

    - 管理员：全局统计（当前激活词书的学习记录）
    - 普通用户：仅统计该用户“绑定”的单词集合
    """
    db = get_db()

    if (not is_admin) and user_id:
        bound_words = db.get_user_bound_words(user_id)
        total_words = len(bound_words)
        learned_records = [w for w in bound_words if int(w.get('status') or 0) == 1]
        scope = 'user'
    else:
        learned_records = db.get_all_records()
        active_book = db.get_active_book()
        total_words = active_book['total_words'] if active_book else 0
        scope = 'global'
    
    # 基础统计
    total_learned = len(learned_records)
    total_reviews = sum(int(w.get('review_count', 0) or 0) for w in learned_records)
    
    # 掌握度统计
    mastery_counts = defaultdict(int)
    for word_data in learned_records:
        level = word_data.get('mastery_level', 0)
        mastery_counts[level] += 1
    
    # 计算掌握率（完成3次以上复习算掌握）
    mastered = sum(count for level, count in mastery_counts.items() if level >= 3)
    mastery_rate = (mastered / total_learned * 100) if total_learned > 0 else 0
    
    # 学习进度
    progress = (total_learned / total_words * 100) if total_words > 0 else 0
    
    # 连续学习天数
    streak_days = calculate_streak(learned_records)
    
    # 今日待复习
    today = datetime.now().strftime('%Y-%m-%d')
    today_review = [
        w for w in learned_records
        if w.get('next_review') and w.get('next_review') <= today
    ]
    
    # 最近学习的单词
    recent_words = sorted(
        learned_records,
        key=lambda x: x.get('last_review', '1970-01-01'),
        reverse=True
    )[:10]
    
    # 按日期统计学习量
    daily_stats = calculate_daily_stats(learned_records)
    
    return {
        'scope': scope,
        'total': total_words,
        'total_learned': total_learned,
        'total_reviews': total_reviews,
        'mastery_rate': round(mastery_rate, 1),
        'progress': round(progress, 2),
        'streak_days': streak_days,
        'today_review_count': len(today_review),
        'mastery_distribution': dict(mastery_counts),
        'recent_words': recent_words[:5],
        'daily_stats': daily_stats,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def calculate_streak(records):
    """计算连续学习天数"""
    if not records:
        return 0
    
    # 获取所有学习日期
    dates = set()
    for word_data in records:
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
    
    # 检查今天是否学习了
    date_set = {d.date() for d in sorted_dates}
    
    check_date = today
    # 如果今天没记录，且昨天也没记录，那就是0
    if check_date not in date_set:
        check_date = today - timedelta(days=1)
        if check_date not in date_set:
            return 0
            
    while check_date in date_set:
        streak += 1
        check_date -= timedelta(days=1)
            
    return streak


def calculate_daily_stats(records):
    """按日期统计学习量"""
    daily_counts = defaultdict(int)
    
    for word_data in records:
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
    stats = calculate_statistics(user_id=session.get('user_id'), is_admin=bool(session.get('is_admin')))
    return render_template('statistics.html', stats=stats)

@app.route('/settings')
def settings_page():
    """设置页面"""
    # Debugging
    try:
        app.logger.error(f"DEBUG: config file: {getattr(config, '__file__', 'unknown')}")
        app.logger.error(f"DEBUG: config dir: {dir(config)}")
    except Exception as e:
        app.logger.error(f"DEBUG Error: {e}")

    db = get_db()
    db_settings = db.get_all_settings()
    
    # 合并配置，优先使用数据库设置，如果数据库为空则使用 config.py 的默认值
    # 使用 getattr 避免 AttributeError
    settings = {
        'daily_new_words': db_settings.get('daily_new_words') or getattr(config, 'DAILY_NEW_WORDS', 5),
        'smtp_server': db_settings.get('smtp_server') or getattr(config, 'SMTP_SERVER', ''),
        'smtp_port': db_settings.get('smtp_port') or getattr(config, 'SMTP_PORT', 587),
        'email_from': db_settings.get('email_from') or getattr(config, 'EMAIL_FROM', ''),
        'email_to': db_settings.get('email_to') or getattr(config, 'EMAIL_TO', ''),
        'smtp_password': db_settings.get('smtp_password') or getattr(config, 'SMTP_PASSWORD', ''),
        'server_url': db_settings.get('server_url') or getattr(config, 'SERVER_URL', ''),
        'webhook_url': db_settings.get('webhook_url') or getattr(config, 'WEBHOOK_URL', '')
    }
    
    return render_template('settings.html', settings=settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """更新设置"""
    data = request.json
    db = get_db()
    for key, value in data.items():
        db.set_setting(key, value)
    return jsonify({'status': 'success'})

@app.route('/books')
def books_page():
    """词书管理页面"""
    db = get_db()
    conn = db._get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    books = []
    for row in rows:
        books.append({
            'id': row[0],
            'name': row[1],
            'total_words': row[2],
            'is_active': bool(row[3]),
            'created_at': row[4]
        })
    return render_template('books.html', books=books)

@app.route('/api/books/upload', methods=['POST'])
def upload_book():
    """上传新词书 - 支持 TXT/CSV/Excel"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    name = request.form.get('name')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not name:
        return jsonify({'error': 'Book name is required'}), 400
        
    try:
        # 保存临时文件
        temp_path = Path('/tmp') / file.filename
        file.save(str(temp_path))
        
        # 使用 WordParser 解析
        parser = WordParser()
        words = parser.parse(str(temp_path))
        
        # 删除临时文件
        temp_path.unlink()
        
        if not words:
            return jsonify({'error': 'No valid words found in file'}), 400
        
        # 保存到数据库
        db = get_db()
        conn = db._get_conn()
        cursor = conn.cursor()
        
        # 1. 创建书
        cursor.execute('INSERT INTO books (name, total_words, is_active) VALUES (?, ?, 0)', (name, len(words)))
        book_id = cursor.lastrowid
        
        # 2. 插入单词
        for w in words:
            cursor.execute('''
            INSERT INTO words (book_id, word, phonetic, definition) 
            VALUES (?, ?, ?, ?)
            ''', (book_id, w['word'], w['phonetic'], w['definition']))
            
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'count': len(words), 'book_id': book_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/activate', methods=['POST'])
def activate_book():
    """切换当前词书"""
    book_id = request.json.get('book_id')
    db = get_db()
    conn = db._get_conn()
    cursor = conn.cursor()
    
    # 1. 取消所有激活
    cursor.execute('UPDATE books SET is_active = 0')
    
    # 2. 激活指定书
    cursor.execute('UPDATE books SET is_active = 1 WHERE id = ?', (book_id,))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/stats')
def api_stats():
    """API接口 - 返回统计数据JSON"""
    stats = calculate_statistics(user_id=session.get('user_id'), is_admin=bool(session.get('is_admin')))
    return jsonify(stats)


@app.route('/words')
def words_page():
    """单词管理页面"""
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q')
    status = request.args.get('status', type=int)
    book_id = request.args.get('book_id', type=int)
    
    db = get_db()
    
    # 获取词书信息
    if book_id:
        book = db.get_book_by_id(book_id)
        if not book:
            return "Book not found", 404
    else:
        # 如果没有指定词书，使用当前激活的词书
        book = db.get_active_book()
        if book:
            book_id = book['id']
    
    # 获取单词列表（修改为按 book_id 过滤）
    words, total = db.get_words(page=page, query=query, status=status, book_id=book_id)

    bound_ids = set()
    user_id = session.get('user_id')
    if user_id and words:
        bound_ids = db.get_user_bound_word_ids(user_id, [w['id'] for w in words])
    
    total_pages = (total + 19) // 20
    
    return render_template('words.html', 
                         words=words, 
                         current_page=page, 
                         total_pages=total_pages,
                         book=book,
                         bound_ids=bound_ids)


@app.route('/my-words')
def my_words_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('words_page'))

    page = request.args.get('page', 1, type=int)
    query = request.args.get('q')

    db = get_db()
    words, total = db.list_user_bound_words(user_id=user_id, page=page, page_size=20, query=query)
    total_pages = (total + 19) // 20

    return render_template('my_words.html', words=words, current_page=page, total_pages=total_pages)


@app.route('/api/words/<int:word_id>/binding', methods=['POST'])
def api_word_binding(word_id: int):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    action = (data.get('action') or '').strip().lower()
    db = get_db()

    if action == 'bind':
        db.bind_word_to_user(user_id, word_id)
        return jsonify({"success": True, "bound": True})
    if action == 'unbind':
        db.unbind_word_from_user(user_id, word_id)
        return jsonify({"success": True, "bound": False})

    # default: toggle
    bound = word_id in db.get_user_bound_word_ids(user_id, [word_id])
    if bound:
        db.unbind_word_from_user(user_id, word_id)
        return jsonify({"success": True, "bound": False})
    db.bind_word_to_user(user_id, word_id)
    return jsonify({"success": True, "bound": True})

@app.route('/api/words', methods=['POST'])
def add_word():
    """添加单词"""
    data = request.json
    if not data or not data.get('word') or not data.get('definition'):
        return jsonify({'error': 'Missing required fields'}), 400
        
    db = get_db()
    success = db.add_word(data)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to add word'}), 500

@app.route('/api/words')
def api_words():
    """API接口 - 返回所有单词详情"""
    db = get_db()
    all_records = db.get_all_records()
    
    # 按最后复习时间排序
    all_records.sort(key=lambda x: x.get('last_review', '1970-01-01'), reverse=True)
    
    return jsonify({
        'total': len(all_records),
        'words': all_records
    })


@app.route('/api/test-email', methods=['POST'])
def send_test_email():
    try:
        db = get_db()
        db_settings = db.get_all_settings()
        
        # 获取配置，优先数据库，其次 config.py
        smtp_server = db_settings.get('smtp_server') or getattr(config, 'SMTP_SERVER', '')
        smtp_port = int(db_settings.get('smtp_port') or getattr(config, 'SMTP_PORT', 587))
        email_from = db_settings.get('email_from') or getattr(config, 'EMAIL_FROM', '')
        email_to = db_settings.get('email_to') or getattr(config, 'EMAIL_TO', '')
        smtp_password = db_settings.get('smtp_password') or getattr(config, 'SMTP_PASSWORD', '')
        
        if not smtp_server or not email_to:
            return jsonify({'success': False, 'message': '请先配置邮件服务器和收件人'}), 400
            
        sender = EmailSender(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            email_from=email_from,
            email_to=email_to,
            use_tls=getattr(config, 'SMTP_USE_TLS', True),
            username=email_from,
            password=smtp_password
        )
        
        # 构造测试数据
        test_words = [{
            'word': 'Hello',
            'phonetic': '/həˈləʊ/',
            'definition': 'n. 你好；问候',
            'translation': '你好',
            'example': 'Hello, world!',
            'example_translation': '你好，世界！'
        }]
        
        # 注意这里的字段需要与正式发送时 main.py/WordSelectorV2.get_progress 保持一致
        test_progress = {
            'total': 100,
            'learned': 1,
            'mastered': 0,
            'progress_percent': 1.0,
            'mastery_percent': 0.0
        }
        
        # 模板路径
        template_path = str(Path(__file__).resolve().parent.parent / 'data' / 'email_template.html')
        
        server_url = db_settings.get('server_url') or getattr(config, 'SERVER_URL', '')
        success = sender.send_words_email(test_words, test_progress, template_path, server_url)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '发送失败，请检查服务器日志'}), 500
            
    except Exception as e:
        app.logger.error(f"Test email failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test-webhook', methods=['POST'])
def send_test_webhook():
    try:
        data = request.json
        webhook_url = data.get('webhook_url')
        
        if not webhook_url:
            return jsonify({'success': False, 'message': 'Webhook URL is required'}), 400
            
        notifier = Notifier(webhook_url)
        success = notifier.send_message("测试通知", "这是一条来自单词学习系统的测试消息。")
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '发送失败，请检查 URL 是否正确'}), 500
            
    except Exception as e:
        app.logger.error(f"Test webhook failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/feedback')
def feedback():
    """处理邮件中的反馈链接"""
    word_id = request.args.get('word_id', type=int)
    action = request.args.get('action')
    
    if not word_id or not action:
        return "Invalid request", 400
        
    selector = WordSelectorV2()
    
    if action == 'known':
        selector.mark_reviewed(word_id)
        message = "已标记为认识/已复习"
    elif action == 'unknown':
        selector.mark_unknown(word_id)
        message = "已标记为不认识，将重新安排复习"
    else:
        return "Unknown action", 400
        
    # 返回一个简单的HTML页面提示成功
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

if __name__ == '__main__':
    print("=" * 60)
    print("单词学习统计系统")
    print("=" * 60)
    print("访问地址: http://localhost:8080")
    print("API接口: http://localhost:8080/api/stats")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=True)

