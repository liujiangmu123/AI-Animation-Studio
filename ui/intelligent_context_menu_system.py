"""
AI Animation Studio - 智能上下文菜单系统
基于对象类型和上下文状态的智能右键菜单设计
"""

from PyQt6.QtWidgets import QMenu, QAction, QWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QKeySequence, QIcon, QContextMenuEvent

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import json
from dataclasses import dataclass

from core.logger import get_logger

logger = get_logger("intelligent_context_menu_system")


class ContextObjectType(Enum):
    """上下文对象类型枚举"""
    AUDIO_SEGMENT = "audio_segment"         # 音频片段
    TIME_SEGMENT = "time_segment"           # 时间段
    STAGE_ELEMENT = "stage_element"         # 舞台元素
    TIMELINE_TRACK = "timeline_track"       # 时间轴轨道
    ELEMENT_LIST_ITEM = "element_list_item" # 元素列表项
    CANVAS_EMPTY = "canvas_empty"           # 空白画布
    CODE_EDITOR = "code_editor"             # 代码编辑器
    PREVIEW_AREA = "preview_area"           # 预览区域
    PROPERTY_PANEL = "property_panel"       # 属性面板
    LIBRARY_ITEM = "library_item"           # 库项目
    RULE_ITEM = "rule_item"                 # 规则项目
    TEMPLATE_ITEM = "template_item"         # 模板项目


class ContextState(Enum):
    """上下文状态枚举"""
    SELECTED = "selected"           # 已选中
    UNSELECTED = "unselected"       # 未选中
    MULTIPLE_SELECTED = "multiple_selected"  # 多选
    EDITING = "editing"             # 编辑中
    PLAYING = "playing"             # 播放中
    PAUSED = "paused"              # 暂停中
    EMPTY = "empty"                # 空状态
    LOADING = "loading"            # 加载中
    ERROR = "error"                # 错误状态


@dataclass
class ContextMenuItem:
    """上下文菜单项定义"""
    action_id: str
    text: str
    description: str
    icon: str = None
    shortcut: str = None
    enabled: bool = True
    visible: bool = True
    checkable: bool = False
    checked: bool = False
    separator_after: bool = False
    submenu: List['ContextMenuItem'] = None
    priority: int = 1  # 优先级 1-5
    
    def __post_init__(self):
        if self.submenu is None:
            self.submenu = []


