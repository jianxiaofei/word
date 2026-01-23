#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发服务器启动脚本
使用方法: python run_dev.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

# 设置环境变量
os.environ.setdefault('FLASK_APP', 'src.web.app:app')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', '1')

if __name__ == '__main__':
    from flask import Flask
    from src.web.app import app
    
    print("=" * 60)
    print("🚀 单词学习统计系统 - 开发服务器")
    print("=" * 60)
    print("📍 访问地址: http://localhost:5000")
    print("📍 访问地址: http://127.0.0.1:5000")
    print("=" * 60)
    print("💡 提示: 按 CTRL+C 停止服务器")
    print("💡 调试模式已开启，代码修改会自动重载")
    print("=" * 60)
    print()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
