"""
AI Animation Studio - 配置管理系统
管理应用程序的配置信息和用户设置
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from enum import Enum

class ThemeType(Enum):
    """主题类型"""
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"

class LanguageType(Enum):
    """语言类型"""
    ZH_CN = "zh_CN"
    EN_US = "en_US"

@dataclass
class CanvasConfig:
    """画布配置"""
    width: int = 1920
    height: int = 1080
    background_color: str = "#ffffff"
    grid_enabled: bool = True
    grid_size: int = 20
    rulers_enabled: bool = True
    snap_to_grid: bool = True

@dataclass
class TimelineConfig:
    """时间轴配置"""
    total_duration: float = 30.0
    fps: int = 30
    time_precision: float = 0.1
    auto_save_interval: int = 300  # 秒
    zoom_level: float = 1.0

@dataclass
class AudioConfig:
    """音频配置"""
    volume: float = 0.8
    fade_in: float = 0.5
    fade_out: float = 0.5
    waveform_color: str = "#3498db"
    show_waveform: bool = True

@dataclass
class AIConfig:
    """AI配置"""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    enable_thinking: bool = False
    api_timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    backup_model: str = "gemini-pro"

@dataclass
class ExportConfig:
    """导出配置"""
    default_format: str = "mp4"
    quality: str = "high"  # high, medium, low
    crf: int = 18
    fps: int = 60
    transparent_background: bool = False
    include_audio: bool = True
    output_directory: str = "exports"

@dataclass
class UIConfig:
    """界面配置"""
    theme: str = ThemeType.LIGHT.value
    language: str = LanguageType.ZH_CN.value
    font_size: int = 9
    window_geometry: Dict[str, int] = field(default_factory=lambda: {
        "x": 100, "y": 100, "width": 1400, "height": 900
    })
    splitter_sizes: List[int] = field(default_factory=lambda: [300, 800, 300])
    show_toolbar: bool = True
    show_statusbar: bool = True
    auto_save_layout: bool = True

@dataclass
class PreviewConfig:
    """预览配置"""
    auto_preview: bool = True
    preview_quality: str = "medium"
    show_debug_info: bool = False
    webengine_cache_enabled: bool = True
    hardware_acceleration: bool = True

class AppConfig:
    """应用程序配置管理器"""
    
    def __init__(self):
        self.canvas = CanvasConfig()
        self.timeline = TimelineConfig()
        self.audio = AudioConfig()
        self.ai = AIConfig()
        self.export = ExportConfig()
        self.ui = UIConfig()
        self.preview = PreviewConfig()
        
        # 配置文件路径
        self.config_dir = Path.home() / ".ai_animation_studio"
        self.config_file = self.config_dir / "config.json"
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "canvas": asdict(self.canvas),
            "timeline": asdict(self.timeline),
            "audio": asdict(self.audio),
            "ai": asdict(self.ai),
            "export": asdict(self.export),
            "ui": asdict(self.ui),
            "preview": asdict(self.preview)
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        if "canvas" in data:
            self.canvas = CanvasConfig(**data["canvas"])
        if "timeline" in data:
            self.timeline = TimelineConfig(**data["timeline"])
        if "audio" in data:
            self.audio = AudioConfig(**data["audio"])
        if "ai" in data:
            self.ai = AIConfig(**data["ai"])
        if "export" in data:
            self.export = ExportConfig(**data["export"])
        if "ui" in data:
            self.ui = UIConfig(**data["ui"])
        if "preview" in data:
            self.preview = PreviewConfig(**data["preview"])
    
    def save(self, file_path: Optional[Path] = None):
        """保存配置"""
        if file_path is None:
            file_path = self.config_file
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    @classmethod
    def load(cls, file_path: Optional[Path] = None) -> 'AppConfig':
        """加载配置"""
        config = cls()

        if file_path is None:
            file_path = config.config_file

        # 首先尝试加载用户配置
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config.from_dict(data)
            except Exception as e:
                print(f"加载用户配置失败: {e}")

        # 然后尝试加载项目根目录的config.json（如果存在）
        project_config = Path(__file__).parent.parent.parent / "config.json"
        if project_config.exists():
            try:
                with open(project_config, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)

                # 只覆盖AI配置中的API Key（如果项目配置中有的话）
                if "ai" in project_data and "gemini_api_key" in project_data["ai"]:
                    if project_data["ai"]["gemini_api_key"]:  # 只有非空时才覆盖
                        config.ai.gemini_api_key = project_data["ai"]["gemini_api_key"]

                print(f"已加载项目配置: {project_config}")
            except Exception as e:
                print(f"加载项目配置失败: {e}")

        return config
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.__init__()
    
    def validate(self) -> List[str]:
        """验证配置有效性"""
        errors = []
        
        # 验证画布配置
        if self.canvas.width < 100 or self.canvas.width > 7680:
            errors.append("画布宽度必须在100-7680之间")
        if self.canvas.height < 100 or self.canvas.height > 4320:
            errors.append("画布高度必须在100-4320之间")
        
        # 验证时间轴配置
        if self.timeline.total_duration <= 0:
            errors.append("动画总时长必须大于0")
        if self.timeline.fps < 1 or self.timeline.fps > 120:
            errors.append("帧率必须在1-120之间")
        
        # 验证音频配置
        if self.audio.volume < 0 or self.audio.volume > 1:
            errors.append("音量必须在0-1之间")
        
        # 验证AI配置
        if not self.ai.gemini_api_key:
            errors.append("Gemini API密钥不能为空")
        
        return errors
