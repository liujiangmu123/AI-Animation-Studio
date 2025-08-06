"""
专业素材拖拽系统
支持多选、预览、智能放置等高级功能
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QMimeData, QPoint, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QDrag, QPainter, QPixmap, QColor, QFont, QPen, QBrush,
    QDragEnterEvent, QDragMoveEvent, QDropEvent
)
from typing import List, Optional, Dict, Any, Tuple
import json
import logging

from core.asset_management import EnhancedAsset

logger = logging.getLogger(__name__)

class DragPreviewWidget(QLabel):
    """拖拽预览组件"""
    
    def __init__(self, assets: List[EnhancedAsset], thumbnail_size: int = 64):
        super().__init__()
        self.assets = assets
        self.thumbnail_size = thumbnail_size
        
        self.create_preview()
    
    def create_preview(self):
        """创建预览图"""
        if not self.assets:
            return
        
        # 计算预览大小
        if len(self.assets) == 1:
            # 单个素材
            preview_size = self.thumbnail_size
        else:
            # 多个素材，显示堆叠效果
            preview_size = self.thumbnail_size + 20
        
        # 创建预览图
        pixmap = QPixmap(preview_size, preview_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if len(self.assets) == 1:
            self._draw_single_asset(painter, self.assets[0])
        else:
            self._draw_multiple_assets(painter, self.assets)
        
        painter.end()
        
        self.setPixmap(pixmap)
        self.setFixedSize(preview_size, preview_size)
    
    def _draw_single_asset(self, painter: QPainter, asset: EnhancedAsset):
        """绘制单个素材预览"""
        # 绘制缩略图背景
        rect = QRect(0, 0, self.thumbnail_size, self.thumbnail_size)
        painter.fillRect(rect, QColor("#F8F9FA"))
        painter.setPen(QPen(QColor("#DEE2E6"), 2))
        painter.drawRect(rect)
        
        # 尝试加载缩略图
        if asset.thumbnail.medium_path:
            try:
                thumbnail = QPixmap(asset.thumbnail.medium_path)
                if not thumbnail.isNull():
                    # 缩放并居中绘制
                    scaled = thumbnail.scaled(
                        self.thumbnail_size - 4, self.thumbnail_size - 4,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    x = (self.thumbnail_size - scaled.width()) // 2
                    y = (self.thumbnail_size - scaled.height()) // 2
                    painter.drawPixmap(x, y, scaled)
                    return
            except Exception as e:
                logger.warning(f"加载拖拽预览缩略图失败: {e}")
        
        # 绘制默认图标
        painter.setPen(QColor("#6C757D"))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, asset.asset_type.value.upper())
    
    def _draw_multiple_assets(self, painter: QPainter, assets: List[EnhancedAsset]):
        """绘制多个素材预览（堆叠效果）"""
        # 绘制堆叠的矩形
        offsets = [(0, 0), (5, 5), (10, 10)]
        colors = [QColor("#007BFF"), QColor("#0056B3"), QColor("#004085")]
        
        for i, (offset_x, offset_y) in enumerate(offsets[:min(3, len(assets))]):
            rect = QRect(offset_x, offset_y, self.thumbnail_size, self.thumbnail_size)
            painter.fillRect(rect, colors[i])
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.drawRect(rect)
        
        # 绘制数量标识
        count_text = str(len(assets))
        painter.setPen(QColor("#FFFFFF"))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        text_rect = QRect(0, 0, self.thumbnail_size, self.thumbnail_size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, count_text)


class AssetDragHandler:
    """素材拖拽处理器"""
    
    MIME_TYPE = "application/x-asset-list"
    
    @staticmethod
    def create_drag_data(assets: List[EnhancedAsset]) -> QMimeData:
        """创建拖拽数据"""
        mime_data = QMimeData()
        
        # 设置素材ID列表
        asset_ids = [asset.asset_id for asset in assets]
        mime_data.setData(AssetDragHandler.MIME_TYPE, json.dumps(asset_ids).encode())
        
        # 设置文本数据（用于外部应用）
        if len(assets) == 1:
            mime_data.setText(assets[0].file_path)
        else:
            file_paths = [asset.file_path for asset in assets]
            mime_data.setText("\n".join(file_paths))
        
        # 设置URL数据
        from PyQt6.QtCore import QUrl
        urls = [QUrl.fromLocalFile(asset.file_path) for asset in assets]
        mime_data.setUrls(urls)
        
        return mime_data
    
    @staticmethod
    def extract_asset_ids(mime_data: QMimeData) -> List[str]:
        """从拖拽数据中提取素材ID"""
        try:
            if mime_data.hasFormat(AssetDragHandler.MIME_TYPE):
                data = mime_data.data(AssetDragHandler.MIME_TYPE).data()
                return json.loads(data.decode())
            return []
        except Exception as e:
            logger.error(f"提取拖拽素材ID失败: {e}")
            return []
    
    @staticmethod
    def can_accept_drop(mime_data: QMimeData) -> bool:
        """检查是否可以接受拖拽"""
        return (mime_data.hasFormat(AssetDragHandler.MIME_TYPE) or
                mime_data.hasUrls() or
                mime_data.hasText())


class DraggableAssetWidget(QWidget):
    """支持拖拽的素材组件基类"""
    
    drag_started = pyqtSignal(list)  # List[EnhancedAsset]
    
    def __init__(self):
        super().__init__()
        self.drag_start_position = QPoint()
        self.dragging = False
        self.selected_assets: List[EnhancedAsset] = []
    
    def set_selected_assets(self, assets: List[EnhancedAsset]):
        """设置选中的素材"""
        self.selected_assets = assets
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if (event.buttons() & Qt.MouseButton.LeftButton and
            not self.dragging and
            self.selected_assets and
            (event.position().toPoint() - self.drag_start_position).manhattanLength() >= 10):
            
            self.start_drag()
        
        super().mouseMoveEvent(event)
    
    def start_drag(self):
        """开始拖拽"""
        if not self.selected_assets:
            return
        
        self.dragging = True
        
        try:
            # 创建拖拽对象
            drag = QDrag(self)
            
            # 设置拖拽数据
            mime_data = AssetDragHandler.create_drag_data(self.selected_assets)
            drag.setMimeData(mime_data)
            
            # 创建拖拽预览
            preview_widget = DragPreviewWidget(self.selected_assets)
            drag.setPixmap(preview_widget.pixmap())
            drag.setHotSpot(QPoint(preview_widget.width() // 2, preview_widget.height() // 2))
            
            # 发送信号
            self.drag_started.emit(self.selected_assets)
            
            # 执行拖拽
            drop_action = drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)
            
            logger.info(f"拖拽完成: {len(self.selected_assets)} 个素材, 动作: {drop_action}")
            
        except Exception as e:
            logger.error(f"拖拽失败: {e}")
        finally:
            self.dragging = False


class DropTargetWidget(QWidget):
    """拖拽目标组件基类"""
    
    assets_dropped = pyqtSignal(list, QPoint)  # List[asset_ids], drop_position
    files_dropped = pyqtSignal(list, QPoint)   # List[file_paths], drop_position
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.drag_hover = False
        
        # 拖拽提示定时器
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_drop_hint)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if AssetDragHandler.can_accept_drop(event.mimeData()):
            event.acceptProposedAction()
            self.drag_hover = True
            self.update()
            
            # 启动提示定时器
            self.hover_timer.start(500)
        else:
            event.ignore()
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        """拖拽移动事件"""
        if AssetDragHandler.can_accept_drop(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.drag_hover = False
        self.hover_timer.stop()
        self.update()
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self.drag_hover = False
        self.hover_timer.stop()
        self.update()
        
        mime_data = event.mimeData()
        drop_position = event.position().toPoint()
        
        # 处理素材拖拽
        asset_ids = AssetDragHandler.extract_asset_ids(mime_data)
        if asset_ids:
            self.assets_dropped.emit(asset_ids, drop_position)
            event.acceptProposedAction()
            return
        
        # 处理文件拖拽
        if mime_data.hasUrls():
            file_paths = []
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_paths.append(url.toLocalFile())
            
            if file_paths:
                self.files_dropped.emit(file_paths, drop_position)
                event.acceptProposedAction()
                return
        
        event.ignore()
    
    def show_drop_hint(self):
        """显示拖拽提示"""
        # 子类可以重写此方法来显示自定义提示
        pass
    
    def paintEvent(self, event):
        """绘制事件"""
        super().paintEvent(event)
        
        if self.drag_hover:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 绘制拖拽高亮边框
            pen = QPen(QColor("#007BFF"), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 123, 255, 30)))
            
            rect = self.rect().adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(rect, 8, 8)
            
            painter.end()


class SmartDropZone(DropTargetWidget):
    """智能拖拽区域"""
    
    def __init__(self, zone_type: str = "canvas"):
        super().__init__()
        self.zone_type = zone_type
        self.drop_hints = {
            "canvas": "拖拽到此处添加到舞台",
            "timeline": "拖拽到此处添加到时间轴",
            "library": "拖拽到此处添加到素材库"
        }
    
    def show_drop_hint(self):
        """显示智能拖拽提示"""
        hint_text = self.drop_hints.get(self.zone_type, "拖拽到此处")
        
        # 这里可以显示工具提示或其他UI反馈
        self.setToolTip(hint_text)
    
    def calculate_smart_position(self, drop_position: QPoint, asset_count: int) -> List[QPoint]:
        """计算智能放置位置"""
        positions = []
        
        if asset_count == 1:
            positions.append(drop_position)
        else:
            # 多个素材时，计算网格排列
            grid_size = int(asset_count ** 0.5) + 1
            spacing = 120
            
            start_x = drop_position.x() - (grid_size * spacing) // 2
            start_y = drop_position.y() - (grid_size * spacing) // 2
            
            for i in range(asset_count):
                row = i // grid_size
                col = i % grid_size
                x = start_x + col * spacing
                y = start_y + row * spacing
                positions.append(QPoint(x, y))
        
        return positions
