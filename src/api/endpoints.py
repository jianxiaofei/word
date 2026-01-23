# -*- coding: utf-8 -*-
"""RESTful API 端点"""

from flask import request, session
from flask_restx import Resource
from api.rest_api import (
    ns_auth, ns_words, ns_books, ns_stats,
    login_model, register_model, user_model,
    word_model, book_model, stats_model,
    success_response, error_response
)
from api.utils import get_db, api_response
from services.auth_service import AuthService
from services.word_service import WordService
from services.stats_service import StatsService


# ============== 认证 API ==============

@ns_auth.route('/login')
class LoginAPI(Resource):
    """用户登录"""
    
    @ns_auth.expect(login_model)
    @ns_auth.response(200, 'Success', success_response)
    @ns_auth.response(401, 'Unauthorized', error_response)
    def post(self):
        """用户登录"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return api_response(False, message='缺少用户名或密码', status_code=400)
        
        auth_service = AuthService(get_db())
        user = auth_service.login(username, password)
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return api_response(True, data=user, message='登录成功')
        else:
            return api_response(False, message='用户名或密码错误', status_code=401)


@ns_auth.route('/register')
class RegisterAPI(Resource):
    """用户注册"""
    
    @ns_auth.expect(register_model)
    @ns_auth.response(201, 'Created', success_response)
    @ns_auth.response(400, 'Bad Request', error_response)
    def post(self):
        """用户注册"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        
        if not username or not password:
            return api_response(False, message='缺少用户名或密码', status_code=400)
        
        try:
            auth_service = AuthService(get_db())
            user = auth_service.register_user(username, password, email)
            return api_response(True, data=user, message='注册成功', status_code=201)
        except ValueError as e:
            return api_response(False, message=str(e), status_code=400)


@ns_auth.route('/logout')
class LogoutAPI(Resource):
    """用户登出"""
    
    @ns_auth.response(200, 'Success', success_response)
    def post(self):
        """用户登出"""
        session.clear()
        return api_response(True, message='登出成功')


@ns_auth.route('/me')
class CurrentUserAPI(Resource):
    """获取当前用户信息"""
    
    @ns_auth.response(200, 'Success', user_model)
    @ns_auth.response(401, 'Unauthorized', error_response)
    def get(self):
        """获取当前登录用户信息"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        user_id = session.get('user_id')
        user = get_db().get_user(user_id)
        
        if user:
            return api_response(True, data={
                'user_id': user['id'],
                'username': user['username'],
                'email': user.get('email', '')
            })
        else:
            return api_response(False, message='用户不存在', status_code=404)


# ============== 单词 API ==============

@ns_words.route('/')
class WordListAPI(Resource):
    """单词列表"""
    
    @ns_words.doc(params={'book_id': '词库ID（可选）', 'status': '状态筛选（可选）'})
    @ns_words.response(200, 'Success', [word_model])
    @ns_words.response(401, 'Unauthorized', error_response)
    def get(self):
        """获取单词列表"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        book_id = request.args.get('book_id', type=int)
        status = request.args.get('status')
        user_id = session.get('user_id')
        
        word_service = WordService(get_db())
        
        if book_id:
            words = word_service.get_words_by_book(book_id)
        else:
            words = word_service.get_user_words(user_id, status)
        
        return api_response(True, data=words)


@ns_words.route('/<int:word_id>')
class WordAPI(Resource):
    """单词详情"""
    
    @ns_words.response(200, 'Success', word_model)
    @ns_words.response(404, 'Not Found', error_response)
    def get(self, word_id):
        """获取单词详情"""
        word = get_db().get_word(word_id)
        
        if word:
            return api_response(True, data=word)
        else:
            return api_response(False, message='单词不存在', status_code=404)


@ns_words.route('/<int:word_id>/mark')
class MarkWordAPI(Resource):
    """标记单词状态"""
    
    @ns_words.doc(params={'action': '操作: known/skip/unknown'})
    @ns_words.response(200, 'Success', success_response)
    @ns_words.response(400, 'Bad Request', error_response)
    @ns_words.response(401, 'Unauthorized', error_response)
    def post(self, word_id):
        """标记单词状态"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        action = request.args.get('action', 'known')
        
        try:
            word_service = WordService(get_db())
            message = word_service.mark_word_status(word_id, action)
            return api_response(True, message=message)
        except ValueError as e:
            return api_response(False, message=str(e), status_code=400)


# ============== 词库 API ==============

@ns_books.route('/')
class BookListAPI(Resource):
    """词库列表"""
    
    @ns_books.response(200, 'Success', [book_model])
    @ns_books.response(401, 'Unauthorized', error_response)
    def get(self):
        """获取所有词库"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        books = get_db().get_all_books()
        return api_response(True, data=books)


@ns_books.route('/<int:book_id>')
class BookAPI(Resource):
    """词库详情"""
    
    @ns_books.response(200, 'Success', book_model)
    @ns_books.response(404, 'Not Found', error_response)
    def get(self, book_id):
        """获取词库详情"""
        book = get_db().get_book(book_id)
        
        if book:
            return api_response(True, data=book)
        else:
            return api_response(False, message='词库不存在', status_code=404)


# ============== 统计 API ==============

@ns_stats.route('/user')
class UserStatsAPI(Resource):
    """用户统计"""
    
    @ns_stats.response(200, 'Success', stats_model)
    @ns_stats.response(401, 'Unauthorized', error_response)
    def get(self):
        """获取用户学习统计"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        user_id = session.get('user_id')
        stats_service = StatsService(get_db())
        
        user_stats = stats_service.get_user_stats(user_id)
        return api_response(True, data=user_stats)


@ns_stats.route('/progress')
class ProgressAPI(Resource):
    """学习进度"""
    
    @ns_stats.doc(params={'days': '统计天数（默认30天）'})
    @ns_stats.response(200, 'Success', success_response)
    @ns_stats.response(401, 'Unauthorized', error_response)
    def get(self):
        """获取学习进度"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        user_id = session.get('user_id')
        days = request.args.get('days', default=30, type=int)
        
        stats_service = StatsService(get_db())
        progress = stats_service.get_learning_progress(user_id, days)
        
        return api_response(True, data=progress)


@ns_stats.route('/distribution')
class DistributionAPI(Resource):
    """单词分布"""
    
    @ns_stats.response(200, 'Success', success_response)
    @ns_stats.response(401, 'Unauthorized', error_response)
    def get(self):
        """获取单词分布统计"""
        if 'user_id' not in session:
            return api_response(False, message='未登录', status_code=401)
        
        user_id = session.get('user_id')
        stats_service = StatsService(get_db())
        
        distribution = stats_service.get_word_distribution(user_id)
        return api_response(True, data=distribution)
