"""
AI Animation Studio - 项目缓存管理器
实现项目创建缓存机制和性能监控
"""

import time
import hashlib
import pickle
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.logger import get_logger
from core.data_structures import Project

logger = get_logger("project_cache")


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_before: int
    memory_after: int
    success: bool
    error_message: Optional[str] = None


class ProjectCache:
    """项目缓存管理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_size_mb: int = 100):
        self.cache_dir = cache_dir or Path.home() / ".ai_animation_studio" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_entries: Dict[str, CacheEntry] = {}
        self.performance_metrics: List[PerformanceMetrics] = []
        
        self._load_cache_index()
        logger.info(f"项目缓存初始化完成，缓存目录: {self.cache_dir}")
    
    def _generate_cache_key(self, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并排序
        key_parts = []
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _load_cache_index(self):
        """加载缓存索引"""
        try:
            index_file = self.cache_dir / "cache_index.pkl"
            if index_file.exists():
                with open(index_file, 'rb') as f:
                    self.cache_entries = pickle.load(f)
                logger.info(f"加载缓存索引，共 {len(self.cache_entries)} 个条目")
        except Exception as e:
            logger.warning(f"加载缓存索引失败: {e}")
            self.cache_entries = {}
    
    def _save_cache_index(self):
        """保存缓存索引"""
        try:
            index_file = self.cache_dir / "cache_index.pkl"
            with open(index_file, 'wb') as f:
                pickle.dump(self.cache_entries, f)
        except Exception as e:
            logger.error(f"保存缓存索引失败: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key not in self.cache_entries:
            return None
        
        entry = self.cache_entries[key]
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if not cache_file.exists():
            # 缓存文件不存在，删除索引条目
            del self.cache_entries[key]
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            # 更新访问信息
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            logger.debug(f"缓存命中: {key}")
            return data
            
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None
    
    def put(self, key: str, data: Any) -> bool:
        """存储缓存数据"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            
            # 序列化数据
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # 计算文件大小
            size_bytes = cache_file.stat().st_size
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                data=None,  # 不在内存中保存数据
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes
            )
            
            self.cache_entries[key] = entry
            
            # 检查缓存大小限制
            self._cleanup_if_needed()
            
            logger.debug(f"缓存存储: {key}, 大小: {size_bytes} 字节")
            return True
            
        except Exception as e:
            logger.error(f"存储缓存失败: {e}")
            return False
    
    def _cleanup_if_needed(self):
        """如果需要，清理缓存"""
        total_size = sum(entry.size_bytes for entry in self.cache_entries.values())
        
        if total_size > self.max_size_bytes:
            logger.info(f"缓存大小超限 ({total_size} > {self.max_size_bytes})，开始清理")
            
            # 按最后访问时间排序，删除最旧的条目
            sorted_entries = sorted(
                self.cache_entries.items(),
                key=lambda x: x[1].last_accessed
            )
            
            for key, entry in sorted_entries:
                if total_size <= self.max_size_bytes * 0.8:  # 清理到80%
                    break
                
                self._remove_cache_entry(key)
                total_size -= entry.size_bytes
                logger.debug(f"清理缓存条目: {key}")
    
    def _remove_cache_entry(self, key: str):
        """删除缓存条目"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                cache_file.unlink()
            
            if key in self.cache_entries:
                del self.cache_entries[key]
                
        except Exception as e:
            logger.error(f"删除缓存条目失败: {e}")
    
    def clear(self):
        """清空缓存"""
        try:
            for key in list(self.cache_entries.keys()):
                self._remove_cache_entry(key)
            
            self.cache_entries.clear()
            logger.info("缓存已清空")
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_size = sum(entry.size_bytes for entry in self.cache_entries.values())
        total_accesses = sum(entry.access_count for entry in self.cache_entries.values())
        
        return {
            "entry_count": len(self.cache_entries),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "usage_percent": (total_size / self.max_size_bytes) * 100,
            "total_accesses": total_accesses,
            "avg_accesses_per_entry": total_accesses / len(self.cache_entries) if self.cache_entries else 0
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetrics] = []
        logger.info("性能监控器初始化完成")
    
    def start_operation(self, operation: str) -> Dict[str, Any]:
        """开始监控操作"""
        import psutil
        import os
        
        context = {
            "operation": operation,
            "start_time": time.time(),
            "memory_before": psutil.Process(os.getpid()).memory_info().rss
        }
        
        logger.debug(f"开始监控操作: {operation}")
        return context
    
    def end_operation(self, context: Dict[str, Any], success: bool = True, 
                     error_message: Optional[str] = None):
        """结束监控操作"""
        import psutil
        import os
        
        end_time = time.time()
        memory_after = psutil.Process(os.getpid()).memory_info().rss
        
        metric = PerformanceMetrics(
            operation=context["operation"],
            start_time=context["start_time"],
            end_time=end_time,
            duration=end_time - context["start_time"],
            memory_before=context["memory_before"],
            memory_after=memory_after,
            success=success,
            error_message=error_message
        )
        
        self.metrics.append(metric)
        
        # 限制指标数量
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        logger.debug(f"操作完成: {metric.operation}, 耗时: {metric.duration:.3f}s")
        
        return metric
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """获取性能统计"""
        if operation:
            filtered_metrics = [m for m in self.metrics if m.operation == operation]
        else:
            filtered_metrics = self.metrics
        
        if not filtered_metrics:
            return {}
        
        durations = [m.duration for m in filtered_metrics]
        memory_deltas = [m.memory_after - m.memory_before for m in filtered_metrics]
        success_count = sum(1 for m in filtered_metrics if m.success)
        
        return {
            "operation": operation or "all",
            "total_operations": len(filtered_metrics),
            "success_rate": success_count / len(filtered_metrics),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "total_memory_delta": sum(memory_deltas)
        }
    
    def get_recent_metrics(self, count: int = 10) -> List[PerformanceMetrics]:
        """获取最近的性能指标"""
        return self.metrics[-count:] if self.metrics else []


# 全局实例
project_cache = ProjectCache()
performance_monitor = PerformanceMonitor()
