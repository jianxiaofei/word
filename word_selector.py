# -*- coding: utf-8 -*-
"""单词选择模块"""

import json
import random
from typing import List, Dict, Set
from datetime import datetime


class WordSelector:
    """单词随机选择器，确保不重复"""
    
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.used_indices: Set[int] = set()
        self.load_history()
    
    def load_history(self):
        """加载已选择的单词历史"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.used_indices = set(data.get('used_indices', []))
        except FileNotFoundError:
            self.used_indices = set()
        except json.JSONDecodeError:
            self.used_indices = set()
    
    def save_history(self):
        """保存历史记录"""
        data = {
            'used_indices': list(self.used_indices),
            'last_update': datetime.now().isoformat()
        }
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def select_words(self, words: List[Dict], count: int) -> List[Dict]:
        """
        随机选择指定数量的未使用单词
        
        Args:
            words: 所有单词列表
            count: 需要选择的单词数量
            
        Returns:
            选中的单词列表
        """
        total_words = len(words)
        available_indices = [i for i in range(total_words) if i not in self.used_indices]
        
        # 如果可用单词不足，重置历史（重新开始）
        if len(available_indices) < count:
            self.used_indices = set()
            available_indices = list(range(total_words))
        
        # 随机选择
        selected_indices = random.sample(available_indices, count)
        selected_words = [words[i] for i in selected_indices]
        
        # 更新历史
        self.used_indices.update(selected_indices)
        self.save_history()
        
        return selected_words
    
    def get_progress(self, total_words: int) -> Dict[str, any]:
        """获取学习进度"""
        return {
            'total': total_words,
            'learned': len(self.used_indices),
            'remaining': total_words - len(self.used_indices),
            'progress_percent': round(len(self.used_indices) / total_words * 100, 2) if total_words > 0 else 0
        }
