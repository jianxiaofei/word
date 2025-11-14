# -*- coding: utf-8 -*-
"""单词邮件系统 - 主程序入口"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.word_parser import WordParser
from core.word_selector import WordSelectorV2
from core.example_fetcher import ExampleFetcher
from core.email_sender import EmailSender
import config


def setup_logging():
    """配置日志"""
    log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'word_system.log')
    
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
        
        # 1. 解析词库
        logger.info("正在解析词库...")
        word_file = os.path.join(os.path.dirname(__file__), 'data/CET4_edited.txt')
        parser = WordParser(word_file)
        all_words = parser.parse()
        logger.info(f"词库加载完成，共 {len(all_words)} 个单词")
        
        # 2. 选择单词（新词+复习词）
        logger.info(f"正在选择单词...")
        history_file = os.path.join(os.path.dirname(__file__), 'data/word_history.json')
        selector = WordSelectorV2(history_file)
        new_words, review_words = selector.select_words(all_words, new_count=3, review_count=2)
        progress = selector.get_progress(len(all_words))
        
        # 合并新词和复习词
        selected_words = new_words + review_words
        
        logger.info(f"已选择单词: 新词{len(new_words)}个 + 复习{len(review_words)}个")
        logger.info(f"新词: {[w['word'] for w in new_words]}")
        logger.info(f"复习: {[w['word'] for w in review_words]}")
        logger.info(f"学习进度: {progress['learned']}/{progress['total']} ({progress['progress_percent']}%)")
        
        # 3. 获取例句、图片、音频
        logger.info("正在获取例句、图片和音频...")
        fetcher = ExampleFetcher()
        for word_info in selected_words:
            data = fetcher.fetch_word_data(word_info['word'])
            word_info['example_en'] = data['example_en']
            word_info['example_zh'] = data['example_zh']
            word_info['image_base64'] = data['image_base64']
            word_info['audio_base64'] = data['audio_base64']
            logger.debug(f"数据: {word_info['word']} -> 例句:{bool(data['example_en'])} 图片:{bool(data['image_base64'])} 音频:{bool(data['audio_base64'])}")
        
        # 4. 发送邮件
        logger.info("正在发送邮件...")
        template_file = os.path.join(os.path.dirname(__file__), 'data/email_template.html')
        sender = EmailSender(
            config.SMTP_SERVER, config.SMTP_PORT, config.EMAIL_FROM, config.EMAIL_TO,
            use_tls=config.SMTP_USE_TLS,
            username=config.SMTP_USERNAME,
            password=config.SMTP_PASSWORD
        )
        
        success = sender.send_words_email(selected_words, progress, template_file)
        
        if success:
            logger.info(f"✓ 邮件发送成功: {config.EMAIL_TO}")
            # 5. 保存学习记录
            selector.save_history()
            logger.info("✓ 学习记录已保存")
        else:
            logger.error(f"✗ 邮件发送失败")
            sys.exit(1)
        
        logger.info("单词邮件系统运行完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
