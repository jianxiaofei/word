# -*- coding: utf-8 -*-
"""单词解析模块"""

import re
from typing import List, Dict


class WordParser:
    """解析CET4词库"""
    
    def __init__(self, word_file: str):
        self.word_file = word_file
        self.words = []
        
    def parse(self) -> List[Dict[str, str]]:
        """解析词库文件，返回单词列表"""
        words = []
        
        with open(self.word_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_word = None
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和标题行
            if not line or line.startswith('大学英语') or line.startswith('(共') or len(line) == 1:
                continue
            
            # 匹配单词行：单词 [音标] 词性.释义
            # 例如: abandon [əˈbændən] vt.丢弃；放弃，抛弃
            word_match = re.match(r'^([a-zA-Z\-]+)\s+(\[.*?\])?\s+(.+)$', line)
            
            if word_match:
                word = word_match.group(1)
                phonetic = word_match.group(2) if word_match.group(2) else ''
                definition = word_match.group(3)
                
                words.append({
                    'word': word,
                    'phonetic': phonetic,
                    'definition': definition
                })
        
        self.words = words
        return words
    
    def get_word_count(self) -> int:
        """获取单词总数"""
        if not self.words:
            self.parse()
        return len(self.words)
