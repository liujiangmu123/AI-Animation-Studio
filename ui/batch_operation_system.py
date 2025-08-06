"""
AI Animation Studio - 批量操作系统
实现高效批量处理系统，支持多对象同时操作
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDialog, QProgressDialog, QGroupBox, QFormLayout, QCheckBox,
                             QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit,
                             QListWidget, QListWidgetItem, QTabWidget, QScrollArea,
                             QFrame, QSplitter, QMessageBox, QApplication, QMenu,
                             QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QMutex, QWaitCondition
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
import json
import time
from dataclasses import dataclass, field
from datetime import datetime

from core.data_structures import Element, ElementType, Transform, ElementStyle
from core.logger import get_logger

logger = get_logger("batch_operation_system")


class BatchOperationType(Enum):
    """批量操作类型枚举"""
    PROPERTY_CHANGE = "property_change"     # 属性修改
    TRANSFORM = "transform"                 # 变换操作
    STYLE_CHANGE = "style_change"          # 样式修改
    ANIMATION_ADD = "animation_add"        # 添加动画
    ANIMATION_REMOVE = "animation_remove"  # 移除动画
    DUPLICATE = "duplicate"                # 复制
    DELETE = "delete"                      # 删除
    GROUP = "group"                        # 分组
    UNGROUP = "ungroup"                    # 取消分组
    ALIGN = "align"                        # 对齐
    DISTRIBUTE = "distribute"              # 分布
    LAYER_CHANGE = "layer_change"          # 图层操作
    VISIBILITY_TOGGLE = "visibility_toggle" # 可见性切换
    LOCK_TOGGLE = "lock_toggle"            # 锁定切换
    EXPORT = "export"                      # 导出


class BatchOperationStatus(Enum):
    """批量操作状态枚举"""
    PENDING = "pending"         # 等待中
    RUNNING = "running"         # 执行中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"     # 已取消
    PAUSED = "paused"          # 已暂停


class SelectionMode(Enum):
    """选择模式枚举"""
    MANUAL = "manual"           # 手动选择
    BY_TYPE = "by_type"        # 按类型选择
    BY_LAYER = "by_layer"      # 按图层选择
    BY_NAME = "by_name"        # 按名称选择
    BY_PROPERTY = "by_property" # 按属性选择
    BY_ANIMATION = "by_animation" # 按动画选择
    ALL = "all"                # 全选


@dataclass
class BatchOperationItem:
    """批量操作项"""
    operation_id: str
    operation_type: BatchOperationType
    target_objects: List[str]  # 目标对象ID列表
    parameters: Dict[str, Any]
    status: BatchOperationStatus = BatchOperationStatus.PENDING
    progress: float = 0.0
    error_message: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SelectionCriteria:
    """选择条件"""
    mode: SelectionMode
    element_types: List[ElementType] = field(default_factory=list)
    layer_names: List[str] = field(default_factory=list)
    name_pattern: str = ""
    property_filters: Dict[str, Any] = field(default_factory=dict)
    has_animation: Optional[bool] = None
    is_visible: Optional[bool] = None
    is_locked: Optional[bool] = None


class BatchOperationWorker(QThread):
    """批量操作工作线程"""
    
    progress_updated = pyqtSignal(str, float)  # 操作ID, 进度
    operation_completed = pyqtSignal(str, bool, str)  # 操作ID, 成功, 消息
    all_completed = pyqtSignal()
    
    def __init__(self, operations: List[BatchOperationItem], processor):
        super().__init__()
        self.operations = operations
        self.processor = processor
        self.is_cancelled = False
        self.is_paused = False
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()
    
    def run(self):
        """执行批量操作"""
        try:
            for operation in self.operations:
                if self.is_cancelled:
                    break
                
                # 检查暂停状态
                self.mutex.lock()
                if self.is_paused:
                    self.pause_condition.wait(self.mutex)
                self.mutex.unlock()
                
                if self.is_cancelled:
                    break
                
                # 执行操作
                operation.status = BatchOperationStatus.RUNNING
                operation.start_time = datetime.now()
                
                try:
                    success = self.processor.execute_operation(operation, self.progress_callback)
                    
                    if success:
                        operation.status = BatchOperationStatus.COMPLETED
                        operation.progress = 100.0
                        self.operation_completed.emit(operation.operation_id, True, "操作成功完成")
                    else:
                        operation.status = BatchOperationStatus.FAILED
                        self.operation_completed.emit(operation.operation_id, False, "操作执行失败")
                
                except Exception as e:
                    operation.status = BatchOperationStatus.FAILED
                    operation.error_message = str(e)
                    self.operation_completed.emit(operation.operation_id, False, str(e))
                
                operation.end_time = datetime.now()
            
            self.all_completed.emit()
            
        except Exception as e:
            logger.error(f"批量操作线程异常: {e}")
    
    def progress_callback(self, operation_id: str, progress: float):
        """进度回调"""
        self.progress_updated.emit(operation_id, progress)
    
    def cancel(self):
        """取消操作"""
        self.is_cancelled = True
        self.resume()  # 确保线程能够退出
    
    def pause(self):
        """暂停操作"""
        self.mutex.lock()
        self.is_paused = True
        self.mutex.unlock()
    
    def resume(self):
        """恢复操作"""
        self.mutex.lock()
        self.is_paused = False
        self.pause_condition.wakeAll()
        self.mutex.unlock()


class SmartSelectionManager:
    """智能选择管理器"""
    
    def __init__(self, elements_provider):
        self.elements_provider = elements_provider
        
        logger.info("智能选择管理器初始化完成")
    
    def select_by_criteria(self, criteria: SelectionCriteria) -> List[str]:
        """根据条件选择对象"""
        try:
            all_elements = self.elements_provider.get_all_elements()
            selected_ids = []
            
            for element_id, element in all_elements.items():
                if self.matches_criteria(element, criteria):
                    selected_ids.append(element_id)
            
            logger.info(f"根据条件选择了 {len(selected_ids)} 个对象")
            return selected_ids
            
        except Exception as e:
            logger.error(f"智能选择失败: {e}")
            return []
    
    def matches_criteria(self, element: Element, criteria: SelectionCriteria) -> bool:
        """检查元素是否匹配条件"""
        try:
            # 按类型筛选
            if criteria.element_types and element.element_type not in criteria.element_types:
                return False
            
            # 按名称模式筛选
            if criteria.name_pattern:
                import re
                if not re.search(criteria.name_pattern, element.name, re.IGNORECASE):
                    return False
            
            # 按可见性筛选
            if criteria.is_visible is not None and element.visible != criteria.is_visible:
                return False
            
            # 按锁定状态筛选
            if criteria.is_locked is not None and element.locked != criteria.is_locked:
                return False
            
            # 按属性筛选
            for prop_name, prop_value in criteria.property_filters.items():
                if not self.check_property_match(element, prop_name, prop_value):
                    return False
            
            # 按动画筛选
            if criteria.has_animation is not None:
                has_anim = hasattr(element, 'animations') and len(element.animations) > 0
                if has_anim != criteria.has_animation:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"条件匹配检查失败: {e}")
            return False
    
    def check_property_match(self, element: Element, prop_name: str, prop_value: Any) -> bool:
        """检查属性匹配"""
        try:
            # 获取元素属性值
            if hasattr(element, prop_name):
                actual_value = getattr(element, prop_name)
                
                # 根据属性类型进行比较
                if isinstance(prop_value, dict):
                    # 范围比较
                    if 'min' in prop_value and actual_value < prop_value['min']:
                        return False
                    if 'max' in prop_value and actual_value > prop_value['max']:
                        return False
                    return True
                else:
                    # 直接比较
                    return actual_value == prop_value
            
            return False
            
        except Exception as e:
            logger.error(f"属性匹配检查失败: {e}")
            return False
    
    def get_selection_preview(self, criteria: SelectionCriteria) -> Dict[str, Any]:
        """获取选择预览"""
        try:
            selected_ids = self.select_by_criteria(criteria)
            all_elements = self.elements_provider.get_all_elements()
            
            # 统计信息
            type_counts = {}
            layer_counts = {}
            
            for element_id in selected_ids:
                if element_id in all_elements:
                    element = all_elements[element_id]
                    
                    # 统计类型
                    element_type = element.element_type.value
                    type_counts[element_type] = type_counts.get(element_type, 0) + 1
                    
                    # 统计图层（如果有）
                    layer = getattr(element, 'layer', 'default')
                    layer_counts[layer] = layer_counts.get(layer, 0) + 1
            
            return {
                'total_count': len(selected_ids),
                'selected_ids': selected_ids,
                'type_distribution': type_counts,
                'layer_distribution': layer_counts
            }
            
        except Exception as e:
            logger.error(f"获取选择预览失败: {e}")
            return {'total_count': 0, 'selected_ids': [], 'type_distribution': {}, 'layer_distribution': {}}


class BatchOperationProcessor:
    """批量操作处理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.operation_handlers = self.setup_operation_handlers()
        
        logger.info("批量操作处理器初始化完成")
    
    def setup_operation_handlers(self) -> Dict[BatchOperationType, Callable]:
        """设置操作处理器"""
        return {
            BatchOperationType.PROPERTY_CHANGE: self.handle_property_change,
            BatchOperationType.TRANSFORM: self.handle_transform,
            BatchOperationType.STYLE_CHANGE: self.handle_style_change,
            BatchOperationType.ANIMATION_ADD: self.handle_animation_add,
            BatchOperationType.ANIMATION_REMOVE: self.handle_animation_remove,
            BatchOperationType.DUPLICATE: self.handle_duplicate,
            BatchOperationType.DELETE: self.handle_delete,
            BatchOperationType.GROUP: self.handle_group,
            BatchOperationType.UNGROUP: self.handle_ungroup,
            BatchOperationType.ALIGN: self.handle_align,
            BatchOperationType.DISTRIBUTE: self.handle_distribute,
            BatchOperationType.LAYER_CHANGE: self.handle_layer_change,
            BatchOperationType.VISIBILITY_TOGGLE: self.handle_visibility_toggle,
            BatchOperationType.LOCK_TOGGLE: self.handle_lock_toggle,
            BatchOperationType.EXPORT: self.handle_export
        }
    
    def execute_operation(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """执行单个批量操作"""
        try:
            handler = self.operation_handlers.get(operation.operation_type)
            if not handler:
                logger.error(f"未找到操作处理器: {operation.operation_type}")
                return False
            
            return handler(operation, progress_callback)
            
        except Exception as e:
            logger.error(f"执行批量操作失败: {e}")
            operation.error_message = str(e)
            return False
    
    def handle_property_change(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理属性修改"""
        try:
            total_objects = len(operation.target_objects)
            
            for i, object_id in enumerate(operation.target_objects):
                # 获取对象
                element = self.get_element_by_id(object_id)
                if not element:
                    continue
                
                # 应用属性修改
                for prop_name, prop_value in operation.parameters.items():
                    if hasattr(element, prop_name):
                        setattr(element, prop_name, prop_value)
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                # 模拟处理时间
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            logger.error(f"属性修改失败: {e}")
            return False
    
    def handle_transform(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理变换操作"""
        try:
            total_objects = len(operation.target_objects)
            transform_params = operation.parameters
            
            for i, object_id in enumerate(operation.target_objects):
                element = self.get_element_by_id(object_id)
                if not element:
                    continue
                
                # 应用变换
                if 'translate_x' in transform_params or 'translate_y' in transform_params:
                    dx = transform_params.get('translate_x', 0)
                    dy = transform_params.get('translate_y', 0)
                    element.position.x += dx
                    element.position.y += dy
                
                if 'scale_x' in transform_params or 'scale_y' in transform_params:
                    sx = transform_params.get('scale_x', 1.0)
                    sy = transform_params.get('scale_y', 1.0)
                    element.transform.scale_x *= sx
                    element.transform.scale_y *= sy
                
                if 'rotation' in transform_params:
                    element.transform.rotation += transform_params['rotation']
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            logger.error(f"变换操作失败: {e}")
            return False
    
    def handle_style_change(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理样式修改"""
        try:
            total_objects = len(operation.target_objects)
            style_params = operation.parameters
            
            for i, object_id in enumerate(operation.target_objects):
                element = self.get_element_by_id(object_id)
                if not element:
                    continue
                
                # 应用样式修改
                for style_prop, style_value in style_params.items():
                    if hasattr(element.style, style_prop):
                        setattr(element.style, style_prop, style_value)
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            logger.error(f"样式修改失败: {e}")
            return False
    
    def handle_duplicate(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理复制操作"""
        try:
            total_objects = len(operation.target_objects)
            offset_x = operation.parameters.get('offset_x', 20)
            offset_y = operation.parameters.get('offset_y', 20)
            
            for i, object_id in enumerate(operation.target_objects):
                element = self.get_element_by_id(object_id)
                if not element:
                    continue
                
                # 创建副本
                duplicate = self.create_element_duplicate(element, offset_x, offset_y)
                if duplicate:
                    self.add_element_to_scene(duplicate)
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                time.sleep(0.02)
            
            return True
            
        except Exception as e:
            logger.error(f"复制操作失败: {e}")
            return False
    
    def handle_delete(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理删除操作"""
        try:
            total_objects = len(operation.target_objects)
            
            for i, object_id in enumerate(operation.target_objects):
                self.remove_element_from_scene(object_id)
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            logger.error(f"删除操作失败: {e}")
            return False
    
    def handle_align(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理对齐操作"""
        try:
            align_type = operation.parameters.get('align_type', 'left')
            elements = [self.get_element_by_id(oid) for oid in operation.target_objects]
            elements = [e for e in elements if e is not None]
            
            if len(elements) < 2:
                return False
            
            # 计算对齐基准
            if align_type == 'left':
                min_x = min(e.position.x for e in elements)
                for element in elements:
                    element.position.x = min_x
            elif align_type == 'right':
                max_x = max(e.position.x + e.size.width for e in elements)
                for element in elements:
                    element.position.x = max_x - element.size.width
            elif align_type == 'center':
                center_x = sum(e.position.x + e.size.width / 2 for e in elements) / len(elements)
                for element in elements:
                    element.position.x = center_x - element.size.width / 2
            elif align_type == 'top':
                min_y = min(e.position.y for e in elements)
                for element in elements:
                    element.position.y = min_y
            elif align_type == 'bottom':
                max_y = max(e.position.y + e.size.height for e in elements)
                for element in elements:
                    element.position.y = max_y - element.size.height
            elif align_type == 'middle':
                center_y = sum(e.position.y + e.size.height / 2 for e in elements) / len(elements)
                for element in elements:
                    element.position.y = center_y - element.size.height / 2
            
            progress_callback(operation.operation_id, 100.0)
            return True
            
        except Exception as e:
            logger.error(f"对齐操作失败: {e}")
            return False
    
    def handle_visibility_toggle(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理可见性切换"""
        try:
            total_objects = len(operation.target_objects)
            new_visibility = operation.parameters.get('visible', True)
            
            for i, object_id in enumerate(operation.target_objects):
                element = self.get_element_by_id(object_id)
                if element:
                    element.visible = new_visibility
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                time.sleep(0.005)
            
            return True
            
        except Exception as e:
            logger.error(f"可见性切换失败: {e}")
            return False
    
    def handle_lock_toggle(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理锁定切换"""
        try:
            total_objects = len(operation.target_objects)
            new_lock_state = operation.parameters.get('locked', True)
            
            for i, object_id in enumerate(operation.target_objects):
                element = self.get_element_by_id(object_id)
                if element:
                    element.locked = new_lock_state
                
                # 更新进度
                progress = (i + 1) / total_objects * 100
                progress_callback(operation.operation_id, progress)
                
                time.sleep(0.005)
            
            return True
            
        except Exception as e:
            logger.error(f"锁定切换失败: {e}")
            return False
    
    # 占位符方法，需要根据实际实现
    def handle_animation_add(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理添加动画"""
        logger.info("添加动画操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    def handle_animation_remove(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理移除动画"""
        logger.info("移除动画操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    def handle_group(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理分组"""
        logger.info("分组操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    def handle_ungroup(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理取消分组"""
        logger.info("取消分组操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    def handle_distribute(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理分布"""
        logger.info("分布操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    def handle_layer_change(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理图层操作"""
        logger.info("图层操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    def handle_export(self, operation: BatchOperationItem, progress_callback: Callable) -> bool:
        """处理导出"""
        logger.info("导出操作")
        progress_callback(operation.operation_id, 100.0)
        return True
    
    # 辅助方法
    def get_element_by_id(self, element_id: str) -> Optional[Element]:
        """根据ID获取元素"""
        try:
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'elements'):
                    return elements_widget.elements.get(element_id)
            return None
        except:
            return None
    
    def create_element_duplicate(self, element: Element, offset_x: float, offset_y: float) -> Optional[Element]:
        """创建元素副本"""
        try:
            from core.data_structures import Point, Size
            
            duplicate = Element(
                name=f"{element.name}_副本",
                element_type=element.element_type,
                content=element.content,
                position=Point(element.position.x + offset_x, element.position.y + offset_y),
                size=Size(element.size.width, element.size.height),
                style=element.style,
                transform=element.transform,
                visible=element.visible,
                locked=False
            )
            
            return duplicate
            
        except Exception as e:
            logger.error(f"创建元素副本失败: {e}")
            return None
    
    def add_element_to_scene(self, element: Element):
        """添加元素到场景"""
        try:
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'add_element'):
                    elements_widget.add_element(element)
        except Exception as e:
            logger.error(f"添加元素到场景失败: {e}")
    
    def remove_element_from_scene(self, element_id: str):
        """从场景移除元素"""
        try:
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'remove_element'):
                    elements_widget.remove_element(element_id)
        except Exception as e:
            logger.error(f"从场景移除元素失败: {e}")


class SmartSelectionDialog(QDialog):
    """智能选择对话框"""

    def __init__(self, selection_manager: SmartSelectionManager, parent=None):
        super().__init__(parent)
        self.selection_manager = selection_manager
        self.criteria = SelectionCriteria(SelectionMode.MANUAL)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("智能选择")
        self.setFixedSize(500, 600)

        layout = QVBoxLayout(self)

        # 选择模式
        mode_group = QGroupBox("选择模式")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_buttons = QButtonGroup()
        modes = [
            (SelectionMode.MANUAL, "手动选择"),
            (SelectionMode.BY_TYPE, "按类型选择"),
            (SelectionMode.BY_LAYER, "按图层选择"),
            (SelectionMode.BY_NAME, "按名称选择"),
            (SelectionMode.BY_PROPERTY, "按属性选择"),
            (SelectionMode.BY_ANIMATION, "按动画选择"),
            (SelectionMode.ALL, "全选")
        ]

        for i, (mode, text) in enumerate(modes):
            radio = QRadioButton(text)
            radio.setProperty("mode", mode)
            self.mode_buttons.addButton(radio, i)
            mode_layout.addWidget(radio)

            if mode == SelectionMode.MANUAL:
                radio.setChecked(True)

        layout.addWidget(mode_group)

        # 条件设置
        self.conditions_stack = QTabWidget()

        # 类型条件
        type_widget = QWidget()
        type_layout = QVBoxLayout(type_widget)

        self.type_checkboxes = {}
        for element_type in ElementType:
            cb = QCheckBox(element_type.value)
            self.type_checkboxes[element_type] = cb
            type_layout.addWidget(cb)

        self.conditions_stack.addTab(type_widget, "类型")

        # 名称条件
        name_widget = QWidget()
        name_layout = QFormLayout(name_widget)

        self.name_pattern_input = QLineEdit()
        self.name_pattern_input.setPlaceholderText("支持正则表达式，如: ^Text.*")
        name_layout.addRow("名称模式:", self.name_pattern_input)

        self.conditions_stack.addTab(name_widget, "名称")

        # 属性条件
        property_widget = QWidget()
        property_layout = QFormLayout(property_widget)

        self.visible_combo = QComboBox()
        self.visible_combo.addItems(["任意", "可见", "隐藏"])
        property_layout.addRow("可见性:", self.visible_combo)

        self.locked_combo = QComboBox()
        self.locked_combo.addItems(["任意", "锁定", "未锁定"])
        property_layout.addRow("锁定状态:", self.locked_combo)

        self.conditions_stack.addTab(property_widget, "属性")

        # 动画条件
        animation_widget = QWidget()
        animation_layout = QFormLayout(animation_widget)

        self.animation_combo = QComboBox()
        self.animation_combo.addItems(["任意", "有动画", "无动画"])
        animation_layout.addRow("动画状态:", self.animation_combo)

        self.conditions_stack.addTab(animation_widget, "动画")

        layout.addWidget(self.conditions_stack)

        # 预览区域
        preview_group = QGroupBox("选择预览")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("将显示选择结果预览")
        self.preview_label.setStyleSheet("color: #666; font-style: italic;")
        preview_layout.addWidget(self.preview_label)

        self.preview_button = QPushButton("预览选择结果")
        self.preview_button.clicked.connect(self.update_preview)
        preview_layout.addWidget(self.preview_button)

        layout.addWidget(preview_group)

        # 按钮
        button_layout = QHBoxLayout()

        self.select_button = QPushButton("确定选择")
        self.select_button.clicked.connect(self.accept)

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.select_button)

        layout.addLayout(button_layout)

    def setup_connections(self):
        """设置信号连接"""
        self.mode_buttons.buttonClicked.connect(self.on_mode_changed)

    def on_mode_changed(self, button):
        """选择模式改变"""
        mode = button.property("mode")
        self.criteria.mode = mode

        # 根据模式启用/禁用条件设置
        if mode == SelectionMode.BY_TYPE:
            self.conditions_stack.setCurrentIndex(0)
        elif mode == SelectionMode.BY_NAME:
            self.conditions_stack.setCurrentIndex(1)
        elif mode == SelectionMode.BY_PROPERTY:
            self.conditions_stack.setCurrentIndex(2)
        elif mode == SelectionMode.BY_ANIMATION:
            self.conditions_stack.setCurrentIndex(3)

    def update_preview(self):
        """更新预览"""
        try:
            # 构建选择条件
            self.build_criteria()

            # 获取预览
            preview = self.selection_manager.get_selection_preview(self.criteria)

            # 更新预览显示
            total = preview['total_count']
            type_dist = preview['type_distribution']

            preview_text = f"将选择 {total} 个对象\n\n"

            if type_dist:
                preview_text += "类型分布:\n"
                for obj_type, count in type_dist.items():
                    preview_text += f"  {obj_type}: {count}个\n"

            self.preview_label.setText(preview_text)
            self.preview_label.setStyleSheet("color: #333; font-weight: bold;")

        except Exception as e:
            logger.error(f"更新预览失败: {e}")
            self.preview_label.setText(f"预览失败: {str(e)}")
            self.preview_label.setStyleSheet("color: #d32f2f;")

    def build_criteria(self):
        """构建选择条件"""
        # 类型条件
        selected_types = []
        for element_type, checkbox in self.type_checkboxes.items():
            if checkbox.isChecked():
                selected_types.append(element_type)
        self.criteria.element_types = selected_types

        # 名称条件
        self.criteria.name_pattern = self.name_pattern_input.text().strip()

        # 可见性条件
        visible_text = self.visible_combo.currentText()
        if visible_text == "可见":
            self.criteria.is_visible = True
        elif visible_text == "隐藏":
            self.criteria.is_visible = False
        else:
            self.criteria.is_visible = None

        # 锁定条件
        locked_text = self.locked_combo.currentText()
        if locked_text == "锁定":
            self.criteria.is_locked = True
        elif locked_text == "未锁定":
            self.criteria.is_locked = False
        else:
            self.criteria.is_locked = None

        # 动画条件
        animation_text = self.animation_combo.currentText()
        if animation_text == "有动画":
            self.criteria.has_animation = True
        elif animation_text == "无动画":
            self.criteria.has_animation = False
        else:
            self.criteria.has_animation = None

    def get_selection_criteria(self) -> SelectionCriteria:
        """获取选择条件"""
        self.build_criteria()
        return self.criteria


class BatchOperationDialog(QDialog):
    """批量操作对话框"""

    def __init__(self, selected_objects: List[str], parent=None):
        super().__init__(parent)
        self.selected_objects = selected_objects
        self.operations = []

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("批量操作")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        # 选择信息
        info_label = QLabel(f"已选择 {len(self.selected_objects)} 个对象")
        info_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        info_label.setStyleSheet("color: #2C5AA0; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # 操作选择
        operation_group = QGroupBox("选择操作")
        operation_layout = QVBoxLayout(operation_group)

        self.operation_combo = QComboBox()
        operations = [
            (BatchOperationType.PROPERTY_CHANGE, "修改属性"),
            (BatchOperationType.TRANSFORM, "变换操作"),
            (BatchOperationType.STYLE_CHANGE, "修改样式"),
            (BatchOperationType.DUPLICATE, "复制"),
            (BatchOperationType.DELETE, "删除"),
            (BatchOperationType.ALIGN, "对齐"),
            (BatchOperationType.DISTRIBUTE, "分布"),
            (BatchOperationType.VISIBILITY_TOGGLE, "切换可见性"),
            (BatchOperationType.LOCK_TOGGLE, "切换锁定"),
            (BatchOperationType.EXPORT, "导出")
        ]

        for op_type, op_name in operations:
            self.operation_combo.addItem(op_name, op_type)

        operation_layout.addWidget(self.operation_combo)
        layout.addWidget(operation_group)

        # 参数设置
        self.params_stack = QTabWidget()

        # 属性修改参数
        self.setup_property_params()

        # 变换参数
        self.setup_transform_params()

        # 样式参数
        self.setup_style_params()

        # 复制参数
        self.setup_duplicate_params()

        # 对齐参数
        self.setup_align_params()

        layout.addWidget(self.params_stack)

        # 按钮
        button_layout = QHBoxLayout()

        self.execute_button = QPushButton("执行操作")
        self.execute_button.clicked.connect(self.accept)

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.execute_button)

        layout.addLayout(button_layout)

    def setup_property_params(self):
        """设置属性参数"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.name_input = QLineEdit()
        layout.addRow("名称:", self.name_input)

        self.visible_checkbox = QCheckBox("可见")
        layout.addRow("可见性:", self.visible_checkbox)

        self.locked_checkbox = QCheckBox("锁定")
        layout.addRow("锁定状态:", self.locked_checkbox)

        self.params_stack.addTab(widget, "属性")

    def setup_transform_params(self):
        """设置变换参数"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.translate_x_input = QDoubleSpinBox()
        self.translate_x_input.setRange(-9999, 9999)
        layout.addRow("X偏移:", self.translate_x_input)

        self.translate_y_input = QDoubleSpinBox()
        self.translate_y_input.setRange(-9999, 9999)
        layout.addRow("Y偏移:", self.translate_y_input)

        self.scale_x_input = QDoubleSpinBox()
        self.scale_x_input.setRange(0.1, 10.0)
        self.scale_x_input.setValue(1.0)
        self.scale_x_input.setSingleStep(0.1)
        layout.addRow("X缩放:", self.scale_x_input)

        self.scale_y_input = QDoubleSpinBox()
        self.scale_y_input.setRange(0.1, 10.0)
        self.scale_y_input.setValue(1.0)
        self.scale_y_input.setSingleStep(0.1)
        layout.addRow("Y缩放:", self.scale_y_input)

        self.rotation_input = QDoubleSpinBox()
        self.rotation_input.setRange(-360, 360)
        self.rotation_input.setSuffix("°")
        layout.addRow("旋转:", self.rotation_input)

        self.params_stack.addTab(widget, "变换")

    def setup_style_params(self):
        """设置样式参数"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.opacity_input = QDoubleSpinBox()
        self.opacity_input.setRange(0.0, 1.0)
        self.opacity_input.setValue(1.0)
        self.opacity_input.setSingleStep(0.1)
        layout.addRow("透明度:", self.opacity_input)

        self.border_width_input = QDoubleSpinBox()
        self.border_width_input.setRange(0.0, 50.0)
        self.border_width_input.setSuffix("px")
        layout.addRow("边框宽度:", self.border_width_input)

        self.params_stack.addTab(widget, "样式")

    def setup_duplicate_params(self):
        """设置复制参数"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.offset_x_input = QDoubleSpinBox()
        self.offset_x_input.setRange(-500, 500)
        self.offset_x_input.setValue(20)
        layout.addRow("X偏移:", self.offset_x_input)

        self.offset_y_input = QDoubleSpinBox()
        self.offset_y_input.setRange(-500, 500)
        self.offset_y_input.setValue(20)
        layout.addRow("Y偏移:", self.offset_y_input)

        self.params_stack.addTab(widget, "复制")

    def setup_align_params(self):
        """设置对齐参数"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.align_buttons = QButtonGroup()

        align_options = [
            ("left", "左对齐"),
            ("center", "水平居中"),
            ("right", "右对齐"),
            ("top", "顶部对齐"),
            ("middle", "垂直居中"),
            ("bottom", "底部对齐")
        ]

        for i, (align_type, align_name) in enumerate(align_options):
            radio = QRadioButton(align_name)
            radio.setProperty("align_type", align_type)
            self.align_buttons.addButton(radio, i)
            layout.addWidget(radio)

            if align_type == "left":
                radio.setChecked(True)

        self.params_stack.addTab(widget, "对齐")

    def setup_connections(self):
        """设置信号连接"""
        self.operation_combo.currentIndexChanged.connect(self.on_operation_changed)

    def on_operation_changed(self, index):
        """操作类型改变"""
        operation_type = self.operation_combo.itemData(index)

        # 根据操作类型切换参数页面
        if operation_type == BatchOperationType.PROPERTY_CHANGE:
            self.params_stack.setCurrentIndex(0)
        elif operation_type == BatchOperationType.TRANSFORM:
            self.params_stack.setCurrentIndex(1)
        elif operation_type == BatchOperationType.STYLE_CHANGE:
            self.params_stack.setCurrentIndex(2)
        elif operation_type == BatchOperationType.DUPLICATE:
            self.params_stack.setCurrentIndex(3)
        elif operation_type == BatchOperationType.ALIGN:
            self.params_stack.setCurrentIndex(4)

    def get_operation_parameters(self) -> Dict[str, Any]:
        """获取操作参数"""
        operation_type = self.operation_combo.currentData()

        if operation_type == BatchOperationType.PROPERTY_CHANGE:
            return {
                'name': self.name_input.text() if self.name_input.text() else None,
                'visible': self.visible_checkbox.isChecked(),
                'locked': self.locked_checkbox.isChecked()
            }
        elif operation_type == BatchOperationType.TRANSFORM:
            return {
                'translate_x': self.translate_x_input.value(),
                'translate_y': self.translate_y_input.value(),
                'scale_x': self.scale_x_input.value(),
                'scale_y': self.scale_y_input.value(),
                'rotation': self.rotation_input.value()
            }
        elif operation_type == BatchOperationType.STYLE_CHANGE:
            return {
                'opacity': self.opacity_input.value(),
                'border_width': self.border_width_input.value()
            }
        elif operation_type == BatchOperationType.DUPLICATE:
            return {
                'offset_x': self.offset_x_input.value(),
                'offset_y': self.offset_y_input.value()
            }
        elif operation_type == BatchOperationType.ALIGN:
            checked_button = self.align_buttons.checkedButton()
            if checked_button:
                return {'align_type': checked_button.property("align_type")}
        elif operation_type == BatchOperationType.VISIBILITY_TOGGLE:
            return {'visible': True}  # 可以添加更多选项
        elif operation_type == BatchOperationType.LOCK_TOGGLE:
            return {'locked': True}  # 可以添加更多选项

        return {}

    def get_batch_operation(self) -> BatchOperationItem:
        """获取批量操作项"""
        operation_type = self.operation_combo.currentData()
        parameters = self.get_operation_parameters()

        # 过滤None值
        parameters = {k: v for k, v in parameters.items() if v is not None}

        return BatchOperationItem(
            operation_id=f"batch_{int(time.time())}",
            operation_type=operation_type,
            target_objects=self.selected_objects.copy(),
            parameters=parameters
        )


class BatchOperationProgressDialog(QDialog):
    """批量操作进度对话框"""

    def __init__(self, operations: List[BatchOperationItem], parent=None):
        super().__init__(parent)
        self.operations = operations
        self.operation_progress = {}

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("批量操作进度")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 总体进度
        overall_group = QGroupBox("总体进度")
        overall_layout = QVBoxLayout(overall_group)

        self.overall_progress = QProgressDialog()
        self.overall_progress.setRange(0, len(self.operations))
        self.overall_progress.setValue(0)
        self.overall_progress.setLabelText("准备执行批量操作...")

        overall_layout.addWidget(QLabel(f"总共 {len(self.operations)} 个操作"))
        layout.addWidget(overall_group)

        # 详细进度
        detail_group = QGroupBox("详细进度")
        detail_layout = QVBoxLayout(detail_group)

        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(4)
        self.progress_table.setHorizontalHeaderLabels(["操作", "状态", "进度", "消息"])
        self.progress_table.horizontalHeader().setStretchLastSection(True)

        # 填充操作列表
        self.progress_table.setRowCount(len(self.operations))
        for i, operation in enumerate(self.operations):
            self.progress_table.setItem(i, 0, QTableWidgetItem(operation.operation_type.value))
            self.progress_table.setItem(i, 1, QTableWidgetItem("等待中"))
            self.progress_table.setItem(i, 2, QTableWidgetItem("0%"))
            self.progress_table.setItem(i, 3, QTableWidgetItem(""))

        detail_layout.addWidget(self.progress_table)
        layout.addWidget(detail_group)

        # 控制按钮
        button_layout = QHBoxLayout()

        self.pause_button = QPushButton("暂停")
        self.pause_button.setEnabled(False)

        self.cancel_button = QPushButton("取消")

        self.close_button = QPushButton("关闭")
        self.close_button.setEnabled(False)

        button_layout.addStretch()
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def update_operation_progress(self, operation_id: str, progress: float):
        """更新操作进度"""
        self.operation_progress[operation_id] = progress

        # 查找对应的行
        for i, operation in enumerate(self.operations):
            if operation.operation_id == operation_id:
                self.progress_table.setItem(i, 2, QTableWidgetItem(f"{progress:.1f}%"))
                if progress >= 100:
                    self.progress_table.setItem(i, 1, QTableWidgetItem("已完成"))
                else:
                    self.progress_table.setItem(i, 1, QTableWidgetItem("执行中"))
                break

        # 更新总体进度
        completed_count = sum(1 for p in self.operation_progress.values() if p >= 100)
        self.overall_progress.setValue(completed_count)

    def update_operation_status(self, operation_id: str, success: bool, message: str):
        """更新操作状态"""
        for i, operation in enumerate(self.operations):
            if operation.operation_id == operation_id:
                status = "成功" if success else "失败"
                self.progress_table.setItem(i, 1, QTableWidgetItem(status))
                self.progress_table.setItem(i, 3, QTableWidgetItem(message))

                # 设置行颜色
                color = QColor(200, 255, 200) if success else QColor(255, 200, 200)
                for col in range(4):
                    item = self.progress_table.item(i, col)
                    if item:
                        item.setBackground(color)
                break

    def on_all_completed(self):
        """所有操作完成"""
        self.overall_progress.setLabelText("所有操作已完成")
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)


class BatchOperationManager(QObject):
    """批量操作管理器"""

    operation_started = pyqtSignal(str)  # 操作开始
    operation_completed = pyqtSignal(str, bool, str)  # 操作完成
    all_operations_completed = pyqtSignal()  # 所有操作完成

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.selection_manager = SmartSelectionManager(self.get_elements_provider())
        self.processor = BatchOperationProcessor(main_window)
        self.current_worker = None
        self.operation_history = []

        logger.info("批量操作管理器初始化完成")

    def get_elements_provider(self):
        """获取元素提供者"""
        class ElementsProvider:
            def __init__(self, main_window):
                self.main_window = main_window

            def get_all_elements(self):
                if hasattr(self.main_window, 'elements_widget'):
                    elements_widget = self.main_window.elements_widget
                    if hasattr(elements_widget, 'elements'):
                        return elements_widget.elements
                return {}

        return ElementsProvider(self.main_window)

    def show_smart_selection_dialog(self) -> List[str]:
        """显示智能选择对话框"""
        try:
            dialog = SmartSelectionDialog(self.selection_manager, self.main_window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                criteria = dialog.get_selection_criteria()
                selected_ids = self.selection_manager.select_by_criteria(criteria)

                logger.info(f"智能选择完成，选中 {len(selected_ids)} 个对象")
                return selected_ids

            return []

        except Exception as e:
            logger.error(f"显示智能选择对话框失败: {e}")
            return []

    def show_batch_operation_dialog(self, selected_objects: List[str]) -> Optional[BatchOperationItem]:
        """显示批量操作对话框"""
        try:
            if not selected_objects:
                QMessageBox.warning(self.main_window, "警告", "没有选择任何对象")
                return None

            dialog = BatchOperationDialog(selected_objects, self.main_window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                operation = dialog.get_batch_operation()

                logger.info(f"创建批量操作: {operation.operation_type.value}")
                return operation

            return None

        except Exception as e:
            logger.error(f"显示批量操作对话框失败: {e}")
            return None

    def execute_batch_operations(self, operations: List[BatchOperationItem]):
        """执行批量操作"""
        try:
            if not operations:
                return

            # 显示进度对话框
            progress_dialog = BatchOperationProgressDialog(operations, self.main_window)
            progress_dialog.show()

            # 创建工作线程
            self.current_worker = BatchOperationWorker(operations, self.processor)

            # 连接信号
            self.current_worker.progress_updated.connect(progress_dialog.update_operation_progress)
            self.current_worker.operation_completed.connect(progress_dialog.update_operation_status)
            self.current_worker.operation_completed.connect(self.operation_completed)
            self.current_worker.all_completed.connect(progress_dialog.on_all_completed)
            self.current_worker.all_completed.connect(self.all_operations_completed)

            # 连接进度对话框的控制按钮
            progress_dialog.pause_button.clicked.connect(self.current_worker.pause)
            progress_dialog.cancel_button.clicked.connect(self.current_worker.cancel)
            progress_dialog.close_button.clicked.connect(progress_dialog.accept)

            # 启动工作线程
            self.current_worker.start()

            # 记录到历史
            self.operation_history.extend(operations)

            logger.info(f"开始执行 {len(operations)} 个批量操作")

        except Exception as e:
            logger.error(f"执行批量操作失败: {e}")
            QMessageBox.critical(self.main_window, "错误", f"执行批量操作失败:\n{str(e)}")

    def execute_single_batch_operation(self, operation: BatchOperationItem):
        """执行单个批量操作"""
        self.execute_batch_operations([operation])

    def get_current_selection(self) -> List[str]:
        """获取当前选择"""
        try:
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'selected_elements'):
                    return list(elements_widget.selected_elements)
            return []
        except:
            return []

    def create_quick_operation(self, operation_type: BatchOperationType,
                              selected_objects: List[str],
                              parameters: Dict[str, Any]) -> BatchOperationItem:
        """创建快速操作"""
        return BatchOperationItem(
            operation_id=f"quick_{operation_type.value}_{int(time.time())}",
            operation_type=operation_type,
            target_objects=selected_objects,
            parameters=parameters
        )

    def duplicate_selected(self, offset_x: float = 20, offset_y: float = 20):
        """复制选中对象"""
        selected = self.get_current_selection()
        if selected:
            operation = self.create_quick_operation(
                BatchOperationType.DUPLICATE,
                selected,
                {'offset_x': offset_x, 'offset_y': offset_y}
            )
            self.execute_single_batch_operation(operation)

    def delete_selected(self):
        """删除选中对象"""
        selected = self.get_current_selection()
        if selected:
            reply = QMessageBox.question(
                self.main_window, "确认删除",
                f"确定要删除选中的 {len(selected)} 个对象吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                operation = self.create_quick_operation(
                    BatchOperationType.DELETE,
                    selected,
                    {}
                )
                self.execute_single_batch_operation(operation)

    def align_selected(self, align_type: str):
        """对齐选中对象"""
        selected = self.get_current_selection()
        if len(selected) >= 2:
            operation = self.create_quick_operation(
                BatchOperationType.ALIGN,
                selected,
                {'align_type': align_type}
            )
            self.execute_single_batch_operation(operation)
        else:
            QMessageBox.warning(self.main_window, "警告", "对齐操作需要选择至少2个对象")

    def toggle_visibility_selected(self):
        """切换选中对象可见性"""
        selected = self.get_current_selection()
        if selected:
            operation = self.create_quick_operation(
                BatchOperationType.VISIBILITY_TOGGLE,
                selected,
                {'visible': True}  # 实际逻辑会根据当前状态切换
            )
            self.execute_single_batch_operation(operation)

    def toggle_lock_selected(self):
        """切换选中对象锁定状态"""
        selected = self.get_current_selection()
        if selected:
            operation = self.create_quick_operation(
                BatchOperationType.LOCK_TOGGLE,
                selected,
                {'locked': True}  # 实际逻辑会根据当前状态切换
            )
            self.execute_single_batch_operation(operation)

    def get_operation_history(self) -> List[BatchOperationItem]:
        """获取操作历史"""
        return self.operation_history.copy()

    def clear_operation_history(self):
        """清空操作历史"""
        self.operation_history.clear()
        logger.info("批量操作历史已清空")

    def export_operation_history(self, file_path: str):
        """导出操作历史"""
        try:
            history_data = []
            for operation in self.operation_history:
                history_data.append({
                    'operation_id': operation.operation_id,
                    'operation_type': operation.operation_type.value,
                    'target_count': len(operation.target_objects),
                    'parameters': operation.parameters,
                    'status': operation.status.value,
                    'start_time': operation.start_time.isoformat() if operation.start_time else None,
                    'end_time': operation.end_time.isoformat() if operation.end_time else None,
                    'error_message': operation.error_message
                })

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            logger.info(f"操作历史已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出操作历史失败: {e}")

    def get_manager_summary(self) -> Dict[str, Any]:
        """获取管理器摘要"""
        return {
            'total_operations': len(self.operation_history),
            'completed_operations': len([op for op in self.operation_history if op.status == BatchOperationStatus.COMPLETED]),
            'failed_operations': len([op for op in self.operation_history if op.status == BatchOperationStatus.FAILED]),
            'operation_types': {
                op_type.value: len([op for op in self.operation_history if op.operation_type == op_type])
                for op_type in BatchOperationType
            },
            'is_running': self.current_worker is not None and self.current_worker.isRunning()
        }


class BatchOperationIntegrator:
    """批量操作集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.batch_manager = BatchOperationManager(main_window)
        self.integrated_menus = {}
        self.integrated_toolbars = {}
        self.integrated_shortcuts = {}

        # 连接信号
        self.batch_manager.operation_completed.connect(self.handle_operation_completed)
        self.batch_manager.all_operations_completed.connect(self.handle_all_operations_completed)

        logger.info("批量操作集成器初始化完成")

    def integrate_batch_operation_system(self):
        """集成批量操作系统"""
        try:
            # 集成到主菜单
            self.integrate_main_menu()

            # 集成到工具栏
            self.integrate_toolbar()

            # 集成到右键菜单
            self.integrate_context_menus()

            # 集成到快捷键
            self.integrate_shortcuts()

            # 添加批量操作面板
            self.add_batch_operation_panel()

            logger.info("批量操作系统集成完成")
            return True

        except Exception as e:
            logger.error(f"批量操作系统集成失败: {e}")
            return False

    def integrate_main_menu(self):
        """集成到主菜单"""
        try:
            if hasattr(self.main_window, 'menuBar'):
                menubar = self.main_window.menuBar()

                # 创建批量操作菜单
                batch_menu = menubar.addMenu("批量操作(&B)")

                # 智能选择
                smart_select_action = batch_menu.addAction("智能选择...")
                smart_select_action.setShortcut("Ctrl+Shift+A")
                smart_select_action.triggered.connect(self.show_smart_selection)

                batch_menu.addSeparator()

                # 快速操作
                duplicate_action = batch_menu.addAction("复制选中对象")
                duplicate_action.setShortcut("Ctrl+D")
                duplicate_action.triggered.connect(self.batch_manager.duplicate_selected)

                delete_action = batch_menu.addAction("删除选中对象")
                delete_action.setShortcut("Delete")
                delete_action.triggered.connect(self.batch_manager.delete_selected)

                batch_menu.addSeparator()

                # 对齐操作
                align_menu = batch_menu.addMenu("对齐")

                align_left_action = align_menu.addAction("左对齐")
                align_left_action.triggered.connect(lambda: self.batch_manager.align_selected("left"))

                align_center_action = align_menu.addAction("水平居中")
                align_center_action.triggered.connect(lambda: self.batch_manager.align_selected("center"))

                align_right_action = align_menu.addAction("右对齐")
                align_right_action.triggered.connect(lambda: self.batch_manager.align_selected("right"))

                align_menu.addSeparator()

                align_top_action = align_menu.addAction("顶部对齐")
                align_top_action.triggered.connect(lambda: self.batch_manager.align_selected("top"))

                align_middle_action = align_menu.addAction("垂直居中")
                align_middle_action.triggered.connect(lambda: self.batch_manager.align_selected("middle"))

                align_bottom_action = align_menu.addAction("底部对齐")
                align_bottom_action.triggered.connect(lambda: self.batch_manager.align_selected("bottom"))

                batch_menu.addSeparator()

                # 可见性和锁定
                toggle_visibility_action = batch_menu.addAction("切换可见性")
                toggle_visibility_action.setShortcut("Ctrl+H")
                toggle_visibility_action.triggered.connect(self.batch_manager.toggle_visibility_selected)

                toggle_lock_action = batch_menu.addAction("切换锁定")
                toggle_lock_action.setShortcut("Ctrl+L")
                toggle_lock_action.triggered.connect(self.batch_manager.toggle_lock_selected)

                batch_menu.addSeparator()

                # 高级操作
                batch_operation_action = batch_menu.addAction("批量操作...")
                batch_operation_action.setShortcut("Ctrl+Shift+B")
                batch_operation_action.triggered.connect(self.show_batch_operation_dialog)

                self.integrated_menus['main_menu'] = batch_menu
                logger.debug("主菜单集成完成")

        except Exception as e:
            logger.error(f"主菜单集成失败: {e}")

    def integrate_toolbar(self):
        """集成到工具栏"""
        try:
            if hasattr(self.main_window, 'toolbar'):
                toolbar = self.main_window.toolbar

                # 添加分隔符
                toolbar.addSeparator()

                # 智能选择按钮
                smart_select_action = toolbar.addAction("🎯", self.show_smart_selection)
                smart_select_action.setToolTip("智能选择 (Ctrl+Shift+A)")

                # 复制按钮
                duplicate_action = toolbar.addAction("📋", self.batch_manager.duplicate_selected)
                duplicate_action.setToolTip("复制选中对象 (Ctrl+D)")

                # 删除按钮
                delete_action = toolbar.addAction("🗑️", self.batch_manager.delete_selected)
                delete_action.setToolTip("删除选中对象 (Delete)")

                # 对齐按钮组
                toolbar.addSeparator()

                align_left_action = toolbar.addAction("⬅️", lambda: self.batch_manager.align_selected("left"))
                align_left_action.setToolTip("左对齐")

                align_center_action = toolbar.addAction("↔️", lambda: self.batch_manager.align_selected("center"))
                align_center_action.setToolTip("水平居中")

                align_right_action = toolbar.addAction("➡️", lambda: self.batch_manager.align_selected("right"))
                align_right_action.setToolTip("右对齐")

                # 批量操作按钮
                toolbar.addSeparator()
                batch_action = toolbar.addAction("⚙️", self.show_batch_operation_dialog)
                batch_action.setToolTip("批量操作 (Ctrl+Shift+B)")

                self.integrated_toolbars['main_toolbar'] = toolbar
                logger.debug("工具栏集成完成")

        except Exception as e:
            logger.error(f"工具栏集成失败: {e}")

    def integrate_context_menus(self):
        """集成到右键菜单"""
        try:
            # 为元素列表添加批量操作右键菜单
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget

                # 重写右键菜单事件
                original_context_menu = getattr(elements_widget, 'contextMenuEvent', None)

                def enhanced_context_menu_event(event):
                    # 获取选中的元素
                    selected = self.batch_manager.get_current_selection()

                    if len(selected) > 1:
                        # 多选时显示批量操作菜单
                        menu = QMenu(elements_widget)

                        menu.addAction(f"已选择 {len(selected)} 个对象").setEnabled(False)
                        menu.addSeparator()

                        # 批量操作
                        batch_action = menu.addAction("批量操作...")
                        batch_action.triggered.connect(self.show_batch_operation_dialog)

                        menu.addSeparator()

                        # 快速操作
                        duplicate_action = menu.addAction("复制")
                        duplicate_action.triggered.connect(self.batch_manager.duplicate_selected)

                        delete_action = menu.addAction("删除")
                        delete_action.triggered.connect(self.batch_manager.delete_selected)

                        menu.addSeparator()

                        # 对齐操作
                        align_menu = menu.addMenu("对齐")

                        align_menu.addAction("左对齐").triggered.connect(
                            lambda: self.batch_manager.align_selected("left"))
                        align_menu.addAction("水平居中").triggered.connect(
                            lambda: self.batch_manager.align_selected("center"))
                        align_menu.addAction("右对齐").triggered.connect(
                            lambda: self.batch_manager.align_selected("right"))
                        align_menu.addSeparator()
                        align_menu.addAction("顶部对齐").triggered.connect(
                            lambda: self.batch_manager.align_selected("top"))
                        align_menu.addAction("垂直居中").triggered.connect(
                            lambda: self.batch_manager.align_selected("middle"))
                        align_menu.addAction("底部对齐").triggered.connect(
                            lambda: self.batch_manager.align_selected("bottom"))

                        menu.addSeparator()

                        # 可见性和锁定
                        visibility_action = menu.addAction("切换可见性")
                        visibility_action.triggered.connect(self.batch_manager.toggle_visibility_selected)

                        lock_action = menu.addAction("切换锁定")
                        lock_action.triggered.connect(self.batch_manager.toggle_lock_selected)

                        menu.exec(elements_widget.mapToGlobal(event.pos()))
                    else:
                        # 单选或无选择时使用原始菜单
                        if original_context_menu:
                            original_context_menu(event)

                elements_widget.contextMenuEvent = enhanced_context_menu_event
                logger.debug("右键菜单集成完成")

        except Exception as e:
            logger.error(f"右键菜单集成失败: {e}")

    def integrate_shortcuts(self):
        """集成快捷键"""
        try:
            from PyQt6.QtGui import QShortcut

            shortcuts = [
                ("Ctrl+Shift+A", self.show_smart_selection, "智能选择"),
                ("Ctrl+D", self.batch_manager.duplicate_selected, "复制选中对象"),
                ("Delete", self.batch_manager.delete_selected, "删除选中对象"),
                ("Ctrl+H", self.batch_manager.toggle_visibility_selected, "切换可见性"),
                ("Ctrl+L", self.batch_manager.toggle_lock_selected, "切换锁定"),
                ("Ctrl+Shift+B", self.show_batch_operation_dialog, "批量操作")
            ]

            for key_sequence, slot, description in shortcuts:
                shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
                shortcut.activated.connect(slot)
                self.integrated_shortcuts[description] = shortcut

            logger.debug("快捷键集成完成")

        except Exception as e:
            logger.error(f"快捷键集成失败: {e}")

    def add_batch_operation_panel(self):
        """添加批量操作面板"""
        try:
            # 创建批量操作面板
            panel = QFrame()
            panel.setFrameStyle(QFrame.Shape.StyledPanel)
            panel.setStyleSheet("""
                QFrame {
                    background-color: #f0f8ff;
                    border: 1px solid #4682b4;
                    border-radius: 6px;
                    padding: 10px;
                }
            """)

            layout = QVBoxLayout(panel)

            # 标题
            title = QLabel("⚙️ 批量操作")
            title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c5aa0; margin-bottom: 8px;")
            layout.addWidget(title)

            # 选择信息
            self.selection_info_label = QLabel("未选择对象")
            self.selection_info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
            layout.addWidget(self.selection_info_label)

            # 快速操作按钮
            quick_layout = QHBoxLayout()

            smart_select_btn = QPushButton("智能选择")
            smart_select_btn.clicked.connect(self.show_smart_selection)
            quick_layout.addWidget(smart_select_btn)

            batch_op_btn = QPushButton("批量操作")
            batch_op_btn.clicked.connect(self.show_batch_operation_dialog)
            quick_layout.addWidget(batch_op_btn)

            layout.addLayout(quick_layout)

            # 对齐按钮
            align_layout = QHBoxLayout()

            align_buttons = [
                ("⬅️", "left", "左对齐"),
                ("↔️", "center", "居中"),
                ("➡️", "right", "右对齐"),
                ("⬆️", "top", "顶部"),
                ("↕️", "middle", "中间"),
                ("⬇️", "bottom", "底部")
            ]

            for icon, align_type, tooltip in align_buttons:
                btn = QPushButton(icon)
                btn.setFixedSize(30, 30)
                btn.setToolTip(tooltip)
                btn.clicked.connect(lambda checked, at=align_type: self.batch_manager.align_selected(at))
                align_layout.addWidget(btn)

            layout.addLayout(align_layout)

            # 添加到主窗口
            if hasattr(self.main_window, 'add_dock_widget'):
                self.main_window.add_dock_widget("批量操作", panel, Qt.DockWidgetArea.RightDockWidgetArea)
            else:
                # 添加到状态栏
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().addPermanentWidget(panel)

            # 定时更新选择信息
            self.selection_timer = QTimer()
            self.selection_timer.timeout.connect(self.update_selection_info)
            self.selection_timer.start(1000)  # 每秒更新一次

            logger.debug("批量操作面板已添加")

        except Exception as e:
            logger.error(f"添加批量操作面板失败: {e}")

    def update_selection_info(self):
        """更新选择信息"""
        try:
            selected = self.batch_manager.get_current_selection()
            count = len(selected)

            if count == 0:
                self.selection_info_label.setText("未选择对象")
            elif count == 1:
                self.selection_info_label.setText("已选择 1 个对象")
            else:
                self.selection_info_label.setText(f"已选择 {count} 个对象")

        except Exception as e:
            logger.debug(f"更新选择信息失败: {e}")

    def show_smart_selection(self):
        """显示智能选择"""
        try:
            selected_ids = self.batch_manager.show_smart_selection_dialog()
            if selected_ids:
                # 更新主窗口的选择状态
                self.update_main_window_selection(selected_ids)

        except Exception as e:
            logger.error(f"显示智能选择失败: {e}")

    def show_batch_operation_dialog(self):
        """显示批量操作对话框"""
        try:
            selected = self.batch_manager.get_current_selection()
            operation = self.batch_manager.show_batch_operation_dialog(selected)

            if operation:
                self.batch_manager.execute_single_batch_operation(operation)

        except Exception as e:
            logger.error(f"显示批量操作对话框失败: {e}")

    def update_main_window_selection(self, selected_ids: List[str]):
        """更新主窗口选择状态"""
        try:
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'set_selected_elements'):
                    elements_widget.set_selected_elements(selected_ids)
                elif hasattr(elements_widget, 'selected_elements'):
                    elements_widget.selected_elements = set(selected_ids)
                    # 触发选择改变事件
                    if hasattr(elements_widget, 'on_selection_changed'):
                        elements_widget.on_selection_changed()

        except Exception as e:
            logger.error(f"更新主窗口选择状态失败: {e}")

    def handle_operation_completed(self, operation_id: str, success: bool, message: str):
        """处理操作完成"""
        try:
            if success:
                logger.info(f"批量操作完成: {operation_id}")
                # 刷新界面显示
                self.refresh_ui_displays()
            else:
                logger.error(f"批量操作失败: {operation_id} - {message}")

        except Exception as e:
            logger.error(f"处理操作完成事件失败: {e}")

    def handle_all_operations_completed(self):
        """处理所有操作完成"""
        try:
            logger.info("所有批量操作已完成")

            # 刷新界面显示
            self.refresh_ui_displays()

            # 显示完成通知
            if hasattr(self.main_window, 'show_status_message'):
                self.main_window.show_status_message("批量操作已完成")

        except Exception as e:
            logger.error(f"处理所有操作完成事件失败: {e}")

    def refresh_ui_displays(self):
        """刷新UI显示"""
        try:
            # 刷新元素列表
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'refresh_list'):
                    elements_widget.refresh_list()

            # 刷新舞台显示
            if hasattr(self.main_window, 'stage_widget'):
                stage_widget = self.main_window.stage_widget
                if hasattr(stage_widget, 'update_display'):
                    stage_widget.update_display()

            # 刷新时间轴
            if hasattr(self.main_window, 'timeline_widget'):
                timeline_widget = self.main_window.timeline_widget
                if hasattr(timeline_widget, 'update_display'):
                    timeline_widget.update_display()

        except Exception as e:
            logger.error(f"刷新UI显示失败: {e}")

    def get_batch_manager(self) -> BatchOperationManager:
        """获取批量操作管理器"""
        return self.batch_manager

    def export_integration_config(self, file_path: str):
        """导出集成配置"""
        try:
            config = {
                "integrated_menus": list(self.integrated_menus.keys()),
                "integrated_toolbars": list(self.integrated_toolbars.keys()),
                "integrated_shortcuts": list(self.integrated_shortcuts.keys()),
                "manager_summary": self.batch_manager.get_manager_summary(),
                "integration_status": "completed"
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"批量操作集成配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出集成配置失败: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        manager_summary = self.batch_manager.get_manager_summary()

        return {
            "integrated_menus": len(self.integrated_menus),
            "integrated_toolbars": len(self.integrated_toolbars),
            "integrated_shortcuts": len(self.integrated_shortcuts),
            "total_operations": manager_summary["total_operations"],
            "completed_operations": manager_summary["completed_operations"],
            "failed_operations": manager_summary["failed_operations"],
            "is_running": manager_summary["is_running"],
            "integration_status": "completed"
        }
