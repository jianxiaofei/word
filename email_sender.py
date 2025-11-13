# -*- coding: utf-8 -*-
"""邮件发送模块"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import List, Dict
from jinja2 import Template


class EmailSender:
    """邮件发送器"""
    
    def __init__(self, smtp_server: str, smtp_port: int, email_from: str, email_to: str, 
                 use_tls: bool = False, username: str = None, password: str = None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_from = email_from
        self.email_to = email_to
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)
    
    def render_html(self, words: List[Dict], progress: Dict, template_file: str) -> str:
        """渲染HTML邮件模板"""
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        html = template.render(
            words=words,
            progress=progress,
            date=datetime.now().strftime('%Y年%m月%d日')
        )
        return html
    
    def send_words_email(self, words: List[Dict], progress: Dict, template_file: str) -> bool:
        """
        发送单词邮件
        
        Args:
            words: 单词列表
            progress: 学习进度信息
            template_file: HTML模板文件路径
            
        Returns:
            是否发送成功
        """
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from  # QQ邮箱要求From必须与登录邮箱一致
            msg['To'] = self.email_to
            msg['Subject'] = Header(
                f"📚 每日单词 - {datetime.now().strftime('%Y年%m月%d日')}", 
                'utf-8'
            )
            
            # 渲染HTML
            html_content = self.render_html(words, progress, template_file)
            
            # 添加纯文本版本（作为备选）
            text_content = self._generate_text_version(words, progress)
            
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # 发送邮件
            if self.use_tls:
                # 使用TLS加密连接
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
                server.quit()
            else:
                # 普通SMTP连接
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.send_message(msg)
            
            self.logger.info(f"邮件发送成功: {self.email_to}")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}", exc_info=True)
            return False
    
    def _generate_text_version(self, words: List[Dict], progress: Dict) -> str:
        """生成纯文本版本的邮件内容"""
        lines = [
            f"📚 每日单词学习 - {datetime.now().strftime('%Y年%m月%d日')}",
            "=" * 50,
            ""
        ]
        
        for i, word in enumerate(words, 1):
            lines.append(f"{i}. {word['word']} {word['phonetic']}")
            lines.append(f"   {word['definition']}")
            lines.append("")
        
        lines.extend([
            "=" * 50,
            f"学习进度: {progress['learned']}/{progress['total']} ({progress['progress_percent']}%)",
            "",
            "💡 坚持每天学习，积累成就未来"
        ])
        
        return "\n".join(lines)
    
    def send_error_notification(self, error_msg: str) -> bool:
        """发送错误通知邮件"""
        try:
            msg = MIMEText(
                f"单词邮件系统运行失败\n\n错误信息:\n{error_msg}\n\n时间: {datetime.now()}",
                'plain',
                'utf-8'
            )
            msg['From'] = Header(f"单词学习系统 <{self.email_from}>", 'utf-8')
            msg['To'] = Header(self.email_to, 'utf-8')
            msg['Subject'] = Header("⚠️ 单词邮件系统错误通知", 'utf-8')
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.send_message(msg)
            
            self.logger.info("错误通知邮件发送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"错误通知邮件发送失败: {str(e)}", exc_info=True)
            return False
