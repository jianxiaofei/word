# -*- coding: utf-8 -*-
"""单词解析模块 - 支持多种格式"""

import re
import csv
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class WordParser:
    """解析多种格式的词库文件"""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.words = []
    
    @staticmethod
    def detect_format(file_path: str) -> str:
        """检测文件格式"""
        suffix = Path(file_path).suffix.lower()
        if suffix in ['.xlsx', '.xls']:
            return 'excel'
        elif suffix == '.csv':
            return 'csv'
        elif suffix == '.txt':
            return 'txt'
        else:
            return 'unknown'
    
    def parse_txt(self, file_path: str) -> List[Dict[str, str]]:
        """解析 TXT 格式（原 CET4 格式）"""
        words = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和标题行
            if not line or line.startswith('大学英语') or line.startswith('(共') or len(line) == 1:
                continue
            
            # 匹配单词行：单词 [音标] 词性.释义
            word_match = re.match(r'^([a-zA-Z\-]+)\s+(\[.*?\])?\s+(.+)$', line)
            
            if word_match:
                words.append({
                    'word': word_match.group(1),
                    'phonetic': word_match.group(2) if word_match.group(2) else '',
                    'definition': word_match.group(3)
                })
        
        return words
    
    def parse_csv(self, file_path: str) -> List[Dict[str, str]]:
        """解析 CSV 格式
        期望格式: word,phonetic,definition 或 word,definition
        """
        words = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig 处理 BOM
            reader = csv.DictReader(f)
            
            for row in reader:
                # 兼容不同的列名
                word = row.get('word') or row.get('Word') or row.get('单词')
                phonetic = row.get('phonetic') or row.get('Phonetic') or row.get('音标') or ''
                definition = row.get('definition') or row.get('Definition') or row.get('释义') or row.get('meaning')
                
                if word and definition:
                    words.append({
                        'word': word.strip(),
                        'phonetic': phonetic.strip() if phonetic else '',
                        'definition': definition.strip()
                    })
        
        return words
    
    def parse_excel(self, file_path: str) -> List[Dict[str, str]]:
        """解析 Excel 格式
        期望格式: word,phonetic,definition 或 word,definition
        """
        words = []
        
        try:
            df = pd.read_excel(file_path)
            
            # 标准化列名（转小写）
            df.columns = df.columns.str.strip().str.lower()
            
            # 尝试多种列名映射
            col_mapping = {}
            for col in df.columns:
                if col in ['word', '单词']:
                    col_mapping['word'] = col
                elif col in ['phonetic', '音标']:
                    col_mapping['phonetic'] = col
                elif col in ['definition', '释义', 'meaning', '意思']:
                    col_mapping['definition'] = col
            
            if 'word' not in col_mapping or 'definition' not in col_mapping:
                raise ValueError("Excel file must contain 'word' and 'definition' columns")
            
            for _, row in df.iterrows():
                word = str(row[col_mapping['word']]).strip()
                definition = str(row[col_mapping['definition']]).strip()
                phonetic = str(row.get(col_mapping.get('phonetic', ''), '')).strip()
                
                # 跳过空行
                if word and word != 'nan' and definition and definition != 'nan':
                    words.append({
                        'word': word,
                        'phonetic': phonetic if phonetic != 'nan' else '',
                        'definition': definition
                    })
            
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
        
        return words
    
    def parse(self, file_path: str = None) -> List[Dict[str, str]]:
        """自动检测格式并解析"""
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No file path provided")
        
        file_format = self.detect_format(file_path)
        
        if file_format == 'txt':
            self.words = self.parse_txt(file_path)
        elif file_format == 'csv':
            self.words = self.parse_csv(file_path)
        elif file_format == 'excel':
            self.words = self.parse_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")
        
        return self.words
    
    def get_word_count(self) -> int:
        """获取单词总数"""
        if not self.words:
            self.parse()
        return len(self.words)
