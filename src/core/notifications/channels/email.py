# -*- coding: utf-8 -*-
"""通知渠道 - 邮件"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from jinja2 import Template
from pathlib import Path
from typing import Dict
from ..base import NotificationChannel, NotificationMessage


class EmailChannel(NotificationChannel):
    """邮件通知渠道"""
    
    def __init__(self, config: Dict):
        """
        初始化邮件渠道
        
        Args:
            config: 配置信息
                - smtp_server: SMTP服务器地址
                - smtp_port: SMTP端口
                - use_tls: 是否使用TLS
                - email_from: 发件人邮箱
                - email_to: 收件人邮箱（可以逗号分隔多个）
                - password: SMTP密码/授权码
                - server_url: 服务器地址（用于生成反馈链接）
                - template_path: 邮件模板路径（可选）
        """
        super().__init__(config)
        
        # 加载邮件模板
        template_path = config.get('template_path') or self._get_default_template_path()
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = Template(f.read())
    
    def _get_default_template_path(self) -> str:
        """获取默认邮件模板路径"""
        return str(Path(__file__).parent.parent.parent / 'data' / 'email_template.html')
    
    def get_channel_name(self) -> str:
        return 'email'
    
    def validate_config(self) -> bool:
        """验证邮件配置"""
        required = ['smtp_server', 'smtp_port', 'email_from', 'email_to', 'password']
        return all(self.config.get(key) for key in required)
    
    def send(self, message: NotificationMessage) -> bool:
        """发送邮件"""
        try:
            # 渲染HTML内容
            html_content = self.template.render(
                words=message.words,
                total_count=len(message.words),
                progress=message.progress,
                server_url=self.config.get('server_url', ''),
                date=message.extra_data.get('date', '') if message.extra_data else ''
            )
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config['email_from']
            msg['Subject'] = Header(message.title, 'utf-8')
            
            # 处理多收件人
            recipients = [r.strip() for r in self.config['email_to'].replace(';', ',').split(',')]
            msg['To'] = ', '.join(recipients)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            smtp_server = self.config['smtp_server']
            smtp_port = int(self.config['smtp_port'])
            use_tls = self.config.get('use_tls', True)
            
            if use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
            
            server.login(self.config['email_from'], self.config['password'])
            server.sendmail(self.config['email_from'], recipients, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            import logging
            logging.error(f"邮件发送失败: {e}")
            return False
