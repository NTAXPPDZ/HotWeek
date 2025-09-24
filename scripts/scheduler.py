#!/usr/bin/env python3
"""
数据更新调度脚本
用于自动化执行数据获取、处理和清理任务
"""

import os
import time
import schedule
import logging
from datetime import datetime
import subprocess
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DataScheduler:
    """数据调度器"""
    
    def __init__(self, scripts_dir: str = "."):
        """
        初始化调度器
        
        Args:
            scripts_dir: 脚本目录路径
        """
        self.scripts_dir = scripts_dir
        self.setup_directories()
    
    def setup_directories(self):
        """设置必要的目录"""
        os.makedirs("../logs", exist_ok=True)
        os.makedirs("../data", exist_ok=True)
    
    def run_script(self, script_name: str) -> bool:
        """
        运行指定的Python脚本
        
        Args:
            script_name: 脚本文件名
            
        Returns:
            运行是否成功
        """
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            logger.error(f"脚本文件不存在: {script_path}")
            return False
        
        try:
            logger.info(f"开始执行脚本: {script_name}")
            start_time = time.time()
            
            # 运行脚本
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=self.scripts_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"脚本执行成功: {script_name} (耗时: {execution_time:.2f}秒)")
                if result.stdout:
                    logger.debug(f"脚本输出:\n{result.stdout}")
                return True
            else:
                logger.error(f"脚本执行失败: {script_name} (退出码: {result.returncode})")
                if result.stderr:
                    logger.error(f"错误输出:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"脚本执行超时: {script_name}")
            return False
        except Exception as e:
            logger.error(f"执行脚本时发生异常 {script_name}: {str(e)}")
            return False
    
    def fetch_trending_data(self) -> bool:
        """获取GitHub热榜数据"""
        logger.info("=== 开始获取GitHub热榜数据 ===")
        return self.run_script("fetch_trending.py")
    
    def process_data(self) -> bool:
        """处理数据"""
        logger.info("=== 开始处理数据 ===")
        return self.run_script("process_data.py")
    
    def cleanup_data(self) -> bool:
        """清理数据"""
        logger.info("=== 开始清理数据 ===")
        return self.run_script("cleanup_data.py")
    
    def full_update(self) -> bool:
        """完整更新流程"""
        logger.info("=== 开始完整数据更新流程 ===")
        
        success_fetch = self.fetch_trending_data()
        if not success_fetch:
            logger.warning("数据获取失败，但继续尝试处理现有数据")
        
        success_process = self.process_data()
        
        # 只有在数据获取或处理成功时才进行清理
        if success_fetch or success_process:
            self.cleanup_data()
        
        overall_success = success_fetch or success_process
        
        if overall_success:
            logger.info("=== 完整数据更新流程完成 ===")
        else:
            logger.error("=== 完整数据更新流程失败 ===")
        
        return overall_success
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每小时执行一次完整更新
        schedule.every().hour.do(self.full_update)
        
        # 每天凌晨2点执行数据清理
        schedule.every().day.at("02:00").do(self.cleanup_data)
        
        logger.info("定时任务设置完成:")
        logger.info("  - 每小时执行完整数据更新")
        logger.info("  - 每天凌晨2点执行数据清理")
    
    def run_once(self):
        """运行一次完整更新"""
        logger.info("执行单次完整更新")
        return self.full_update()
    
    def run_scheduler(self):
        """运行调度器（持续运行）"""
        logger.info("启动数据调度器")
        self.setup_schedule()
        
        # 立即执行一次完整更新
        self.full_update()
        
        logger.info("调度器开始运行，按Ctrl+C停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"调度器运行异常: {str(e)}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub热榜数据调度器")
    parser.add_argument(
        "--mode", 
        choices=["once", "scheduler"], 
        default="once",
        help="运行模式: once(单次运行) 或 scheduler(持续调度)"
    )
    
    args = parser.parse_args()
    
    scheduler = DataScheduler()
    
    if args.mode == "once":
        # 单次运行模式
        success = scheduler.run_once()
        return 0 if success else 1
    else:
        # 持续调度模式
        scheduler.run_scheduler()
        return 0


if __name__ == "__main__":
    exit(main())