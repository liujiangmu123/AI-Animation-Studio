"""
AI Animation Studio - 动画过渡效果系统
实现界面元素的流畅动画过渡效果
"""

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QLabel, QPushButton
from PyQt6.QtCore import (Qt, pyqtSignal, QObject, QPropertyAnimation, QSequentialAnimationGroup,
                          QParallelAnimationGroup, QEasingCurve, QTimer, QRect, QPoint, QSize)
from PyQt6.QtGui import QColor, QPalette

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import json
from dataclasses import dataclass
import math

from core.logger import get_logger

logger = get_logger("animation_transition_system")


class AnimationType(Enum):
    """动画类型枚举"""
    FADE_IN = "fade_in"                 # 淡入
    FADE_OUT = "fade_out"               # 淡出
    SLIDE_IN_LEFT = "slide_in_left"     # 从左滑入
    SLIDE_IN_RIGHT = "slide_in_right"   # 从右滑入
    SLIDE_IN_UP = "slide_in_up"         # 从上滑入
    SLIDE_IN_DOWN = "slide_in_down"     # 从下滑入
    SLIDE_OUT_LEFT = "slide_out_left"   # 向左滑出
    SLIDE_OUT_RIGHT = "slide_out_right" # 向右滑出
    SLIDE_OUT_UP = "slide_out_up"       # 向上滑出
    SLIDE_OUT_DOWN = "slide_out_down"   # 向下滑出
    SCALE_IN = "scale_in"               # 缩放进入
    SCALE_OUT = "scale_out"             # 缩放退出
    BOUNCE_IN = "bounce_in"             # 弹跳进入
    BOUNCE_OUT = "bounce_out"           # 弹跳退出
    ROTATE_IN = "rotate_in"             # 旋转进入
    ROTATE_OUT = "rotate_out"           # 旋转退出


class EasingType(Enum):
    """缓动类型枚举"""
    LINEAR = QEasingCurve.Type.Linear
    IN_QUAD = QEasingCurve.Type.InQuad
    OUT_QUAD = QEasingCurve.Type.OutQuad
    IN_OUT_QUAD = QEasingCurve.Type.InOutQuad
    IN_CUBIC = QEasingCurve.Type.InCubic
    OUT_CUBIC = QEasingCurve.Type.OutCubic
    IN_OUT_CUBIC = QEasingCurve.Type.InOutCubic
    IN_BOUNCE = QEasingCurve.Type.InBounce
    OUT_BOUNCE = QEasingCurve.Type.OutBounce
    IN_OUT_BOUNCE = QEasingCurve.Type.InOutBounce
    IN_ELASTIC = QEasingCurve.Type.InElastic
    OUT_ELASTIC = QEasingCurve.Type.OutElastic
    IN_OUT_ELASTIC = QEasingCurve.Type.InOutElastic


@dataclass
class AnimationConfig:
    """动画配置"""
    duration: int = 300                 # 持续时间（毫秒）
    easing: EasingType = EasingType.IN_OUT_QUAD  # 缓动类型
    delay: int = 0                      # 延迟时间（毫秒）
    loop_count: int = 1                 # 循环次数（-1为无限循环）
    auto_reverse: bool = False          # 自动反向
    callback: Optional[Callable] = None # 完成回调


