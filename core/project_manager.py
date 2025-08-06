"""
AI Animation Studio - 项目管理器
管理项目的创建、保存、加载等操作
"""

import json
import shutil
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .data_structures import Project, Element, TimeSegment, AnimationSolution
from .logger import get_logger
from .project_cache import project_cache, performance_monitor

logger = get_logger("project_manager")

class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.project_file: Optional[Path] = None
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5分钟
        self._auto_save_timer = None  # 自动保存定时器
        
        # 项目目录
        self.projects_dir = Path.home() / ".ai_animation_studio" / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
    
    def create_new_project(self, name: str = None, template_id: str = None,
                          config: dict = None) -> Project:
        """创建新项目 - 增强版"""
        # 开始性能监控
        perf_context = performance_monitor.start_operation("create_new_project")

        try:
            if name is None:
                name = self._generate_unique_project_name()

            # 检查缓存
            cache_key = project_cache._generate_cache_key(
                name=name,
                template_id=template_id or "none",
                config_hash=hash(str(sorted(config.items()))) if config else 0
            )

            cached_project = project_cache.get(cache_key)
            if cached_project:
                logger.info(f"从缓存创建项目: {name}")
                cached_project.name = name  # 更新名称
                cached_project.project_id = str(uuid.uuid4())  # 新的ID
                cached_project.created_at = datetime.now()
                cached_project.modified_at = datetime.now()

                self.current_project = cached_project
                self.project_file = None

                performance_monitor.end_operation(perf_context, success=True)
                return cached_project

            # 应用模板或默认配置
            if template_id:
                project = self._create_from_template(name, template_id)
            else:
                project = Project(name=name)
                if config:
                    self._apply_config_to_project(project, config)

            # 项目验证
            self._validate_project(project)

            # 设置默认元素
            self._setup_default_elements(project)

            # 缓存项目模板（不包含具体的ID和时间）
            if template_id or config:
                cache_template = Project(name="template")
                if config:
                    self._apply_config_to_project(cache_template, config)
                self._setup_default_elements(cache_template)
                project_cache.put(cache_key, cache_template)

            self.current_project = project
            self.project_file = None

            performance_monitor.end_operation(perf_context, success=True)
            logger.info(f"创建新项目: {name}")
            return project

        except Exception as e:
            performance_monitor.end_operation(perf_context, success=False, error_message=str(e))
            raise

    def create_project_from_template(self, name: str, template_data: Dict[str, Any]) -> Project:
        """从模板创建项目"""
        try:
            # 创建基础项目
            project = Project(name=name)

            # 应用模板配置
            if "config" in template_data:
                config = template_data["config"]
                project.duration = config.get("duration", 30.0)
                project.fps = config.get("fps", 30)
                project.resolution = config.get("resolution", {"width": 1920, "height": 1080})
                project.background = config.get("background", {"type": "solid", "color": "#ffffff"})

            # 添加模板元素
            if "elements" in template_data:
                for element_data in template_data["elements"]:
                    element = Element(
                        id=element_data.get("id", f"element_{len(project.elements)}"),
                        type=element_data.get("type", "text"),
                        name=element_data.get("content", "元素"),
                        properties=element_data
                    )
                    project.elements.append(element)

            # 添加时间段
            if "segments" in template_data:
                for segment_data in template_data["segments"]:
                    segment = TimeSegment(
                        id=segment_data.get("id", f"segment_{len(project.segments)}"),
                        name=segment_data.get("name", "时间段"),
                        start_time=segment_data.get("start_time", 0.0),
                        duration=segment_data.get("duration", 5.0),
                        description=segment_data.get("description", "")
                    )
                    project.segments.append(segment)

            # 保存模板信息
            project.metadata["template_id"] = template_data.get("template_id")
            project.metadata["template_version"] = template_data.get("template_version")
            project.metadata["styles"] = template_data.get("styles", {})
            project.metadata["animations"] = template_data.get("animations", {})

            self.current_project = project
            self.project_file = None

            logger.info(f"从模板创建项目: {name}")
            return project

        except Exception as e:
            logger.error(f"从模板创建项目失败: {e}")
            raise

    def _generate_unique_project_name(self) -> str:
        """生成唯一的项目名称"""
        base_name = "新项目"
        counter = 1

        while True:
            if counter == 1:
                name = base_name
            else:
                name = f"{base_name}_{counter}"

            # 检查项目目录是否存在
            project_path = self.projects_dir / f"{name}.aas"
            if not project_path.exists():
                return name

            counter += 1
            if counter > 1000:  # 防止无限循环
                return f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _create_from_template(self, name: str, template_id: str) -> Project:
        """从模板创建项目"""
        from core.template_manager import TemplateManager

        template_manager = TemplateManager()
        template = template_manager.get_template(template_id)

        if not template:
            raise ValueError(f"模板不存在: {template_id}")

        # 应用模板创建项目
        template_data = template_manager.apply_template(template_id, {"name": name})
        return self.create_project_from_template(name, template_data)

    def _apply_config_to_project(self, project: Project, config: dict):
        """将配置应用到项目"""
        if "duration" in config:
            project.duration = config["duration"]
        if "fps" in config:
            project.fps = config["fps"]
        if "resolution" in config:
            project.resolution = config["resolution"]
        if "description" in config:
            project.description = config.get("description", "")

        # 应用其他配置
        if "auto_save" in config:
            project.settings = project.settings or {}
            project.settings["auto_save"] = config["auto_save"]
        if "show_grid" in config:
            project.settings = project.settings or {}
            project.settings["show_grid"] = config["show_grid"]
        if "performance_mode" in config:
            project.settings = project.settings or {}
            project.settings["performance_mode"] = config["performance_mode"]

    def _validate_project(self, project: Project) -> bool:
        """验证项目"""
        try:
            # 验证项目名称
            if not project.name or not project.name.strip():
                raise ValueError("项目名称不能为空")

            # 验证持续时间
            if project.duration <= 0:
                raise ValueError("项目持续时间必须大于0")

            # 验证帧率
            if project.fps <= 0 or project.fps > 120:
                raise ValueError("帧率必须在1-120之间")

            # 验证分辨率
            if project.resolution:
                width = project.resolution.get("width", 0)
                height = project.resolution.get("height", 0)
                if width <= 0 or height <= 0:
                    raise ValueError("分辨率必须大于0")

            logger.info(f"项目验证通过: {project.name}")
            return True

        except ValueError as e:
            logger.error(f"项目验证失败: {e}")
            raise

    def _setup_default_elements(self, project: Project):
        """设置默认元素"""
        try:
            from core.data_structures import Element, ElementType, ElementStyle, Point

            # 如果项目没有元素，添加一些默认元素
            if not project.elements:
                # 创建背景样式
                background_style = ElementStyle(
                    width=f"{project.resolution.get('width', 1920)}px",
                    height=f"{project.resolution.get('height', 1080)}px",
                    background_color="#ffffff",
                    z_index=0
                )

                # 添加默认背景元素
                background_element = Element(
                    name="背景",
                    element_type=ElementType.RECTANGLE,
                    position=Point(0, 0),
                    style=background_style
                )
                project.add_element(background_element)

                logger.info(f"已为项目添加默认元素: {project.name}")

            # 设置默认素材
            self._setup_default_assets(project)

        except Exception as e:
            logger.warning(f"设置默认元素失败: {e}")
            # 不抛出异常，因为这不是关键功能

    def _setup_default_assets(self, project: Project):
        """设置默认素材"""
        try:
            from pathlib import Path
            import os
            from datetime import datetime

            # 创建默认素材目录
            assets_dir = Path(__file__).parent.parent / "assets" / "samples"
            assets_dir.mkdir(parents=True, exist_ok=True)

            # 创建一些默认的SVG素材文件
            default_assets = [
                {
                    "name": "圆形",
                    "filename": "circle.svg",
                    "content": '''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="#3B82F6" stroke="#1E40AF" stroke-width="2"/>
</svg>'''
                },
                {
                    "name": "矩形",
                    "filename": "rectangle.svg",
                    "content": '''<svg width="120" height="80" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="100" height="60" fill="#10B981" stroke="#059669" stroke-width="2" rx="5"/>
</svg>'''
                },
                {
                    "name": "星形",
                    "filename": "star.svg",
                    "content": '''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,10 61,35 90,35 69,57 79,91 50,70 21,91 31,57 10,35 39,35"
           fill="#F59E0B" stroke="#D97706" stroke-width="2"/>
</svg>'''
                },
                {
                    "name": "三角形",
                    "filename": "triangle.svg",
                    "content": '''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,10 90,80 10,80" fill="#8B5CF6" stroke="#7C3AED" stroke-width="2"/>
</svg>'''
                }
            ]

            # 创建默认素材文件
            for asset_data in default_assets:
                asset_file = assets_dir / asset_data["filename"]
                if not asset_file.exists():
                    asset_file.write_text(asset_data["content"], encoding='utf-8')
                    logger.info(f"已创建默认素材: {asset_data['name']}")

            # 将默认素材添加到项目中
            if not project.assets:
                from core.data_structures import Asset

                for asset_data in default_assets:
                    asset_file = assets_dir / asset_data["filename"]
                    if asset_file.exists():
                        asset = Asset(
                            name=asset_data["name"],
                            file_path=str(asset_file),
                            asset_type="image",
                            created_at=datetime.now().isoformat()
                        )
                        project.add_asset(asset)
                        logger.info(f"已添加默认素材到项目: {asset_data['name']}")

        except Exception as e:
            logger.warning(f"设置默认素材失败: {e}")
    
    def save_project(self, file_path: Optional[Path] = None, create_backup: bool = True, incremental: bool = True) -> bool:
        """保存项目 - 增强版"""
        if not self.current_project:
            logger.error("没有当前项目可保存")
            return False

        if file_path is None:
            if self.project_file is None:
                # 生成默认文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.current_project.name}_{timestamp}.aas"
                file_path = self.projects_dir / filename
            else:
                file_path = self.project_file

        try:
            # 创建项目目录
            project_dir = file_path.parent / file_path.stem
            project_dir.mkdir(exist_ok=True)

            # 创建版本历史备份
            if create_backup and file_path.exists():
                self._create_version_backup(file_path)

            # 获取项目数据
            project_data = self._project_to_dict(self.current_project)

            # 增量保存检查
            if incremental and file_path.exists():
                if self._is_incremental_save_beneficial(file_path, project_data):
                    success = self._save_incremental(file_path, project_data)
                    if success:
                        self.project_file = file_path
                        self.current_project.modified_at = datetime.now()
                        logger.info(f"项目增量保存完成: {file_path}")
                        return True

            # 完整保存
            success = self._save_complete(file_path, project_data)
            if success:
                self.project_file = file_path
                self.current_project.modified_at = datetime.now()

                # 生成缩略图
                self._generate_project_thumbnail(file_path)

                logger.info(f"项目完整保存完成: {file_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"保存项目失败: {e}")
            return False

    def _create_version_backup(self, file_path: Path):
        """创建版本历史备份"""
        try:
            backup_dir = file_path.parent / f"{file_path.stem}_versions"
            backup_dir.mkdir(exist_ok=True)

            # 限制备份数量
            existing_backups = list(backup_dir.glob("*.aas"))
            if len(existing_backups) >= 10:  # 最多保留10个版本
                # 删除最旧的备份
                existing_backups.sort(key=lambda x: x.stat().st_mtime)
                for old_backup in existing_backups[:-9]:
                    old_backup.unlink()

            # 创建新备份
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{file_path.stem}_v{timestamp}.aas"

            import shutil
            shutil.copy2(file_path, backup_path)

            logger.debug(f"创建版本备份: {backup_path}")

        except Exception as e:
            logger.warning(f"创建版本备份失败: {e}")

    def _is_incremental_save_beneficial(self, file_path: Path, new_data: dict) -> bool:
        """检查是否适合增量保存"""
        try:
            if not file_path.exists():
                return False

            # 读取现有数据
            with open(file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)

            # 简单的变化检测
            old_elements = old_data.get("elements", {})
            new_elements = new_data.get("elements", {})

            # 如果元素数量变化超过20%，使用完整保存
            if abs(len(old_elements) - len(new_elements)) / max(len(old_elements), 1) > 0.2:
                return False

            return True

        except Exception as e:
            logger.warning(f"增量保存检查失败: {e}")
            return False

    def _save_incremental(self, file_path: Path, project_data: dict) -> bool:
        """增量保存"""
        try:
            # 读取现有数据
            with open(file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)

            # 合并变化
            old_data.update({
                "name": project_data["name"],
                "description": project_data["description"],
                "modified_at": project_data["modified_at"],
                "elements": project_data["elements"],
                "segments": project_data.get("segments", {}),
                "canvas_width": project_data["canvas_width"],
                "canvas_height": project_data["canvas_height"],
                "total_duration": project_data["total_duration"]
            })

            # 保存合并后的数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(old_data, f, indent=2, ensure_ascii=False, default=str)

            return True

        except Exception as e:
            logger.error(f"增量保存失败: {e}")
            return False

    def _save_complete(self, file_path: Path, project_data: dict) -> bool:
        """完整保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            logger.error(f"完整保存失败: {e}")
            return False

    def _generate_project_thumbnail(self, file_path: Path):
        """生成项目缩略图"""
        try:
            # 这里可以实现缩略图生成逻辑
            # 简化实现：创建一个占位符文件
            thumbnail_path = file_path.parent / f"{file_path.stem}_thumbnail.png"

            # 实际实现中，这里应该渲染项目的第一帧或关键帧
            # 现在只创建一个标记文件
            thumbnail_path.touch()

            logger.debug(f"生成项目缩略图: {thumbnail_path}")

        except Exception as e:
            logger.warning(f"生成缩略图失败: {e}")

    # ==================== 自动保存系统 ====================

    def enable_auto_save(self, interval_seconds: int = 300):
        """启用自动保存"""
        self.auto_save_enabled = True
        self.auto_save_interval = interval_seconds
        self._start_auto_save_timer()
        logger.info(f"自动保存已启用，间隔: {interval_seconds}秒")

    def disable_auto_save(self):
        """禁用自动保存"""
        self.auto_save_enabled = False
        self._stop_auto_save_timer()
        logger.info("自动保存已禁用")

    def _start_auto_save_timer(self):
        """启动自动保存定时器"""
        try:
            from PyQt6.QtCore import QTimer

            if self._auto_save_timer:
                self._auto_save_timer.stop()

            self._auto_save_timer = QTimer()
            self._auto_save_timer.timeout.connect(self._auto_save_check)
            self._auto_save_timer.start(self.auto_save_interval * 1000)  # 转换为毫秒

        except Exception as e:
            logger.warning(f"启动自动保存定时器失败: {e}")

    def _stop_auto_save_timer(self):
        """停止自动保存定时器"""
        if self._auto_save_timer:
            self._auto_save_timer.stop()
            self._auto_save_timer = None

    def _auto_save_check(self):
        """自动保存检查"""
        try:
            if not self.auto_save_enabled or not self.current_project:
                return

            if self.has_unsaved_changes:
                # 创建自动保存文件
                auto_save_path = self._get_auto_save_path()
                if self.save_project(auto_save_path, create_backup=False, incremental=True):
                    logger.debug("自动保存完成")
                    self.last_save_time = datetime.now()
                else:
                    logger.warning("自动保存失败")

        except Exception as e:
            logger.error(f"自动保存检查失败: {e}")

    def _get_auto_save_path(self) -> Path:
        """获取自动保存文件路径"""
        if self.project_file:
            # 在原文件旁边创建自动保存文件
            return self.project_file.parent / f"{self.project_file.stem}_autosave.aas"
        else:
            # 新项目，在临时目录创建自动保存文件
            temp_name = f"untitled_autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}.aas"
            return self.projects_dir / "autosave" / temp_name

    def mark_unsaved_changes(self):
        """标记有未保存的更改"""
        self.has_unsaved_changes = True

    def mark_saved(self):
        """标记已保存"""
        self.has_unsaved_changes = False
        self.last_save_time = datetime.now()

    def get_auto_save_files(self) -> List[Path]:
        """获取自动保存文件列表"""
        auto_save_files = []
        try:
            # 查找当前项目的自动保存文件
            if self.project_file:
                auto_save_path = self._get_auto_save_path()
                if auto_save_path.exists():
                    auto_save_files.append(auto_save_path)

            # 查找临时自动保存文件
            autosave_dir = self.projects_dir / "autosave"
            if autosave_dir.exists():
                auto_save_files.extend(autosave_dir.glob("*_autosave.aas"))

        except Exception as e:
            logger.error(f"获取自动保存文件失败: {e}")

        return auto_save_files

    def recover_from_auto_save(self, auto_save_path: Path) -> bool:
        """从自动保存文件恢复"""
        try:
            if not auto_save_path.exists():
                logger.error(f"自动保存文件不存在: {auto_save_path}")
                return False

            # 加载自动保存的项目
            if self.load_project(auto_save_path):
                logger.info(f"从自动保存文件恢复成功: {auto_save_path}")
                return True
            else:
                logger.error(f"从自动保存文件恢复失败: {auto_save_path}")
                return False

        except Exception as e:
            logger.error(f"恢复自动保存失败: {e}")
            return False

    def load_project(self, file_path: Path) -> bool:
        """加载项目 - 增强版"""
        perf_context = performance_monitor.start_operation("load_project")

        try:
            # 预检查
            if not self._validate_project_file(file_path):
                logger.error(f"无效的项目文件: {file_path}")
                performance_monitor.end_operation(perf_context, success=False, error_message="无效的项目文件")
                return False

            # 版本兼容性检查
            version_info = self._get_project_version(file_path)
            if not self._is_version_compatible(version_info):
                if not self._migrate_project(file_path):
                    logger.error(f"项目版本不兼容且迁移失败: {file_path}")
                    performance_monitor.end_operation(perf_context, success=False, error_message="版本不兼容")
                    return False

            # 安全加载项目
            project = self._load_project_safe(file_path)
            if not project:
                performance_monitor.end_operation(perf_context, success=False, error_message="加载失败")
                return False

            # 后处理
            self._post_load_processing(project)

            # 更新状态
            self.current_project = project
            self.project_file = file_path

            # 添加到最近项目列表
            self.add_to_recent_projects(str(file_path))

            performance_monitor.end_operation(perf_context, success=True)
            logger.info(f"项目加载成功: {project.name}")
            return True

        except Exception as e:
            performance_monitor.end_operation(perf_context, success=False, error_message=str(e))
            logger.error(f"加载项目失败: {e}")
            return False
    
    def export_project(self, export_path: Path, include_assets: bool = True) -> bool:
        """导出项目"""
        if not self.current_project:
            logger.error("没有当前项目可导出")
            return False
        
        try:
            # 创建导出目录
            export_path.mkdir(parents=True, exist_ok=True)
            
            # 保存项目文件
            project_file = export_path / f"{self.current_project.name}.aas"
            self.save_project(project_file)
            
            # 复制资源文件
            if include_assets and self.project_file:
                assets_dir = self.project_file.parent / f"{self.project_file.stem}_assets"
                if assets_dir.exists():
                    export_assets_dir = export_path / "assets"
                    shutil.copytree(assets_dir, export_assets_dir, dirs_exist_ok=True)
            
            logger.info(f"项目已导出: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出项目失败: {e}")
            return False
    
    def get_recent_projects(self, limit: int = 10) -> list:
        """获取最近的项目列表"""
        recent_projects = []
        
        try:
            for project_file in self.projects_dir.glob("*.aas"):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                    
                    recent_projects.append({
                        "name": project_data.get("name", "未知项目"),
                        "file_path": project_file,
                        "modified_at": project_data.get("modified_at", ""),
                        "description": project_data.get("description", "")
                    })
                except Exception as e:
                    logger.warning(f"读取项目文件失败 {project_file}: {e}")
            
            # 按修改时间排序
            recent_projects.sort(key=lambda x: x["modified_at"], reverse=True)
            return recent_projects[:limit]
            
        except Exception as e:
            logger.error(f"获取最近项目失败: {e}")
            return []
    
    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        """将项目转换为字典"""
        return {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "canvas_width": project.canvas_width,
            "canvas_height": project.canvas_height,
            "total_duration": project.total_duration,
            "audio_file": project.audio_file,
            "elements": {
                element_id: {
                    "element_id": element.element_id,
                    "name": element.name,
                    "element_type": element.element_type.value,
                    "content": element.content,
                    "position": element.position.to_dict(),
                    "transform": element.transform.__dict__,
                    "style": element.style.__dict__,
                    "visible": element.visible,
                    "locked": element.locked,
                    "parent_id": element.parent_id,
                    "children_ids": element.children_ids,
                    "custom_data": element.custom_data,
                    "created_at": element.created_at.isoformat()
                }
                for element_id, element in project.elements.items()
            },
            "time_segments": [
                {
                    "segment_id": segment.segment_id,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "description": segment.description,
                    "narration_text": segment.narration_text,
                    "animation_type": segment.animation_type.value,
                    "elements": segment.elements
                }
                for segment in project.time_segments
            ],
            "animation_solutions": {
                segment_id: [
                    {
                        "solution_id": solution.solution_id,
                        "name": solution.name,
                        "description": solution.description,
                        "html_code": solution.html_code,
                        "tech_stack": solution.tech_stack.value,
                        "element_states": [state.to_dict() for state in solution.element_states],
                        "applied_rules": solution.applied_rules,
                        "complexity_level": solution.complexity_level,
                        "recommended": solution.recommended,
                        "generated_at": solution.generated_at.isoformat()
                    }
                    for solution in solutions
                ]
                for segment_id, solutions in project.animation_solutions.items()
            },
            "animation_rules": project.animation_rules,
            "created_at": project.created_at.isoformat(),
            "modified_at": project.modified_at.isoformat()
        }
    
    def _dict_to_project(self, data: Dict[str, Any]) -> Project:
        """从字典创建项目"""
        from .data_structures import ElementType, AnimationType, TechStack, Point, Transform, ElementStyle
        
        project = Project(
            project_id=data.get("project_id", ""),
            name=data.get("name", "未知项目"),
            description=data.get("description", ""),
            canvas_width=data.get("canvas_width", 1920),
            canvas_height=data.get("canvas_height", 1080),
            duration=data.get("duration", data.get("total_duration", 30.0)),
            audio_file=data.get("audio_file"),
            animation_rules=data.get("animation_rules", "")
        )
        
        # 解析创建和修改时间
        if "created_at" in data:
            project.created_at = datetime.fromisoformat(data["created_at"])
        if "modified_at" in data:
            project.modified_at = datetime.fromisoformat(data["modified_at"])
        
        # 解析元素
        for element_id, element_data in data.get("elements", {}).items():
            element = Element(
                element_id=element_data["element_id"],
                name=element_data["name"],
                element_type=ElementType(element_data["element_type"]),
                content=element_data["content"],
                position=Point.from_dict(element_data["position"]),
                visible=element_data.get("visible", True),
                locked=element_data.get("locked", False),
                parent_id=element_data.get("parent_id"),
                children_ids=element_data.get("children_ids", []),
                custom_data=element_data.get("custom_data", {})
            )
            
            # 解析变换和样式
            if "transform" in element_data:
                element.transform = Transform(**element_data["transform"])
            if "style" in element_data:
                element.style = ElementStyle(**element_data["style"])
            
            # 解析创建时间
            if "created_at" in element_data:
                element.created_at = datetime.fromisoformat(element_data["created_at"])
            
            project.elements[element_id] = element
        
        # 解析时间段
        for segment_data in data.get("time_segments", []):
            segment = TimeSegment(
                segment_id=segment_data["segment_id"],
                start_time=segment_data["start_time"],
                end_time=segment_data["end_time"],
                description=segment_data.get("description", ""),
                narration_text=segment_data.get("narration_text", ""),
                animation_type=AnimationType(segment_data["animation_type"]),
                elements=segment_data.get("elements", [])
            )
            project.time_segments.append(segment)
        
        # 解析动画方案
        for segment_id, solutions_data in data.get("animation_solutions", {}).items():
            solutions = []
            for solution_data in solutions_data:
                solution = AnimationSolution(
                    solution_id=solution_data["solution_id"],
                    name=solution_data["name"],
                    description=solution_data.get("description", ""),
                    html_code=solution_data.get("html_code", ""),
                    tech_stack=TechStack(solution_data["tech_stack"]),
                    applied_rules=solution_data.get("applied_rules", []),
                    complexity_level=solution_data.get("complexity_level", "medium"),
                    recommended=solution_data.get("recommended", False)
                )
                
                # 解析生成时间
                if "generated_at" in solution_data:
                    solution.generated_at = datetime.fromisoformat(solution_data["generated_at"])
                
                solutions.append(solution)
            
            project.animation_solutions[segment_id] = solutions
        
        return project

    # ==================== 元素管理方法 ====================

    def add_element(self, element):
        """添加元素到当前项目"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        self.current_project.add_element(element)
        logger.info(f"添加元素: {element.name} ({element.element_id})")

    def remove_element(self, element_id: str):
        """从当前项目中移除元素"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        if element_id in self.current_project.elements:
            element_name = self.current_project.elements[element_id].name
            self.current_project.remove_element(element_id)
            logger.info(f"移除元素: {element_name} ({element_id})")
        else:
            raise ValueError(f"元素不存在: {element_id}")

    def get_element(self, element_id: str):
        """获取元素"""
        if not self.current_project:
            return None

        return self.current_project.elements.get(element_id)

    def update_element(self, element):
        """更新元素"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        if element.element_id in self.current_project.elements:
            self.current_project.elements[element.element_id] = element
            self.current_project.modified_at = datetime.now()
            logger.info(f"更新元素: {element.name} ({element.element_id})")
        else:
            raise ValueError(f"元素不存在: {element.element_id}")

    def get_all_elements(self):
        """获取所有元素"""
        if not self.current_project:
            return {}

        return self.current_project.elements.copy()

    def get_elements_by_type(self, element_type):
        """获取指定类型的所有元素"""
        if not self.current_project:
            return []

        return self.current_project.get_elements_by_type(element_type)

    def get_visible_elements(self):
        """获取所有可见元素"""
        if not self.current_project:
            return []

        return self.current_project.get_visible_elements()

    def get_elements_count(self) -> int:
        """获取元素总数"""
        if not self.current_project:
            return 0

        return self.current_project.get_elements_count()

    def get_elements_by_parent(self, parent_id=None):
        """获取指定父元素的子元素"""
        if not self.current_project:
            return []

        return self.current_project.get_elements_by_parent(parent_id)

    def move_element(self, element_id: str, new_position):
        """移动元素到新位置"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        self.current_project.move_element(element_id, new_position)
        logger.info(f"移动元素: {element_id} 到位置 ({new_position.x}, {new_position.y})")

    def set_element_visibility(self, element_id: str, visible: bool):
        """设置元素可见性"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        self.current_project.set_element_visibility(element_id, visible)
        logger.info(f"设置元素可见性: {element_id} = {visible}")

    def duplicate_element(self, element_id: str):
        """复制元素"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        duplicated = self.current_project.duplicate_element(element_id)
        if duplicated:
            logger.info(f"复制元素: {element_id} -> {duplicated.element_id}")
            return duplicated
        else:
            raise ValueError(f"元素不存在: {element_id}")

    def clear_elements(self):
        """清空所有元素"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        element_count = self.current_project.get_elements_count()
        self.current_project.clear_elements()
        logger.info(f"清空了 {element_count} 个元素")

    # ==================== 时间段管理方法 ====================

    def add_time_segment(self, time_segment):
        """添加时间段到当前项目"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        self.current_project.add_time_segment(time_segment)
        logger.info(f"添加时间段: {time_segment.start_time}s-{time_segment.end_time}s")

    def remove_time_segment(self, segment_id: str):
        """从当前项目中移除时间段"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        for i, segment in enumerate(self.current_project.time_segments):
            if segment.segment_id == segment_id:
                removed_segment = self.current_project.time_segments.pop(i)
                self.current_project.modified_at = datetime.now()
                logger.info(f"移除时间段: {removed_segment.start_time}s-{removed_segment.end_time}s")
                return

        raise ValueError(f"时间段不存在: {segment_id}")

    def get_time_segment(self, segment_id: str):
        """获取时间段"""
        if not self.current_project:
            return None

        for segment in self.current_project.time_segments:
            if segment.segment_id == segment_id:
                return segment

        return None

    def update_time_segment(self, time_segment):
        """更新时间段"""
        if not self.current_project:
            raise ValueError("没有打开的项目")

        for i, segment in enumerate(self.current_project.time_segments):
            if segment.segment_id == time_segment.segment_id:
                self.current_project.time_segments[i] = time_segment
                self.current_project.modified_at = datetime.now()
                logger.info(f"更新时间段: {time_segment.start_time}s-{time_segment.end_time}s")
                return

        raise ValueError(f"时间段不存在: {time_segment.segment_id}")

    # ==================== 项目加载增强方法 ====================

    def _validate_project_file(self, file_path: Path) -> bool:
        """验证项目文件"""
        try:
            if not file_path.exists():
                logger.error(f"项目文件不存在: {file_path}")
                return False

            if not file_path.suffix.lower() == '.aas':
                logger.error(f"不支持的文件格式: {file_path.suffix}")
                return False

            # 检查文件大小（防止过大的文件）
            file_size = file_path.stat().st_size
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                logger.error(f"项目文件过大: {file_size / (1024*1024):.1f}MB > {max_size / (1024*1024)}MB")
                return False

            # 基本JSON格式检查
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return True
            except json.JSONDecodeError as e:
                logger.error(f"项目文件JSON格式错误: {e}")
                return False

        except Exception as e:
            logger.error(f"验证项目文件失败: {e}")
            return False

    def _get_project_version(self, file_path: Path) -> Dict[str, Any]:
        """获取项目版本信息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                "version": data.get("version", "1.0.0"),
                "created_with": data.get("created_with", "AI Animation Studio"),
                "format_version": data.get("format_version", 1)
            }

        except Exception as e:
            logger.warning(f"获取项目版本信息失败: {e}")
            return {"version": "unknown", "created_with": "unknown", "format_version": 1}

    def _is_version_compatible(self, version_info: Dict[str, Any]) -> bool:
        """检查版本兼容性"""
        try:
            format_version = version_info.get("format_version", 1)
            current_format_version = 1  # 当前支持的格式版本

            # 支持当前版本和之前的版本
            if format_version <= current_format_version:
                return True

            logger.warning(f"项目格式版本过新: {format_version} > {current_format_version}")
            return False

        except Exception as e:
            logger.error(f"版本兼容性检查失败: {e}")
            return False

    def _migrate_project(self, file_path: Path) -> bool:
        """迁移项目到当前版本"""
        try:
            # 创建备份
            backup_path = file_path.with_suffix('.aas.backup')
            shutil.copy2(file_path, backup_path)
            logger.info(f"已创建项目备份: {backup_path}")

            # 这里可以实现具体的迁移逻辑
            # 目前简单返回True，表示迁移成功
            logger.info(f"项目迁移完成: {file_path}")
            return True

        except Exception as e:
            logger.error(f"项目迁移失败: {e}")
            return False

    def _load_project_safe(self, file_path: Path) -> Optional[Project]:
        """安全加载项目"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # 使用现有的转换方法
            project = self._dict_to_project(project_data)
            return project

        except Exception as e:
            logger.error(f"安全加载项目失败: {e}")
            return None

    def _post_load_processing(self, project: Project):
        """项目加载后处理"""
        try:
            # 验证项目数据完整性
            self._validate_project_data(project)

            # 修复可能的数据问题
            self._repair_project_data(project)

            # 更新项目统计信息
            self._update_project_stats(project)

            logger.debug(f"项目后处理完成: {project.name}")

        except Exception as e:
            logger.warning(f"项目后处理失败: {e}")

    def _validate_project_data(self, project: Project):
        """验证项目数据完整性"""
        # 检查必要字段
        if not project.name:
            project.name = "未命名项目"

        if not project.project_id:
            project.project_id = str(uuid.uuid4())

        # 检查元素引用完整性
        for element_id, element in project.elements.items():
            if element.parent_id and element.parent_id not in project.elements:
                logger.warning(f"元素 {element.name} 的父元素不存在，已清除父元素引用")
                element.parent_id = None

    def _repair_project_data(self, project: Project):
        """修复项目数据问题"""
        try:
            # 修复缺失的默认值
            if not hasattr(project, 'duration') or project.duration <= 0:
                project.duration = 30.0

            if not hasattr(project, 'fps') or project.fps <= 0:
                project.fps = 30

            if not hasattr(project, 'resolution'):
                project.resolution = {"width": 1920, "height": 1080}

            logger.debug("项目数据修复完成")

        except Exception as e:
            logger.warning(f"修复项目数据失败: {e}")

    def _update_project_stats(self, project: Project):
        """更新项目统计信息"""
        try:
            # 更新修改时间
            project.modified_at = datetime.now()

            # 计算项目统计信息（可以扩展）
            element_count = len(project.elements)
            logger.debug(f"项目统计: {element_count} 个元素")

        except Exception as e:
            logger.warning(f"更新项目统计失败: {e}")

    def add_to_recent_projects(self, file_path: str):
        """添加到最近项目列表"""
        try:
            recent_file = self.projects_dir / "recent_projects.json"
            recent_projects = []

            # 加载现有列表
            if recent_file.exists():
                with open(recent_file, 'r', encoding='utf-8') as f:
                    recent_projects = json.load(f)

            # 移除重复项
            recent_projects = [p for p in recent_projects if p != file_path]

            # 添加到开头
            recent_projects.insert(0, file_path)

            # 限制数量
            recent_projects = recent_projects[:10]

            # 保存
            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump(recent_projects, f, ensure_ascii=False, indent=2)

            logger.debug(f"已添加到最近项目: {file_path}")

        except Exception as e:
            logger.warning(f"添加到最近项目失败: {e}")
