"""
AI Animation Studio - 描述历史管理器
管理动画描述的历史记录、版本控制、智能推荐等功能
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from core.logger import get_logger

logger = get_logger("description_history")


class HistoryEntryType(Enum):
    """历史条目类型"""
    MANUAL_INPUT = "manual_input"
    TEMPLATE_APPLIED = "template_applied"
    AI_GENERATED = "ai_generated"
    VOICE_INPUT = "voice_input"
    OPTIMIZED = "optimized"


@dataclass
class DescriptionHistoryEntry:
    """描述历史条目"""
    id: str
    description: str
    entry_type: HistoryEntryType
    timestamp: str
    language: str
    analysis_result: Optional[Dict[str, Any]] = None
    prompt_generated: Optional[str] = None
    quality_score: Optional[float] = None
    usage_count: int = 0
    success_rate: float = 0.0
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class DescriptionHistoryManager:
    """描述历史管理器"""
    
    def __init__(self, history_file: str = "description_history.json"):
        self.history_file = history_file
        self.history_entries: List[DescriptionHistoryEntry] = []
        self.max_history_size = 1000
        self.auto_save = True
        
        # 加载历史记录
        self.load_history()
        
        logger.info(f"描述历史管理器初始化完成，加载了 {len(self.history_entries)} 条记录")
    
    def add_entry(self, description: str, entry_type: HistoryEntryType, 
                  language: str = "zh", **kwargs) -> str:
        """添加历史条目"""
        try:
            # 生成唯一ID
            entry_id = self.generate_entry_id(description)
            
            # 检查是否已存在相同描述
            existing_entry = self.find_entry_by_description(description)
            if existing_entry:
                # 更新现有条目
                existing_entry.usage_count += 1
                existing_entry.timestamp = datetime.now().isoformat()
                
                # 更新其他信息
                for key, value in kwargs.items():
                    if hasattr(existing_entry, key):
                        setattr(existing_entry, key, value)
                
                if self.auto_save:
                    self.save_history()
                
                return existing_entry.id
            
            # 创建新条目
            entry = DescriptionHistoryEntry(
                id=entry_id,
                description=description,
                entry_type=entry_type,
                timestamp=datetime.now().isoformat(),
                language=language,
                usage_count=1,
                **kwargs
            )
            
            # 添加到历史记录
            self.history_entries.insert(0, entry)  # 最新的在前面
            
            # 限制历史记录大小
            if len(self.history_entries) > self.max_history_size:
                self.history_entries = self.history_entries[:self.max_history_size]
            
            # 自动保存
            if self.auto_save:
                self.save_history()
            
            logger.info(f"添加历史条目: {entry_id}")
            
            return entry_id
            
        except Exception as e:
            logger.error(f"添加历史条目失败: {e}")
            return ""
    
    def generate_entry_id(self, description: str) -> str:
        """生成条目ID"""
        # 使用描述的哈希值和时间戳生成唯一ID
        hash_obj = hashlib.md5(description.encode('utf-8'))
        timestamp = str(int(datetime.now().timestamp() * 1000))
        return f"{hash_obj.hexdigest()[:8]}_{timestamp[-6:]}"
    
    def find_entry_by_description(self, description: str) -> Optional[DescriptionHistoryEntry]:
        """根据描述查找条目"""
        for entry in self.history_entries:
            if entry.description == description:
                return entry
        return None
    
    def find_entry_by_id(self, entry_id: str) -> Optional[DescriptionHistoryEntry]:
        """根据ID查找条目"""
        for entry in self.history_entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def get_recent_entries(self, limit: int = 20) -> List[DescriptionHistoryEntry]:
        """获取最近的条目"""
        return self.history_entries[:limit]
    
    def get_entries_by_type(self, entry_type: HistoryEntryType) -> List[DescriptionHistoryEntry]:
        """根据类型获取条目"""
        return [entry for entry in self.history_entries if entry.entry_type == entry_type]
    
    def get_entries_by_language(self, language: str) -> List[DescriptionHistoryEntry]:
        """根据语言获取条目"""
        return [entry for entry in self.history_entries if entry.language == language]
    
    def search_entries(self, query: str, search_fields: List[str] = None) -> List[DescriptionHistoryEntry]:
        """搜索条目"""
        if search_fields is None:
            search_fields = ["description", "tags"]
        
        results = []
        query_lower = query.lower()
        
        try:
            for entry in self.history_entries:
                match_found = False
                
                for field in search_fields:
                    if field == "description" and query_lower in entry.description.lower():
                        match_found = True
                        break
                    elif field == "tags" and any(query_lower in tag.lower() for tag in entry.tags):
                        match_found = True
                        break
                    elif field == "metadata" and entry.metadata:
                        metadata_str = json.dumps(entry.metadata, ensure_ascii=False).lower()
                        if query_lower in metadata_str:
                            match_found = True
                            break
                
                if match_found:
                    results.append(entry)
            
        except Exception as e:
            logger.error(f"搜索条目失败: {e}")
        
        return results
    
    def get_popular_descriptions(self, limit: int = 10) -> List[DescriptionHistoryEntry]:
        """获取热门描述"""
        try:
            # 按使用次数排序
            sorted_entries = sorted(
                self.history_entries, 
                key=lambda x: x.usage_count, 
                reverse=True
            )
            
            return sorted_entries[:limit]
            
        except Exception as e:
            logger.error(f"获取热门描述失败: {e}")
            return []
    
    def get_high_quality_descriptions(self, min_score: float = 0.7, limit: int = 10) -> List[DescriptionHistoryEntry]:
        """获取高质量描述"""
        try:
            high_quality = [
                entry for entry in self.history_entries 
                if entry.quality_score and entry.quality_score >= min_score
            ]
            
            # 按质量分数排序
            high_quality.sort(key=lambda x: x.quality_score or 0, reverse=True)
            
            return high_quality[:limit]
            
        except Exception as e:
            logger.error(f"获取高质量描述失败: {e}")
            return []
    
    def get_similar_descriptions(self, description: str, limit: int = 5) -> List[Tuple[DescriptionHistoryEntry, float]]:
        """获取相似描述"""
        try:
            similarities = []
            
            for entry in self.history_entries:
                if entry.description != description:
                    similarity = self.calculate_similarity(description, entry.description)
                    if similarity > 0.3:  # 相似度阈值
                        similarities.append((entry, similarity))
            
            # 按相似度排序
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"获取相似描述失败: {e}")
            return []
    
    def calculate_similarity(self, desc1: str, desc2: str) -> float:
        """计算描述相似度"""
        try:
            # 简化的相似度计算（基于词汇重叠）
            words1 = set(desc1.lower().split())
            words2 = set(desc2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    def update_entry_quality(self, entry_id: str, quality_score: float):
        """更新条目质量分数"""
        try:
            entry = self.find_entry_by_id(entry_id)
            if entry:
                entry.quality_score = quality_score
                
                if self.auto_save:
                    self.save_history()
                
                logger.info(f"更新条目质量分数: {entry_id} -> {quality_score}")
            
        except Exception as e:
            logger.error(f"更新条目质量失败: {e}")
    
    def update_entry_success_rate(self, entry_id: str, success: bool):
        """更新条目成功率"""
        try:
            entry = self.find_entry_by_id(entry_id)
            if entry:
                # 简化的成功率计算
                if success:
                    entry.success_rate = min(1.0, entry.success_rate + 0.1)
                else:
                    entry.success_rate = max(0.0, entry.success_rate - 0.1)
                
                if self.auto_save:
                    self.save_history()
                
                logger.info(f"更新条目成功率: {entry_id} -> {entry.success_rate}")
            
        except Exception as e:
            logger.error(f"更新条目成功率失败: {e}")
    
    def add_tags_to_entry(self, entry_id: str, tags: List[str]):
        """为条目添加标签"""
        try:
            entry = self.find_entry_by_id(entry_id)
            if entry:
                # 添加新标签，避免重复
                for tag in tags:
                    if tag not in entry.tags:
                        entry.tags.append(tag)
                
                if self.auto_save:
                    self.save_history()
                
                logger.info(f"为条目添加标签: {entry_id} -> {tags}")
            
        except Exception as e:
            logger.error(f"添加标签失败: {e}")
    
    def get_trending_tags(self, limit: int = 20) -> List[Tuple[str, int]]:
        """获取热门标签"""
        try:
            tag_counts = {}
            
            for entry in self.history_entries:
                for tag in entry.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # 按使用次数排序
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_tags[:limit]
            
        except Exception as e:
            logger.error(f"获取热门标签失败: {e}")
            return []
    
    def cleanup_old_entries(self, days: int = 30):
        """清理旧条目"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            original_count = len(self.history_entries)
            
            # 保留最近的条目和高质量条目
            self.history_entries = [
                entry for entry in self.history_entries
                if (datetime.fromisoformat(entry.timestamp) > cutoff_date or
                    entry.usage_count > 5 or
                    (entry.quality_score and entry.quality_score > 0.8))
            ]
            
            cleaned_count = original_count - len(self.history_entries)
            
            if cleaned_count > 0:
                if self.auto_save:
                    self.save_history()
                
                logger.info(f"清理了 {cleaned_count} 条旧记录")
            
        except Exception as e:
            logger.error(f"清理旧条目失败: {e}")
    
    def export_history(self, file_path: str, format: str = "json"):
        """导出历史记录"""
        try:
            if format == "json":
                export_data = {
                    "export_time": datetime.now().isoformat(),
                    "total_entries": len(self.history_entries),
                    "entries": [asdict(entry) for entry in self.history_entries]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            elif format == "csv":
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # 写入标题行
                    writer.writerow([
                        "ID", "描述", "类型", "时间", "语言", "使用次数", 
                        "成功率", "质量分数", "标签"
                    ])
                    
                    # 写入数据行
                    for entry in self.history_entries:
                        writer.writerow([
                            entry.id,
                            entry.description,
                            entry.entry_type.value,
                            entry.timestamp,
                            entry.language,
                            entry.usage_count,
                            entry.success_rate,
                            entry.quality_score or 0,
                            ",".join(entry.tags)
                        ])
            
            logger.info(f"历史记录已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"导出历史记录失败: {e}")
    
    def import_history(self, file_path: str):
        """导入历史记录"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"历史文件不存在: {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "entries" in data:
                imported_count = 0
                
                for entry_data in data["entries"]:
                    try:
                        # 转换entry_type
                        if isinstance(entry_data.get("entry_type"), str):
                            entry_data["entry_type"] = HistoryEntryType(entry_data["entry_type"])
                        
                        entry = DescriptionHistoryEntry(**entry_data)
                        
                        # 检查是否已存在
                        if not self.find_entry_by_id(entry.id):
                            self.history_entries.append(entry)
                            imported_count += 1
                        
                    except Exception as e:
                        logger.warning(f"导入条目失败: {e}")
                
                # 按时间排序
                self.history_entries.sort(key=lambda x: x.timestamp, reverse=True)
                
                if self.auto_save:
                    self.save_history()
                
                logger.info(f"成功导入 {imported_count} 条历史记录")
            
        except Exception as e:
            logger.error(f"导入历史记录失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            if not self.history_entries:
                return {}
            
            # 基本统计
            total_entries = len(self.history_entries)
            total_usage = sum(entry.usage_count for entry in self.history_entries)
            
            # 类型统计
            type_counts = {}
            for entry in self.history_entries:
                entry_type = entry.entry_type.value
                type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
            
            # 语言统计
            language_counts = {}
            for entry in self.history_entries:
                language_counts[entry.language] = language_counts.get(entry.language, 0) + 1
            
            # 质量统计
            quality_scores = [entry.quality_score for entry in self.history_entries if entry.quality_score]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # 成功率统计
            success_rates = [entry.success_rate for entry in self.history_entries]
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
            
            # 时间统计
            now = datetime.now()
            recent_entries = [
                entry for entry in self.history_entries
                if (now - datetime.fromisoformat(entry.timestamp)).days <= 7
            ]
            
            return {
                "total_entries": total_entries,
                "total_usage": total_usage,
                "type_distribution": type_counts,
                "language_distribution": language_counts,
                "average_quality": avg_quality,
                "average_success_rate": avg_success_rate,
                "recent_entries_count": len(recent_entries),
                "most_used_entry": max(self.history_entries, key=lambda x: x.usage_count) if self.history_entries else None
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def get_smart_recommendations(self, current_description: str = "", 
                                context: Dict[str, Any] = None) -> List[DescriptionHistoryEntry]:
        """获取智能推荐"""
        try:
            recommendations = []
            
            # 如果有当前描述，查找相似的
            if current_description:
                similar_entries = self.get_similar_descriptions(current_description)
                recommendations.extend([entry for entry, _ in similar_entries])
            
            # 添加高质量描述
            high_quality = self.get_high_quality_descriptions(limit=5)
            for entry in high_quality:
                if entry not in recommendations:
                    recommendations.append(entry)
            
            # 添加热门描述
            popular = self.get_popular_descriptions(limit=5)
            for entry in popular:
                if entry not in recommendations:
                    recommendations.append(entry)
            
            # 基于上下文过滤
            if context:
                language = context.get("language", "zh")
                recommendations = [
                    entry for entry in recommendations 
                    if entry.language == language
                ]
            
            return recommendations[:10]  # 返回前10个推荐
            
        except Exception as e:
            logger.error(f"获取智能推荐失败: {e}")
            return []
    
    def save_history(self):
        """保存历史记录"""
        try:
            # 准备保存数据
            save_data = {
                "version": "1.0",
                "save_time": datetime.now().isoformat(),
                "total_entries": len(self.history_entries),
                "entries": []
            }
            
            # 转换条目为字典
            for entry in self.history_entries:
                entry_dict = asdict(entry)
                entry_dict["entry_type"] = entry.entry_type.value  # 转换枚举为字符串
                save_data["entries"].append(entry_dict)
            
            # 保存到文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"历史记录已保存: {len(self.history_entries)} 条")
            
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
    
    def load_history(self):
        """加载历史记录"""
        try:
            if not os.path.exists(self.history_file):
                logger.info("历史文件不存在，创建新的历史记录")
                return
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "entries" in data:
                for entry_data in data["entries"]:
                    try:
                        # 转换entry_type
                        if isinstance(entry_data.get("entry_type"), str):
                            entry_data["entry_type"] = HistoryEntryType(entry_data["entry_type"])
                        
                        entry = DescriptionHistoryEntry(**entry_data)
                        self.history_entries.append(entry)
                        
                    except Exception as e:
                        logger.warning(f"加载历史条目失败: {e}")
                
                logger.info(f"成功加载 {len(self.history_entries)} 条历史记录")
            
        except Exception as e:
            logger.error(f"加载历史记录失败: {e}")
    
    def delete_entry(self, entry_id: str) -> bool:
        """删除条目"""
        try:
            entry = self.find_entry_by_id(entry_id)
            if entry:
                self.history_entries.remove(entry)
                
                if self.auto_save:
                    self.save_history()
                
                logger.info(f"删除历史条目: {entry_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"删除条目失败: {e}")
            return False
    
    def clear_history(self, confirm: bool = False):
        """清空历史记录"""
        try:
            if confirm:
                self.history_entries.clear()
                
                if self.auto_save:
                    self.save_history()
                
                logger.info("历史记录已清空")
            
        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")
    
    def get_entry_details(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """获取条目详情"""
        try:
            entry = self.find_entry_by_id(entry_id)
            if entry:
                return {
                    "basic_info": {
                        "id": entry.id,
                        "description": entry.description,
                        "type": entry.entry_type.value,
                        "timestamp": entry.timestamp,
                        "language": entry.language
                    },
                    "usage_info": {
                        "usage_count": entry.usage_count,
                        "success_rate": entry.success_rate,
                        "quality_score": entry.quality_score
                    },
                    "content_info": {
                        "tags": entry.tags,
                        "analysis_result": entry.analysis_result,
                        "prompt_generated": entry.prompt_generated
                    },
                    "metadata": entry.metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取条目详情失败: {e}")
            return None
