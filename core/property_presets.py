"""
AI Animation Studio - 属性预设管理器
提供属性预设的创建、管理、应用功能
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.logger import get_logger
from core.data_structures import ElementType

logger = get_logger("property_presets")


class PropertyPresetManager:
    """属性预设管理器"""
    
    def __init__(self):
        self.presets_dir = Path("presets")
        self.presets_dir.mkdir(exist_ok=True)
        
        # 预设分类
        self.categories = {
            "basic": "基本属性",
            "style": "样式属性", 
            "transform": "变换属性",
            "animation": "动画属性",
            "custom": "自定义"
        }
        
        # 内置预设
        self.builtin_presets = {}
        self.user_presets = {}
        
        self.load_builtin_presets()
        self.load_user_presets()
        
        logger.info("属性预设管理器初始化完成")
    
    def load_builtin_presets(self):
        """加载内置预设"""
        try:
            # 基本属性预设
            self.builtin_presets["basic"] = {
                "标题文本": {
                    "name": "标题文本",
                    "description": "大标题样式预设",
                    "category": "basic",
                    "element_types": [ElementType.TEXT],
                    "properties": {
                        "font_size": 32,
                        "font_weight": "bold",
                        "color": "#333333",
                        "text_align": "center"
                    }
                },
                "正文文本": {
                    "name": "正文文本", 
                    "description": "正文样式预设",
                    "category": "basic",
                    "element_types": [ElementType.TEXT],
                    "properties": {
                        "font_size": 16,
                        "font_weight": "normal",
                        "color": "#666666",
                        "line_height": 1.5
                    }
                },
                "小标题": {
                    "name": "小标题",
                    "description": "小标题样式预设", 
                    "category": "basic",
                    "element_types": [ElementType.TEXT],
                    "properties": {
                        "font_size": 24,
                        "font_weight": "600",
                        "color": "#444444",
                        "margin_bottom": 10
                    }
                }
            }
            
            # 样式属性预设
            self.builtin_presets["style"] = {
                "渐变背景": {
                    "name": "渐变背景",
                    "description": "线性渐变背景",
                    "category": "style",
                    "element_types": [ElementType.SHAPE, ElementType.TEXT],
                    "properties": {
                        "background": "linear-gradient(45deg, #ff6b6b, #4ecdc4)",
                        "border_radius": 8,
                        "padding": 20
                    }
                },
                "阴影效果": {
                    "name": "阴影效果",
                    "description": "柔和阴影效果",
                    "category": "style", 
                    "element_types": [ElementType.SHAPE, ElementType.TEXT, ElementType.IMAGE],
                    "properties": {
                        "box_shadow": "0 4px 12px rgba(0,0,0,0.15)",
                        "border_radius": 4
                    }
                },
                "霓虹效果": {
                    "name": "霓虹效果",
                    "description": "霓虹发光效果",
                    "category": "style",
                    "element_types": [ElementType.TEXT, ElementType.SHAPE],
                    "properties": {
                        "color": "#00ffff",
                        "text_shadow": "0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff",
                        "background": "transparent"
                    }
                }
            }
            
            # 变换属性预设
            self.builtin_presets["transform"] = {
                "居中对齐": {
                    "name": "居中对齐",
                    "description": "水平垂直居中",
                    "category": "transform",
                    "element_types": [ElementType.TEXT, ElementType.SHAPE, ElementType.IMAGE],
                    "properties": {
                        "position": "absolute",
                        "left": "50%",
                        "top": "50%",
                        "transform": "translate(-50%, -50%)"
                    }
                },
                "左上角": {
                    "name": "左上角",
                    "description": "定位到左上角",
                    "category": "transform",
                    "element_types": [ElementType.TEXT, ElementType.SHAPE, ElementType.IMAGE],
                    "properties": {
                        "position": "absolute",
                        "left": 20,
                        "top": 20
                    }
                },
                "右下角": {
                    "name": "右下角",
                    "description": "定位到右下角",
                    "category": "transform",
                    "element_types": [ElementType.TEXT, ElementType.SHAPE, ElementType.IMAGE],
                    "properties": {
                        "position": "absolute",
                        "right": 20,
                        "bottom": 20
                    }
                }
            }
            
            # 动画属性预设
            self.builtin_presets["animation"] = {
                "淡入效果": {
                    "name": "淡入效果",
                    "description": "渐显动画效果",
                    "category": "animation",
                    "element_types": [ElementType.TEXT, ElementType.SHAPE, ElementType.IMAGE],
                    "properties": {
                        "animation": "fadeIn 1s ease-in-out",
                        "opacity": 0,
                        "animation_fill_mode": "forwards"
                    }
                },
                "滑入效果": {
                    "name": "滑入效果", 
                    "description": "从左滑入动画",
                    "category": "animation",
                    "element_types": [ElementType.TEXT, ElementType.SHAPE, ElementType.IMAGE],
                    "properties": {
                        "animation": "slideInLeft 0.8s ease-out",
                        "transform": "translateX(-100%)",
                        "animation_fill_mode": "forwards"
                    }
                },
                "缩放效果": {
                    "name": "缩放效果",
                    "description": "缩放动画效果",
                    "category": "animation", 
                    "element_types": [ElementType.TEXT, ElementType.SHAPE, ElementType.IMAGE],
                    "properties": {
                        "animation": "zoomIn 0.6s ease-out",
                        "transform": "scale(0)",
                        "animation_fill_mode": "forwards"
                    }
                }
            }
            
            logger.info("内置预设加载完成")
            
        except Exception as e:
            logger.error(f"加载内置预设失败: {e}")
    
    def load_user_presets(self):
        """加载用户预设"""
        try:
            user_presets_file = self.presets_dir / "user_presets.json"
            
            if user_presets_file.exists():
                with open(user_presets_file, 'r', encoding='utf-8') as f:
                    self.user_presets = json.load(f)
                logger.info(f"用户预设加载完成，共 {len(self.user_presets)} 个预设")
            else:
                self.user_presets = {}
                logger.info("未找到用户预设文件，创建空预设")
                
        except Exception as e:
            logger.error(f"加载用户预设失败: {e}")
            self.user_presets = {}
    
    def save_user_presets(self):
        """保存用户预设"""
        try:
            user_presets_file = self.presets_dir / "user_presets.json"
            
            with open(user_presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_presets, f, indent=2, ensure_ascii=False)
            
            logger.info("用户预设保存完成")
            
        except Exception as e:
            logger.error(f"保存用户预设失败: {e}")
    
    def get_presets_by_category(self, category: str) -> Dict[str, Dict]:
        """根据分类获取预设"""
        presets = {}
        
        # 添加内置预设
        if category in self.builtin_presets:
            presets.update(self.builtin_presets[category])
        
        # 添加用户预设
        for preset_name, preset_data in self.user_presets.items():
            if preset_data.get("category") == category:
                presets[preset_name] = preset_data
        
        return presets
    
    def get_presets_by_element_type(self, element_type: ElementType) -> Dict[str, Dict]:
        """根据元素类型获取适用的预设"""
        applicable_presets = {}
        
        # 检查内置预设
        for category_presets in self.builtin_presets.values():
            for preset_name, preset_data in category_presets.items():
                if element_type in preset_data.get("element_types", []):
                    applicable_presets[preset_name] = preset_data
        
        # 检查用户预设
        for preset_name, preset_data in self.user_presets.items():
            if element_type in preset_data.get("element_types", []):
                applicable_presets[preset_name] = preset_data
        
        return applicable_presets
    
    def create_preset(self, name: str, description: str, category: str, 
                     element_types: List[ElementType], properties: Dict[str, Any]) -> bool:
        """创建新预设"""
        try:
            preset_data = {
                "name": name,
                "description": description,
                "category": category,
                "element_types": [et.value for et in element_types],
                "properties": properties,
                "created_at": datetime.now().isoformat(),
                "is_user_preset": True
            }
            
            self.user_presets[name] = preset_data
            self.save_user_presets()
            
            logger.info(f"预设创建成功: {name}")
            return True
            
        except Exception as e:
            logger.error(f"创建预设失败: {e}")
            return False
    
    def update_preset(self, name: str, properties: Dict[str, Any]) -> bool:
        """更新预设"""
        try:
            if name in self.user_presets:
                self.user_presets[name]["properties"].update(properties)
                self.user_presets[name]["updated_at"] = datetime.now().isoformat()
                self.save_user_presets()
                
                logger.info(f"预设更新成功: {name}")
                return True
            else:
                logger.warning(f"预设不存在: {name}")
                return False
                
        except Exception as e:
            logger.error(f"更新预设失败: {e}")
            return False
    
    def delete_preset(self, name: str) -> bool:
        """删除预设"""
        try:
            if name in self.user_presets:
                del self.user_presets[name]
                self.save_user_presets()
                
                logger.info(f"预设删除成功: {name}")
                return True
            else:
                logger.warning(f"预设不存在: {name}")
                return False
                
        except Exception as e:
            logger.error(f"删除预设失败: {e}")
            return False
    
    def get_preset(self, name: str) -> Optional[Dict]:
        """获取指定预设"""
        # 先查找用户预设
        if name in self.user_presets:
            return self.user_presets[name]
        
        # 再查找内置预设
        for category_presets in self.builtin_presets.values():
            if name in category_presets:
                return category_presets[name]
        
        return None
    
    def get_all_presets(self) -> Dict[str, Dict]:
        """获取所有预设"""
        all_presets = {}
        
        # 添加内置预设
        for category_presets in self.builtin_presets.values():
            all_presets.update(category_presets)
        
        # 添加用户预设
        all_presets.update(self.user_presets)
        
        return all_presets
    
    def search_presets(self, keyword: str) -> Dict[str, Dict]:
        """搜索预设"""
        results = {}
        keyword = keyword.lower()
        
        all_presets = self.get_all_presets()
        
        for preset_name, preset_data in all_presets.items():
            # 搜索名称和描述
            if (keyword in preset_name.lower() or 
                keyword in preset_data.get("description", "").lower()):
                results[preset_name] = preset_data
        
        return results
    
    def export_presets(self, file_path: Path, preset_names: List[str] = None) -> bool:
        """导出预设"""
        try:
            if preset_names is None:
                # 导出所有用户预设
                export_data = self.user_presets
            else:
                # 导出指定预设
                export_data = {}
                for name in preset_names:
                    preset = self.get_preset(name)
                    if preset:
                        export_data[name] = preset
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"预设导出成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出预设失败: {e}")
            return False
    
    def import_presets(self, file_path: Path, overwrite: bool = False) -> bool:
        """导入预设"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for preset_name, preset_data in import_data.items():
                if preset_name not in self.user_presets or overwrite:
                    self.user_presets[preset_name] = preset_data
                    imported_count += 1
            
            if imported_count > 0:
                self.save_user_presets()
            
            logger.info(f"预设导入成功，导入 {imported_count} 个预设")
            return True
            
        except Exception as e:
            logger.error(f"导入预设失败: {e}")
            return False
