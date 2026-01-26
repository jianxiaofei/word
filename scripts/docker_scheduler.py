# -*- coding: utf-8 -*-
import schedule
import time
import subprocess
import os
import sys
import logging
from pathlib import Path
from datetime import datetime


def setup_logging() -> logging.Logger:
    """配置日志（stdout + logs/scheduler.log）"""
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'scheduler.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("scheduler")


logger = setup_logging()

def run_task():
    """执行主程序"""
    logger.info("开始执行定时任务...")
    try:
        # 获取当前脚本所在目录的上一级目录（即项目根目录）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_script = os.path.join(project_root, 'src', 'main.py')
        
        # 执行 main.py
        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=True,
            text=True,
            env=os.environ.copy(),  # 传递环境变量
        )
        
        if result.returncode == 0:
            logger.info("任务执行成功")
            logger.info(result.stdout)
        else:
            logger.error("任务执行失败")
            logger.error(result.stderr)
            
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")

def main():
    # 从环境变量获取执行时间，默认为 07:30
    run_time = os.getenv('SCHEDULE_TIME', '07:30')
    tz = os.getenv('TZ', '')
    
    logger.info("=" * 60)
    logger.info("调度器启动")
    logger.info(f"时间: {datetime.now()}")
    if tz:
        logger.info(f"TZ: {tz}")
    logger.info(f"将于每天 {run_time} 执行: src/main.py")
    
    # 设置定时任务
    schedule.every().day.at(run_time).do(run_task)

    # 启动即跑一次：用于部署验证
    # RUN_ON_START=1 / true / yes
    run_on_start = os.getenv('RUN_ON_START', '').strip().lower() in {'1', 'true', 'yes'}
    if run_on_start:
        logger.info("RUN_ON_START 已开启：启动后立即执行一次")
        run_task()

    try:
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"下一次计划执行时间: {next_run}")
    except Exception:
        # schedule.next_run() 在极端情况下可能抛异常，不影响主循环
        pass

    logger.info("进入轮询循环（每60秒检查一次）")
    logger.info("=" * 60)
    
    # 立即运行一次（可选，用于测试，生产环境可注释）
    # if os.getenv('RUN_ON_START'):
    #     run_task()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
