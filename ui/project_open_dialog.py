"""
AI Animation Studio - 项目打开对话框
提供增强的项目打开功能，包括最近项目列表、项目预览等
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTabWidget, QWidget, QFileDialog,
    QTextEdit, QGroupBox, QSplitter, QMessageBox, QProgressBar,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon, QDragEnterEvent, QDropEvent

from core.logger import get_logger
from core.project_manager import ProjectManager

logger = get_logger("project_open_dialog")


class ProjectPreviewWidget(QWidget):
    """项目预览组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_project_info = None
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 项目信息组
        info_group = QGroupBox("项目信息")
        info_layout = QGridLayout(info_group)
        
        # 项目名称
        info_layout.addWidget(QLabel("项目名称:"), 0, 0)
        self.name_label = QLabel("未选择项目")
        self.name_label.setFont(QFont("", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.name_label, 0, 1)
        
        # 项目描述
        info_layout.addWidget(QLabel("描述:"), 1, 0)
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        info_layout.addWidget(self.description_label, 1, 1)
        
        # 创建时间
        info_layout.addWidget(QLabel("创建时间:"), 2, 0)
        self.created_label = QLabel("")
        info_layout.addWidget(self.created_label, 2, 1)
        
        # 修改时间
        info_layout.addWidget(QLabel("修改时间:"), 3, 0)
        self.modified_label = QLabel("")
        info_layout.addWidget(self.modified_label, 3, 1)
        
        # 文件大小
        info_layout.addWidget(QLabel("文件大小:"), 4, 0)
        self.size_label = QLabel("")
        info_layout.addWidget(self.size_label, 4, 1)
        
        layout.addWidget(info_group)
        
        # 项目统计组
        stats_group = QGroupBox("项目统计")
        stats_layout = QGridLayout(stats_group)
        
        # 元素数量
        stats_layout.addWidget(QLabel("元素数量:"), 0, 0)
        self.elements_label = QLabel("0")
        stats_layout.addWidget(self.elements_label, 0, 1)
        
        # 时间段数量
        stats_layout.addWidget(QLabel("时间段数量:"), 1, 0)
        self.segments_label = QLabel("0")
        stats_layout.addWidget(self.segments_label, 1, 1)
        
        # 项目时长
        stats_layout.addWidget(QLabel("项目时长:"), 2, 0)
        self.duration_label = QLabel("0秒")
        stats_layout.addWidget(self.duration_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        # 缩略图（如果有）
        self.thumbnail_label = QLabel("无预览图")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setMinimumHeight(150)
        self.thumbnail_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        layout.addWidget(self.thumbnail_label)
        
        layout.addStretch()
    
    def load_project_preview(self, project_info: Dict[str, Any]):
        """加载项目预览信息"""
        try:
            self.current_project_info = project_info
            
            # 更新基本信息
            self.name_label.setText(project_info.get("name", "未知项目"))
            self.description_label.setText(project_info.get("description", "无描述"))
            self.created_label.setText(project_info.get("created_at", "未知"))
            self.modified_label.setText(project_info.get("modified_at", "未知"))
            
            # 文件大小
            file_path = Path(project_info.get("file_path", ""))
            if file_path.exists():
                size_bytes = file_path.stat().st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                self.size_label.setText(size_str)
            else:
                self.size_label.setText("文件不存在")
            
            # 项目统计
            self.elements_label.setText(str(project_info.get("element_count", 0)))
            self.segments_label.setText(str(project_info.get("segment_count", 0)))
            
            duration = project_info.get("duration", 0)
            if duration > 60:
                duration_str = f"{duration // 60}分{duration % 60:.0f}秒"
            else:
                duration_str = f"{duration:.1f}秒"
            self.duration_label.setText(duration_str)
            
            # 加载缩略图（如果有）
            self._load_thumbnail(file_path)
            
        except Exception as e:
            logger.error(f"加载项目预览失败: {e}")
    
    def _load_thumbnail(self, project_file: Path):
        """加载项目缩略图"""
        try:
            # 查找缩略图文件
            thumbnail_path = project_file.parent / f"{project_file.stem}_thumbnail.png"
            
            if thumbnail_path.exists():
                pixmap = QPixmap(str(thumbnail_path))
                if not pixmap.isNull():
                    # 缩放到合适大小
                    scaled_pixmap = pixmap.scaled(
                        200, 150, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                    return
            
            # 没有缩略图，显示默认文本
            self.thumbnail_label.clear()
            self.thumbnail_label.setText("无预览图")
            
        except Exception as e:
            logger.warning(f"加载缩略图失败: {e}")
            self.thumbnail_label.clear()
            self.thumbnail_label.setText("预览图加载失败")
    
    def clear_preview(self):
        """清空预览"""
        self.current_project_info = None
        self.name_label.setText("未选择项目")
        self.description_label.setText("")
        self.created_label.setText("")
        self.modified_label.setText("")
        self.size_label.setText("")
        self.elements_label.setText("0")
        self.segments_label.setText("0")
        self.duration_label.setText("0秒")
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("无预览图")


class ProjectOpenDialog(QDialog):
    """项目打开对话框"""
    
    def __init__(self, parent=None, project_manager: ProjectManager = None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.selected_file_path = None
        
        self.setWindowTitle("打开项目")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # 启用拖拽
        self.setAcceptDrops(True)
        
        self.setup_ui()
        self.load_recent_projects()
        
        logger.info("项目打开对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("打开动画项目")
        title_label.setFont(QFont("", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：项目列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 最近项目选项卡
        self.recent_list = QListWidget()
        self.recent_list.itemClicked.connect(self.on_recent_project_selected)
        self.tab_widget.addTab(self.recent_list, "最近项目")
        
        # 浏览文件选项卡
        browse_widget = QWidget()
        browse_layout = QVBoxLayout(browse_widget)
        
        browse_button = QPushButton("浏览文件...")
        browse_button.clicked.connect(self.browse_files)
        browse_layout.addWidget(browse_button)
        
        # 拖拽提示
        drag_label = QLabel("或将 .aas 文件拖拽到此处")
        drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                color: #666;
                background-color: #f9f9f9;
            }
        """)
        browse_layout.addWidget(drag_label)
        browse_layout.addStretch()
        
        self.tab_widget.addTab(browse_widget, "浏览文件")
        
        left_layout.addWidget(self.tab_widget)
        splitter.addWidget(left_widget)
        
        # 右侧：项目预览
        self.preview_widget = ProjectPreviewWidget()
        splitter.addWidget(self.preview_widget)
        
        # 设置分割器比例
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.open_button = QPushButton("打开项目")
        self.open_button.setDefault(True)
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.accept)
        button_layout.addWidget(self.open_button)
        
        layout.addLayout(button_layout)
    
    def load_recent_projects(self):
        """加载最近项目列表"""
        try:
            if not self.project_manager:
                return
            
            recent_projects = self.project_manager.get_recent_projects(20)
            
            self.recent_list.clear()
            for project_info in recent_projects:
                item = QListWidgetItem(project_info["name"])
                item.setData(Qt.ItemDataRole.UserRole, project_info)
                
                # 检查文件是否存在
                file_path = Path(project_info["file_path"])
                if not file_path.exists():
                    item.setText(f"{project_info['name']} (文件不存在)")
                    item.setForeground(QColor("gray"))
                
                self.recent_list.addItem(item)
            
            logger.info(f"已加载 {len(recent_projects)} 个最近项目")
            
        except Exception as e:
            logger.error(f"加载最近项目失败: {e}")
    
    def on_recent_project_selected(self, item: QListWidgetItem):
        """最近项目选择事件"""
        try:
            project_info = item.data(Qt.ItemDataRole.UserRole)
            if project_info:
                file_path = Path(project_info["file_path"])
                if file_path.exists():
                    self.selected_file_path = str(file_path)
                    self.preview_widget.load_project_preview(project_info)
                    self.open_button.setEnabled(True)
                else:
                    QMessageBox.warning(self, "警告", "项目文件不存在")
                    self.open_button.setEnabled(False)
        except Exception as e:
            logger.error(f"选择最近项目失败: {e}")
    
    def browse_files(self):
        """浏览文件"""
        try:
            recent_dir = ""
            if self.project_manager and hasattr(self.project_manager, 'projects_dir'):
                recent_dir = str(self.project_manager.projects_dir)
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择项目文件", recent_dir, 
                "AI Animation Studio项目 (*.aas);;所有文件 (*.*)"
            )
            
            if file_path:
                self.selected_file_path = file_path
                # 加载项目信息用于预览
                self._load_project_info_for_preview(file_path)
                self.open_button.setEnabled(True)
                
        except Exception as e:
            logger.error(f"浏览文件失败: {e}")
    
    def _load_project_info_for_preview(self, file_path: str):
        """为预览加载项目信息"""
        try:
            # 这里可以快速读取项目文件的基本信息
            # 简化实现，实际可以更详细
            project_info = {
                "name": Path(file_path).stem,
                "file_path": file_path,
                "description": "从文件浏览器选择的项目",
                "created_at": "未知",
                "modified_at": "未知",
                "element_count": 0,
                "segment_count": 0,
                "duration": 0
            }
            
            self.preview_widget.load_project_preview(project_info)
            
        except Exception as e:
            logger.error(f"加载项目信息失败: {e}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().endswith('.aas'):
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        try:
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.endswith('.aas'):
                    self.selected_file_path = file_path
                    self._load_project_info_for_preview(file_path)
                    self.open_button.setEnabled(True)
                    
                    # 切换到浏览文件选项卡
                    self.tab_widget.setCurrentIndex(1)
                    
                    logger.info(f"通过拖拽选择项目: {file_path}")
                    
        except Exception as e:
            logger.error(f"拖拽文件失败: {e}")
    
    def get_selected_file(self) -> Optional[str]:
        """获取选择的文件路径"""
        return self.selected_file_path