class IntelligentContextMenuBuilder:
    """智能上下文菜单构建器"""
    
    def __init__(self):
        self.menu_templates = self.build_menu_templates()
        self.dynamic_rules = self.build_dynamic_rules()
        
        logger.info("智能上下文菜单构建器初始化完成")
    
    def build_menu_templates(self) -> Dict[ContextObjectType, List[ContextMenuItem]]:
        """构建菜单模板"""
        return {
            # 音频片段上下文菜单
            ContextObjectType.AUDIO_SEGMENT: [
                ContextMenuItem(
                    "play_segment", "播放片段", "播放选中的音频片段",
                    "play", "Space", priority=5
                ),
                ContextMenuItem(
                    "edit_segment", "编辑片段", "编辑音频片段属性",
                    "edit", "F2", priority=4
                ),
                ContextMenuItem(
                    "split_segment", "分割片段", "在当前位置分割音频片段",
                    "split", "Ctrl+K", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "copy_segment", "复制片段", "复制音频片段",
                    "copy", "Ctrl+C", priority=3
                ),
                ContextMenuItem(
                    "delete_segment", "删除片段", "删除音频片段",
                    "delete", "Delete", priority=3, separator_after=True
                ),
                ContextMenuItem(
                    "add_animation_desc", "添加动画描述", "为此片段添加动画描述",
                    "animation_desc", priority=5
                ),
                ContextMenuItem(
                    "generate_ai_animation", "AI生成动画", "使用AI为此片段生成动画",
                    "ai_generation", "Ctrl+G", priority=5
                )
            ],
            
            # 时间段上下文菜单
            ContextObjectType.TIME_SEGMENT: [
                ContextMenuItem(
                    "edit_time_range", "编辑时间范围", "调整时间段的开始和结束时间",
                    "time_segment", priority=5
                ),
                ContextMenuItem(
                    "set_description", "设置描述", "为时间段设置动画描述",
                    "description", priority=5
                ),
                ContextMenuItem(
                    "duplicate_segment", "复制时间段", "复制时间段及其设置",
                    "duplicate", "Ctrl+D", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "merge_segments", "合并时间段", "与相邻时间段合并",
                    "merge", priority=3
                ),
                ContextMenuItem(
                    "split_at_cursor", "在光标处分割", "在当前光标位置分割时间段",
                    "split", "Ctrl+Shift+K", priority=3, separator_after=True
                ),
                ContextMenuItem(
                    "preview_segment", "预览时间段", "预览此时间段的动画效果",
                    "preview", "P", priority=4
                ),
                ContextMenuItem(
                    "export_segment", "导出时间段", "单独导出此时间段",
                    "export", priority=2
                )
            ],
            
            # 舞台元素上下文菜单
            ContextObjectType.STAGE_ELEMENT: [
                ContextMenuItem(
                    "edit_properties", "编辑属性", "编辑元素属性",
                    "properties", "F4", priority=5
                ),
                ContextMenuItem(
                    "duplicate_element", "复制元素", "复制选中元素",
                    "duplicate", "Ctrl+D", priority=4
                ),
                ContextMenuItem(
                    "delete_element", "删除元素", "删除选中元素",
                    "delete", "Delete", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "transform", "变换", "变换操作子菜单",
                    submenu=[
                        ContextMenuItem("move_to_front", "移到最前", "移动到最前层", "front"),
                        ContextMenuItem("move_forward", "向前移动", "向前移动一层", "forward"),
                        ContextMenuItem("move_backward", "向后移动", "向后移动一层", "backward"),
                        ContextMenuItem("move_to_back", "移到最后", "移动到最后层", "back"),
                        ContextMenuItem("separator1", "", "", separator_after=True),
                        ContextMenuItem("flip_horizontal", "水平翻转", "水平翻转元素"),
                        ContextMenuItem("flip_vertical", "垂直翻转", "垂直翻转元素"),
                        ContextMenuItem("rotate_90", "旋转90°", "顺时针旋转90度")
                    ],
                    priority=3
                ),
                ContextMenuItem(
                    "align", "对齐", "对齐操作子菜单",
                    submenu=[
                        ContextMenuItem("align_left", "左对齐", "与画布左边对齐"),
                        ContextMenuItem("align_center", "居中对齐", "与画布中心对齐"),
                        ContextMenuItem("align_right", "右对齐", "与画布右边对齐"),
                        ContextMenuItem("separator2", "", "", separator_after=True),
                        ContextMenuItem("align_top", "顶部对齐", "与画布顶部对齐"),
                        ContextMenuItem("align_middle", "垂直居中", "与画布垂直中心对齐"),
                        ContextMenuItem("align_bottom", "底部对齐", "与画布底部对齐")
                    ],
                    priority=3, separator_after=True
                ),
                ContextMenuItem(
                    "add_animation", "添加动画", "为元素添加动画效果",
                    "add_animation", priority=4
                ),
                ContextMenuItem(
                    "preview_element", "预览元素", "预览元素动画效果",
                    "preview", "Ctrl+P", priority=3
                )
            ],
            
            # 时间轴轨道上下文菜单
            ContextObjectType.TIMELINE_TRACK: [
                ContextMenuItem(
                    "add_keyframe", "添加关键帧", "在当前时间添加关键帧",
                    "keyframe", "K", priority=5
                ),
                ContextMenuItem(
                    "delete_keyframe", "删除关键帧", "删除选中的关键帧",
                    "delete_keyframe", "Shift+Delete", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "copy_track", "复制轨道", "复制整个轨道",
                    "copy", "Ctrl+C", priority=3
                ),
                ContextMenuItem(
                    "paste_track", "粘贴轨道", "粘贴轨道数据",
                    "paste", "Ctrl+V", priority=3, separator_after=True
                ),
                ContextMenuItem(
                    "track_properties", "轨道属性", "编辑轨道属性",
                    "properties", priority=3
                ),
                ContextMenuItem(
                    "mute_track", "静音轨道", "静音/取消静音轨道",
                    "mute", "M", checkable=True, priority=2
                ),
                ContextMenuItem(
                    "solo_track", "独奏轨道", "独奏/取消独奏轨道",
                    "solo", "S", checkable=True, priority=2
                )
            ],
            
            # 元素列表项上下文菜单
            ContextObjectType.ELEMENT_LIST_ITEM: [
                ContextMenuItem(
                    "select_in_stage", "在舞台中选择", "在舞台中选择此元素",
                    "select", priority=5
                ),
                ContextMenuItem(
                    "edit_element", "编辑元素", "编辑元素属性",
                    "edit", "F2", priority=5
                ),
                ContextMenuItem(
                    "rename_element", "重命名", "重命名元素",
                    "rename", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "duplicate_element", "复制元素", "复制元素",
                    "duplicate", "Ctrl+D", priority=4
                ),
                ContextMenuItem(
                    "delete_element", "删除元素", "删除元素",
                    "delete", "Delete", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "show_properties", "显示属性", "在属性面板中显示",
                    "properties", priority=3
                ),
                ContextMenuItem(
                    "isolate_element", "隔离元素", "隐藏其他元素",
                    "isolate", priority=2
                )
            ],
            
            # 空白画布上下文菜单
            ContextObjectType.CANVAS_EMPTY: [
                ContextMenuItem(
                    "paste_element", "粘贴", "粘贴剪贴板中的元素",
                    "paste", "Ctrl+V", priority=4
                ),
                ContextMenuItem(
                    "add_element", "添加元素", "添加新元素子菜单",
                    submenu=[
                        ContextMenuItem("add_text", "添加文本", "添加文本元素", "text"),
                        ContextMenuItem("add_shape", "添加图形", "添加几何图形", "shape"),
                        ContextMenuItem("add_image", "添加图片", "添加图片元素", "image"),
                        ContextMenuItem("add_path", "添加路径", "添加运动路径", "path")
                    ],
                    priority=5, separator_after=True
                ),
                ContextMenuItem(
                    "select_all", "全选", "选择所有元素",
                    "select_all", "Ctrl+A", priority=3
                ),
                ContextMenuItem(
                    "clear_canvas", "清空画布", "清空画布上的所有元素",
                    "clear", priority=2, separator_after=True
                ),
                ContextMenuItem(
                    "canvas_properties", "画布属性", "设置画布属性",
                    "properties", priority=3
                ),
                ContextMenuItem(
                    "background_settings", "背景设置", "设置画布背景",
                    "background", priority=2
                )
            ],
            
            # 代码编辑器上下文菜单
            ContextObjectType.CODE_EDITOR: [
                ContextMenuItem(
                    "copy_code", "复制代码", "复制选中的代码",
                    "copy", "Ctrl+C", priority=5
                ),
                ContextMenuItem(
                    "copy_all_code", "复制全部代码", "复制所有代码",
                    "copy_all", "Ctrl+Shift+C", priority=4, separator_after=True
                ),
                ContextMenuItem(
                    "format_code", "格式化代码", "格式化代码",
                    "format", "Ctrl+Shift+F", priority=4
                ),
                ContextMenuItem(
                    "find_replace", "查找替换", "查找和替换",
                    "find", "Ctrl+H", priority=3, separator_after=True
                ),
                ContextMenuItem(
                    "save_to_file", "保存到文件", "将代码保存到文件",
                    "save", "Ctrl+S", priority=3
                ),
                ContextMenuItem(
                    "open_in_browser", "在浏览器中打开", "在浏览器中预览",
                    "browser", priority=3
                )
            ]
        }
    
    def build_dynamic_rules(self) -> Dict[str, Callable]:
        """构建动态规则"""
        return {
            # 根据选择状态调整菜单
            "adjust_for_selection": self.adjust_menu_for_selection,
            # 根据播放状态调整菜单
            "adjust_for_playback": self.adjust_menu_for_playback,
            # 根据编辑状态调整菜单
            "adjust_for_editing": self.adjust_menu_for_editing,
            # 根据剪贴板状态调整菜单
            "adjust_for_clipboard": self.adjust_menu_for_clipboard,
            # 根据权限调整菜单
            "adjust_for_permissions": self.adjust_menu_for_permissions
        }
    
    def build_context_menu(self, object_type: ContextObjectType, 
                          context: Dict[str, Any]) -> List[ContextMenuItem]:
        """构建上下文菜单"""
        try:
            # 获取基础菜单模板
            base_menu = self.menu_templates.get(object_type, [])
            
            # 深拷贝菜单项以避免修改原模板
            menu_items = self.deep_copy_menu_items(base_menu)
            
            # 应用动态规则
            for rule_name, rule_func in self.dynamic_rules.items():
                menu_items = rule_func(menu_items, context)
            
            # 按优先级排序
            menu_items = self.sort_menu_by_priority(menu_items)
            
            return menu_items
            
        except Exception as e:
            logger.error(f"构建上下文菜单失败: {e}")
            return []
    
    def deep_copy_menu_items(self, items: List[ContextMenuItem]) -> List[ContextMenuItem]:
        """深拷贝菜单项"""
        copied_items = []
        for item in items:
            copied_item = ContextMenuItem(
                action_id=item.action_id,
                text=item.text,
                description=item.description,
                icon=item.icon,
                shortcut=item.shortcut,
                enabled=item.enabled,
                visible=item.visible,
                checkable=item.checkable,
                checked=item.checked,
                separator_after=item.separator_after,
                priority=item.priority
            )
            
            # 递归复制子菜单
            if item.submenu:
                copied_item.submenu = self.deep_copy_menu_items(item.submenu)
            
            copied_items.append(copied_item)
        
        return copied_items
    
    def adjust_menu_for_selection(self, menu_items: List[ContextMenuItem], 
                                 context: Dict[str, Any]) -> List[ContextMenuItem]:
        """根据选择状态调整菜单"""
        selection_count = context.get('selection_count', 0)
        has_selection = selection_count > 0
        multiple_selection = selection_count > 1
        
        for item in menu_items:
            # 需要选择才能执行的操作
            if item.action_id in ['edit_properties', 'duplicate_element', 'delete_element', 
                                 'copy_segment', 'edit_segment']:
                item.enabled = has_selection
            
            # 多选时禁用的操作
            if item.action_id in ['edit_properties', 'rename_element'] and multiple_selection:
                item.enabled = False
            
            # 多选时启用的操作
            if item.action_id in ['align', 'transform'] and not multiple_selection:
                item.visible = False
        
        return menu_items
    
    def adjust_menu_for_playback(self, menu_items: List[ContextMenuItem], 
                                context: Dict[str, Any]) -> List[ContextMenuItem]:
        """根据播放状态调整菜单"""
        is_playing = context.get('is_playing', False)
        
        for item in menu_items:
            # 播放时禁用某些操作
            if item.action_id in ['delete_segment', 'split_segment', 'edit_segment'] and is_playing:
                item.enabled = False
            
            # 根据播放状态调整播放/暂停菜单
            if item.action_id == 'play_segment':
                if is_playing:
                    item.text = "暂停片段"
                    item.icon = "pause"
                else:
                    item.text = "播放片段"
                    item.icon = "play"
        
        return menu_items
    
    def adjust_menu_for_editing(self, menu_items: List[ContextMenuItem], 
                               context: Dict[str, Any]) -> List[ContextMenuItem]:
        """根据编辑状态调整菜单"""
        is_editing = context.get('is_editing', False)
        
        for item in menu_items:
            # 编辑时禁用某些操作
            if item.action_id in ['delete_element', 'duplicate_element'] and is_editing:
                item.enabled = False
        
        return menu_items
    
    def adjust_menu_for_clipboard(self, menu_items: List[ContextMenuItem], 
                                 context: Dict[str, Any]) -> List[ContextMenuItem]:
        """根据剪贴板状态调整菜单"""
        has_clipboard_data = context.get('has_clipboard_data', False)
        
        for item in menu_items:
            # 根据剪贴板状态启用/禁用粘贴
            if item.action_id in ['paste_element', 'paste_track']:
                item.enabled = has_clipboard_data
        
        return menu_items
    
    def adjust_menu_for_permissions(self, menu_items: List[ContextMenuItem], 
                                   context: Dict[str, Any]) -> List[ContextMenuItem]:
        """根据权限调整菜单"""
        is_readonly = context.get('is_readonly', False)
        
        for item in menu_items:
            # 只读模式下禁用修改操作
            if is_readonly and item.action_id in ['delete_element', 'edit_properties', 
                                                 'add_element', 'clear_canvas']:
                item.enabled = False
        
        return menu_items
    
    def sort_menu_by_priority(self, menu_items: List[ContextMenuItem]) -> List[ContextMenuItem]:
        """按优先级排序菜单项"""
        return sorted(menu_items, key=lambda x: x.priority, reverse=True)
    
    def get_menu_template(self, object_type: ContextObjectType) -> List[ContextMenuItem]:
        """获取菜单模板"""
        return self.menu_templates.get(object_type, [])


