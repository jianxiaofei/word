# -*- coding: utf-8 -*-
import schedule
import time
import subprocess
import os
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("scheduler")

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
            env=os.environ.copy()  # 传递环境变量
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
    
    logger.info(f"调度器启动，将在每天 {run_time} 执行任务")
    
    # 设置定时任务
    schedule.every().day.at(run_time).do(run_task)
    
    # 立即运行一次（可选，用于测试，生产环境可注释）
    # if os.getenv('RUN_ON_START'):
    #     run_task()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
