# -*- coding: utf-8 -*-
"""通知系统基础抽象类"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class NotificationMessage:
    """通知消息数据结构"""
    title: str
    content: str
    words: List[Dict]
    progress: Dict
    extra_data: Optional[Dict] = None


class NotificationChannel(ABC):
    """通知渠道抽象基类"""
    
    def __init__(self, config: Dict):
        """
        初始化通知渠道
        
        Args:
            config: 渠道配置信息
        """
        self.config = config
        self.is_enabled = config.get('enabled', True)
    
    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        """
        发送通知消息
        
        Args:
            message: 通知消息对象
            
        Returns:
            bool: 发送是否成功
        """
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """
        获取渠道名称
        
        Returns:
            str: 渠道名称（如 'email', 'wechat', 'telegram'）
        """
        pass
    
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        return True
    
    def format_words_text(self, words: List[Dict]) -> str:
        """
        格式化单词列表为文本
        
        Args:
            words: 单词列表
            
        Returns:
            str: 格式化后的文本
        """
        lines = []
        for i, word in enumerate(words, 1):
            word_text = word['word']
            phonetic = word.get('phonetic', '')
            definition = word.get('definition', '')
            is_review = word.get('is_review', False)
            
            tag = '🔄' if is_review else '🆕'
            lines.append(f"{tag} {i}. {word_text} {phonetic}")
            lines.append(f"   {definition}")
        
        return '\n'.join(lines)
