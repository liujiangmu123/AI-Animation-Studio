"""
AI Animation Studio - 项目模板管理器
管理和应用项目模板
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from core.logger import get_logger
from core.project_cache import project_cache, performance_monitor

logger = get_logger("template_manager")

@dataclass
class ProjectTemplate:
    """项目模板数据结构"""
    id: str
    name: str
    description: str
    category: str
    author: str
    version: str
    created_time: str
    tags: List[str]

    # 模板配置
    config: Dict[str, Any]

    # 预设元素
    elements: List[Dict[str, Any]]

    # 时间段配置
    segments: List[Dict[str, Any]]

    # 样式预设
    styles: Dict[str, Any]

    # 动画预设
    animations: Dict[str, Any]

    # 缩略图路径
    thumbnail: Optional[str] = None

    # 示例HTML
    example_html: Optional[str] = None

    # 评分推荐系统
    rating: float = 0.0  # 平均评分 (0-5)
    rating_count: int = 0  # 评分人数
    download_count: int = 0  # 下载次数
    difficulty: str = "初级"  # 难度等级: 初级、中级、高级
    duration: float = 30.0  # 预计时长(秒)
    tech_stack: str = "CSS"  # 技术栈
    features: List[str] = None  # 特性列表

    def __post_init__(self):
        """初始化后处理"""
        if self.features is None:
            self.features = []

    @property
    def popularity_score(self) -> float:
        """计算流行度评分"""
        # 综合评分、下载量、评分人数计算流行度
        if self.rating_count == 0:
            return 0.0

        rating_weight = 0.4
        download_weight = 0.3
        count_weight = 0.3

        # 标准化评分 (0-5 -> 0-1)
        normalized_rating = self.rating / 5.0

        # 标准化下载量 (使用对数缩放)
        normalized_downloads = min(1.0, self.download_count / 1000.0)

        # 标准化评分人数 (使用对数缩放)
        normalized_count = min(1.0, self.rating_count / 100.0)

        return (normalized_rating * rating_weight +
                normalized_downloads * download_weight +
                normalized_count * count_weight)

    def add_rating(self, new_rating: float):
        """添加新评分"""
        if not 0 <= new_rating <= 5:
            raise ValueError("评分必须在0-5之间")

        total_score = self.rating * self.rating_count
        self.rating_count += 1
        self.rating = (total_score + new_rating) / self.rating_count

    def increment_download(self):
        """增加下载次数"""
        self.download_count += 1

class TemplateManager:
    """项目模板管理器"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "assets" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, ProjectTemplate] = {}
        self.load_templates()
        self.create_default_templates()
        
        # 启动预加载策略
        self._preload_popular_templates()

        logger.info("项目模板管理器初始化完成")
    
    def load_templates(self):
        """加载所有模板 - 带缓存优化"""
        perf_context = performance_monitor.start_operation("load_templates")

        try:
            self.templates.clear()

            # 检查缓存
            cache_key = project_cache._generate_cache_key(
                operation="load_templates",
                templates_dir=str(self.templates_dir),
                timestamp=int(self.templates_dir.stat().st_mtime) if self.templates_dir.exists() else 0
            )

            cached_templates = project_cache.get(cache_key)
            if cached_templates:
                self.templates = cached_templates
                logger.info(f"从缓存加载 {len(self.templates)} 个模板")
                performance_monitor.end_operation(perf_context, success=True)
                return

            # 从文件系统加载
            for template_dir in self.templates_dir.iterdir():
                if template_dir.is_dir():
                    template_file = template_dir / "template.json"
                    if template_file.exists():
                        template = self.load_template_from_file(template_file)
                        if template:
                            self.templates[template.id] = template

            # 缓存结果
            project_cache.put(cache_key, self.templates.copy())

            logger.info(f"已加载 {len(self.templates)} 个模板")
            performance_monitor.end_operation(perf_context, success=True)

        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            performance_monitor.end_operation(perf_context, success=False, error_message=str(e))
    
    def load_template_from_file(self, file_path: Path) -> Optional[ProjectTemplate]:
        """从文件加载模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载示例HTML（如果存在）
            html_file = file_path.parent / "example.html"
            example_html = None
            if html_file.exists():
                example_html = html_file.read_text(encoding='utf-8')
            
            # 设置缩略图路径
            thumbnail_file = file_path.parent / "thumbnail.png"
            thumbnail = str(thumbnail_file) if thumbnail_file.exists() else None
            
            template = ProjectTemplate(
                **data,
                thumbnail=thumbnail,
                example_html=example_html
            )
            
            return template
            
        except Exception as e:
            logger.error(f"加载模板文件失败 {file_path}: {e}")
            return None
    
    def create_default_templates(self):
        """创建默认模板"""
        default_templates = [
            {
                "id": "simple_presentation",
                "name": "简单演示",
                "description": "适合产品介绍和简单演示的模板",
                "category": "演示",
                "author": "AI Animation Studio",
                "version": "1.0",
                "tags": ["简单", "演示", "产品"],
                "rating": 4.2,
                "rating_count": 156,
                "download_count": 1240,
                "difficulty": "初级",
                "duration": 30.0,
                "tech_stack": "CSS",
                "features": ["响应式", "易定制", "快速加载"],
                "config": {
                    "duration": 30.0,
                    "fps": 30,
                    "resolution": {"width": 1920, "height": 1080},
                    "background": {"type": "gradient", "colors": ["#667eea", "#764ba2"]}
                },
                "elements": [
                    {
                        "type": "text",
                        "id": "title",
                        "content": "产品标题",
                        "style": {
                            "fontSize": "48px",
                            "fontWeight": "bold",
                            "color": "#ffffff",
                            "textAlign": "center"
                        },
                        "position": {"x": 960, "y": 300}
                    },
                    {
                        "type": "text",
                        "id": "subtitle",
                        "content": "产品副标题",
                        "style": {
                            "fontSize": "24px",
                            "color": "#f0f0f0",
                            "textAlign": "center"
                        },
                        "position": {"x": 960, "y": 400}
                    }
                ],
                "segments": [
                    {
                        "id": "intro",
                        "name": "介绍",
                        "start_time": 0.0,
                        "duration": 5.0,
                        "description": "标题淡入"
                    },
                    {
                        "id": "content",
                        "name": "内容",
                        "start_time": 5.0,
                        "duration": 20.0,
                        "description": "主要内容展示"
                    },
                    {
                        "id": "outro",
                        "name": "结尾",
                        "start_time": 25.0,
                        "duration": 5.0,
                        "description": "结尾动画"
                    }
                ],
                "styles": {
                    "primary_color": "#667eea",
                    "secondary_color": "#764ba2",
                    "text_color": "#ffffff",
                    "accent_color": "#ffd700"
                },
                "animations": {
                    "fade_in": {
                        "type": "opacity",
                        "from": 0,
                        "to": 1,
                        "duration": 1.0,
                        "easing": "ease-in-out"
                    },
                    "slide_up": {
                        "type": "transform",
                        "from": {"translateY": 50},
                        "to": {"translateY": 0},
                        "duration": 0.8,
                        "easing": "ease-out"
                    }
                }
            },
            {
                "id": "tech_showcase",
                "name": "科技展示",
                "description": "适合科技产品和数据展示的模板",
                "category": "科技",
                "author": "AI Animation Studio",
                "version": "1.0",
                "tags": ["科技", "数据", "现代"],
                "rating": 4.7,
                "rating_count": 89,
                "download_count": 567,
                "difficulty": "中级",
                "duration": 45.0,
                "tech_stack": "GSAP",
                "features": ["动态效果", "数据可视化", "科技感"],
                "config": {
                    "duration": 45.0,
                    "fps": 30,
                    "resolution": {"width": 1920, "height": 1080},
                    "background": {"type": "solid", "color": "#0a0a0a"}
                },
                "elements": [
                    {
                        "type": "text",
                        "id": "tech_title",
                        "content": "科技标题",
                        "style": {
                            "fontSize": "56px",
                            "fontWeight": "300",
                            "color": "#00ff00",
                            "fontFamily": "monospace",
                            "textShadow": "0 0 20px #00ff00"
                        },
                        "position": {"x": 960, "y": 200}
                    },
                    {
                        "type": "shape",
                        "id": "grid_bg",
                        "shape": "grid",
                        "style": {
                            "stroke": "#333333",
                            "strokeWidth": 1,
                            "opacity": 0.3
                        },
                        "size": {"width": 1920, "height": 1080}
                    }
                ],
                "segments": [
                    {
                        "id": "boot",
                        "name": "启动",
                        "start_time": 0.0,
                        "duration": 3.0,
                        "description": "系统启动动画"
                    },
                    {
                        "id": "data_load",
                        "name": "数据加载",
                        "start_time": 3.0,
                        "duration": 15.0,
                        "description": "数据加载和展示"
                    },
                    {
                        "id": "analysis",
                        "name": "分析",
                        "start_time": 18.0,
                        "duration": 20.0,
                        "description": "数据分析展示"
                    },
                    {
                        "id": "result",
                        "name": "结果",
                        "start_time": 38.0,
                        "duration": 7.0,
                        "description": "结果展示"
                    }
                ],
                "styles": {
                    "primary_color": "#00ff00",
                    "secondary_color": "#0066ff",
                    "background_color": "#0a0a0a",
                    "grid_color": "#333333"
                },
                "animations": {
                    "matrix_effect": {
                        "type": "custom",
                        "name": "matrix_rain",
                        "duration": 2.0
                    },
                    "glow_pulse": {
                        "type": "filter",
                        "property": "drop-shadow",
                        "keyframes": [
                            {"time": 0, "value": "0 0 5px #00ff00"},
                            {"time": 0.5, "value": "0 0 20px #00ff00"},
                            {"time": 1, "value": "0 0 5px #00ff00"}
                        ],
                        "duration": 2.0,
                        "iteration": "infinite"
                    }
                }
            }
        ]
        
        # 创建默认模板文件
        for template_data in default_templates:
            template_id = template_data["id"]
            template_dir = self.templates_dir / template_id
            
            if not template_dir.exists():
                template_dir.mkdir()
                
                # 保存模板配置
                template_file = template_dir / "template.json"
                template_data["created_time"] = datetime.now().isoformat()
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)
                
                # 创建示例HTML
                example_html = self.generate_example_html(template_data)
                html_file = template_dir / "example.html"
                html_file.write_text(example_html, encoding='utf-8')
                
                logger.info(f"已创建默认模板: {template_data['name']}")
    
    def generate_example_html(self, template_data: Dict) -> str:
        """生成示例HTML"""
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template_data['name']} - 示例</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: {template_data['config']['resolution']['width']}px;
            height: {template_data['config']['resolution']['height']}px;
            overflow: hidden;
            font-family: 'Microsoft YaHei', sans-serif;
        }}
        
        .container {{
            width: 100%;
            height: 100%;
            position: relative;
        }}
        
        .element {{
            position: absolute;
            transition: all 0.5s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 模板元素将在这里生成 -->
    </div>
    
    <script>
        // 模板动画脚本
        console.log('模板示例已加载: {template_data['name']}');
    </script>
</body>
</html>"""
        return html_template
    
    def get_templates(self) -> List[ProjectTemplate]:
        """获取所有模板"""
        return list(self.templates.values())

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return self.get_all_categories()

    def get_templates_by_category(self, category: str) -> List[ProjectTemplate]:
        """按分类获取模板"""
        return [template for template in self.templates.values()
                if template.category == category]
    
    def get_templates_by_tags(self, tags: List[str]) -> List[ProjectTemplate]:
        """按标签获取模板"""
        result = []
        for template in self.templates.values():
            if any(tag in template.tags for tag in tags):
                result.append(template)
        return result
    
    def search_templates(self, query: str) -> List[ProjectTemplate]:
        """搜索模板"""
        query = query.lower()
        result = []
        
        for template in self.templates.values():
            if (query in template.name.lower() or 
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                result.append(template)
        
        return result
    
    def apply_template(self, template_id: str, project_data: Dict) -> Dict[str, Any]:
        """应用模板到项目"""
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        template = self.templates[template_id]
        
        # 合并模板配置到项目
        result = {
            "name": project_data.get("name", template.name),
            "description": project_data.get("description", template.description),
            "config": template.config.copy(),
            "elements": template.elements.copy(),
            "segments": template.segments.copy(),
            "styles": template.styles.copy(),
            "animations": template.animations.copy(),
            "template_id": template_id,
            "template_version": template.version
        }
        
        # 更新用户自定义的配置
        if "config" in project_data:
            result["config"].update(project_data["config"])
        
        logger.info(f"已应用模板: {template.name}")
        return result
    
    def create_template_from_project(self, project_data: Dict, 
                                   template_info: Dict) -> ProjectTemplate:
        """从项目创建模板"""
        template_id = template_info["id"]
        template_dir = self.templates_dir / template_id
        template_dir.mkdir(exist_ok=True)
        
        # 创建模板数据
        template_data = {
            "id": template_id,
            "name": template_info["name"],
            "description": template_info["description"],
            "category": template_info["category"],
            "author": template_info.get("author", "用户"),
            "version": "1.0",
            "created_time": datetime.now().isoformat(),
            "tags": template_info.get("tags", []),
            "config": project_data.get("config", {}),
            "elements": project_data.get("elements", []),
            "segments": project_data.get("segments", []),
            "styles": project_data.get("styles", {}),
            "animations": project_data.get("animations", {})
        }
        
        # 保存模板文件
        template_file = template_dir / "template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        # 创建模板对象
        template = ProjectTemplate(**template_data)
        self.templates[template_id] = template
        
        logger.info(f"已创建模板: {template.name}")
        return template
    
    def delete_template(self, template_id: str):
        """删除模板"""
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        template_dir = self.templates_dir / template_id
        if template_dir.exists():
            shutil.rmtree(template_dir)
        
        del self.templates[template_id]
        logger.info(f"已删除模板: {template_id}")
    
    def export_template(self, template_id: str, export_path: str):
        """导出模板"""
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        template_dir = self.templates_dir / template_id
        shutil.copytree(template_dir, export_path)
        logger.info(f"模板已导出到: {export_path}")
    
    def import_template(self, import_path: str):
        """导入模板"""
        import_dir = Path(import_path)
        template_file = import_dir / "template.json"
        
        if not template_file.exists():
            raise ValueError("无效的模板目录")
        
        template = self.load_template_from_file(template_file)
        if not template:
            raise ValueError("加载模板失败")
        
        # 复制到模板目录
        target_dir = self.templates_dir / template.id
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        shutil.copytree(import_dir, target_dir)
        self.templates[template.id] = template
        
        logger.info(f"模板已导入: {template.name}")

    def get_all_templates(self) -> List[ProjectTemplate]:
        """获取所有模板"""
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """获取指定模板"""
        return self.templates.get(template_id)

    def _preload_popular_templates(self):
        """预加载热门模板"""
        try:
            # 预加载前3个最常用的模板
            popular_template_ids = ["simple_demo", "tech_showcase", "creative_intro"]

            for template_id in popular_template_ids:
                if template_id in self.templates:
                    template = self.templates[template_id]
                    # 预生成缩略图
                    self._generate_thumbnail_if_needed(template)
                    # 预加载示例HTML
                    self._preload_example_html(template)

            logger.info("热门模板预加载完成")

        except Exception as e:
            logger.warning(f"预加载模板失败: {e}")

    def _generate_thumbnail_if_needed(self, template: ProjectTemplate):
        """如果需要，生成模板缩略图"""
        try:
            if template.thumbnail and Path(template.thumbnail).exists():
                return  # 缩略图已存在

            # 生成缩略图的逻辑
            thumbnail_path = self.templates_dir / template.id / "thumbnail.png"

            if not thumbnail_path.exists():
                # 从示例HTML生成缩略图
                if template.example_html:
                    self._generate_thumbnail_from_html(template.example_html, thumbnail_path)
                else:
                    # 生成默认缩略图
                    self._generate_default_thumbnail(template, thumbnail_path)

                template.thumbnail = str(thumbnail_path)
                logger.debug(f"已生成模板缩略图: {template.name}")

        except Exception as e:
            logger.warning(f"生成缩略图失败: {e}")

    def _generate_thumbnail_from_html(self, html_content: str, output_path: Path):
        """从HTML内容生成缩略图"""
        try:
            # 这里可以使用webkit2png或其他工具生成缩略图
            # 简化实现：创建一个占位符图片
            from PIL import Image, ImageDraw, ImageFont

            # 创建200x150的缩略图
            img = Image.new('RGB', (200, 150), color='white')
            draw = ImageDraw.Draw(img)

            # 绘制简单的预览
            draw.rectangle([10, 10, 190, 140], outline='gray', width=2)
            draw.text((20, 60), "HTML Preview", fill='black')

            img.save(output_path)
            logger.debug(f"HTML缩略图已生成: {output_path}")

        except Exception as e:
            logger.warning(f"从HTML生成缩略图失败: {e}")

    def _generate_default_thumbnail(self, template: ProjectTemplate, output_path: Path):
        """生成默认缩略图"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建200x150的默认缩略图
            img = Image.new('RGB', (200, 150), color='lightblue')
            draw = ImageDraw.Draw(img)

            # 绘制模板信息
            draw.rectangle([5, 5, 195, 145], outline='darkblue', width=2)
            draw.text((10, 20), template.name[:20], fill='darkblue')
            draw.text((10, 40), template.category, fill='gray')
            draw.text((10, 120), f"v{template.version}", fill='gray')

            img.save(output_path)
            logger.debug(f"默认缩略图已生成: {output_path}")

        except Exception as e:
            logger.warning(f"生成默认缩略图失败: {e}")

    def _preload_example_html(self, template: ProjectTemplate):
        """预加载示例HTML"""
        try:
            if not template.example_html:
                html_file = self.templates_dir / template.id / "example.html"
                if html_file.exists():
                    template.example_html = html_file.read_text(encoding='utf-8')
                    logger.debug(f"已预加载示例HTML: {template.name}")

        except Exception as e:
            logger.warning(f"预加载示例HTML失败: {e}")

    def get_template_stats(self) -> Dict[str, Any]:
        """获取模板统计信息"""
        categories = {}
        total_size = 0

        for template in self.templates.values():
            # 统计分类
            if template.category not in categories:
                categories[template.category] = 0
            categories[template.category] += 1

            # 计算大小（简化）
            template_dir = self.templates_dir / template.id
            if template_dir.exists():
                for file_path in template_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size

        return {
            "total_templates": len(self.templates),
            "categories": categories,
            "total_size_mb": total_size / (1024 * 1024),
            "cache_stats": project_cache.get_stats(),
            "performance_stats": performance_monitor.get_stats("load_templates")
        }
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for template in self.templates.values():
            categories.add(template.category)
        return sorted(list(categories))
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for template in self.templates.values():
            tags.update(template.tags)
        return sorted(list(tags))

    # ==================== 评分推荐系统 ====================

    def get_recommended_templates(self, limit: int = 5, user_preferences: Dict[str, Any] = None) -> List[ProjectTemplate]:
        """获取推荐模板"""
        templates = list(self.templates.values())

        if not templates:
            return []

        # 计算推荐分数
        for template in templates:
            template._recommendation_score = self._calculate_recommendation_score(template, user_preferences)

        # 按推荐分数排序
        templates.sort(key=lambda t: t._recommendation_score, reverse=True)

        return templates[:limit]

    def _calculate_recommendation_score(self, template: ProjectTemplate, user_preferences: Dict[str, Any] = None) -> float:
        """计算推荐分数"""
        score = 0.0

        # 基础流行度分数 (权重: 40%)
        popularity_score = template.popularity_score
        score += popularity_score * 0.4

        # 评分分数 (权重: 30%)
        if template.rating_count > 0:
            rating_score = template.rating / 5.0
            score += rating_score * 0.3

        # 新鲜度分数 (权重: 20%)
        try:
            from datetime import datetime
            created_date = datetime.fromisoformat(template.created_time)
            days_old = (datetime.now() - created_date).days
            freshness_score = max(0, 1 - days_old / 365)  # 一年内的模板有新鲜度加分
            score += freshness_score * 0.2
        except:
            pass

        # 用户偏好匹配 (权重: 10%)
        if user_preferences:
            preference_score = self._calculate_preference_match(template, user_preferences)
            score += preference_score * 0.1

        return score

    def _calculate_preference_match(self, template: ProjectTemplate, preferences: Dict[str, Any]) -> float:
        """计算用户偏好匹配度"""
        match_score = 0.0
        total_factors = 0

        # 分类偏好
        if "preferred_categories" in preferences:
            preferred_categories = preferences["preferred_categories"]
            if template.category in preferred_categories:
                match_score += 1.0
            total_factors += 1

        # 难度偏好
        if "preferred_difficulty" in preferences:
            preferred_difficulty = preferences["preferred_difficulty"]
            if template.difficulty == preferred_difficulty:
                match_score += 1.0
            total_factors += 1

        # 技术栈偏好
        if "preferred_tech_stack" in preferences:
            preferred_tech_stack = preferences["preferred_tech_stack"]
            if template.tech_stack == preferred_tech_stack:
                match_score += 1.0
            total_factors += 1

        # 标签偏好
        if "preferred_tags" in preferences:
            preferred_tags = set(preferences["preferred_tags"])
            template_tags = set(template.tags)
            tag_overlap = len(preferred_tags & template_tags)
            if tag_overlap > 0:
                match_score += tag_overlap / len(preferred_tags)
            total_factors += 1

        return match_score / total_factors if total_factors > 0 else 0.0

    def get_templates_by_rating(self, min_rating: float = 0.0, limit: int = 10) -> List[ProjectTemplate]:
        """按评分获取模板"""
        templates = [t for t in self.templates.values() if t.rating >= min_rating and t.rating_count > 0]
        templates.sort(key=lambda t: (t.rating, t.rating_count), reverse=True)
        return templates[:limit]

    def get_popular_templates(self, limit: int = 10) -> List[ProjectTemplate]:
        """获取热门模板"""
        templates = list(self.templates.values())
        templates.sort(key=lambda t: t.popularity_score, reverse=True)
        return templates[:limit]

    def get_templates_by_difficulty(self, difficulty: str) -> List[ProjectTemplate]:
        """按难度获取模板"""
        return [t for t in self.templates.values() if t.difficulty == difficulty]

    def get_templates_by_tech_stack(self, tech_stack: str) -> List[ProjectTemplate]:
        """按技术栈获取模板"""
        return [t for t in self.templates.values() if t.tech_stack == tech_stack]

    def rate_template(self, template_id: str, rating: float) -> bool:
        """为模板评分"""
        if template_id not in self.templates:
            return False

        try:
            template = self.templates[template_id]
            template.add_rating(rating)

            # 保存更新后的模板数据
            self._save_template_metadata(template)

            logger.info(f"模板 {template_id} 评分更新: {rating}")
            return True
        except Exception as e:
            logger.error(f"模板评分失败: {e}")
            return False

    def increment_template_download(self, template_id: str) -> bool:
        """增加模板下载次数"""
        if template_id not in self.templates:
            return False

        try:
            template = self.templates[template_id]
            template.increment_download()

            # 保存更新后的模板数据
            self._save_template_metadata(template)

            logger.debug(f"模板 {template_id} 下载次数更新: {template.download_count}")
            return True
        except Exception as e:
            logger.error(f"更新下载次数失败: {e}")
            return False

    def _save_template_metadata(self, template: ProjectTemplate):
        """保存模板元数据"""
        try:
            template_file = self.templates_dir / f"{template.id}.json"

            # 读取现有数据
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}

            # 更新评分和下载数据
            data.update({
                "rating": template.rating,
                "rating_count": template.rating_count,
                "download_count": template.download_count,
                "difficulty": template.difficulty,
                "duration": template.duration,
                "tech_stack": template.tech_stack,
                "features": template.features
            })

            # 保存数据
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存模板元数据失败: {e}")
