# -*- coding: utf-8 -*-
"""词库相关路由"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.word_service import WordService
from api.utils import login_required, get_db
import os
from werkzeug.utils import secure_filename

books_bp = Blueprint('books', __name__, url_prefix='/books')


@books_bp.route('/')
@login_required
def book_list():
    """词库列表"""
    books = get_db().get_all_books()
    
    return render_template('books.html', books=books)


@books_bp.route('/activate', methods=['POST'])
@login_required
def activate_book():
    """激活词书"""
    from flask import jsonify
    book_id = request.json.get('book_id')
    
    if not book_id:
        return jsonify({'success': False, 'message': '词书ID不能为空'}), 400
    
    try:
        word_service = WordService(get_db())
        word_service.activate_book(book_id)
        return jsonify({'success': True, 'message': '词书已激活'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@books_bp.route('/import', methods=['POST'])
@login_required
def import_book():
    """导入词库"""
    if 'file' not in request.files:
        flash('请选择文件', 'error')
        return redirect(url_for('books.book_list'))
    
    file = request.files['file']
    book_name = request.form.get('book_name', '').strip()
    
    if not file.filename:
        flash('请选择文件', 'error')
        return redirect(url_for('books.book_list'))
    
    if not book_name:
        book_name = os.path.splitext(file.filename)[0]
    
    # 保存文件
    filename = secure_filename(file.filename)
    temp_path = os.path.join('/tmp', filename)
    file.save(temp_path)
    
    try:
        word_service = WordService(get_db())
        result = word_service.import_words_from_file(temp_path, book_name)
        
        flash(f'成功导入 {result["word_count"]} 个单词', 'success')
    except Exception as e:
        flash(f'导入失败: {str(e)}', 'error')
    finally:
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return redirect(url_for('books.book_list'))


# upload_book 作为 import_book 的别名
upload_book = import_book
