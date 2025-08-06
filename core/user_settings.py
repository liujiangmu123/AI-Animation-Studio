"""
AI Animation Studio - 用户设置管理器
保存和恢复用户的输入内容和偏好设置
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from core.logger import get_logger

logger = get_logger("user_settings")

@dataclass
class UserSettings:
    """用户设置数据类"""
    # AI生成设置
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    enable_thinking: bool = False
    
    # 动画描述历史
    last_animation_description: str = ""
    animation_description_history: list = None
    
    # 动画类型偏好
    preferred_animation_type: str = "CSS动画"
    
    # 预览设置
    auto_inject_libraries: bool = True
    prefer_local_libraries: bool = True
    
    # 界面设置
    last_window_size: tuple = (1400, 900)
    last_window_position: tuple = (100, 100)
    splitter_sizes: list = None
    
    # 项目设置
    last_project_path: str = ""
    recent_projects: list = None
    auto_save_interval: int = 300  # 秒
    
    # 导出设置
    last_export_path: str = ""
    export_format: str = "mp4"
    export_quality: str = "high"
    
    def __post_init__(self):
        if self.animation_description_history is None:
            self.animation_description_history = []
        if self.splitter_sizes is None:
            self.splitter_sizes = [300, 800, 300]
        if self.recent_projects is None:
            self.recent_projects = []

class UserSettingsManager:
    """用户设置管理器"""
    
    def __init__(self, settings_file: Path = None):
        if settings_file is None:
            # 保存到用户目录
            user_dir = Path.home() / ".ai_animation_studio"
            user_dir.mkdir(exist_ok=True)
            settings_file = user_dir / "user_settings.json"
        
        self.settings_file = settings_file
        self.settings = UserSettings()
        self.load_settings()
    
    def load_settings(self) -> bool:
        """加载用户设置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新设置对象
                for key, value in data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)
                
                logger.info(f"用户设置已加载: {self.settings_file}")
                return True
            else:
                logger.info("用户设置文件不存在，使用默认设置")
                return False
                
        except Exception as e:
            logger.error(f"加载用户设置失败: {e}")
            return False
    
    def save_settings(self) -> bool:
        """保存用户设置"""
        try:
            # 确保目录存在
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典并保存
            data = asdict(self.settings)
            data['last_updated'] = datetime.now().isoformat()
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"用户设置已保存: {self.settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存用户设置失败: {e}")
            return False
    
    def get_api_key(self) -> str:
        """获取API Key"""
        return self.settings.gemini_api_key
    
    def set_api_key(self, api_key: str) -> bool:
        """设置API Key"""
        self.settings.gemini_api_key = api_key
        return self.save_settings()
    
    def get_model_settings(self) -> Dict[str, Any]:
        """获取模型设置"""
        return {
            "model": self.settings.gemini_model,
            "enable_thinking": self.settings.enable_thinking
        }
    
    def set_model_settings(self, model: str, enable_thinking: bool) -> bool:
        """设置模型参数"""
        self.settings.gemini_model = model
        self.settings.enable_thinking = enable_thinking
        return self.save_settings()
    
    def add_animation_description(self, description: str) -> bool:
        """添加动画描述到历史"""
        if description and description.strip():
            description = description.strip()
            
            # 移除重复项
            if description in self.settings.animation_description_history:
                self.settings.animation_description_history.remove(description)
            
            # 添加到开头
            self.settings.animation_description_history.insert(0, description)
            
            # 限制历史记录数量
            max_history = 20
            if len(self.settings.animation_description_history) > max_history:
                self.settings.animation_description_history = self.settings.animation_description_history[:max_history]
            
            # 更新最后使用的描述
            self.settings.last_animation_description = description
            
            return self.save_settings()
        return False
    
    def get_animation_description_history(self) -> list:
        """获取动画描述历史"""
        return self.settings.animation_description_history.copy()
    
    def get_last_animation_description(self) -> str:
        """获取最后使用的动画描述"""
        return self.settings.last_animation_description
    
    def set_preferred_animation_type(self, animation_type: str) -> bool:
        """设置偏好的动画类型"""
        self.settings.preferred_animation_type = animation_type
        return self.save_settings()
    
    def get_preferred_animation_type(self) -> str:
        """获取偏好的动画类型"""
        return self.settings.preferred_animation_type
    
    def set_window_geometry(self, size: tuple, position: tuple) -> bool:
        """设置窗口几何信息"""
        self.settings.last_window_size = size
        self.settings.last_window_position = position
        return self.save_settings()
    
    def get_window_geometry(self) -> Dict[str, tuple]:
        """获取窗口几何信息"""
        return {
            "size": self.settings.last_window_size,
            "position": self.settings.last_window_position
        }
    
    def set_splitter_sizes(self, sizes: list) -> bool:
        """设置分割器尺寸"""
        self.settings.splitter_sizes = sizes
        return self.save_settings()
    
    def get_splitter_sizes(self) -> list:
        """获取分割器尺寸"""
        return self.settings.splitter_sizes.copy()
    
    def add_recent_project(self, project_path: str) -> bool:
        """添加最近项目"""
        if project_path and Path(project_path).exists():
            # 移除重复项
            if project_path in self.settings.recent_projects:
                self.settings.recent_projects.remove(project_path)
            
            # 添加到开头
            self.settings.recent_projects.insert(0, project_path)
            
            # 限制数量
            max_recent = 10
            if len(self.settings.recent_projects) > max_recent:
                self.settings.recent_projects = self.settings.recent_projects[:max_recent]
            
            # 更新最后项目路径
            self.settings.last_project_path = project_path
            
            return self.save_settings()
        return False
    
    def get_recent_projects(self) -> list:
        """获取最近项目列表"""
        # 过滤不存在的项目
        valid_projects = [p for p in self.settings.recent_projects if Path(p).exists()]
        if len(valid_projects) != len(self.settings.recent_projects):
            self.settings.recent_projects = valid_projects
            self.save_settings()
        return valid_projects.copy()
    
    def set_library_preferences(self, auto_inject: bool, prefer_local: bool) -> bool:
        """设置库偏好"""
        self.settings.auto_inject_libraries = auto_inject
        self.settings.prefer_local_libraries = prefer_local
        return self.save_settings()
    
    def get_library_preferences(self) -> Dict[str, bool]:
        """获取库偏好"""
        return {
            "auto_inject": self.settings.auto_inject_libraries,
            "prefer_local": self.settings.prefer_local_libraries
        }
    
    def set_export_settings(self, export_path: str, format: str, quality: str) -> bool:
        """设置导出设置"""
        self.settings.last_export_path = export_path
        self.settings.export_format = format
        self.settings.export_quality = quality
        return self.save_settings()
    
    def get_export_settings(self) -> Dict[str, str]:
        """获取导出设置"""
        return {
            "path": self.settings.last_export_path,
            "format": self.settings.export_format,
            "quality": self.settings.export_quality
        }
    
    def reset_settings(self) -> bool:
        """重置所有设置"""
        self.settings = UserSettings()
        return self.save_settings()
    
    def export_settings(self, export_path: Path) -> bool:
        """导出设置到文件"""
        try:
            data = asdict(self.settings)
            data['exported_at'] = datetime.now().isoformat()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"设置已导出到: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出设置失败: {e}")
            return False
    
    def import_settings(self, import_path: Path) -> bool:
        """从文件导入设置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 移除导出时间戳
            data.pop('exported_at', None)
            data.pop('last_updated', None)
            
            # 更新设置
            for key, value in data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # 保存导入的设置
            success = self.save_settings()
            if success:
                logger.info(f"设置已从 {import_path} 导入")
            return success
            
        except Exception as e:
            logger.error(f"导入设置失败: {e}")
            return False
