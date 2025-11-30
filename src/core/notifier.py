# -*- coding: utf-8 -*-
import requests
import logging
import json

class Notifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)

    def send_message(self, title, content):
        """发送通知消息"""
        if not self.webhook_url:
            return False
            
        try:
            # 1. Server酱 (Turbo)
            if 'sct.ftqq.com' in self.webhook_url:
                data = {
                    'title': title,
                    'desp': content
                }
                response = requests.post(self.webhook_url, data=data, timeout=10)
                
            # 2. 钉钉机器人
            elif 'dingtalk.com' in self.webhook_url:
                data = {
                    "msgtype": "text",
                    "text": {
                        "content": f"【{title}】\n{content}"
                    }
                }
                response = requests.post(self.webhook_url, json=data, timeout=10)
                
            # 3. 企业微信机器人
            elif 'weixin.qq.com' in self.webhook_url:
                data = {
                    "msgtype": "text",
                    "text": {
                        "content": f"【{title}】\n{content}"
                    }
                }
                response = requests.post(self.webhook_url, json=data, timeout=10)
                
            # 4. 飞书机器人
            elif 'feishu.cn' in self.webhook_url:
                data = {
                    "msg_type": "text",
                    "content": {
                        "text": f"【{title}】\n{content}"
                    }
                }
                response = requests.post(self.webhook_url, json=data, timeout=10)
                
            # 5. 其他 (默认发送 JSON)
            else:
                data = {
                    "title": title,
                    "content": content
                }
                response = requests.post(self.webhook_url, json=data, timeout=10)
                
            response.raise_for_status()
            return True
            
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            return False
