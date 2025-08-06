"""
AI Animation Studio - 专业图标系统设计
替换Emoji图标，建立统一的专业图标语言
"""

from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QFont, QColor, QPainterPath
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json
from dataclasses import dataclass
import math

from core.logger import get_logger

logger = get_logger("professional_icon_system")


class IconCategory(Enum):
    """图标分类枚举"""
    WORKFLOW = "workflow"       # 工作流程图标
    ACTION = "action"          # 操作动作图标
    STATUS = "status"          # 状态指示图标
    NAVIGATION = "navigation"   # 导航图标
    MEDIA = "media"            # 媒体图标
    INTERFACE = "interface"     # 界面图标


class WorkflowIcon(Enum):
    """工作流程图标枚举"""
    AUDIO_IMPORT = "audio_import"           # 音频导入
    TIME_SEGMENT = "time_segment"           # 时间段标记
    ANIMATION_DESC = "animation_desc"       # 动画描述
    AI_GENERATION = "ai_generation"         # AI生成
    PREVIEW_ADJUST = "preview_adjust"       # 预览调整
    EXPORT_RENDER = "export_render"         # 导出渲染


class ActionIcon(Enum):
    """操作动作图标枚举"""
    PLAY = "play"               # 播放
    PAUSE = "pause"             # 暂停
    STOP = "stop"               # 停止
    RECORD = "record"           # 录制
    EDIT = "edit"               # 编辑
    DELETE = "delete"           # 删除
    COPY = "copy"               # 复制
    PASTE = "paste"             # 粘贴
    UNDO = "undo"               # 撤销
    REDO = "redo"               # 重做
    SAVE = "save"               # 保存
    LOAD = "load"               # 加载


class StatusIcon(Enum):
    """状态指示图标枚举"""
    SUCCESS = "success"         # 成功
    WARNING = "warning"         # 警告
    ERROR = "error"            # 错误
    INFO = "info"              # 信息
    LOADING = "loading"        # 加载中
    PROCESSING = "processing"   # 处理中


@dataclass
class IconDefinition:
    """图标定义"""
    name: str
    category: IconCategory
    svg_path: str
    description: str
    size_variants: List[int]
    color_variants: List[str]
    
    def get_svg_content(self, size: int = 24, color: str = "#000000") -> str:
        """获取SVG内容"""
        # 这里应该返回实际的SVG内容
        # 为了演示，返回一个简单的SVG模板
        return f"""
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="{self.svg_path}" fill="{color}"/>
        </svg>
        """


