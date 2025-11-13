#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词邮件系统主程序
每天发送5个随机CET4单词到指定邮箱
"""

import os
import sys
import logging
from datetime import datetime

from config import (
    SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_TO,
    WORD_FILE, HISTORY_FILE, WORDS_PER_EMAIL, LOG_FILE
)

# 导入可选的SMTP认证配置
try:
    from config import SMTP_USE_TLS, SMTP_USERNAME, SMTP_PASSWORD
except ImportError:
    SMTP_USE_TLS = False
    SMTP_USERNAME = None
    SMTP_PASSWORD = None
from word_parser import WordParser
from word_selector import WordSelector
from email_sender import EmailSender


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("单词邮件系统启动")
    logger.info(f"时间: {datetime.now()}")
    
    try:
        # 1. 解析词库
        logger.info("正在解析词库...")
        parser = WordParser(WORD_FILE)
        all_words = parser.parse()
        logger.info(f"词库加载完成，共 {len(all_words)} 个单词")
        
        # 2. 选择单词
        logger.info(f"正在随机选择 {WORDS_PER_EMAIL} 个单词...")
        selector = WordSelector(HISTORY_FILE)
        selected_words = selector.select_words(all_words, WORDS_PER_EMAIL)
        progress = selector.get_progress(len(all_words))
        
        logger.info(f"已选择单词: {[w['word'] for w in selected_words]}")
        logger.info(f"学习进度: {progress['learned']}/{progress['total']} ({progress['progress_percent']}%)")
        
        # 3. 发送邮件
        logger.info("正在发送邮件...")
        template_file = os.path.join(os.path.dirname(__file__), 'email_template.html')
        sender = EmailSender(
            SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_TO,
            use_tls=SMTP_USE_TLS,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD
        )
        
        success = sender.send_words_email(selected_words, progress, template_file)
        
        if success:
            logger.info(f"✓ 邮件发送成功: {EMAIL_TO}")
            logger.info("单词邮件系统运行完成")
        else:
            logger.error("✗ 邮件发送失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
        
        # 可选：发送错误通知邮件
        # try:
        #     sender = EmailSender(SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_TO)
        #     sender.send_error_notification(str(e))
        # except:
        #     pass
        
        sys.exit(1)
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
