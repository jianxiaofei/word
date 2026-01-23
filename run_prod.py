#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产服务器启动脚本
使用方法: python run_prod.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', '0')

if __name__ == '__main__':
    try:
        from gunicorn.app.base import BaseApplication
        
        class StandaloneApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        from src.web.app import app
        
        print("=" * 60)
        print("🚀 单词学习统计系统 - 生产服务器")
        print("=" * 60)
        
        options = {
            'bind': '0.0.0.0:5000',
            'workers': 4,
            'worker_class': 'sync',
            'timeout': 120,
            'keepalive': 5,
            'accesslog': 'logs/access.log',
            'errorlog': 'logs/error.log',
            'loglevel': 'info',
        }
        
        print(f"📍 监听地址: {options['bind']}")
        print(f"👷 Worker 数量: {options['workers']}")
        print("=" * 60)
        
        StandaloneApplication(app, options).run()
        
    except ImportError:
        print("❌ 错误: 未安装 gunicorn")
        print("请运行: pip install gunicorn")
        sys.exit(1)
