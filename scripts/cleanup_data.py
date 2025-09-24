#!/usr/bin/env python3
"""
数据清理脚本
用于定期清理旧数据，避免数据文件过大
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCleanup:
    """数据清理类"""
    
    def __init__(self, data_dir: str = "../data"):
        """
        初始化数据清理器
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = data_dir
        self.trending_file = os.path.join(data_dir, "trending.json")
        self.processed_file = os.path.join(data_dir, "processed_trending.json")
    
    def load_data(self, filename: str) -> Optional[Dict]:
        """
        加载数据文件
        
        Args:
            filename: 文件名
            
        Returns:
            数据字典或None
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"加载文件失败 {filename}: {str(e)}")
            return None
    
    def save_data(self, data: Dict, filename: str) -> bool:
        """
        保存数据到文件
        
        Args:
            data: 数据字典
            filename: 文件名
            
        Returns:
            保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存文件失败 {filename}: {str(e)}")
            return False
    
    def cleanup_trending_data(self, max_days: int = 30, max_items: int = 200) -> bool:
        """
        清理trending.json数据
        
        Args:
            max_days: 最大保留天数
            max_items: 最大保留项目数
            
        Returns:
            清理是否成功
        """
        logger.info(f"开始清理trending数据: 保留最近{max_days}天，最多{max_items}个项目")
        
        data = self.load_data(self.trending_file)
        if not data:
            logger.warning("trending.json文件不存在或为空")
            return False
        
        if 'repositories' not in data:
            logger.warning("trending.json格式不正确")
            return False
        
        repositories = data.get('repositories', [])
        original_count = len(repositories)
        
        if original_count == 0:
            logger.info("没有数据需要清理")
            return True
        
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=max_days)
        
        # 过滤数据（这里简化处理，实际应该根据时间戳过滤）
        # 由于我们的数据没有时间戳，我们按顺序保留最新的数据
        cleaned_repositories = repositories[:max_items]
        
        # 更新元数据
        data['metadata'] = {
            "last_updated": datetime.now().isoformat(),
            "count": len(cleaned_repositories),
            "source": "GitHub Trending API",
            "cleaned": True,
            "original_count": original_count,
            "cleaned_count": len(cleaned_repositories),
            "max_days": max_days,
            "max_items": max_items
        }
        data['repositories'] = cleaned_repositories
        
        # 保存清理后的数据
        if self.save_data(data, self.trending_file):
            logger.info(f"trending数据清理完成: {original_count} -> {len(cleaned_repositories)} 个项目")
            return True
        else:
            logger.error("trending数据清理失败")
            return False
    
    def cleanup_processed_data(self, max_items: int = 50) -> bool:
        """
        清理processed_trending.json数据
        
        Args:
            max_items: 最大保留项目数
            
        Returns:
            清理是否成功
        """
        logger.info(f"开始清理processed数据: 最多保留{max_items}个项目")
        
        data = self.load_data(self.processed_file)
        if not data:
            logger.warning("processed_trending.json文件不存在或为空")
            return False
        
        if 'repositories' not in data:
            logger.warning("processed_trending.json格式不正确")
            return False
        
        repositories = data.get('repositories', [])
        original_count = len(repositories)
        
        if original_count == 0:
            logger.info("没有数据需要清理")
            return True
        
        # 保留最新的数据
        cleaned_repositories = repositories[:max_items]
        
        # 更新元数据
        data['metadata'] = {
            "last_updated": datetime.now().isoformat(),
            "count": len(cleaned_repositories),
            "source": "GitHub Trending API",
            "cleaned": True,
            "original_count": original_count,
            "cleaned_count": len(cleaned_repositories),
            "max_items": max_items
        }
        data['repositories'] = cleaned_repositories
        
        # 保存清理后的数据
        if self.save_data(data, self.processed_file):
            logger.info(f"processed数据清理完成: {original_count} -> {len(cleaned_repositories)} 个项目")
            return True
        else:
            logger.error("processed数据清理失败")
            return False
    
    def get_data_stats(self) -> Dict:
        """
        获取数据统计信息
        
        Returns:
            统计信息字典
        """
        stats = {}
        
        # trending.json统计
        trending_data = self.load_data(self.trending_file)
        if trending_data:
            stats['trending'] = {
                'file_exists': True,
                'item_count': len(trending_data.get('repositories', [])),
                'last_updated': trending_data.get('metadata', {}).get('last_updated', '未知')
            }
        else:
            stats['trending'] = {'file_exists': False}
        
        # processed_trending.json统计
        processed_data = self.load_data(self.processed_file)
        if processed_data:
            stats['processed'] = {
                'file_exists': True,
                'item_count': len(processed_data.get('repositories', [])),
                'last_updated': processed_data.get('metadata', {}).get('last_updated', '未知')
            }
        else:
            stats['processed'] = {'file_exists': False}
        
        return stats


def main():
    """主函数"""
    cleanup = DataCleanup()
    
    # 显示当前数据统计
    stats = cleanup.get_data_stats()
    logger.info("当前数据统计:")
    
    if stats['trending']['file_exists']:
        logger.info(f"  trending.json: {stats['trending']['item_count']} 个项目, 最后更新: {stats['trending']['last_updated']}")
    else:
        logger.info("  trending.json: 文件不存在")
    
    if stats['processed']['file_exists']:
        logger.info(f"  processed_trending.json: {stats['processed']['item_count']} 个项目, 最后更新: {stats['processed']['last_updated']}")
    else:
        logger.info("  processed_trending.json: 文件不存在")
    
    # 执行数据清理
    success1 = cleanup.cleanup_trending_data(max_days=30, max_items=200)
    success2 = cleanup.cleanup_processed_data(max_items=50)
    
    if success1 and success2:
        logger.info("数据清理完成")
        return 0
    else:
        logger.error("数据清理过程中出现错误")
        return 1


if __name__ == "__main__":
    exit(main())