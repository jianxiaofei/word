# -*- coding: utf-8 -*-
"""RESTful API 配置和文档"""

from flask import Blueprint
from flask_restx import Api

# 创建 API Blueprint
api_blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# 创建 API 实例（Swagger UI）
api = Api(
    api_blueprint,
    version='1.0',
    title='单词学习系统 API',
    description='单词学习管理系统的 RESTful API 文档',
    doc='/doc',  # Swagger UI 路径
    authorizations={
        'sessionAuth': {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'session'
        }
    },
    security='sessionAuth'
)

# 命名空间
ns_auth = api.namespace('auth', description='用户认证')
ns_words = api.namespace('words', description='单词管理')
ns_books = api.namespace('books', description='词库管理')
ns_stats = api.namespace('stats', description='学习统计')

# 数据模型定义
from flask_restx import fields

# 登录请求
login_model = api.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码')
})

# 注册请求
register_model = api.model('Register', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码'),
    'email': fields.String(description='邮箱（可选）')
})

# 用户信息
user_model = api.model('User', {
    'user_id': fields.Integer(description='用户ID'),
    'username': fields.String(description='用户名'),
    'email': fields.String(description='邮箱')
})

# 单词模型
word_model = api.model('Word', {
    'id': fields.Integer(description='单词ID'),
    'word': fields.String(description='单词'),
    'phonetic': fields.String(description='音标'),
    'definition': fields.String(description='释义'),
    'status': fields.String(description='学习状态', enum=['new', 'learning', 'known']),
    'book_name': fields.String(description='所属词库')
})

# 词库模型
book_model = api.model('Book', {
    'id': fields.Integer(description='词库ID'),
    'name': fields.String(description='词库名称'),
    'word_count': fields.Integer(description='单词数量'),
    'created_at': fields.String(description='创建时间')
})

# 统计数据模型
stats_model = api.model('Stats', {
    'total': fields.Integer(description='总单词数'),
    'known': fields.Integer(description='已掌握'),
    'learning': fields.Integer(description='学习中'),
    'mastery_rate': fields.Float(description='掌握率(%)')
})

# 统一响应模型
success_response = api.model('SuccessResponse', {
    'success': fields.Boolean(description='是否成功'),
    'message': fields.String(description='响应消息'),
    'data': fields.Raw(description='响应数据')
})

error_response = api.model('ErrorResponse', {
    'success': fields.Boolean(description='是否成功', default=False),
    'message': fields.String(description='错误消息'),
    'error': fields.String(description='错误详情')
})
