# -*- coding: utf-8 -*-
"""单词邮件系统 - 主程序入口"""

import sys
import logging
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.word_selector import WordSelectorV2
from core.example_fetcher import ExampleFetcher
from core.email_sender import EmailSender
from core.database import DatabaseManager
from core.notifier import Notifier
import config


def setup_logging():
    """配置日志"""
    log_dir = Path(__file__).resolve().parent.parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'word_system.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def main():
    """主函数"""
    logger = setup_logging()
    
    try:
        logger.info("=" * 60)
        logger.info("单词邮件系统启动")
        logger.info(f"时间: {datetime.now()}")
        
        # 初始化数据库管理器
        db = DatabaseManager()

        # 防止同一天发送多次邮件
        if db.has_sent_email_today():
            logger.info("今天的单词邮件已发送过，本次不再重复发送。")
            return
        
        # 获取系统设置
        daily_new_words = int(db.get_setting('daily_new_words') or 5)
        smtp_server = db.get_setting('smtp_server') or config.SMTP_SERVER
        smtp_port = int(db.get_setting('smtp_port') or config.SMTP_PORT)
        email_from = db.get_setting('email_from') or config.EMAIL_FROM
        email_to = db.get_setting('email_to') or config.EMAIL_TO
        smtp_password = db.get_setting('smtp_password') or config.SMTP_PASSWORD
        server_url = db.get_setting('server_url') or ''
        daily_review_words = int(db.get_setting('daily_review_words') or 5)
        
        # 0. 自动标记24小时前发送但未反馈的单词
        logger.info("检查需要自动标记的单词...")
        selector = WordSelectorV2()
        auto_marked = selector.auto_mark_sent_words(hours=24)
        if auto_marked > 0:
            logger.info(f"✓ 已自动标记 {auto_marked} 个超时未反馈的单词为已复习")
        
        # 1. 选择单词（新词+复习词）
        logger.info(f"正在选择单词...")
        new_words, review_words = selector.select_words(new_count=daily_new_words, review_count=daily_review_words)
        progress = selector.get_progress()
        
        # 合并新词和复习词
        selected_words = new_words + review_words
        
        if not selected_words:
            logger.info("今天没有需要学习或复习的单词。")
            return

        logger.info(f"已选择单词: 新词{len(new_words)}个 + 复习{len(review_words)}个")
        logger.info(f"新词: {[w['word'] for w in new_words]}")
        logger.info(f"复习: {[w['word'] for w in review_words]}")
        logger.info(f"学习进度: {progress['learned']}/{progress['total']} ({progress['progress_percent']}%)")
        
        # 2. 获取例句、图片、音频
        logger.info("正在获取例句、图片和音频...")
        fetcher = ExampleFetcher()
        for word_info in selected_words:
            data = fetcher.fetch_word_data(word_info['word'])
            word_info['example_en'] = data['example_en']
            word_info['example_zh'] = data['example_zh']
            word_info['image_base64'] = data['image_base64']
            word_info['audio_base64'] = data['audio_base64']
            logger.debug(f"数据: {word_info['word']} -> 例句:{bool(data['example_en'])} 图片:{bool(data['image_base64'])} 音频:{bool(data['audio_base64'])}")
        
        # 3. 发送通知（支持多渠道）
        logger.info("正在发送学习通知...")
        
        # 创建通知管理器
        from core.notifications import NotificationManager, EmailChannel, TelegramChannel, WeChatChannel
        
        notifier = NotificationManager()
        
        # 添加邮件渠道（默认启用）
        email_config = {
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'use_tls': config.SMTP_USE_TLS,
            'email_from': email_from,
            'email_to': email_to,
            'password': smtp_password,
            'server_url': server_url
        }
        notifier.add_channel(EmailChannel(email_config))
        
        # 添加 Telegram 渠道（如果已配置）
        telegram_token = db.get_setting('telegram_bot_token')
        telegram_chat_id = db.get_setting('telegram_chat_id')
        if telegram_token and telegram_chat_id:
            telegram_config = {
                'enabled': True,
                'bot_token': telegram_token,
                'chat_id': telegram_chat_id
            }
            notifier.add_channel(TelegramChannel(telegram_config))
        
        # 添加微信渠道（如果已配置）
        wechat_app_id = db.get_setting('wechat_app_id')
        wechat_secret = db.get_setting('wechat_app_secret')
        wechat_template_id = db.get_setting('wechat_template_id')
        wechat_openid = db.get_setting('wechat_openid')
        if all([wechat_app_id, wechat_secret, wechat_template_id, wechat_openid]):
            wechat_config = {
                'enabled': True,
                'app_id': wechat_app_id,
                'app_secret': wechat_secret,
                'template_id': wechat_template_id,
                'openid': wechat_openid,
                'url': server_url
            }
            notifier.add_channel(WeChatChannel(wechat_config))
        
        # 并发发送到所有渠道
        start_time = time.perf_counter()
        results = notifier.send_daily_words(
            words=selected_words,
            progress=progress,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        # 记录发送结果
        if results.get('email', False):
            logger.info(f"✓ 邮件发送成功: {email_to}")
            db.mark_email_sent_today(
                status='success',
                to_email=email_to,
                from_email=email_from,
                duration_ms=duration_ms,
                provider='smtp'
            )
            logger.info("✓ 邮件已发送，复习单词等待用户反馈（24小时内）")
            logger.info(f"  提示：请访问 {server_url} 或点击邮件中的按钮反馈学习效果")
        else:
            logger.error(f"✗ 邮件发送失败")
            db.mark_email_sent_today(
                status='failed',
                to_email=email_to,
                from_email=email_from,
                duration_ms=duration_ms,
                provider='smtp'
            )
        
        # 显示其他渠道的发送结果
        for channel, success in results.items():
            if channel != 'email':
                status = '✓ 成功' if success else '✗ 失败'
                logger.info(f"{status} {channel.capitalize()} 通知发送")
        
        # 如果所有渠道都失败，发送失败通知
        if not any(results.values()):
            webhook_url = db.get_setting('webhook_url', '')
            if webhook_url:
                notifier = Notifier(webhook_url)
                notifier.send_message("邮件发送失败", "邮件发送函数返回失败，请检查邮件配置或网络连接。")
                
            sys.exit(1)
        
        logger.info("单词邮件系统运行完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
        
        # 发送错误通知
        try:
            # 尝试获取 Webhook URL (如果数据库连接正常)
            webhook_url = None
            if 'db' in locals():
                webhook_url = db.get_setting('webhook_url', '')
            
            if webhook_url:
                notifier = Notifier(webhook_url)
                notifier.send_message("运行出错", f"错误信息：{str(e)}\n请检查服务器日志。")
        except Exception as notify_error:
            logger.error(f"发送错误通知失败: {notify_error}")

        sys.exit(1)


if __name__ == "__main__":
    main()
