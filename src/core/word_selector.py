# -*- coding: utf-8 -*-
"""单词选择模块 - 艾宾浩斯复习版"""

import random
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
from .database import DatabaseManager


class WordSelectorV2:
    """单词选择器 - 支持艾宾浩斯复习算法"""
    
    # 艾宾浩斯复习间隔（天数）
    REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]
    
    def __init__(self, history_file: str = None):
        # history_file 参数保留以兼容旧代码，但不再使用
        self.db = DatabaseManager()
    
    def load_history(self):
        """加载学习历史 - 数据库版本不再需要手动加载"""
        pass
    
    def save_history(self):
        """保存学习历史 - 数据库版本实时保存，无需手动调用"""
        pass
    
    def get_due_review_words(self) -> List[Dict]:
        """
        获取今天需要复习的单词 (V2: 直接从数据库获取)
        """
        today = datetime.now().date().isoformat()
        return self.db.get_words_for_review(today)
    
    def select_new_words(self, count: int) -> List[Dict]:
        """
        选择新单词 (V2: 直接从数据库获取)
        """
        new_words = self.db.get_new_words(count)
        
        today = datetime.now().date()
        next_review = (today + timedelta(days=self.REVIEW_INTERVALS[0])).isoformat()
        
        # 更新这些单词的状态为"学习中"
        for word in new_words:
            progress_data = {
                'first_learned': today.isoformat(),
                'last_review': today.isoformat(),
                'next_review': next_review,
                'review_count': 0,
                'mastery_level': 0
            }
            self.db.update_word_progress(word['id'], progress_data)
            
            # 合并进度数据到返回的单词对象中
            word.update(progress_data)
            word['is_review'] = False
            
        return new_words
    
    def select_words(self, new_count: int = 5, review_count: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """
        选择单词：新单词 + 复习单词
        
        Args:
            new_count: 新单词数量，默认5个
            review_count: 复习单词数量，默认5个（从所有到期单词中随机选择）
        """
        # 1. 获取所有到期的复习单词
        all_due_words = self.get_due_review_words()
        
        # 2. 如果到期单词超过限制，随机选择 review_count 个
        if len(all_due_words) > review_count:
            review_words = random.sample(all_due_words, review_count)
        else:
            review_words = all_due_words
            
        for w in review_words:
            w['is_review'] = True
            
        # 3. 获取新单词
        new_words = self.select_new_words(new_count)
        
        return new_words, review_words
    
    def mark_reviewed(self, word_id: int):
        """
        标记单词已复习，更新下次复习时间 (V2)
        """
        record = self.db.get_word_by_id(word_id)
        if not record:
            return
            
        today = datetime.now().date()
        
        # 更新复习次数和掌握等级
        new_review_count = record['review_count'] + 1
        new_mastery_level = min(new_review_count, len(self.REVIEW_INTERVALS) - 1)
        
        # 计算下次复习时间
        if new_mastery_level < len(self.REVIEW_INTERVALS):
            next_interval = self.REVIEW_INTERVALS[new_mastery_level]
            next_review = (today + timedelta(days=next_interval)).isoformat()
        else:
            # 已完成所有复习，30天后再复习
            next_review = (today + timedelta(days=30)).isoformat()
            
        self.db.update_word_progress(word_id, {
            'last_review': today.isoformat(),
            'next_review': next_review,
            'review_count': new_review_count,
            'mastery_level': new_mastery_level
        })
    
    def mark_unknown(self, word_id: int):
        """
        标记单词不认识，重置掌握等级 (V2)
        """
        record = self.db.get_word_by_id(word_id)
        if not record:
            return
            
        today = datetime.now().date()
        
        # 重置掌握等级为0，复习次数不重置（或者也可以选择重置）
        # 这里选择重置掌握等级，下次复习间隔变为1天
        new_mastery_level = 0
        
        next_interval = self.REVIEW_INTERVALS[0] # 1天后
        next_review = (today + timedelta(days=next_interval)).isoformat()
            
        self.db.update_word_progress(word_id, {
            'last_review': today.isoformat(),
            'next_review': next_review,
            'review_count': record['review_count'] + 1, # 增加一次复习记录
            'mastery_level': new_mastery_level
        })
    
    def get_progress(self) -> Dict:
        """
        获取学习进度统计 (V2)
        """
        active_book = self.db.get_active_book()
        total_words = active_book['total_words'] if active_book else 0
        
        all_records = self.db.get_all_records()
        learned = len(all_records)
        mastered = sum(1 for w in all_records if w['mastery_level'] >= 5)
        
        return {
            'total': total_words,
            'learned': learned,
            'mastered': mastered,
            'progress_percent': round(learned / total_words * 100, 2) if total_words > 0 else 0,
            'mastery_percent': round(mastered / learned * 100, 2) if learned > 0 else 0
        }
