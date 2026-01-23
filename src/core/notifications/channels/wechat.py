# -*- coding: utf-8 -*-
"""通知渠道 - 微信公众号模板消息"""

import requests
import logging
import time
from typing import Dict
from ..base import NotificationChannel, NotificationMessage


class WeChatChannel(NotificationChannel):
    """微信公众号模板消息通知渠道"""
    
    def __init__(self, config: Dict):
        """
        初始化微信渠道
        
        Args:
            config: 配置信息
                - app_id: 微信公众号 AppID
                - app_secret: 微信公众号 AppSecret
                - template_id: 模板消息ID
                - openid: 用户的 OpenID
                - url: 点击模板消息跳转的URL（可选）
        """
        super().__init__(config)
        self.access_token = None
        self.token_expires_at = 0
        self.logger = logging.getLogger(__name__)
    
    def get_channel_name(self) -> str:
        return 'wechat'
    
    def validate_config(self) -> bool:
        """验证微信配置"""
        required = ['app_id', 'app_secret', 'template_id', 'openid']
        return all(self.config.get(key) for key in required)
    
    def _get_access_token(self) -> str:
        """获取微信 Access Token（带缓存）"""
        now = time.time()
        
        # 如果 token 未过期，直接返回
        if self.access_token and now < self.token_expires_at:
            return self.access_token
        
        # 获取新 token
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.config['app_id'],
            'secret': self.config['app_secret']
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                # 提前5分钟刷新 token
                self.token_expires_at = now + result.get('expires_in', 7200) - 300
                return self.access_token
            else:
                self.logger.error(f"获取 Access Token 失败: {result}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取 Access Token 异常: {e}")
            return None
    
    def send(self, message: NotificationMessage) -> bool:
        """发送微信模板消息"""
        try:
            access_token = self._get_access_token()
            if not access_token:
                return False
            
            # 构建模板消息数据
            template_data = self._build_template_data(message)
            
            url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
            payload = {
                'touser': self.config['openid'],
                'template_id': self.config['template_id'],
                'url': self.config.get('url', ''),
                'data': template_data
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                self.logger.info(f"微信模板消息发送成功")
                return True
            else:
                self.logger.error(f"微信模板消息发送失败: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"微信发送失败: {e}")
            return False
    
    def _build_template_data(self, message: NotificationMessage) -> Dict:
        """
        构建微信模板消息数据
        
        模板格式示例：
        {{first.DATA}}
        学习内容: {{keyword1.DATA}}
        学习进度: {{keyword2.DATA}}
        {{remark.DATA}}
        """
        new_count = sum(1 for w in message.words if not w.get('is_review'))
        review_count = sum(1 for w in message.words if w.get('is_review'))
        
        progress = message.progress
        
        return {
            'first': {
                'value': message.title,
                'color': '#173177'
            },
            'keyword1': {
                'value': f"{new_count}个新词 + {review_count}个复习",
                'color': '#000000'
            },
            'keyword2': {
                'value': f"{progress.get('learned', 0)}/{progress.get('total', 0)} ({progress.get('progress_percent', 0)}%)",
                'color': '#000000'
            },
            'remark': {
                'value': '点击查看详情，记得及时标记学习效果！',
                'color': '#FF6B6B'
            }
        }
