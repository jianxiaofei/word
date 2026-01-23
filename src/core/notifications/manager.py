# -*- coding: utf-8 -*-
"""通知管理器 - 统一调度多渠道通知"""

import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import NotificationChannel, NotificationMessage


class NotificationManager:
    """通知管理器 - 支持多渠道并发发送"""
    
    def __init__(self):
        self.channels: List[NotificationChannel] = []
        self.logger = logging.getLogger(__name__)
    
    def add_channel(self, channel: NotificationChannel):
        """
        添加通知渠道
        
        Args:
            channel: 通知渠道实例
        """
        if channel.validate_config():
            self.channels.append(channel)
            self.logger.info(f"✓ 已添加通知渠道: {channel.get_channel_name()}")
        else:
            self.logger.warning(f"⚠️ 渠道配置无效，跳过: {channel.get_channel_name()}")
    
    def send_daily_words(self, words: List[Dict], progress: Dict, **kwargs) -> Dict[str, bool]:
        """
        发送每日单词通知到所有已配置的渠道
        
        Args:
            words: 单词列表
            progress: 学习进度信息
            **kwargs: 其他额外数据
            
        Returns:
            Dict[str, bool]: 各渠道发送结果 {'email': True, 'telegram': False, ...}
        """
        if not self.channels:
            self.logger.warning("⚠️ 没有配置任何通知渠道")
            return {}
        
        # 构建通知消息
        new_count = sum(1 for w in words if not w.get('is_review'))
        review_count = sum(1 for w in words if w.get('is_review'))
        
        message = NotificationMessage(
            title="📚 今日单词学习",
            content=f"今日学习计划：{new_count}个新词 + {review_count}个复习",
            words=words,
            progress=progress,
            extra_data=kwargs
        )
        
        # 并发发送到所有渠道
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(self.channels)) as executor:
            future_to_channel = {
                executor.submit(self._send_to_channel, channel, message): channel
                for channel in self.channels if channel.is_enabled
            }
            
            for future in as_completed(future_to_channel):
                channel = future_to_channel[future]
                channel_name = channel.get_channel_name()
                
                try:
                    success = future.result()
                    results[channel_name] = success
                    
                    if success:
                        self.logger.info(f"✓ {channel_name} 发送成功")
                    else:
                        self.logger.error(f"✗ {channel_name} 发送失败")
                        
                except Exception as e:
                    self.logger.error(f"✗ {channel_name} 发送异常: {e}")
                    results[channel_name] = False
        
        return results
    
    def _send_to_channel(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """
        向单个渠道发送消息
        
        Args:
            channel: 通知渠道
            message: 消息对象
            
        Returns:
            bool: 是否成功
        """
        try:
            return channel.send(message)
        except Exception as e:
            self.logger.error(f"渠道 {channel.get_channel_name()} 发送失败: {e}")
            return False
    
    def get_enabled_channels(self) -> List[str]:
        """
        获取已启用的渠道列表
        
        Returns:
            List[str]: 渠道名称列表
        """
        return [ch.get_channel_name() for ch in self.channels if ch.is_enabled]
