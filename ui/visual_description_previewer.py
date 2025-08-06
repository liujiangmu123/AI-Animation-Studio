"""
AI Animation Studio - 可视化描述预览器
将文字描述转换为可视化预览，帮助用户更好地理解和完善动画描述
"""

import math
import json
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGroupBox, QSlider, QComboBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QLinearGradient

from core.logger import get_logger

logger = get_logger("visual_description_previewer")


class AnimationPreviewCanvas(QWidget):
    """动画预览画布"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        
        # 预览元素
        self.preview_elements = []
        self.animation_paths = []
        self.current_time = 0.0
        self.total_duration = 3.0
        self.is_playing = False
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        # 网格设置
        self.show_grid = True
        self.grid_size = 20
        
        logger.info("动画预览画布初始化完成")
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制网格
        if self.show_grid:
            self.draw_grid(painter)
        
        # 绘制动画路径
        self.draw_animation_paths(painter)
        
        # 绘制预览元素
        self.draw_preview_elements(painter)
        
        # 绘制时间指示器
        self.draw_time_indicator(painter)
    
    def draw_grid(self, painter: QPainter):
        """绘制网格"""
        painter.setPen(QPen(QColor("#e0e0e0"), 1))
        
        width = self.width()
        height = self.height()
        
        # 垂直线
        for x in range(0, width, self.grid_size):
            painter.drawLine(x, 0, x, height)
        
        # 水平线
        for y in range(0, height, self.grid_size):
            painter.drawLine(0, y, width, y)
    
    def draw_animation_paths(self, painter: QPainter):
        """绘制动画路径"""
        painter.setPen(QPen(QColor("#2196F3"), 2, Qt.PenStyle.DashLine))
        
        for path in self.animation_paths:
            if len(path) > 1:
                for i in range(len(path) - 1):
                    painter.drawLine(path[i], path[i + 1])
    
    def draw_preview_elements(self, painter: QPainter):
        """绘制预览元素"""
        for element in self.preview_elements:
            self.draw_element(painter, element)
    
    def draw_element(self, painter: QPainter, element: Dict[str, Any]):
        """绘制单个元素"""
        try:
            # 计算当前位置和状态
            current_state = self.calculate_element_state(element, self.current_time)
            
            # 设置画笔和画刷
            color = QColor(element.get("color", "#2196F3"))
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            
            # 应用透明度
            opacity = current_state.get("opacity", 1.0)
            color.setAlphaF(opacity)
            painter.setBrush(QBrush(color))
            
            # 绘制元素
            element_type = element.get("type", "rectangle")
            x = current_state.get("x", 100)
            y = current_state.get("y", 100)
            width = current_state.get("width", 50)
            height = current_state.get("height", 50)
            
            if element_type == "rectangle":
                painter.drawRect(x, y, width, height)
            elif element_type == "circle":
                painter.drawEllipse(x, y, width, height)
            elif element_type == "text":
                painter.setPen(QPen(color, 1))
                painter.setFont(QFont("Arial", 12))
                painter.drawText(x, y, element.get("text", "文本"))
            
            # 绘制元素标签
            painter.setPen(QPen(QColor("#666"), 1))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(x, y - 5, element.get("name", f"元素{element.get('id', '')}"))
            
        except Exception as e:
            logger.error(f"绘制元素失败: {e}")
    
    def calculate_element_state(self, element: Dict[str, Any], time: float) -> Dict[str, Any]:
        """计算元素在指定时间的状态"""
        try:
            animation = element.get("animation", {})
            
            if not animation or time < animation.get("start_time", 0):
                # 返回初始状态
                return element.get("initial_state", {})
            
            start_time = animation.get("start_time", 0)
            duration = animation.get("duration", 1.0)
            end_time = start_time + duration
            
            if time >= end_time:
                # 返回结束状态
                return animation.get("end_state", element.get("initial_state", {}))
            
            # 计算动画进度
            progress = (time - start_time) / duration
            
            # 应用缓动函数
            easing = animation.get("easing", "ease")
            eased_progress = self.apply_easing(progress, easing)
            
            # 插值计算当前状态
            initial_state = element.get("initial_state", {})
            end_state = animation.get("end_state", {})
            
            current_state = {}
            for key in initial_state:
                if key in end_state:
                    initial_value = initial_state[key]
                    end_value = end_state[key]
                    
                    if isinstance(initial_value, (int, float)) and isinstance(end_value, (int, float)):
                        current_value = initial_value + (end_value - initial_value) * eased_progress
                        current_state[key] = current_value
                    else:
                        # 非数值属性，使用阶跃变化
                        current_state[key] = end_value if eased_progress > 0.5 else initial_value
                else:
                    current_state[key] = initial_state[key]
            
            return current_state
            
        except Exception as e:
            logger.error(f"计算元素状态失败: {e}")
            return element.get("initial_state", {})
    
    def apply_easing(self, progress: float, easing: str) -> float:
        """应用缓动函数"""
        try:
            if easing == "linear":
                return progress
            elif easing == "ease-in":
                return progress * progress
            elif easing == "ease-out":
                return 1 - (1 - progress) * (1 - progress)
            elif easing == "ease-in-out":
                if progress < 0.5:
                    return 2 * progress * progress
                else:
                    return 1 - 2 * (1 - progress) * (1 - progress)
            elif easing == "bounce":
                return self.bounce_easing(progress)
            else:
                return progress  # 默认线性
                
        except Exception as e:
            logger.error(f"应用缓动函数失败: {e}")
            return progress
    
    def bounce_easing(self, t: float) -> float:
        """弹跳缓动函数"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375
    
    def add_preview_element(self, element_data: Dict[str, Any]):
        """添加预览元素"""
        try:
            self.preview_elements.append(element_data)
            self.update()
            
        except Exception as e:
            logger.error(f"添加预览元素失败: {e}")
    
    def clear_preview(self):
        """清空预览"""
        self.preview_elements.clear()
        self.animation_paths.clear()
        self.current_time = 0.0
        self.update()
    
    def play_animation(self):
        """播放动画"""
        if not self.is_playing:
            self.is_playing = True
            self.current_time = 0.0
            self.animation_timer.start(50)  # 20 FPS
    
    def pause_animation(self):
        """暂停动画"""
        self.is_playing = False
        self.animation_timer.stop()
    
    def stop_animation(self):
        """停止动画"""
        self.is_playing = False
        self.animation_timer.stop()
        self.current_time = 0.0
        self.update()
    
    def update_animation(self):
        """更新动画"""
        self.current_time += 0.05  # 增加50ms
        
        if self.current_time >= self.total_duration:
            self.current_time = 0.0  # 循环播放
        
        self.update()
    
    def set_time(self, time: float):
        """设置时间"""
        self.current_time = max(0, min(time, self.total_duration))
        self.update()
    
    def draw_time_indicator(self, painter: QPainter):
        """绘制时间指示器"""
        if self.total_duration > 0:
            progress = self.current_time / self.total_duration
            x = int(progress * self.width())
            
            painter.setPen(QPen(QColor("#FF5722"), 3))
            painter.drawLine(x, 0, x, self.height())
            
            # 绘制时间标签
            painter.setPen(QPen(QColor("#333"), 1))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(x + 5, 15, f"{self.current_time:.1f}s")