class ProfessionalIconRenderer:
    """专业图标渲染器"""
    
    def __init__(self):
        self.icon_cache: Dict[str, QIcon] = {}
        self.svg_cache: Dict[str, str] = {}
        
        logger.info("专业图标渲染器初始化完成")
    
    def render_workflow_icon(self, icon_type: WorkflowIcon, size: int = 24, color: str = "#2196F3") -> QPixmap:
        """渲染工作流程图标"""
        cache_key = f"{icon_type.value}_{size}_{color}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key].pixmap(size, size)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据图标类型绘制不同的图标
        if icon_type == WorkflowIcon.AUDIO_IMPORT:
            self._draw_audio_import_icon(painter, size, color)
        elif icon_type == WorkflowIcon.TIME_SEGMENT:
            self._draw_time_segment_icon(painter, size, color)
        elif icon_type == WorkflowIcon.ANIMATION_DESC:
            self._draw_animation_desc_icon(painter, size, color)
        elif icon_type == WorkflowIcon.AI_GENERATION:
            self._draw_ai_generation_icon(painter, size, color)
        elif icon_type == WorkflowIcon.PREVIEW_ADJUST:
            self._draw_preview_adjust_icon(painter, size, color)
        elif icon_type == WorkflowIcon.EXPORT_RENDER:
            self._draw_export_render_icon(painter, size, color)
        
        painter.end()
        
        # 缓存图标
        icon = QIcon(pixmap)
        self.icon_cache[cache_key] = icon
        
        return pixmap
    
    def render_action_icon(self, icon_type: ActionIcon, size: int = 24, color: str = "#424242") -> QPixmap:
        """渲染操作动作图标"""
        cache_key = f"{icon_type.value}_{size}_{color}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key].pixmap(size, size)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据图标类型绘制不同的图标
        if icon_type == ActionIcon.PLAY:
            self._draw_play_icon(painter, size, color)
        elif icon_type == ActionIcon.PAUSE:
            self._draw_pause_icon(painter, size, color)
        elif icon_type == ActionIcon.STOP:
            self._draw_stop_icon(painter, size, color)
        elif icon_type == ActionIcon.RECORD:
            self._draw_record_icon(painter, size, color)
        elif icon_type == ActionIcon.EDIT:
            self._draw_edit_icon(painter, size, color)
        elif icon_type == ActionIcon.DELETE:
            self._draw_delete_icon(painter, size, color)
        elif icon_type == ActionIcon.COPY:
            self._draw_copy_icon(painter, size, color)
        elif icon_type == ActionIcon.PASTE:
            self._draw_paste_icon(painter, size, color)
        elif icon_type == ActionIcon.UNDO:
            self._draw_undo_icon(painter, size, color)
        elif icon_type == ActionIcon.REDO:
            self._draw_redo_icon(painter, size, color)
        elif icon_type == ActionIcon.SAVE:
            self._draw_save_icon(painter, size, color)
        elif icon_type == ActionIcon.LOAD:
            self._draw_load_icon(painter, size, color)
        
        painter.end()
        
        # 缓存图标
        icon = QIcon(pixmap)
        self.icon_cache[cache_key] = icon
        
        return pixmap
    
    def render_status_icon(self, icon_type: StatusIcon, size: int = 24, color: str = "#4CAF50") -> QPixmap:
        """渲染状态指示图标"""
        cache_key = f"{icon_type.value}_{size}_{color}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key].pixmap(size, size)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据图标类型绘制不同的图标
        if icon_type == StatusIcon.SUCCESS:
            self._draw_success_icon(painter, size, color)
        elif icon_type == StatusIcon.WARNING:
            self._draw_warning_icon(painter, size, color)
        elif icon_type == StatusIcon.ERROR:
            self._draw_error_icon(painter, size, color)
        elif icon_type == StatusIcon.INFO:
            self._draw_info_icon(painter, size, color)
        elif icon_type == StatusIcon.LOADING:
            self._draw_loading_icon(painter, size, color)
        elif icon_type == StatusIcon.PROCESSING:
            self._draw_processing_icon(painter, size, color)
        
        painter.end()
        
        # 缓存图标
        icon = QIcon(pixmap)
        self.icon_cache[cache_key] = icon
        
        return pixmap
    
    def _draw_audio_import_icon(self, painter: QPainter, size: int, color: str):
        """绘制音频导入图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制音频波形
        center_y = size // 2
        wave_width = size - 8
        wave_start_x = 4
        
        for i in range(0, wave_width, 3):
            x = wave_start_x + i
            height = int(size * 0.3 * math.sin(i * 0.3) + size * 0.1)
            painter.drawLine(x, center_y - height//2, x, center_y + height//2)
        
        # 绘制导入箭头
        arrow_size = size // 4
        arrow_x = size - arrow_size - 2
        arrow_y = 2
        
        path = QPainterPath()
        path.moveTo(arrow_x, arrow_y + arrow_size)
        path.lineTo(arrow_x + arrow_size//2, arrow_y)
        path.lineTo(arrow_x + arrow_size, arrow_y + arrow_size)
        path.lineTo(arrow_x + arrow_size//2, arrow_y + arrow_size//2)
        path.lineTo(arrow_x + arrow_size//2, arrow_y + arrow_size)
        path.closeSubpath()
        
        painter.fillPath(path, QBrush(QColor(color)))
    
    def _draw_time_segment_icon(self, painter: QPainter, size: int, color: str):
        """绘制时间段标记图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制时间轴
        timeline_y = size // 2
        painter.drawLine(4, timeline_y, size - 4, timeline_y)
        
        # 绘制时间段标记
        segment_width = (size - 8) // 3
        for i in range(3):
            x = 4 + i * segment_width
            painter.drawLine(x, timeline_y - 6, x, timeline_y + 6)
        
        # 绘制最后一个标记
        painter.drawLine(size - 4, timeline_y - 6, size - 4, timeline_y + 6)
    
    def _draw_animation_desc_icon(self, painter: QPainter, size: int, color: str):
        """绘制动画描述图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制文档
        doc_rect = QRect(4, 4, size - 8, size - 8)
        painter.drawRect(doc_rect)
        
        # 绘制文本行
        line_y = 8
        for i in range(3):
            line_width = size - 12 - (i * 4)
            painter.drawLine(8, line_y, 8 + line_width, line_y)
            line_y += 4
    
    def _draw_ai_generation_icon(self, painter: QPainter, size: int, color: str):
        """绘制AI生成图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制AI大脑图标
        center = size // 2
        radius = size // 3
        
        # 主圆
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
        
        # 神经网络连接线
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x1 = center + radius * 0.6 * math.cos(rad)
            y1 = center + radius * 0.6 * math.sin(rad)
            x2 = center + radius * 0.9 * math.cos(rad)
            y2 = center + radius * 0.9 * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            painter.drawEllipse(int(x2-2), int(y2-2), 4, 4)
    
    def _draw_preview_adjust_icon(self, painter: QPainter, size: int, color: str):
        """绘制预览调整图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制眼睛
        center = size // 2
        eye_width = size - 8
        eye_height = size // 2
        
        # 眼睛轮廓
        eye_rect = QRect(4, center - eye_height//2, eye_width, eye_height)
        painter.drawEllipse(eye_rect)
        
        # 瞳孔
        pupil_size = eye_height // 2
        pupil_rect = QRect(center - pupil_size//2, center - pupil_size//2, pupil_size, pupil_size)
        painter.fillRect(pupil_rect, QBrush(QColor(color)))
    
    def _draw_export_render_icon(self, painter: QPainter, size: int, color: str):
        """绘制导出渲染图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制导出箭头
        center = size // 2
        arrow_size = size - 8
        
        path = QPainterPath()
        path.moveTo(4, center)
        path.lineTo(center, 4)
        path.lineTo(center, center - 2)
        path.lineTo(size - 4, center - 2)
        path.lineTo(size - 4, center + 2)
        path.lineTo(center, center + 2)
        path.lineTo(center, size - 4)
        path.closeSubpath()
        
        painter.fillPath(path, QBrush(QColor(color)))
    
    def _draw_play_icon(self, painter: QPainter, size: int, color: str):
        """绘制播放图标"""
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制播放三角形
        center = size // 2
        triangle_size = size - 8
        
        path = QPainterPath()
        path.moveTo(4, 4)
        path.lineTo(size - 4, center)
        path.lineTo(4, size - 4)
        path.closeSubpath()
        
        painter.fillPath(path, QBrush(QColor(color)))
    
    def _draw_pause_icon(self, painter: QPainter, size: int, color: str):
        """绘制暂停图标"""
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制两个竖条
        bar_width = (size - 12) // 2
        bar_height = size - 8
        
        painter.fillRect(4, 4, bar_width, bar_height, QBrush(QColor(color)))
        painter.fillRect(size - 4 - bar_width, 4, bar_width, bar_height, QBrush(QColor(color)))
    
    def _draw_stop_icon(self, painter: QPainter, size: int, color: str):
        """绘制停止图标"""
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制正方形
        square_size = size - 8
        painter.fillRect(4, 4, square_size, square_size, QBrush(QColor(color)))
    
    def _draw_record_icon(self, painter: QPainter, size: int, color: str):
        """绘制录制图标"""
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制圆形
        center = size // 2
        radius = (size - 8) // 2
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
    
    def _draw_edit_icon(self, painter: QPainter, size: int, color: str):
        """绘制编辑图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制铅笔
        painter.drawLine(4, size - 4, size - 4, 4)
        painter.drawLine(size - 8, 4, size - 4, 8)
        painter.drawLine(4, size - 8, 8, size - 4)
    
    def _draw_delete_icon(self, painter: QPainter, size: int, color: str):
        """绘制删除图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制垃圾桶
        painter.drawRect(6, 8, size - 12, size - 12)
        painter.drawLine(4, 8, size - 4, 8)
        painter.drawLine(8, 4, 8, 8)
        painter.drawLine(size - 8, 4, size - 8, 8)
        
        # 垃圾桶内的线条
        painter.drawLine(10, 12, 10, size - 6)
        painter.drawLine(size - 10, 12, size - 10, size - 6)
    
    def _draw_copy_icon(self, painter: QPainter, size: int, color: str):
        """绘制复制图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制两个重叠的矩形
        painter.drawRect(4, 4, size - 8, size - 8)
        painter.drawRect(8, 8, size - 8, size - 8)
    
    def _draw_paste_icon(self, painter: QPainter, size: int, color: str):
        """绘制粘贴图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制剪贴板
        painter.drawRect(6, 8, size - 12, size - 12)
        painter.drawRect(8, 4, size - 16, 6)
    
    def _draw_undo_icon(self, painter: QPainter, size: int, color: str):
        """绘制撤销图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制弯曲箭头
        center = size // 2
        radius = (size - 8) // 2
        
        # 弧线
        painter.drawArc(4, 4, size - 8, size - 8, 0, 180 * 16)
        
        # 箭头
        painter.drawLine(4, center, 8, center - 4)
        painter.drawLine(4, center, 8, center + 4)
    
    def _draw_redo_icon(self, painter: QPainter, size: int, color: str):
        """绘制重做图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制弯曲箭头（方向相反）
        center = size // 2
        radius = (size - 8) // 2
        
        # 弧线
        painter.drawArc(4, 4, size - 8, size - 8, 0, 180 * 16)
        
        # 箭头
        painter.drawLine(size - 4, center, size - 8, center - 4)
        painter.drawLine(size - 4, center, size - 8, center + 4)
    
    def _draw_save_icon(self, painter: QPainter, size: int, color: str):
        """绘制保存图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制软盘
        painter.drawRect(4, 4, size - 8, size - 8)
        painter.fillRect(6, 6, size - 12, 6, QBrush(QColor(color)))
        painter.drawRect(8, size - 10, size - 16, 6)
    
    def _draw_load_icon(self, painter: QPainter, size: int, color: str):
        """绘制加载图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制文件夹
        painter.drawRect(4, 8, size - 8, size - 12)
        painter.drawLine(4, 8, 10, 4)
        painter.drawLine(10, 4, 16, 4)
        painter.drawLine(16, 4, 16, 8)
    
    def _draw_success_icon(self, painter: QPainter, size: int, color: str):
        """绘制成功图标"""
        painter.setPen(QPen(QColor(color), 3))
        
        # 绘制对勾
        center = size // 2
        painter.drawLine(6, center, center - 2, size - 6)
        painter.drawLine(center - 2, size - 6, size - 4, 6)
    
    def _draw_warning_icon(self, painter: QPainter, size: int, color: str):
        """绘制警告图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制三角形
        path = QPainterPath()
        path.moveTo(size // 2, 4)
        path.lineTo(4, size - 4)
        path.lineTo(size - 4, size - 4)
        path.closeSubpath()
        
        painter.drawPath(path)
        
        # 感叹号
        center = size // 2
        painter.drawLine(center, 8, center, center + 2)
        painter.drawEllipse(center - 1, size - 8, 2, 2)
    
    def _draw_error_icon(self, painter: QPainter, size: int, color: str):
        """绘制错误图标"""
        painter.setPen(QPen(QColor(color), 3))
        
        # 绘制X
        painter.drawLine(6, 6, size - 6, size - 6)
        painter.drawLine(6, size - 6, size - 6, 6)
    
    def _draw_info_icon(self, painter: QPainter, size: int, color: str):
        """绘制信息图标"""
        painter.setPen(QPen(QColor(color), 2))
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制圆形
        center = size // 2
        radius = (size - 8) // 2
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
        
        # i字母
        painter.drawEllipse(center - 1, 8, 2, 2)
        painter.drawLine(center, 12, center, size - 6)
    
    def _draw_loading_icon(self, painter: QPainter, size: int, color: str):
        """绘制加载图标"""
        painter.setPen(QPen(QColor(color), 2))
        
        # 绘制旋转圆圈
        center = size // 2
        radius = (size - 8) // 2
        
        # 绘制部分圆弧表示加载
        painter.drawArc(center - radius, center - radius, radius * 2, radius * 2, 0, 270 * 16)
    
    def _draw_processing_icon(self, painter: QPainter, size: int, color: str):
        """绘制处理中图标"""
        painter.setBrush(QBrush(QColor(color)))
        
        # 绘制三个点
        dot_size = 4
        spacing = 6
        start_x = (size - (3 * dot_size + 2 * spacing)) // 2
        center_y = size // 2
        
        for i in range(3):
            x = start_x + i * (dot_size + spacing)
            painter.drawEllipse(x, center_y - dot_size//2, dot_size, dot_size)


class ProfessionalIconManager(QObject):
    """专业图标管理器"""

    icon_theme_changed = pyqtSignal(str)  # 图标主题改变信号

    def __init__(self):
        super().__init__()
        self.renderer = ProfessionalIconRenderer()
        self.current_theme = "default"
        self.icon_size = 24
        self.icon_color = "#424242"

        # 图标映射表 - 将旧的Emoji图标映射到新的专业图标
        self.icon_mapping = {
            # 工作流程图标映射
            "🎵": WorkflowIcon.AUDIO_IMPORT,
            "⏱️": WorkflowIcon.TIME_SEGMENT,
            "📝": WorkflowIcon.ANIMATION_DESC,
            "🤖": WorkflowIcon.AI_GENERATION,
            "👁️": WorkflowIcon.PREVIEW_ADJUST,
            "📤": WorkflowIcon.EXPORT_RENDER,

            # 操作动作图标映射
            "▶️": ActionIcon.PLAY,
            "⏸️": ActionIcon.PAUSE,
            "⏹️": ActionIcon.STOP,
            "🔴": ActionIcon.RECORD,
            "✏️": ActionIcon.EDIT,
            "🗑️": ActionIcon.DELETE,
            "📋": ActionIcon.COPY,
            "📄": ActionIcon.PASTE,
            "↶": ActionIcon.UNDO,
            "↷": ActionIcon.REDO,
            "💾": ActionIcon.SAVE,
            "📂": ActionIcon.LOAD,

            # 状态图标映射
            "✅": StatusIcon.SUCCESS,
            "⚠️": StatusIcon.WARNING,
            "❌": StatusIcon.ERROR,
            "ℹ️": StatusIcon.INFO,
            "⏳": StatusIcon.LOADING,
            "⚙️": StatusIcon.PROCESSING
        }

        logger.info("专业图标管理器初始化完成")

    def get_workflow_icon(self, icon_type: WorkflowIcon, size: int = None, color: str = None) -> QPixmap:
        """获取工作流程图标"""
        size = size or self.icon_size
        color = color or self.icon_color
        return self.renderer.render_workflow_icon(icon_type, size, color)

    def get_action_icon(self, icon_type: ActionIcon, size: int = None, color: str = None) -> QPixmap:
        """获取操作动作图标"""
        size = size or self.icon_size
        color = color or self.icon_color
        return self.renderer.render_action_icon(icon_type, size, color)

    def get_status_icon(self, icon_type: StatusIcon, size: int = None, color: str = None) -> QPixmap:
        """获取状态指示图标"""
        size = size or self.icon_size
        color = color or self.icon_color
        return self.renderer.render_status_icon(icon_type, size, color)

    def get_icon_by_emoji(self, emoji: str, size: int = None, color: str = None) -> Optional[QPixmap]:
        """通过Emoji获取对应的专业图标"""
        if emoji not in self.icon_mapping:
            return None

        icon_enum = self.icon_mapping[emoji]
        size = size or self.icon_size
        color = color or self.icon_color

        # 根据图标类型调用相应的渲染方法
        if isinstance(icon_enum, WorkflowIcon):
            return self.renderer.render_workflow_icon(icon_enum, size, color)
        elif isinstance(icon_enum, ActionIcon):
            return self.renderer.render_action_icon(icon_enum, size, color)
        elif isinstance(icon_enum, StatusIcon):
            return self.renderer.render_status_icon(icon_enum, size, color)

        return None

    def replace_emoji_in_text(self, text: str, size: int = None, color: str = None) -> str:
        """替换文本中的Emoji为专业图标描述"""
        size = size or self.icon_size
        color = color or self.icon_color

        # 图标名称映射
        icon_names = {
            "🎵": "音频导入",
            "⏱️": "时间段标记",
            "📝": "动画描述",
            "🤖": "AI生成",
            "👁️": "预览调整",
            "📤": "导出渲染",
            "▶️": "播放",
            "⏸️": "暂停",
            "⏹️": "停止",
            "🔴": "录制",
            "✏️": "编辑",
            "🗑️": "删除",
            "📋": "复制",
            "📄": "粘贴",
            "↶": "撤销",
            "↷": "重做",
            "💾": "保存",
            "📂": "加载",
            "✅": "成功",
            "⚠️": "警告",
            "❌": "错误",
            "ℹ️": "信息",
            "⏳": "加载中",
            "⚙️": "处理中"
        }

        result_text = text
        for emoji, name in icon_names.items():
            result_text = result_text.replace(emoji, name)

        return result_text

    def set_default_size(self, size: int):
        """设置默认图标大小"""
        self.icon_size = size
        logger.debug(f"默认图标大小设置为: {size}px")

    def set_default_color(self, color: str):
        """设置默认图标颜色"""
        self.icon_color = color
        logger.debug(f"默认图标颜色设置为: {color}")

    def clear_cache(self):
        """清除图标缓存"""
        self.renderer.icon_cache.clear()
        self.renderer.svg_cache.clear()
        logger.info("图标缓存已清除")

    def get_icon_statistics(self) -> Dict[str, int]:
        """获取图标统计信息"""
        return {
            "workflow_icons": len([i for i in WorkflowIcon]),
            "action_icons": len([i for i in ActionIcon]),
            "status_icons": len([i for i in StatusIcon]),
            "cached_icons": len(self.renderer.icon_cache),
            "emoji_mappings": len(self.icon_mapping)
        }


class IconWidget(QLabel):
    """图标组件"""

    def __init__(self, icon_type, size: int = 24, color: str = "#424242"):
        super().__init__()
        self.icon_type = icon_type
        self.icon_size = size
        self.icon_color = color
        self.icon_manager = ProfessionalIconManager()

        self.update_icon()

    def update_icon(self):
        """更新图标"""
        pixmap = None

        if isinstance(self.icon_type, WorkflowIcon):
            pixmap = self.icon_manager.get_workflow_icon(self.icon_type, self.icon_size, self.icon_color)
        elif isinstance(self.icon_type, ActionIcon):
            pixmap = self.icon_manager.get_action_icon(self.icon_type, self.icon_size, self.icon_color)
        elif isinstance(self.icon_type, StatusIcon):
            pixmap = self.icon_manager.get_status_icon(self.icon_type, self.icon_size, self.icon_color)
        elif isinstance(self.icon_type, str):
            # 如果是Emoji字符串
            pixmap = self.icon_manager.get_icon_by_emoji(self.icon_type, self.icon_size, self.icon_color)

        if pixmap:
            self.setPixmap(pixmap)
            self.setFixedSize(self.icon_size, self.icon_size)

    def set_size(self, size: int):
        """设置图标大小"""
        self.icon_size = size
        self.update_icon()

    def set_color(self, color: str):
        """设置图标颜色"""
        self.icon_color = color
        self.update_icon()


class IconReplacementTool:
    """图标替换工具"""

    def __init__(self, icon_manager: ProfessionalIconManager):
        self.icon_manager = icon_manager
        self.replacement_log = []

        logger.info("图标替换工具初始化完成")

    def scan_and_replace_icons(self, widget: QWidget) -> int:
        """扫描并替换组件中的Emoji图标"""
        replacement_count = 0

        try:
            # 递归扫描所有子组件
            replacement_count += self._scan_widget_recursive(widget)

            logger.info(f"图标替换完成，共替换 {replacement_count} 个图标")

        except Exception as e:
            logger.error(f"图标替换失败: {e}")

        return replacement_count

    def _scan_widget_recursive(self, widget: QWidget) -> int:
        """递归扫描组件"""
        replacement_count = 0

        # 检查当前组件
        replacement_count += self._replace_widget_icons(widget)

        # 递归检查子组件
        for child in widget.findChildren(QWidget):
            replacement_count += self._replace_widget_icons(child)

        return replacement_count

    def _replace_widget_icons(self, widget: QWidget) -> int:
        """替换组件图标"""
        replacement_count = 0

        try:
            # 替换文本中的Emoji
            if hasattr(widget, 'text') and callable(widget.text):
                original_text = widget.text()
                new_text = self.icon_manager.replace_emoji_in_text(original_text)

                if original_text != new_text:
                    widget.setText(new_text)
                    replacement_count += 1

                    self.replacement_log.append({
                        'widget': widget.__class__.__name__,
                        'original': original_text,
                        'replaced': new_text
                    })

            # 替换工具提示中的Emoji
            if hasattr(widget, 'toolTip') and callable(widget.toolTip):
                original_tooltip = widget.toolTip()
                new_tooltip = self.icon_manager.replace_emoji_in_text(original_tooltip)

                if original_tooltip != new_tooltip:
                    widget.setToolTip(new_tooltip)
                    replacement_count += 1

            # 替换窗口标题中的Emoji
            if hasattr(widget, 'windowTitle') and callable(widget.windowTitle):
                original_title = widget.windowTitle()
                new_title = self.icon_manager.replace_emoji_in_text(original_title)

                if original_title != new_title:
                    widget.setWindowTitle(new_title)
                    replacement_count += 1

        except Exception as e:
            logger.error(f"替换组件图标失败: {e}")

        return replacement_count

    def get_replacement_log(self) -> List[Dict[str, str]]:
        """获取替换日志"""
        return self.replacement_log.copy()

    def clear_replacement_log(self):
        """清除替换日志"""
        self.replacement_log.clear()
