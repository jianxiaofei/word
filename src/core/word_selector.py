# -*- coding: utf-8 -*-
"""单词选择模块 - 艾宾浩斯复习版"""

import json
import random
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta


class WordSelectorV2:
    """单词选择器 - 支持艾宾浩斯复习算法"""
    
    # 艾宾浩斯复习间隔（天数）
    REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]
    
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.words_data: Dict[str, Dict] = {}  # 单词学习数据
        self.used_indices: Set[int] = set()
        self.load_history()
    
    def load_history(self):
        """加载学习历史"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.words_data = data.get('words', {})
                self.used_indices = set(data.get('used_indices', []))
        except FileNotFoundError:
            self.words_data = {}
            self.used_indices = set()
        except json.JSONDecodeError:
            self.words_data = {}
            self.used_indices = set()
    
    def save_history(self):
        """保存学习历史"""
        data = {
            'words': self.words_data,
            'used_indices': list(self.used_indices),
            'last_update': datetime.now().isoformat()
        }
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_due_review_words(self, all_words: List[Dict]) -> List[Dict]:
        """
        获取今天需要复习的单词
        
        Returns:
            需要复习的单词列表（带索引和复习信息）
        """
        today = datetime.now().date()
        due_words = []
        
        for idx_str, word_info in self.words_data.items():
            # 检查是否到了复习时间
            next_review = datetime.fromisoformat(word_info['next_review']).date()
            
            if next_review <= today:
                idx = int(idx_str)
                if idx < len(all_words):
                    word = all_words[idx].copy()
                    word['index'] = idx
                    word['is_review'] = True
                    word['review_count'] = word_info['review_count']
                    word['mastery_level'] = word_info['mastery_level']
                    due_words.append(word)
        
        return due_words
    
    def select_new_words(self, all_words: List[Dict], count: int) -> List[Dict]:
        """
        选择新单词
        
        Args:
            all_words: 所有单词列表
            count: 需要选择的单词数量
            
        Returns:
            选中的新单词列表
        """
        total_words = len(all_words)
        available_indices = [i for i in range(total_words) if i not in self.used_indices]
        
        # 如果可用单词不足，重置历史
        if len(available_indices) < count:
            self.used_indices = set()
            self.words_data = {}
            available_indices = list(range(total_words))
        
        # 随机选择
        selected_indices = random.sample(available_indices, min(count, len(available_indices)))
        selected_words = []
        
        today = datetime.now()
        
        for idx in selected_indices:
            word = all_words[idx].copy()
            word['index'] = idx
            word['is_review'] = False
            
            # 记录新单词学习信息
            self.words_data[str(idx)] = {
                'word': word['word'],
                'first_learned': today.date().isoformat(),
                'review_count': 0,
                'last_review': today.date().isoformat(),
                'next_review': (today.date() + timedelta(days=self.REVIEW_INTERVALS[0])).isoformat(),
                'mastery_level': 0
            }
            
            self.used_indices.add(idx)
            selected_words.append(word)
        
        return selected_words
    
    def select_words(self, all_words: List[Dict], new_count: int = 3, review_count: int = 2) -> Tuple[List[Dict], List[Dict]]:
        """
        选择单词：新单词 + 复习单词
        
        Args:
            all_words: 所有单词列表
            new_count: 新单词数量
            review_count: 复习单词数量
            
        Returns:
            (新单词列表, 复习单词列表)
        """
        # 1. 获取需要复习的单词
        review_words = self.get_due_review_words(all_words)
        
        # 随机选择复习单词（如果超过需要的数量）
        if len(review_words) > review_count:
            review_words = random.sample(review_words, review_count)
        
        # 2. 如果复习单词不足，增加新单词数量补充
        actual_review = len(review_words)
        actual_new = new_count + (review_count - actual_review)
        
        # 3. 选择新单词
        new_words = self.select_new_words(all_words, actual_new)
        
        return new_words, review_words
    
    def mark_reviewed(self, word_index: int):
        """
        标记单词已复习，更新下次复习时间
        
        Args:
            word_index: 单词索引
        """
        idx_str = str(word_index)
        if idx_str not in self.words_data:
            return
        
        word_info = self.words_data[idx_str]
        today = datetime.now().date()
        
        # 更新复习次数和掌握等级
        word_info['review_count'] += 1
        word_info['last_review'] = today.isoformat()
        word_info['mastery_level'] = min(word_info['review_count'], len(self.REVIEW_INTERVALS) - 1)
        
        # 计算下次复习时间
        level = word_info['mastery_level']
        if level < len(self.REVIEW_INTERVALS):
            next_interval = self.REVIEW_INTERVALS[level]
            word_info['next_review'] = (today + timedelta(days=next_interval)).isoformat()
        else:
            # 已完成所有复习，30天后再复习
            word_info['next_review'] = (today + timedelta(days=30)).isoformat()
    
    def get_progress(self, total_words: int) -> Dict:
        """
        获取学习进度统计
        
        Returns:
            进度信息字典
        """
        learned = len(self.used_indices)
        mastered = sum(1 for w in self.words_data.values() if w['mastery_level'] >= 5)
        
        return {
            'total': total_words,
            'learned': learned,
            'mastered': mastered,
            'progress_percent': round(learned / total_words * 100, 2) if total_words > 0 else 0,
            'mastery_percent': round(mastered / learned * 100, 2) if learned > 0 else 0
        }
