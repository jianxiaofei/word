# -*- coding: utf-8 -*-
"""单词业务服务"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.database import DatabaseManager
from core.word_selector import WordSelectorV2


class WordService:
    """单词相关业务逻辑"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.selector = WordSelectorV2(db)
    
    def get_words_by_book(self, book_id: int) -> List[Dict]:
        """获取指定词库的单词列表"""
        return self.db.get_words_by_book(book_id)
    
    def get_user_words(self, user_id: int, status: Optional[str] = None) -> List[Dict]:
        """获取用户的单词（可按状态筛选）"""
        words = self.db.get_user_bound_words(user_id)
        if status:
            words = [w for w in words if w.get('status') == status]
        return words
    
    def mark_word_status(self, word_id: int, action: str) -> str:
        """标记单词状态"""
        if action == 'known':
            self.selector.mark_known(word_id)
            return "已标记为已掌握"
        elif action == 'skip':
            self.selector.mark_skip(word_id)
            return "已跳过"
        elif action == 'unknown':
            self.selector.mark_unknown(word_id)
            return "已标记为不认识，将重新安排复习"
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def import_words_from_file(self, file_path: str, book_name: str) -> Dict:
        """从文件导入单词"""
        from core.word_parser import WordParser
        
        parser = WordParser(file_path)
        words = parser.parse()
        
        # 创建词库
        book_id = self.db.create_book(book_name)
        
        # 导入单词
        count = 0
        for word_data in words:
            self.db.add_word(
                word=word_data['word'],
                phonetic=word_data.get('phonetic', ''),
                definition=word_data['definition'],
                book_id=book_id
            )
            count += 1
        
        return {
            'book_id': book_id,
            'word_count': count
        }
    
    def activate_book(self, book_id: int) -> bool:
        """激活指定词书"""
        return self.db.activate_book(book_id)
