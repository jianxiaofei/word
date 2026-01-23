# -*- coding: utf-8 -*-
"""单词学习系统 Web 应用 - 重构版"""

from flask import Flask, render_template, session, redirect, url_for, send_from_directory
import sys
import os
from pathlib import Path
from werkzeug.middleware.proxy_fix import ProxyFix

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class PrefixMiddleware:
    """支持把 Flask 挂在子路径下（例如 /word-web）
    
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
                new_path = path_info[len(script_name):]
                environ["PATH_INFO"] = new_path if new_path else "/"
        return self.wsgi_app(environ, start_response)


def create_app():
    """应用工厂"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('WEB_SECRET_KEY', 'dev-secret-key-please-change')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 文件上传限制
    
    # 中间件
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app)
    
    # 数据库连接管理
    from api.utils import close_db
    app.teardown_appcontext(close_db)
    
    # 注册蓝图
    from api.routes.auth import auth_bp
    from api.routes.words import words_bp
    from api.routes.books import books_bp
    from api.routes.stats import stats_bp
    from api.routes.settings import settings_bp
    from api.routes.users import users_bp
    
    # RESTful API (Swagger)
    from api.rest_api import api_blueprint
    import api.endpoints  # 导入所有 API 端点
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(words_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_blueprint)  # RESTful API
    
    # 主页路由
    @app.route('/')
    def index():
        """主页 - 重定向到统计页面"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return redirect(url_for('stats.statistics'))
    
    # 健康检查
    @app.route('/health')
    def health():
        """健康检查接口"""
        return {'status': 'ok'}, 200

    # 浏览器会自动请求 /favicon.ico；若没有会产生 404 日志
    @app.route('/favicon.ico')
    def favicon():
        static_dir = Path(__file__).resolve().parent / 'static'
        icon_path = static_dir / 'favicon.ico'
        if icon_path.exists():
            return send_from_directory(
                str(static_dir),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon',
            )
        return '', 204
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    print("=" * 60)
    print("单词学习统计系统")
    print("=" * 60)
    print("访问地址: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)

