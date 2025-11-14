# -*- coding: utf-8 -*-
"""例句获取模块 - 有道词典API"""

import requests
import logging
import re
from typing import Dict, Optional


class ExampleFetcher:
    """从有道词典获取例句"""
    
    def __init__(self):
        self.api_url = "https://dict.youdao.com/jsonapi"
        self.logger = logging.getLogger(__name__)
    
    def fetch_example(self, word: str) -> Optional[Dict[str, str]]:
        """
        获取单词的例句
        
        Args:
            word: 单词
            
        Returns:
            包含example_en和example_zh的字典，失败返回None
        """
        try:
            params = {'q': word}
            response = requests.get(self.api_url, params=params, timeout=5)
            
            if response.status_code != 200:
                self.logger.warning(f"API请求失败: {word}, status={response.status_code}")
                return None
            
            data = response.json()
            
            # 从返回数据中提取例句
            sentences = data.get('blng_sents_part', {}).get('sentence-pair', [])
            
            if not sentences:
                self.logger.debug(f"未找到例句: {word}")
                return None
            
            # 取第一个例句（通常最简单）
            first_sentence = sentences[0]
            
            # 清理HTML标签
            example_en = self._clean_html(first_sentence.get('sentence', ''))
            example_zh = first_sentence.get('sentence-translation', '')
            
            if example_en and example_zh:
                self.logger.debug(f"获取例句成功: {word}")
                return {
                    'example_en': example_en,
                    'example_zh': example_zh
                }
            
            return None
            
        except requests.Timeout:
            self.logger.warning(f"API请求超时: {word}")
            return None
        except Exception as e:
            self.logger.error(f"获取例句失败: {word}, error={str(e)}")
            return None
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        # 移除<b>等标签
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
