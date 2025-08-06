"""
AI Animation Studio - 应用程序配置
管理应用程序的各种配置选项
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from core.logger import get_logger

logger = get_logger("app_config")


@dataclass
class UIConfig:
    """用户界面配置"""
    theme: str = "light"                    # 主题：light, dark
    language: str = "zh_CN"                 # 语言
    window_width: int = 1200                # 窗口宽度
    window_height: int = 800                # 窗口高度
    window_maximized: bool = False          # 窗口最大化
    auto_save_interval: int = 300           # 自动保存间隔（秒）
    show_welcome_dialog: bool = True        # 显示欢迎对话框
    enable_animations: bool = True          # 启用界面动画
    font_size: int = 12                     # 字体大小
    code_editor_theme: str = "default"      # 代码编辑器主题


@dataclass
class SolutionConfig:
    """方案配置"""
    auto_evaluate: bool = True              # 自动评估方案
    auto_backup: bool = True                # 自动备份
    backup_interval_hours: int = 24         # 备份间隔（小时）
    max_solutions_cache: int = 1000         # 最大方案缓存数
    enable_version_control: bool = True     # 启用版本控制
    default_tech_stack: str = "css_animation"  # 默认技术栈
    quality_threshold: float = 0.6          # 质量阈值
    enable_performance_hints: bool = True   # 启用性能提示


@dataclass
class RecommendationConfig:
    """推荐配置"""
    enable_recommendations: bool = True     # 启用推荐
    recommendation_limit: int = 10          # 推荐数量限制
    cache_expiry_hours: int = 1            # 缓存过期时间（小时）
    track_user_behavior: bool = True        # 跟踪用户行为
    personalization_level: float = 0.7     # 个性化程度 (0-1)
    novelty_weight: float = 0.3            # 新颖性权重
    popularity_weight: float = 0.4         # 流行度权重
    quality_weight: float = 0.3            # 质量权重


@dataclass
class PerformanceConfig:
    """性能配置"""
    enable_auto_optimization: bool = True   # 启用自动优化
    optimization_aggressiveness: float = 0.5  # 优化激进程度 (0-1)
    enable_compatibility_checks: bool = True  # 启用兼容性检查
    target_browsers: list = None            # 目标浏览器
    performance_budget_ms: int = 16         # 性能预算（毫秒）
    enable_gpu_acceleration: bool = True    # 启用GPU加速优化
    
    def __post_init__(self):
        if self.target_browsers is None:
            self.target_browsers = ["chrome", "firefox", "safari", "edge"]


@dataclass
class ExportConfig:
    """导出配置"""
    default_format: str = "html"            # 默认导出格式
    include_dependencies: bool = True       # 包含依赖
    minify_code: bool = False              # 压缩代码
    add_comments: bool = True              # 添加注释
    export_directory: str = "exports"      # 导出目录
    auto_open_exported: bool = True        # 自动打开导出文件
    backup_before_export: bool = True      # 导出前备份


@dataclass
class AIConfig:
    """AI配置"""
    api_key: str = ""                      # API密钥
    model_name: str = "gemini-pro"         # 模型名称
    max_tokens: int = 2048                 # 最大令牌数
    temperature: float = 0.7               # 创意度
    enable_caching: bool = True            # 启用缓存
    cache_ttl_hours: int = 24             # 缓存生存时间
    retry_attempts: int = 3                # 重试次数
    timeout_seconds: int = 30              # 超时时间


class AppConfig:
    """应用程序配置管理器"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        
        # 默认配置
        self.ui = UIConfig()
        self.solution = SolutionConfig()
        self.recommendation = RecommendationConfig()
        self.performance = PerformanceConfig()
        self.export = ExportConfig()
        self.ai = AIConfig()
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(exist_ok=True)
        
        # 加载配置
        self.load_config()
        
        logger.info(f"应用程序配置已加载: {self.config_file}")
    
    def load_config(self):
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新配置对象
                if "ui" in config_data:
                    self.ui = UIConfig(**config_data["ui"])
                
                if "solution" in config_data:
                    self.solution = SolutionConfig(**config_data["solution"])
                
                if "recommendation" in config_data:
                    self.recommendation = RecommendationConfig(**config_data["recommendation"])
                
                if "performance" in config_data:
                    self.performance = PerformanceConfig(**config_data["performance"])
                
                if "export" in config_data:
                    self.export = ExportConfig(**config_data["export"])
                
                if "ai" in config_data:
                    self.ai = AIConfig(**config_data["ai"])
                
                logger.info("配置文件加载成功")
            else:
                # 首次运行，保存默认配置
                self.save_config()
                logger.info("创建默认配置文件")
                
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            # 使用默认配置
    
    def save_config(self):
        """保存配置"""
        try:
            config_data = {
                "ui": asdict(self.ui),
                "solution": asdict(self.solution),
                "recommendation": asdict(self.recommendation),
                "performance": asdict(self.performance),
                "export": asdict(self.export),
                "ai": asdict(self.ai)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("配置文件保存成功")
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def get_config_value(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            section_obj = getattr(self, section, None)
            if section_obj:
                return getattr(section_obj, key, default)
            return default
            
        except Exception as e:
            logger.error(f"获取配置值失败: {e}")
            return default
    
    def set_config_value(self, section: str, key: str, value: Any):
        """设置配置值"""
        try:
            section_obj = getattr(self, section, None)
            if section_obj:
                setattr(section_obj, key, value)
                self.save_config()
                logger.info(f"配置已更新: {section}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"设置配置值失败: {e}")
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        try:
            self.ui = UIConfig()
            self.solution = SolutionConfig()
            self.recommendation = RecommendationConfig()
            self.performance = PerformanceConfig()
            self.export = ExportConfig()
            self.ai = AIConfig()
            
            self.save_config()
            logger.info("配置已重置为默认值")
            
        except Exception as e:
            logger.error(f"重置配置失败: {e}")
    
    def export_config(self, export_path: str):
        """导出配置"""
        try:
            config_data = {
                "export_info": {
                    "export_time": datetime.now().isoformat(),
                    "app_version": "1.0.0"
                },
                "config": {
                    "ui": asdict(self.ui),
                    "solution": asdict(self.solution),
                    "recommendation": asdict(self.recommendation),
                    "performance": asdict(self.performance),
                    "export": asdict(self.export),
                    "ai": asdict(self.ai)
                }
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已导出到: {export_path}")
            
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
    
    def import_config(self, import_path: str):
        """导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 导入配置数据
            if "config" in config_data:
                imported_config = config_data["config"]
                
                if "ui" in imported_config:
                    self.ui = UIConfig(**imported_config["ui"])
                
                if "solution" in imported_config:
                    self.solution = SolutionConfig(**imported_config["solution"])
                
                if "recommendation" in imported_config:
                    self.recommendation = RecommendationConfig(**imported_config["recommendation"])
                
                if "performance" in imported_config:
                    self.performance = PerformanceConfig(**imported_config["performance"])
                
                if "export" in imported_config:
                    self.export = ExportConfig(**imported_config["export"])
                
                if "ai" in imported_config:
                    self.ai = AIConfig(**imported_config["ai"])
                
                self.save_config()
                logger.info(f"配置已从 {import_path} 导入")
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
    
    def validate_config(self) -> Dict[str, List[str]]:
        """验证配置"""
        issues = {
            "errors": [],
            "warnings": []
        }
        
        try:
            # 验证UI配置
            if self.ui.window_width < 800:
                issues["warnings"].append("窗口宽度过小，建议至少800px")
            
            if self.ui.window_height < 600:
                issues["warnings"].append("窗口高度过小，建议至少600px")
            
            # 验证AI配置
            if not self.ai.api_key:
                issues["warnings"].append("未设置AI API密钥，AI功能将不可用")
            
            # 验证性能配置
            if self.performance.performance_budget_ms < 8:
                issues["warnings"].append("性能预算过低，可能影响动画流畅度")
            
            # 验证导出配置
            export_dir = Path(self.export.export_directory)
            if not export_dir.exists():
                try:
                    export_dir.mkdir(parents=True, exist_ok=True)
                except:
                    issues["errors"].append(f"无法创建导出目录: {export_dir}")
            
        except Exception as e:
            issues["errors"].append(f"配置验证过程出错: {str(e)}")
        
        return issues


# 全局配置实例
app_config = AppConfig()


def get_config() -> AppConfig:
    """获取全局配置实例"""
    return app_config


def reload_config():
    """重新加载配置"""
    global app_config
    app_config.load_config()
    logger.info("配置已重新加载")