class DescriptionToVisualizationConverter:
    """描述到可视化转换器"""
    
    def __init__(self):
        # 元素类型映射
        self.element_type_map = {
            "按钮": "rectangle",
            "方块": "rectangle", 
            "矩形": "rectangle",
            "圆形": "circle",
            "球": "circle",
            "圆": "circle",
            "文字": "text",
            "文本": "text",
            "标题": "text"
        }
        
        # 颜色映射
        self.color_map = {
            "红色": "#F44336",
            "蓝色": "#2196F3", 
            "绿色": "#4CAF50",
            "黄色": "#FFEB3B",
            "紫色": "#9C27B0",
            "橙色": "#FF9800",
            "粉色": "#E91E63",
            "青色": "#00BCD4"
        }
        
        # 动作映射
        self.action_map = {
            "移动": self.create_move_animation,
            "滑动": self.create_slide_animation,
            "旋转": self.create_rotate_animation,
            "缩放": self.create_scale_animation,
            "淡入": self.create_fade_in_animation,
            "淡出": self.create_fade_out_animation,
            "弹跳": self.create_bounce_animation
        }
    
    def convert_description_to_preview(self, description: str, analysis: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """将描述转换为预览元素"""
        try:
            elements = []
            
            # 解析描述中的元素
            detected_elements = self.detect_elements(description)
            
            for i, element_info in enumerate(detected_elements):
                element = self.create_preview_element(element_info, i)
                elements.append(element)
            
            # 如果没有检测到元素，创建默认元素
            if not elements:
                default_element = self.create_default_element(description)
                elements.append(default_element)
            
            logger.info(f"描述转换完成，生成 {len(elements)} 个预览元素")
            
            return elements
            
        except Exception as e:
            logger.error(f"转换描述到预览失败: {e}")
            return []
    
    def detect_elements(self, description: str) -> List[Dict[str, Any]]:
        """检测描述中的元素"""
        elements = []
        desc_lower = description.lower()
        
        try:
            # 检测元素类型
            for element_name, element_type in self.element_type_map.items():
                if element_name in desc_lower:
                    elements.append({
                        "name": element_name,
                        "type": element_type,
                        "color": self.detect_color(description),
                        "actions": self.detect_actions(description),
                        "position": self.detect_position(description),
                        "size": self.detect_size(description)
                    })
            
            # 如果没有明确的元素类型，根据动作推断
            if not elements:
                actions = self.detect_actions(description)
                if actions:
                    elements.append({
                        "name": "动画元素",
                        "type": "rectangle",
                        "color": self.detect_color(description),
                        "actions": actions,
                        "position": self.detect_position(description),
                        "size": self.detect_size(description)
                    })
            
        except Exception as e:
            logger.error(f"检测元素失败: {e}")
        
        return elements
    
    def detect_color(self, description: str) -> str:
        """检测颜色"""
        desc_lower = description.lower()
        
        for color_name, color_value in self.color_map.items():
            if color_name in desc_lower:
                return color_value
        
        return "#2196F3"  # 默认蓝色
    
    def detect_actions(self, description: str) -> List[str]:
        """检测动作"""
        actions = []
        desc_lower = description.lower()
        
        for action_name in self.action_map.keys():
            if action_name in desc_lower:
                actions.append(action_name)
        
        return actions
    
    def detect_position(self, description: str) -> Dict[str, Any]:
        """检测位置信息"""
        position = {"start": {"x": 100, "y": 150}, "end": {"x": 300, "y": 150}}
        desc_lower = description.lower()
        
        # 检测起始位置
        if "左" in desc_lower or "左侧" in desc_lower:
            position["start"]["x"] = 50
        elif "右" in desc_lower or "右侧" in desc_lower:
            position["start"]["x"] = 350
        elif "中" in desc_lower or "中央" in desc_lower:
            position["start"]["x"] = 200
        
        if "上" in desc_lower or "顶部" in desc_lower:
            position["start"]["y"] = 50
        elif "下" in desc_lower or "底部" in desc_lower:
            position["start"]["y"] = 250
        
        # 检测结束位置（简化实现）
        if "到右" in desc_lower:
            position["end"]["x"] = 350
        elif "到左" in desc_lower:
            position["end"]["x"] = 50
        elif "到中" in desc_lower:
            position["end"]["x"] = 200
        
        return position
    
    def detect_size(self, description: str) -> Dict[str, int]:
        """检测大小信息"""
        size = {"width": 50, "height": 50}
        desc_lower = description.lower()
        
        # 检测大小描述
        if "大" in desc_lower or "大型" in desc_lower:
            size = {"width": 80, "height": 80}
        elif "小" in desc_lower or "小型" in desc_lower:
            size = {"width": 30, "height": 30}
        elif "长" in desc_lower:
            size = {"width": 100, "height": 30}
        elif "高" in desc_lower:
            size = {"width": 30, "height": 100}
        
        return size
    
    def create_preview_element(self, element_info: Dict[str, Any], index: int) -> Dict[str, Any]:
        """创建预览元素"""
        try:
            position = element_info.get("position", {})
            size = element_info.get("size", {"width": 50, "height": 50})
            
            element = {
                "id": index,
                "name": element_info.get("name", f"元素{index}"),
                "type": element_info.get("type", "rectangle"),
                "color": element_info.get("color", "#2196F3"),
                "initial_state": {
                    "x": position.get("start", {}).get("x", 100),
                    "y": position.get("start", {}).get("y", 150),
                    "width": size.get("width", 50),
                    "height": size.get("height", 50),
                    "opacity": 1.0,
                    "rotation": 0,
                    "scale": 1.0
                }
            }
            
            # 创建动画
            actions = element_info.get("actions", [])
            if actions:
                element["animation"] = self.create_animation_from_actions(
                    actions, element["initial_state"], position
                )
            
            return element
            
        except Exception as e:
            logger.error(f"创建预览元素失败: {e}")
            return {}
    
    def create_default_element(self, description: str) -> Dict[str, Any]:
        """创建默认元素"""
        return {
            "id": 0,
            "name": "默认元素",
            "type": "rectangle",
            "color": self.detect_color(description),
            "initial_state": {
                "x": 100,
                "y": 150,
                "width": 50,
                "height": 50,
                "opacity": 1.0,
                "rotation": 0,
                "scale": 1.0
            },
            "animation": {
                "start_time": 0,
                "duration": 2.0,
                "easing": "ease-in-out",
                "end_state": {
                    "x": 300,
                    "y": 150,
                    "width": 50,
                    "height": 50,
                    "opacity": 1.0,
                    "rotation": 0,
                    "scale": 1.0
                }
            }
        }
    
    def create_animation_from_actions(self, actions: List[str], initial_state: Dict[str, Any], 
                                    position: Dict[str, Any]) -> Dict[str, Any]:
        """从动作创建动画"""
        try:
            animation = {
                "start_time": 0,
                "duration": 2.0,
                "easing": "ease-in-out",
                "end_state": initial_state.copy()
            }
            
            # 根据动作修改结束状态
            for action in actions:
                if action == "移动" or action == "滑动":
                    end_pos = position.get("end", position.get("start", {}))
                    animation["end_state"]["x"] = end_pos.get("x", initial_state["x"] + 200)
                    animation["end_state"]["y"] = end_pos.get("y", initial_state["y"])
                
                elif action == "旋转":
                    animation["end_state"]["rotation"] = 360
                
                elif action == "缩放":
                    animation["end_state"]["scale"] = 1.5
                    animation["end_state"]["width"] = int(initial_state["width"] * 1.5)
                    animation["end_state"]["height"] = int(initial_state["height"] * 1.5)
                
                elif action == "淡入":
                    animation["end_state"]["opacity"] = 1.0
                    initial_state["opacity"] = 0.0
                
                elif action == "淡出":
                    animation["end_state"]["opacity"] = 0.0
                
                elif action == "弹跳":
                    animation["easing"] = "bounce"
                    animation["end_state"]["y"] = initial_state["y"] - 50
            
            return animation
            
        except Exception as e:
            logger.error(f"创建动画失败: {e}")
            return {}
    
    # 具体动画创建方法
    def create_move_animation(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> Dict[str, Any]:
        """创建移动动画"""
        return {
            "type": "move",
            "start_position": start_pos,
            "end_position": end_pos,
            "duration": 2.0,
            "easing": "ease-in-out"
        }
    
    def create_slide_animation(self, direction: str) -> Dict[str, Any]:
        """创建滑动动画"""
        return {
            "type": "slide",
            "direction": direction,
            "distance": 200,
            "duration": 1.5,
            "easing": "ease-out"
        }
    
    def create_rotate_animation(self, degrees: float = 360) -> Dict[str, Any]:
        """创建旋转动画"""
        return {
            "type": "rotate",
            "degrees": degrees,
            "duration": 2.0,
            "easing": "linear"
        }
    
    def create_scale_animation(self, scale_factor: float = 1.5) -> Dict[str, Any]:
        """创建缩放动画"""
        return {
            "type": "scale",
            "scale_factor": scale_factor,
            "duration": 1.0,
            "easing": "ease-in-out"
        }
    
    def create_fade_in_animation(self) -> Dict[str, Any]:
        """创建淡入动画"""
        return {
            "type": "fade_in",
            "duration": 1.5,
            "easing": "ease-in"
        }
    
    def create_fade_out_animation(self) -> Dict[str, Any]:
        """创建淡出动画"""
        return {
            "type": "fade_out",
            "duration": 1.5,
            "easing": "ease-out"
        }
    
    def create_bounce_animation(self) -> Dict[str, Any]:
        """创建弹跳动画"""
        return {
            "type": "bounce",
            "height": 50,
            "duration": 1.0,
            "easing": "bounce"
        }


class VisualDescriptionPreviewer(QWidget):
    """可视化描述预览器"""
    
    # 信号定义
    preview_updated = pyqtSignal(list)           # 预览更新
    animation_state_changed = pyqtSignal(bool)   # 动画状态改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.converter = DescriptionToVisualizationConverter()
        self.current_elements = []
        
        self.setup_ui()
        
        logger.info("可视化描述预览器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # 预览画布
        self.preview_canvas = AnimationPreviewCanvas()
        layout.addWidget(self.preview_canvas)
        
        # 时间控制
        time_control = self.create_time_control()
        layout.addWidget(time_control)
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(panel)
        
        # 播放控制
        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.toggle_playback)
        layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_preview)
        layout.addWidget(self.stop_btn)
        
        layout.addWidget(QLabel("|"))
        
        # 视图控制
        self.grid_cb = QCheckBox("显示网格")
        self.grid_cb.setChecked(True)
        self.grid_cb.toggled.connect(self.toggle_grid)
        layout.addWidget(self.grid_cb)
        
        # 速度控制
        layout.addWidget(QLabel("速度:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(25, 200)  # 0.25x - 2x
        self.speed_slider.setValue(100)  # 1x
        self.speed_slider.setMaximumWidth(100)
        layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        layout.addWidget(self.speed_label)
        
        layout.addStretch()
        
        # 预览质量
        layout.addWidget(QLabel("质量:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["低", "中", "高"])
        self.quality_combo.setCurrentText("中")
        layout.addWidget(self.quality_combo)
        
        return panel
    
    def create_time_control(self):
        """创建时间控制"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(panel)
        
        # 时间滑块
        layout.addWidget(QLabel("时间:"))
        
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 300)  # 0-3秒，精度0.01秒
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.on_time_changed)
        layout.addWidget(self.time_slider)
        
        # 时间显示
        self.time_label = QLabel("0.0s / 3.0s")
        layout.addWidget(self.time_label)
        
        return panel
    
    def update_preview_from_description(self, description: str, analysis: Dict[str, Any] = None):
        """根据描述更新预览"""
        try:
            # 转换描述为预览元素
            elements = self.converter.convert_description_to_preview(description, analysis)
            
            # 更新画布
            self.preview_canvas.clear_preview()
            
            for element in elements:
                self.preview_canvas.add_preview_element(element)
            
            self.current_elements = elements
            
            # 发送更新信号
            self.preview_updated.emit(elements)
            
            logger.info(f"预览已更新，包含 {len(elements)} 个元素")
            
        except Exception as e:
            logger.error(f"更新预览失败: {e}")
    
    def toggle_playback(self):
        """切换播放状态"""
        if self.preview_canvas.is_playing:
            self.preview_canvas.pause_animation()
            self.play_btn.setText("▶️ 播放")
            self.animation_state_changed.emit(False)
        else:
            self.preview_canvas.play_animation()
            self.play_btn.setText("⏸️ 暂停")
            self.animation_state_changed.emit(True)
    
    def stop_preview(self):
        """停止预览"""
        self.preview_canvas.stop_animation()
        self.play_btn.setText("▶️ 播放")
        self.time_slider.setValue(0)
        self.animation_state_changed.emit(False)
    
    def toggle_grid(self, show: bool):
        """切换网格显示"""
        self.preview_canvas.show_grid = show
        self.preview_canvas.update()
    
    def on_time_changed(self, value: int):
        """时间改变事件"""
        time = value / 100.0  # 转换为秒
        self.preview_canvas.set_time(time)
        self.time_label.setText(f"{time:.1f}s / {self.preview_canvas.total_duration:.1f}s")
    
    def export_preview_as_image(self, file_path: str):
        """导出预览为图片"""
        try:
            pixmap = self.preview_canvas.grab()
            pixmap.save(file_path)
            logger.info(f"预览图片已导出: {file_path}")
            
        except Exception as e:
            logger.error(f"导出预览图片失败: {e}")
    
    def get_preview_data(self) -> Dict[str, Any]:
        """获取预览数据"""
        return {
            "elements": self.current_elements,
            "total_duration": self.preview_canvas.total_duration,
            "current_time": self.preview_canvas.current_time,
            "settings": {
                "show_grid": self.preview_canvas.show_grid,
                "grid_size": self.preview_canvas.grid_size,
                "quality": self.quality_combo.currentText()
            }
        }
