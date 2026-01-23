# -*- coding: utf-8 -*-
"""通知渠道 - Telegram Bot"""

import requests
import logging
from typing import Dict
from ..base import NotificationChannel, NotificationMessage


class TelegramChannel(NotificationChannel):
    """Telegram Bot 通知渠道"""
    
    def __init__(self, config: Dict):
        """
        初始化 Telegram 渠道
        
        Args:
            config: 配置信息
                - bot_token: Telegram Bot Token
                - chat_id: 目标聊天ID（用户ID或群组ID）
                - parse_mode: 消息格式（可选：'Markdown', 'HTML'）
        """
        super().__init__(config)
        self.api_base = f"https://api.telegram.org/bot{config['bot_token']}"
        self.logger = logging.getLogger(__name__)
    
    def get_channel_name(self) -> str:
        return 'telegram'
    
    def validate_config(self) -> bool:
        """验证 Telegram 配置"""
        return bool(self.config.get('bot_token') and self.config.get('chat_id'))
    
    def send(self, message: NotificationMessage) -> bool:
        """发送 Telegram 消息"""
        try:
            # 格式化消息文本
            text = self._format_message(message)
            
            # 发送消息
            url = f"{self.api_base}/sendMessage"
            payload = {
                'chat_id': self.config['chat_id'],
                'text': text,
                'parse_mode': self.config.get('parse_mode', 'Markdown'),
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                self.logger.info(f"Telegram 消息发送成功")
                return True
            else:
                self.logger.error(f"Telegram API 返回错误: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Telegram 发送失败: {e}")
            return False
    
    def _format_message(self, message: NotificationMessage) -> str:
        """格式化 Telegram 消息"""
        lines = []
        
        # 标题
        lines.append(f"*{message.title}*")
        lines.append("")
        
        # 学习进度
        progress = message.progress
        lines.append(f"📊 *学习进度*")
        lines.append(f"总词数: {progress.get('total', 0)}")
        lines.append(f"已学习: {progress.get('learned', 0)} ({progress.get('progress_percent', 0)}%)")
        lines.append("")
        
        # 今日单词
        new_words = [w for w in message.words if not w.get('is_review')]
        review_words = [w for w in message.words if w.get('is_review')]
        
        if new_words:
            lines.append(f"🆕 *新词 ({len(new_words)}个)*")
            for i, word in enumerate(new_words[:5], 1):  # 最多显示5个
                lines.append(f"{i}. `{word['word']}` - {word.get('definition', '')[:50]}")
            if len(new_words) > 5:
                lines.append(f"   ... 还有 {len(new_words) - 5} 个")
            lines.append("")
        
        if review_words:
            lines.append(f"🔄 *复习 ({len(review_words)}个)*")
            for i, word in enumerate(review_words[:5], 1):
                lines.append(f"{i}. `{word['word']}`")
            if len(review_words) > 5:
                lines.append(f"   ... 还有 {len(review_words) - 5} 个")
            lines.append("")
        
        # 学习提示
        lines.append("💡 _记得及时标记学习效果哦！_")
        
        return '\n'.join(lines)
