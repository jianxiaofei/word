# -*- coding: utf-8 -*-
"""配置文件模板 - 复制为 config.py 并填入真实信息"""

import os

# 邮件配置 - 使用QQ邮箱SMTP服务
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SMTP_USERNAME = "your_email@qq.com"  # 填入你的QQ邮箱
SMTP_PASSWORD = "your_smtp_auth_code"  # 填入QQ邮箱SMTP授权码

EMAIL_FROM = "your_email@qq.com"  # 发件人（与SMTP_USERNAME相同）
EMAIL_TO = "recipient@example.com"  # 收件人邮箱

# 服务器信息（可选，仅作备注）
# SERVER_IP = "your_server_ip"

# 词库配置
WORD_FILE = os.path.join(os.path.dirname(__file__), "CET4_edited.txt")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "word_history.json")

# 每次发送的单词数量
WORDS_PER_EMAIL = 5

# 日志配置
LOG_FILE = os.path.join(os.path.dirname(__file__), "word_system.log")