class AnimationTransitionManager(QObject):
    """动画过渡管理器"""
    
    animation_started = pyqtSignal(str, str)    # 动画开始信号 (widget_id, animation_type)
    animation_finished = pyqtSignal(str, str)   # 动画完成信号 (widget_id, animation_type)
    
    def __init__(self):
        super().__init__()
        self.active_animations: Dict[str, QPropertyAnimation] = {}
        self.animation_groups: Dict[str, QSequentialAnimationGroup] = {}
        self.widget_registry: Dict[str, QWidget] = {}
        
        # 预设动画配置
        self.preset_configs = {
            AnimationType.FADE_IN: AnimationConfig(300, EasingType.OUT_QUAD),
            AnimationType.FADE_OUT: AnimationConfig(300, EasingType.IN_QUAD),
            AnimationType.SLIDE_IN_LEFT: AnimationConfig(400, EasingType.OUT_CUBIC),
            AnimationType.SLIDE_IN_RIGHT: AnimationConfig(400, EasingType.OUT_CUBIC),
            AnimationType.SLIDE_IN_UP: AnimationConfig(400, EasingType.OUT_CUBIC),
            AnimationType.SLIDE_IN_DOWN: AnimationConfig(400, EasingType.OUT_CUBIC),
            AnimationType.SCALE_IN: AnimationConfig(350, EasingType.OUT_BOUNCE),
            AnimationType.SCALE_OUT: AnimationConfig(250, EasingType.IN_CUBIC),
            AnimationType.BOUNCE_IN: AnimationConfig(600, EasingType.OUT_BOUNCE),
            AnimationType.ROTATE_IN: AnimationConfig(500, EasingType.OUT_ELASTIC)
        }
        
        logger.info("动画过渡管理器初始化完成")
    
    def register_widget(self, widget_id: str, widget: QWidget):
        """注册组件"""
        self.widget_registry[widget_id] = widget
        logger.debug(f"注册动画组件: {widget_id}")
    
    def animate_widget(self, widget_id: str, animation_type: AnimationType, 
                      config: Optional[AnimationConfig] = None) -> bool:
        """为组件添加动画"""
        if widget_id not in self.widget_registry:
            logger.warning(f"组件未注册: {widget_id}")
            return False
        
        widget = self.widget_registry[widget_id]
        config = config or self.preset_configs.get(animation_type, AnimationConfig())
        
        # 停止现有动画
        self.stop_animation(widget_id)
        
        # 创建动画
        animation = self.create_animation(widget, animation_type, config)
        if not animation:
            return False
        
        # 设置动画属性
        animation.setDuration(config.duration)
        animation.setEasingCurve(config.easing.value)
        animation.setLoopCount(config.loop_count)
        
        # 连接信号
        animation.started.connect(lambda: self.animation_started.emit(widget_id, animation_type.value))
        animation.finished.connect(lambda: self.on_animation_finished(widget_id, animation_type.value, config.callback))
        
        # 延迟启动
        if config.delay > 0:
            QTimer.singleShot(config.delay, animation.start)
        else:
            animation.start()
        
        # 保存动画引用
        self.active_animations[widget_id] = animation
        
        logger.debug(f"启动动画: {widget_id} - {animation_type.value}")
        return True
    
    def create_animation(self, widget: QWidget, animation_type: AnimationType, 
                        config: AnimationConfig) -> Optional[QPropertyAnimation]:
        """创建动画"""
        try:
            if animation_type == AnimationType.FADE_IN:
                return self.create_fade_in_animation(widget)
            elif animation_type == AnimationType.FADE_OUT:
                return self.create_fade_out_animation(widget)
            elif animation_type == AnimationType.SLIDE_IN_LEFT:
                return self.create_slide_in_left_animation(widget)
            elif animation_type == AnimationType.SLIDE_IN_RIGHT:
                return self.create_slide_in_right_animation(widget)
            elif animation_type == AnimationType.SLIDE_IN_UP:
                return self.create_slide_in_up_animation(widget)
            elif animation_type == AnimationType.SLIDE_IN_DOWN:
                return self.create_slide_in_down_animation(widget)
            elif animation_type == AnimationType.SLIDE_OUT_LEFT:
                return self.create_slide_out_left_animation(widget)
            elif animation_type == AnimationType.SLIDE_OUT_RIGHT:
                return self.create_slide_out_right_animation(widget)
            elif animation_type == AnimationType.SLIDE_OUT_UP:
                return self.create_slide_out_up_animation(widget)
            elif animation_type == AnimationType.SLIDE_OUT_DOWN:
                return self.create_slide_out_down_animation(widget)
            elif animation_type == AnimationType.SCALE_IN:
                return self.create_scale_in_animation(widget)
            elif animation_type == AnimationType.SCALE_OUT:
                return self.create_scale_out_animation(widget)
            elif animation_type == AnimationType.BOUNCE_IN:
                return self.create_bounce_in_animation(widget)
            elif animation_type == AnimationType.BOUNCE_OUT:
                return self.create_bounce_out_animation(widget)
            elif animation_type == AnimationType.ROTATE_IN:
                return self.create_rotate_in_animation(widget)
            elif animation_type == AnimationType.ROTATE_OUT:
                return self.create_rotate_out_animation(widget)
            
        except Exception as e:
            logger.error(f"创建动画失败: {e}")
        
        return None
    
    def create_fade_in_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建淡入动画"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        
        return animation
    
    def create_fade_out_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建淡出动画"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        
        return animation
    
    def create_slide_in_left_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建从左滑入动画"""
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x() - widget.width(), original_pos.y())
        
        widget.move(start_pos)
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        
        return animation
    
    def create_slide_in_right_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建从右滑入动画"""
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x() + widget.width(), original_pos.y())
        
        widget.move(start_pos)
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        
        return animation
    
    def create_slide_in_up_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建从上滑入动画"""
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x(), original_pos.y() - widget.height())
        
        widget.move(start_pos)
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        
        return animation
    
    def create_slide_in_down_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建从下滑入动画"""
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x(), original_pos.y() + widget.height())
        
        widget.move(start_pos)
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        
        return animation
    
    def create_slide_out_left_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建向左滑出动画"""
        start_pos = widget.pos()
        end_pos = QPoint(start_pos.x() - widget.width(), start_pos.y())
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        
        return animation
    
    def create_slide_out_right_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建向右滑出动画"""
        start_pos = widget.pos()
        end_pos = QPoint(start_pos.x() + widget.width(), start_pos.y())
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        
        return animation
    
    def create_slide_out_up_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建向上滑出动画"""
        start_pos = widget.pos()
        end_pos = QPoint(start_pos.x(), start_pos.y() - widget.height())
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        
        return animation
    
    def create_slide_out_down_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建向下滑出动画"""
        start_pos = widget.pos()
        end_pos = QPoint(start_pos.x(), start_pos.y() + widget.height())
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        
        return animation
    
    def create_scale_in_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建缩放进入动画"""
        original_size = widget.size()
        start_size = QSize(0, 0)
        
        widget.resize(start_size)
        
        animation = QPropertyAnimation(widget, b"size")
        animation.setStartValue(start_size)
        animation.setEndValue(original_size)
        
        return animation
    
    def create_scale_out_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建缩放退出动画"""
        start_size = widget.size()
        end_size = QSize(0, 0)
        
        animation = QPropertyAnimation(widget, b"size")
        animation.setStartValue(start_size)
        animation.setEndValue(end_size)
        
        return animation
    
    def create_bounce_in_animation(self, widget: QWidget) -> QSequentialAnimationGroup:
        """创建弹跳进入动画"""
        group = QSequentialAnimationGroup()
        
        # 第一阶段：快速放大
        scale_up = QPropertyAnimation(widget, b"size")
        original_size = widget.size()
        scale_up.setStartValue(QSize(0, 0))
        scale_up.setEndValue(QSize(int(original_size.width() * 1.2), int(original_size.height() * 1.2)))
        scale_up.setDuration(200)
        scale_up.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 第二阶段：回弹到正常大小
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setStartValue(QSize(int(original_size.width() * 1.2), int(original_size.height() * 1.2)))
        scale_down.setEndValue(original_size)
        scale_down.setDuration(400)
        scale_down.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        
        return group
    
    def create_bounce_out_animation(self, widget: QWidget) -> QSequentialAnimationGroup:
        """创建弹跳退出动画"""
        group = QSequentialAnimationGroup()
        
        # 第一阶段：轻微放大
        scale_up = QPropertyAnimation(widget, b"size")
        original_size = widget.size()
        scale_up.setStartValue(original_size)
        scale_up.setEndValue(QSize(int(original_size.width() * 1.1), int(original_size.height() * 1.1)))
        scale_up.setDuration(150)
        scale_up.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 第二阶段：快速缩小到消失
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setStartValue(QSize(int(original_size.width() * 1.1), int(original_size.height() * 1.1)))
        scale_down.setEndValue(QSize(0, 0))
        scale_down.setDuration(250)
        scale_down.setEasingCurve(QEasingCurve.Type.InQuad)
        
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        
        return group
    
    def create_rotate_in_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建旋转进入动画"""
        # 注意：Qt的QWidget不直接支持旋转，这里使用几何变换模拟
        # 实际实现可能需要使用QGraphicsView或自定义绘制
        
        # 使用透明度和位置组合模拟旋转效果
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        
        return animation
    
    def create_rotate_out_animation(self, widget: QWidget) -> QPropertyAnimation:
        """创建旋转退出动画"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        
        return animation
    
    def stop_animation(self, widget_id: str):
        """停止动画"""
        if widget_id in self.active_animations:
            animation = self.active_animations[widget_id]
            animation.stop()
            del self.active_animations[widget_id]
            logger.debug(f"停止动画: {widget_id}")
    
    def stop_all_animations(self):
        """停止所有动画"""
        for widget_id in list(self.active_animations.keys()):
            self.stop_animation(widget_id)
        logger.info("停止所有动画")
    
    def on_animation_finished(self, widget_id: str, animation_type: str, callback: Optional[Callable]):
        """动画完成处理"""
        # 清理动画引用
        if widget_id in self.active_animations:
            del self.active_animations[widget_id]
        
        # 执行回调
        if callback:
            try:
                callback()
            except Exception as e:
                logger.error(f"动画回调执行失败: {e}")
        
        # 发送完成信号
        self.animation_finished.emit(widget_id, animation_type)
        
        logger.debug(f"动画完成: {widget_id} - {animation_type}")
    
    def create_sequential_animation(self, widget_id: str, animation_sequence: List[Tuple[AnimationType, AnimationConfig]]) -> bool:
        """创建序列动画"""
        if widget_id not in self.widget_registry:
            return False
        
        widget = self.widget_registry[widget_id]
        group = QSequentialAnimationGroup()
        
        for animation_type, config in animation_sequence:
            animation = self.create_animation(widget, animation_type, config)
            if animation:
                animation.setDuration(config.duration)
                animation.setEasingCurve(config.easing.value)
                group.addAnimation(animation)
        
        # 连接信号
        group.started.connect(lambda: self.animation_started.emit(widget_id, "sequential"))
        group.finished.connect(lambda: self.animation_finished.emit(widget_id, "sequential"))
        
        # 保存并启动
        self.animation_groups[widget_id] = group
        group.start()
        
        return True
    
    def create_parallel_animation(self, widget_ids: List[str], animation_type: AnimationType, 
                                 config: Optional[AnimationConfig] = None) -> bool:
        """创建并行动画"""
        config = config or self.preset_configs.get(animation_type, AnimationConfig())
        group = QParallelAnimationGroup()
        
        for widget_id in widget_ids:
            if widget_id in self.widget_registry:
                widget = self.widget_registry[widget_id]
                animation = self.create_animation(widget, animation_type, config)
                if animation:
                    animation.setDuration(config.duration)
                    animation.setEasingCurve(config.easing.value)
                    group.addAnimation(animation)
        
        # 启动并行动画
        group.start()
        
        return True
    
    def get_animation_summary(self) -> Dict[str, Any]:
        """获取动画摘要"""
        return {
            "active_animations": len(self.active_animations),
            "animation_groups": len(self.animation_groups),
            "registered_widgets": len(self.widget_registry),
            "preset_configs": len(self.preset_configs)
        }
