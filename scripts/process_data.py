#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub热榜数据处理脚本

功能：清洗和格式化从API获取的热榜项目数据
作者：Auto-generated
版本：1.0.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubDataProcessor:
    """GitHub热榜数据处理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.required_fields = [
            'author', 'name', 'url', 'description', 'language', 
            'stars', 'forks', 'currentPeriodStars'
        ]
    
    def load_data(self, filename: str = "../data/trending.json") -> Optional[Dict]:
        """
        从文件加载原始数据
        
        Args:
            filename: 数据文件名
            
        Returns:
            原始数据字典或None（加载失败时）
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功加载数据文件: {filename}")
            return data
            
        except FileNotFoundError:
            logger.error(f"数据文件不存在: {filename}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"加载数据文件失败: {str(e)}")
            return None
    
    def validate_data(self, data: Dict) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 要验证的数据
            
        Returns:
            数据是否有效
        """
        if not data:
            logger.error("数据为空")
            return False
        
        # 检查必需字段
        if 'repositories' not in data:
            logger.error("数据中缺少'repositories'字段")
            return False
        
        repositories = data['repositories']
        if not isinstance(repositories, list):
            logger.error("'repositories'字段不是列表类型")
            return False
        
        # 验证每个仓库的必需字段
        for i, repo in enumerate(repositories):
            if not isinstance(repo, dict):
                logger.error(f"第{i}个仓库数据不是字典类型")
                return False
            
            for field in self.required_fields:
                if field not in repo:
                    logger.warning(f"第{i}个仓库缺少字段: {field}")
        
        logger.info(f"数据验证通过，共{len(repositories)}个仓库")
        return True
    
    def clean_repository_data(self, repo: Dict) -> Dict:
        """
        清洗单个仓库数据
        
        Args:
            repo: 原始仓库数据
            
        Returns:
            清洗后的仓库数据
        """
        cleaned = {}
        
        # 基础信息
        cleaned['author'] = repo.get('author', '').strip()
        cleaned['name'] = repo.get('name', '').strip()
        cleaned['full_name'] = f"{cleaned['author']}/{cleaned['name']}"
        cleaned['url'] = repo.get('url', '').strip()
        
        # 描述信息
        description = repo.get('description', '')
        if description:
            # 清理描述中的特殊字符和多余空格
            description = description.replace('\n', ' ').replace('\r', ' ').strip()
            # 限制描述长度
            if len(description) > 200:
                description = description[:197] + '...'
        cleaned['description'] = description
        
        # 技术信息
        cleaned['language'] = repo.get('language', 'Unknown')
        if cleaned['language'] == '':
            cleaned['language'] = 'Unknown'
        
        # 统计数据（确保为数字）
        cleaned['stars'] = self._safe_int(repo.get('stars', 0))
        cleaned['forks'] = self._safe_int(repo.get('forks', 0))
        cleaned['current_period_stars'] = self._safe_int(repo.get('currentPeriodStars', 0))
        
        # 格式化显示文本
        cleaned['stars_text'] = self._format_number(cleaned['stars'])
        cleaned['forks_text'] = self._format_number(cleaned['forks'])
        cleaned['trending_stars_text'] = self._format_number(cleaned['current_period_stars'])
        
        # 添加颜色标识（基于语言）
        cleaned['language_color'] = self._get_language_color(cleaned['language'])
        
        return cleaned
    
    def _safe_int(self, value: Any) -> int:
        """安全转换为整数"""
        try:
            if isinstance(value, str):
                # 处理带逗号的数字字符串
                value = value.replace(',', '')
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def _format_number(self, num: int) -> str:
        """格式化数字显示"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)
    
    def _get_language_color(self, language: str) -> str:
        """获取编程语言对应的颜色"""
        color_map = {
            'JavaScript': '#f1e05a',
            'Python': '#3572A5',
            'Java': '#b07219',
            'TypeScript': '#2b7489',
            'C++': '#f34b7d',
            'C': '#555555',
            'Go': '#00ADD8',
            'Rust': '#dea584',
            'Ruby': '#701516',
            'PHP': '#4F5D95',
            'Swift': '#ffac45',
            'Kotlin': '#A97BFF',
            'HTML': '#e34c26',
            'CSS': '#563d7c',
            'Vue': '#41b883',
            'React': '#61dafb',
            'Shell': '#89e051',
            'Dockerfile': '#384d54',
            'Unknown': '#6c757d'
        }
        return color_map.get(language, '#6c757d')
    
    def process_data(self, raw_data: Dict) -> Optional[Dict]:
        """
        处理完整的数据集
        
        Args:
            raw_data: 原始数据
            
        Returns:
            处理后的数据或None（处理失败时）
        """
        try:
            # 验证数据
            if not self.validate_data(raw_data):
                return None
            
            # 提取元数据
            metadata = raw_data.get('metadata', {})
            repositories = raw_data['repositories']
            
            # 处理每个仓库
            processed_repos = []
            language_stats = {}
            
            for repo in repositories:
                cleaned_repo = self.clean_repository_data(repo)
                processed_repos.append(cleaned_repo)
                
                # 统计语言分布
                lang = cleaned_repo['language']
                language_stats[lang] = language_stats.get(lang, 0) + 1
            
            # 按star数排序
            processed_repos.sort(key=lambda x: x['stars'], reverse=True)
            
            # 构建处理后的数据结构
            result = {
                'metadata': {
                    **metadata,
                    'processed_at': datetime.now().isoformat(),
                    'total_repositories': len(processed_repos),
                    'language_distribution': language_stats
                },
                'repositories': processed_repos,
                'languages': sorted(language_stats.keys())
            }
            
            logger.info(f"数据处理完成，共处理{len(processed_repos)}个仓库")
            logger.info(f"语言分布: {language_stats}")
            
            return result
            
        except Exception as e:
            logger.error(f"数据处理过程中发生异常: {str(e)}")
            return None
    
    def save_processed_data(self, processed_data: Dict, filename: str = "../data/processed_trending.json") -> bool:
        """
        保存处理后的数据
        
        Args:
            processed_data: 处理后的数据
            filename: 文件名
            
        Returns:
            保存是否成功
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"处理后的数据已保存到: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存处理后的数据失败: {str(e)}")
            return False

def main():
    """主函数"""
    # 创建数据处理器实例
    processor = GitHubDataProcessor()
    
    # 加载原始数据
    raw_data = processor.load_data()
    
    if not raw_data:
        logger.error("无法加载原始数据")
        return 1
    
    # 处理数据
    processed_data = processor.process_data(raw_data)
    
    if processed_data:
        # 保存处理后的数据
        success = processor.save_processed_data(processed_data)
        if success:
            logger.info("GitHub热榜数据处理完成！")
        else:
            logger.error("处理后的数据保存失败！")
            return 1
    else:
        logger.error("数据处理失败！")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())