class IntelligentContextMenuManager(QObject):
    """智能上下文菜单管理器"""

    context_action_triggered = pyqtSignal(str, dict)  # 上下文动作触发信号

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.menu_builder = IntelligentContextMenuBuilder()
        self.active_menus: Dict[str, QMenu] = {}
        self.context_cache: Dict[str, Dict[str, Any]] = {}

        logger.info("智能上下文菜单管理器初始化完成")

    def show_context_menu(self, object_type: ContextObjectType, position: QPoint,
                         context: Dict[str, Any] = None):
        """显示智能上下文菜单"""
        try:
            if context is None:
                context = {}

            # 增强上下文信息
            enhanced_context = self.enhance_context(object_type, context)

            # 构建菜单项
            menu_items = self.menu_builder.build_context_menu(object_type, enhanced_context)

            if not menu_items:
                logger.warning(f"没有可用的上下文菜单项: {object_type}")
                return

            # 创建QMenu
            menu = self.create_qmenu(menu_items, enhanced_context)

            # 显示菜单
            menu.exec(position)

            logger.debug(f"显示上下文菜单: {object_type.value} at {position}")

        except Exception as e:
            logger.error(f"显示上下文菜单失败: {e}")

    def enhance_context(self, object_type: ContextObjectType,
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """增强上下文信息"""
        enhanced = context.copy()

        try:
            # 添加应用程序状态信息
            enhanced['is_playing'] = self.get_playback_state()
            enhanced['has_clipboard_data'] = self.has_clipboard_data()
            enhanced['is_readonly'] = self.is_readonly_mode()
            enhanced['selection_count'] = self.get_selection_count(object_type)
            enhanced['is_editing'] = self.is_editing_mode()

            # 添加对象特定的上下文信息
            if object_type == ContextObjectType.AUDIO_SEGMENT:
                enhanced.update(self.get_audio_segment_context(context))
            elif object_type == ContextObjectType.STAGE_ELEMENT:
                enhanced.update(self.get_stage_element_context(context))
            elif object_type == ContextObjectType.TIMELINE_TRACK:
                enhanced.update(self.get_timeline_track_context(context))

        except Exception as e:
            logger.error(f"增强上下文信息失败: {e}")

        return enhanced

    def create_qmenu(self, menu_items: List[ContextMenuItem],
                    context: Dict[str, Any]) -> QMenu:
        """创建QMenu对象"""
        menu = QMenu(self.main_window)

        for item in menu_items:
            if not item.visible:
                continue

            if item.action_id.startswith("separator") or item.separator_after:
                if menu.actions():  # 只有在有其他动作时才添加分隔符
                    menu.addSeparator()
                continue

            if item.submenu:
                # 创建子菜单
                submenu = menu.addMenu(item.text)
                submenu.setToolTip(item.description)
                self.populate_submenu(submenu, item.submenu, context)
            else:
                # 创建普通菜单项
                action = menu.addAction(item.text)
                action.setToolTip(item.description)
                action.setEnabled(item.enabled)

                if item.checkable:
                    action.setCheckable(True)
                    action.setChecked(item.checked)

                if item.shortcut:
                    action.setShortcut(QKeySequence(item.shortcut))

                # 连接信号
                action.triggered.connect(
                    lambda checked, aid=item.action_id: self.handle_context_action(aid, context)
                )

            # 添加分隔符
            if item.separator_after:
                menu.addSeparator()

        return menu

    def populate_submenu(self, submenu: QMenu, items: List[ContextMenuItem],
                        context: Dict[str, Any]):
        """填充子菜单"""
        for item in items:
            if not item.visible:
                continue

            if item.action_id.startswith("separator") or item.separator_after:
                if submenu.actions():
                    submenu.addSeparator()
                continue

            action = submenu.addAction(item.text)
            action.setToolTip(item.description)
            action.setEnabled(item.enabled)

            if item.checkable:
                action.setCheckable(True)
                action.setChecked(item.checked)

            # 连接信号
            action.triggered.connect(
                lambda checked, aid=item.action_id: self.handle_context_action(aid, context)
            )

            if item.separator_after:
                submenu.addSeparator()

    def handle_context_action(self, action_id: str, context: Dict[str, Any]):
        """处理上下文菜单动作"""
        try:
            logger.info(f"执行上下文菜单动作: {action_id}")

            # 发送信号
            self.context_action_triggered.emit(action_id, context)

        except Exception as e:
            logger.error(f"处理上下文菜单动作失败 {action_id}: {e}")

    def get_playback_state(self) -> bool:
        """获取播放状态"""
        try:
            if hasattr(self.main_window, 'is_playing'):
                return self.main_window.is_playing
            return False
        except:
            return False

    def has_clipboard_data(self) -> bool:
        """检查剪贴板是否有数据"""
        try:
            clipboard = QApplication.clipboard()
            return not clipboard.text().strip() == ""
        except:
            return False

    def is_readonly_mode(self) -> bool:
        """检查是否为只读模式"""
        try:
            if hasattr(self.main_window, 'is_readonly'):
                return self.main_window.is_readonly
            return False
        except:
            return False

    def get_selection_count(self, object_type: ContextObjectType) -> int:
        """获取选择数量"""
        try:
            if object_type == ContextObjectType.STAGE_ELEMENT:
                if hasattr(self.main_window, 'stage_widget'):
                    return len(getattr(self.main_window.stage_widget, 'selected_elements', []))
            elif object_type == ContextObjectType.ELEMENT_LIST_ITEM:
                if hasattr(self.main_window, 'elements_widget'):
                    return len(getattr(self.main_window.elements_widget, 'selected_items', []))
            return 0
        except:
            return 0

    def is_editing_mode(self) -> bool:
        """检查是否为编辑模式"""
        try:
            if hasattr(self.main_window, 'is_editing'):
                return self.main_window.is_editing
            return False
        except:
            return False

    def get_audio_segment_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取音频片段上下文"""
        additional_context = {}
        try:
            segment_id = context.get('segment_id')
            if segment_id and hasattr(self.main_window, 'audio_widget'):
                audio_widget = self.main_window.audio_widget
                # 添加音频片段特定信息
                additional_context['segment_duration'] = getattr(audio_widget, 'get_segment_duration', lambda x: 0)(segment_id)
                additional_context['has_description'] = getattr(audio_widget, 'has_description', lambda x: False)(segment_id)
        except Exception as e:
            logger.debug(f"获取音频片段上下文失败: {e}")

        return additional_context

    def get_stage_element_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取舞台元素上下文"""
        additional_context = {}
        try:
            element_id = context.get('element_id')
            if element_id and hasattr(self.main_window, 'stage_widget'):
                stage_widget = self.main_window.stage_widget
                # 添加舞台元素特定信息
                additional_context['element_type'] = getattr(stage_widget, 'get_element_type', lambda x: 'unknown')(element_id)
                additional_context['is_locked'] = getattr(stage_widget, 'is_element_locked', lambda x: False)(element_id)
                additional_context['has_animation'] = getattr(stage_widget, 'has_animation', lambda x: False)(element_id)
        except Exception as e:
            logger.debug(f"获取舞台元素上下文失败: {e}")

        return additional_context

    def get_timeline_track_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取时间轴轨道上下文"""
        additional_context = {}
        try:
            track_id = context.get('track_id')
            if track_id and hasattr(self.main_window, 'timeline_widget'):
                timeline_widget = self.main_window.timeline_widget
                # 添加时间轴轨道特定信息
                additional_context['track_type'] = getattr(timeline_widget, 'get_track_type', lambda x: 'unknown')(track_id)
                additional_context['is_muted'] = getattr(timeline_widget, 'is_track_muted', lambda x: False)(track_id)
                additional_context['keyframe_count'] = getattr(timeline_widget, 'get_keyframe_count', lambda x: 0)(track_id)
        except Exception as e:
            logger.debug(f"获取时间轴轨道上下文失败: {e}")

        return additional_context


class ContextMenuActionHandler:
    """上下文菜单动作处理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.action_handlers = self.setup_action_handlers()

        logger.info("上下文菜单动作处理器初始化完成")

    def setup_action_handlers(self) -> Dict[str, Callable]:
        """设置动作处理器映射"""
        return {
            # 音频片段操作
            "play_segment": self.play_audio_segment,
            "edit_segment": self.edit_audio_segment,
            "split_segment": self.split_audio_segment,
            "copy_segment": self.copy_audio_segment,
            "delete_segment": self.delete_audio_segment,
            "add_animation_desc": self.add_animation_description,
            "generate_ai_animation": self.generate_ai_animation,

            # 时间段操作
            "edit_time_range": self.edit_time_range,
            "set_description": self.set_time_segment_description,
            "duplicate_segment": self.duplicate_time_segment,
            "merge_segments": self.merge_time_segments,
            "split_at_cursor": self.split_at_cursor,
            "preview_segment": self.preview_time_segment,
            "export_segment": self.export_time_segment,

            # 舞台元素操作
            "edit_properties": self.edit_element_properties,
            "duplicate_element": self.duplicate_stage_element,
            "delete_element": self.delete_stage_element,
            "move_to_front": self.move_element_to_front,
            "move_forward": self.move_element_forward,
            "move_backward": self.move_element_backward,
            "move_to_back": self.move_element_to_back,
            "flip_horizontal": self.flip_element_horizontal,
            "flip_vertical": self.flip_element_vertical,
            "rotate_90": self.rotate_element_90,
            "align_left": self.align_elements_left,
            "align_center": self.align_elements_center,
            "align_right": self.align_elements_right,
            "align_top": self.align_elements_top,
            "align_middle": self.align_elements_middle,
            "align_bottom": self.align_elements_bottom,
            "add_animation": self.add_element_animation,
            "preview_element": self.preview_element_animation,

            # 时间轴轨道操作
            "add_keyframe": self.add_timeline_keyframe,
            "delete_keyframe": self.delete_timeline_keyframe,
            "copy_track": self.copy_timeline_track,
            "paste_track": self.paste_timeline_track,
            "track_properties": self.edit_track_properties,
            "mute_track": self.toggle_track_mute,
            "solo_track": self.toggle_track_solo,

            # 元素列表操作
            "select_in_stage": self.select_element_in_stage,
            "edit_element": self.edit_list_element,
            "rename_element": self.rename_element,
            "show_properties": self.show_element_properties,
            "isolate_element": self.isolate_element,

            # 画布操作
            "paste_element": self.paste_canvas_element,
            "add_text": self.add_text_element,
            "add_shape": self.add_shape_element,
            "add_image": self.add_image_element,
            "add_path": self.add_path_element,
            "select_all": self.select_all_elements,
            "clear_canvas": self.clear_canvas,
            "canvas_properties": self.show_canvas_properties,
            "background_settings": self.show_background_settings,

            # 代码编辑器操作
            "copy_code": self.copy_selected_code,
            "copy_all_code": self.copy_all_code,
            "format_code": self.format_code,
            "find_replace": self.show_find_replace,
            "save_to_file": self.save_code_to_file,
            "open_in_browser": self.open_code_in_browser
        }

    def handle_action(self, action_id: str, context: Dict[str, Any]):
        """处理上下文菜单动作"""
        try:
            if action_id in self.action_handlers:
                self.action_handlers[action_id](context)
            else:
                logger.warning(f"未处理的上下文菜单动作: {action_id}")

        except Exception as e:
            logger.error(f"处理上下文菜单动作失败 {action_id}: {e}")

    # 音频片段操作实现
    def play_audio_segment(self, context: Dict[str, Any]):
        """播放音频片段"""
        segment_id = context.get('segment_id')
        if segment_id and hasattr(self.main_window, 'play_audio_segment'):
            self.main_window.play_audio_segment(segment_id)

    def edit_audio_segment(self, context: Dict[str, Any]):
        """编辑音频片段"""
        segment_id = context.get('segment_id')
        if segment_id and hasattr(self.main_window, 'edit_audio_segment'):
            self.main_window.edit_audio_segment(segment_id)

    def split_audio_segment(self, context: Dict[str, Any]):
        """分割音频片段"""
        segment_id = context.get('segment_id')
        position = context.get('position', 0)
        if segment_id and hasattr(self.main_window, 'split_audio_segment'):
            self.main_window.split_audio_segment(segment_id, position)

    def copy_audio_segment(self, context: Dict[str, Any]):
        """复制音频片段"""
        segment_id = context.get('segment_id')
        if segment_id and hasattr(self.main_window, 'copy_audio_segment'):
            self.main_window.copy_audio_segment(segment_id)

    def delete_audio_segment(self, context: Dict[str, Any]):
        """删除音频片段"""
        segment_id = context.get('segment_id')
        if segment_id and hasattr(self.main_window, 'delete_audio_segment'):
            self.main_window.delete_audio_segment(segment_id)

    def add_animation_description(self, context: Dict[str, Any]):
        """添加动画描述"""
        segment_id = context.get('segment_id')
        if segment_id and hasattr(self.main_window, 'add_animation_description'):
            self.main_window.add_animation_description(segment_id)

    def generate_ai_animation(self, context: Dict[str, Any]):
        """生成AI动画"""
        segment_id = context.get('segment_id')
        if segment_id and hasattr(self.main_window, 'generate_ai_animation'):
            self.main_window.generate_ai_animation(segment_id)

    # 其他操作的占位符实现
    def edit_time_range(self, context: Dict[str, Any]):
        """编辑时间范围"""
        logger.info("编辑时间范围")

    def set_time_segment_description(self, context: Dict[str, Any]):
        """设置时间段描述"""
        logger.info("设置时间段描述")

    def duplicate_time_segment(self, context: Dict[str, Any]):
        """复制时间段"""
        logger.info("复制时间段")

    def merge_time_segments(self, context: Dict[str, Any]):
        """合并时间段"""
        logger.info("合并时间段")

    def split_at_cursor(self, context: Dict[str, Any]):
        """在光标处分割"""
        logger.info("在光标处分割")

    def preview_time_segment(self, context: Dict[str, Any]):
        """预览时间段"""
        logger.info("预览时间段")

    def export_time_segment(self, context: Dict[str, Any]):
        """导出时间段"""
        logger.info("导出时间段")

    # 舞台元素操作占位符
    def edit_element_properties(self, context: Dict[str, Any]):
        """编辑元素属性"""
        logger.info("编辑元素属性")

    def duplicate_stage_element(self, context: Dict[str, Any]):
        """复制舞台元素"""
        logger.info("复制舞台元素")

    def delete_stage_element(self, context: Dict[str, Any]):
        """删除舞台元素"""
        logger.info("删除舞台元素")

    def move_element_to_front(self, context: Dict[str, Any]):
        """移动元素到最前"""
        logger.info("移动元素到最前")

    def move_element_forward(self, context: Dict[str, Any]):
        """向前移动元素"""
        logger.info("向前移动元素")

    def move_element_backward(self, context: Dict[str, Any]):
        """向后移动元素"""
        logger.info("向后移动元素")

    def move_element_to_back(self, context: Dict[str, Any]):
        """移动元素到最后"""
        logger.info("移动元素到最后")

    def flip_element_horizontal(self, context: Dict[str, Any]):
        """水平翻转元素"""
        logger.info("水平翻转元素")

    def flip_element_vertical(self, context: Dict[str, Any]):
        """垂直翻转元素"""
        logger.info("垂直翻转元素")

    def rotate_element_90(self, context: Dict[str, Any]):
        """旋转元素90度"""
        logger.info("旋转元素90度")

    def align_elements_left(self, context: Dict[str, Any]):
        """左对齐元素"""
        logger.info("左对齐元素")

    def align_elements_center(self, context: Dict[str, Any]):
        """居中对齐元素"""
        logger.info("居中对齐元素")

    def align_elements_right(self, context: Dict[str, Any]):
        """右对齐元素"""
        logger.info("右对齐元素")

    def align_elements_top(self, context: Dict[str, Any]):
        """顶部对齐元素"""
        logger.info("顶部对齐元素")

    def align_elements_middle(self, context: Dict[str, Any]):
        """垂直居中对齐元素"""
        logger.info("垂直居中对齐元素")

    def align_elements_bottom(self, context: Dict[str, Any]):
        """底部对齐元素"""
        logger.info("底部对齐元素")

    def add_element_animation(self, context: Dict[str, Any]):
        """添加元素动画"""
        logger.info("添加元素动画")

    def preview_element_animation(self, context: Dict[str, Any]):
        """预览元素动画"""
        logger.info("预览元素动画")

    # 时间轴轨道操作占位符
    def add_timeline_keyframe(self, context: Dict[str, Any]):
        """添加时间轴关键帧"""
        logger.info("添加时间轴关键帧")

    def delete_timeline_keyframe(self, context: Dict[str, Any]):
        """删除时间轴关键帧"""
        logger.info("删除时间轴关键帧")

    def copy_timeline_track(self, context: Dict[str, Any]):
        """复制时间轴轨道"""
        logger.info("复制时间轴轨道")

    def paste_timeline_track(self, context: Dict[str, Any]):
        """粘贴时间轴轨道"""
        logger.info("粘贴时间轴轨道")

    def edit_track_properties(self, context: Dict[str, Any]):
        """编辑轨道属性"""
        logger.info("编辑轨道属性")

    def toggle_track_mute(self, context: Dict[str, Any]):
        """切换轨道静音"""
        logger.info("切换轨道静音")

    def toggle_track_solo(self, context: Dict[str, Any]):
        """切换轨道独奏"""
        logger.info("切换轨道独奏")

    # 元素列表操作占位符
    def select_element_in_stage(self, context: Dict[str, Any]):
        """在舞台中选择元素"""
        logger.info("在舞台中选择元素")

    def edit_list_element(self, context: Dict[str, Any]):
        """编辑列表元素"""
        logger.info("编辑列表元素")

    def rename_element(self, context: Dict[str, Any]):
        """重命名元素"""
        logger.info("重命名元素")

    def show_element_properties(self, context: Dict[str, Any]):
        """显示元素属性"""
        logger.info("显示元素属性")

    def isolate_element(self, context: Dict[str, Any]):
        """隔离元素"""
        logger.info("隔离元素")

    # 画布操作占位符
    def paste_canvas_element(self, context: Dict[str, Any]):
        """粘贴画布元素"""
        logger.info("粘贴画布元素")

    def add_text_element(self, context: Dict[str, Any]):
        """添加文本元素"""
        logger.info("添加文本元素")

    def add_shape_element(self, context: Dict[str, Any]):
        """添加图形元素"""
        logger.info("添加图形元素")

    def add_image_element(self, context: Dict[str, Any]):
        """添加图片元素"""
        logger.info("添加图片元素")

    def add_path_element(self, context: Dict[str, Any]):
        """添加路径元素"""
        logger.info("添加路径元素")

    def select_all_elements(self, context: Dict[str, Any]):
        """选择所有元素"""
        logger.info("选择所有元素")

    def clear_canvas(self, context: Dict[str, Any]):
        """清空画布"""
        logger.info("清空画布")

    def show_canvas_properties(self, context: Dict[str, Any]):
        """显示画布属性"""
        logger.info("显示画布属性")

    def show_background_settings(self, context: Dict[str, Any]):
        """显示背景设置"""
        logger.info("显示背景设置")

    # 代码编辑器操作占位符
    def copy_selected_code(self, context: Dict[str, Any]):
        """复制选中代码"""
        logger.info("复制选中代码")

    def copy_all_code(self, context: Dict[str, Any]):
        """复制全部代码"""
        logger.info("复制全部代码")

    def format_code(self, context: Dict[str, Any]):
        """格式化代码"""
        logger.info("格式化代码")

    def show_find_replace(self, context: Dict[str, Any]):
        """显示查找替换"""
        logger.info("显示查找替换")

    def save_code_to_file(self, context: Dict[str, Any]):
        """保存代码到文件"""
        logger.info("保存代码到文件")

    def open_code_in_browser(self, context: Dict[str, Any]):
        """在浏览器中打开代码"""
        logger.info("在浏览器中打开代码")


class IntelligentContextMenuIntegrator:
    """智能上下文菜单集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_manager = IntelligentContextMenuManager(main_window)
        self.action_handler = ContextMenuActionHandler(main_window)

        # 连接信号
        self.menu_manager.context_action_triggered.connect(
            self.action_handler.handle_action
        )

        logger.info("智能上下文菜单集成器初始化完成")

    def integrate_context_menu_system(self):
        """集成智能上下文菜单系统"""
        try:
            # 为各个组件安装上下文菜单
            self.install_audio_context_menus()
            self.install_stage_context_menus()
            self.install_timeline_context_menus()
            self.install_elements_context_menus()
            self.install_code_context_menus()

            logger.info("智能上下文菜单系统集成完成")
            return True

        except Exception as e:
            logger.error(f"智能上下文菜单系统集成失败: {e}")
            return False

    def install_audio_context_menus(self):
        """安装音频组件上下文菜单"""
        try:
            if hasattr(self.main_window, 'audio_widget'):
                audio_widget = self.main_window.audio_widget

                # 重写右键菜单事件
                original_context_menu = getattr(audio_widget, 'contextMenuEvent', None)

                def audio_context_menu_event(event):
                    position = event.pos()
                    global_position = audio_widget.mapToGlobal(position)

                    # 检测点击的音频片段
                    segment_id = self.get_audio_segment_at_position(audio_widget, position)

                    if segment_id:
                        context = {
                            'segment_id': segment_id,
                            'position': position.x(),
                            'widget': audio_widget
                        }
                        self.menu_manager.show_context_menu(
                            ContextObjectType.AUDIO_SEGMENT,
                            global_position,
                            context
                        )
                    elif original_context_menu:
                        original_context_menu(event)

                audio_widget.contextMenuEvent = audio_context_menu_event
                logger.debug("音频组件上下文菜单已安装")

        except Exception as e:
            logger.error(f"安装音频上下文菜单失败: {e}")

    def install_stage_context_menus(self):
        """安装舞台组件上下文菜单"""
        try:
            if hasattr(self.main_window, 'stage_widget'):
                stage_widget = self.main_window.stage_widget

                # 重写右键菜单事件
                original_context_menu = getattr(stage_widget, 'contextMenuEvent', None)

                def stage_context_menu_event(event):
                    position = event.pos()
                    global_position = stage_widget.mapToGlobal(position)

                    # 检测点击的舞台元素
                    element_id = self.get_stage_element_at_position(stage_widget, position)

                    if element_id:
                        context = {
                            'element_id': element_id,
                            'position': position,
                            'widget': stage_widget
                        }
                        self.menu_manager.show_context_menu(
                            ContextObjectType.STAGE_ELEMENT,
                            global_position,
                            context
                        )
                    else:
                        # 空白画布
                        context = {
                            'position': position,
                            'widget': stage_widget
                        }
                        self.menu_manager.show_context_menu(
                            ContextObjectType.CANVAS_EMPTY,
                            global_position,
                            context
                        )

                stage_widget.contextMenuEvent = stage_context_menu_event
                logger.debug("舞台组件上下文菜单已安装")

        except Exception as e:
            logger.error(f"安装舞台上下文菜单失败: {e}")

    def install_timeline_context_menus(self):
        """安装时间轴组件上下文菜单"""
        try:
            if hasattr(self.main_window, 'timeline_widget'):
                timeline_widget = self.main_window.timeline_widget

                # 重写右键菜单事件
                original_context_menu = getattr(timeline_widget, 'contextMenuEvent', None)

                def timeline_context_menu_event(event):
                    position = event.pos()
                    global_position = timeline_widget.mapToGlobal(position)

                    # 检测点击的轨道或时间段
                    track_id = self.get_timeline_track_at_position(timeline_widget, position)
                    segment_id = self.get_time_segment_at_position(timeline_widget, position)

                    if segment_id:
                        context = {
                            'segment_id': segment_id,
                            'track_id': track_id,
                            'position': position,
                            'widget': timeline_widget
                        }
                        self.menu_manager.show_context_menu(
                            ContextObjectType.TIME_SEGMENT,
                            global_position,
                            context
                        )
                    elif track_id:
                        context = {
                            'track_id': track_id,
                            'position': position,
                            'widget': timeline_widget
                        }
                        self.menu_manager.show_context_menu(
                            ContextObjectType.TIMELINE_TRACK,
                            global_position,
                            context
                        )
                    elif original_context_menu:
                        original_context_menu(event)

                timeline_widget.contextMenuEvent = timeline_context_menu_event
                logger.debug("时间轴组件上下文菜单已安装")

        except Exception as e:
            logger.error(f"安装时间轴上下文菜单失败: {e}")

    def install_elements_context_menus(self):
        """安装元素列表上下文菜单"""
        try:
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget

                # 查找元素列表组件
                if hasattr(elements_widget, 'elements_list'):
                    elements_list = elements_widget.elements_list

                    # 重写右键菜单事件
                    original_context_menu = getattr(elements_list, 'contextMenuEvent', None)

                    def elements_context_menu_event(event):
                        position = event.pos()
                        global_position = elements_list.mapToGlobal(position)

                        # 检测点击的元素项
                        item = elements_list.itemAt(position)

                        if item:
                            element_id = self.get_element_id_from_item(item)
                            context = {
                                'element_id': element_id,
                                'item': item,
                                'position': position,
                                'widget': elements_list
                            }
                            self.menu_manager.show_context_menu(
                                ContextObjectType.ELEMENT_LIST_ITEM,
                                global_position,
                                context
                            )
                        elif original_context_menu:
                            original_context_menu(event)

                    elements_list.contextMenuEvent = elements_context_menu_event
                    logger.debug("元素列表上下文菜单已安装")

        except Exception as e:
            logger.error(f"安装元素列表上下文菜单失败: {e}")

    def install_code_context_menus(self):
        """安装代码编辑器上下文菜单"""
        try:
            if hasattr(self.main_window, 'code_view'):
                code_view = self.main_window.code_view

                # 重写右键菜单事件
                original_context_menu = getattr(code_view, 'contextMenuEvent', None)

                def code_context_menu_event(event):
                    position = event.pos()
                    global_position = code_view.mapToGlobal(position)

                    context = {
                        'position': position,
                        'widget': code_view,
                        'has_selection': code_view.textCursor().hasSelection()
                    }
                    self.menu_manager.show_context_menu(
                        ContextObjectType.CODE_EDITOR,
                        global_position,
                        context
                    )

                code_view.contextMenuEvent = code_context_menu_event
                logger.debug("代码编辑器上下文菜单已安装")

        except Exception as e:
            logger.error(f"安装代码编辑器上下文菜单失败: {e}")

    def get_audio_segment_at_position(self, widget, position) -> Optional[str]:
        """获取指定位置的音频片段ID"""
        try:
            if hasattr(widget, 'get_segment_at_position'):
                return widget.get_segment_at_position(position)
            return None
        except:
            return None

    def get_stage_element_at_position(self, widget, position) -> Optional[str]:
        """获取指定位置的舞台元素ID"""
        try:
            if hasattr(widget, 'get_element_at_position'):
                return widget.get_element_at_position(position)
            return None
        except:
            return None

    def get_timeline_track_at_position(self, widget, position) -> Optional[str]:
        """获取指定位置的时间轴轨道ID"""
        try:
            if hasattr(widget, 'get_track_at_position'):
                return widget.get_track_at_position(position)
            return None
        except:
            return None

    def get_time_segment_at_position(self, widget, position) -> Optional[str]:
        """获取指定位置的时间段ID"""
        try:
            if hasattr(widget, 'get_segment_at_position'):
                return widget.get_segment_at_position(position)
            return None
        except:
            return None

    def get_element_id_from_item(self, item) -> Optional[str]:
        """从列表项获取元素ID"""
        try:
            if hasattr(item, 'data'):
                return item.data(Qt.ItemDataRole.UserRole)
            return None
        except:
            return None

    def get_menu_manager(self) -> IntelligentContextMenuManager:
        """获取菜单管理器"""
        return self.menu_manager

    def get_action_handler(self) -> ContextMenuActionHandler:
        """获取动作处理器"""
        return self.action_handler

    def export_context_menu_configuration(self, file_path: str):
        """导出上下文菜单配置"""
        try:
            config = {
                "object_types": [obj_type.value for obj_type in ContextObjectType],
                "context_states": [state.value for state in ContextState],
                "menu_templates": len(self.menu_manager.menu_builder.menu_templates),
                "dynamic_rules": len(self.menu_manager.menu_builder.dynamic_rules),
                "action_handlers": len(self.action_handler.action_handlers)
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"上下文菜单配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出上下文菜单配置失败: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        return {
            "object_types": len(ContextObjectType),
            "context_states": len(ContextState),
            "menu_templates": len(self.menu_manager.menu_builder.menu_templates),
            "dynamic_rules": len(self.menu_manager.menu_builder.dynamic_rules),
            "action_handlers": len(self.action_handler.action_handlers),
            "integration_status": "completed"
        }
