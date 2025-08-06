"""
AI Animation Studio - 状态衔接管理器
实现动画状态的记录、验证和衔接功能
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from core.logger import get_logger

logger = get_logger("state_manager")

@dataclass
class ElementState:
    """元素状态数据结构"""
    element_id: str
    timestamp: float
    segment_id: str
    
    # Transform属性
    transform: Dict[str, Any]
    
    # 视觉属性
    visual: Dict[str, Any]
    
    # 布局属性
    layout: Dict[str, Any]
    
    # 动画属性
    animation: Dict[str, Any]
    
    # 自定义属性
    custom_properties: Dict[str, Any]
    
    # 状态来源
    source: str = "ai_generated"  # ai_generated, live_captured, user_defined
    confidence: float = 1.0

@dataclass
class StateTransition:
    """状态转换数据"""
    from_segment: str
    to_segment: str
    element_id: str
    start_state: ElementState
    end_state: ElementState
    transition_type: str = "smooth"  # smooth, jump, fade
    validation_result: Optional[Dict] = None

class StateManager(QObject):
    """状态管理器"""

    # 信号定义
    state_changed = pyqtSignal(str, dict)  # element_id, state_data
    state_updated = pyqtSignal(str, str, dict)  # element_id, segment_id, state_data
    transition_created = pyqtSignal(str, str, str)  # from_segment, to_segment, element_id

    def __init__(self):
        super().__init__()
        self.element_states: Dict[str, List[ElementState]] = {}
        self.transitions: List[StateTransition] = []
        self.tolerance_settings = {
            'position': 5.0,      # 位置误差5px内可接受
            'rotation': 2.0,      # 旋转误差2度内可接受
            'scale': 0.05,        # 缩放误差5%内可接受
            'opacity': 0.1        # 透明度误差0.1内可接受
        }

        # 订阅者管理
        self._subscribers: Dict[str, List[Callable]] = {}

        logger.info("状态管理器初始化完成")
    
    def record_element_state(self, element_id: str, segment_id: str, 
                           state_data: Dict, source: str = "ai_generated") -> ElementState:
        """记录元素状态"""
        try:
            # 创建状态对象
            state = ElementState(
                element_id=element_id,
                timestamp=time.time(),
                segment_id=segment_id,
                transform=state_data.get('transform', {}),
                visual=state_data.get('visual', {}),
                layout=state_data.get('layout', {}),
                animation=state_data.get('animation', {}),
                custom_properties=state_data.get('custom_properties', {}),
                source=source
            )
            
            # 存储状态
            if element_id not in self.element_states:
                self.element_states[element_id] = []
            
            self.element_states[element_id].append(state)

            # 发射状态更新信号
            self.state_updated.emit(element_id, segment_id, asdict(state))
            self.notify_subscribers('state_updated', element_id, segment_id, asdict(state))

            logger.info(f"已记录元素状态: {element_id} @ {segment_id}")
            return state
            
        except Exception as e:
            logger.error(f"记录元素状态失败: {e}")
            raise
    
    def get_element_state(self, element_id: str, segment_id: str) -> Optional[ElementState]:
        """获取元素在指定段落的状态"""
        if element_id not in self.element_states:
            return None
        
        # 查找指定段落的状态
        for state in self.element_states[element_id]:
            if state.segment_id == segment_id:
                return state
        
        return None
    
    def get_latest_state(self, element_id: str) -> Optional[ElementState]:
        """获取元素的最新状态"""
        if element_id not in self.element_states:
            return None
        
        states = self.element_states[element_id]
        if not states:
            return None
        
        # 按时间戳排序，返回最新的
        return max(states, key=lambda s: s.timestamp)
    
    def validate_state_continuity(self, from_segment: str, to_segment: str) -> Dict[str, Any]:
        """验证状态连续性"""
        validation_results = {
            'overall_status': 'success',
            'element_results': {},
            'conflicts': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # 获取所有涉及的元素
            elements = set()
            for element_id in self.element_states:
                for state in self.element_states[element_id]:
                    if state.segment_id in [from_segment, to_segment]:
                        elements.add(element_id)
            
            # 验证每个元素的状态连续性
            for element_id in elements:
                from_state = self.get_element_state(element_id, from_segment)
                to_state = self.get_element_state(element_id, to_segment)
                
                element_result = self.validate_element_continuity(
                    element_id, from_state, to_state
                )
                
                validation_results['element_results'][element_id] = element_result
                
                # 收集冲突和警告
                if element_result['status'] == 'conflict':
                    validation_results['conflicts'].extend(element_result['issues'])
                elif element_result['status'] == 'warning':
                    validation_results['warnings'].extend(element_result['issues'])
            
            # 确定整体状态
            if validation_results['conflicts']:
                validation_results['overall_status'] = 'conflict'
            elif validation_results['warnings']:
                validation_results['overall_status'] = 'warning'
            
            logger.info(f"状态连续性验证完成: {from_segment} -> {to_segment}")
            
        except Exception as e:
            logger.error(f"状态连续性验证失败: {e}")
            validation_results['overall_status'] = 'error'
            validation_results['error'] = str(e)
        
        return validation_results
    
    def validate_element_continuity(self, element_id: str, 
                                  from_state: Optional[ElementState], 
                                  to_state: Optional[ElementState]) -> Dict[str, Any]:
        """验证单个元素的状态连续性"""
        result = {
            'element_id': element_id,
            'status': 'success',
            'issues': [],
            'differences': {}
        }
        
        # 如果缺少状态
        if not from_state and not to_state:
            return result
        
        if not from_state:
            result['status'] = 'warning'
            result['issues'].append(f"元素 {element_id} 缺少起始状态")
            return result
        
        if not to_state:
            result['status'] = 'warning'
            result['issues'].append(f"元素 {element_id} 缺少结束状态")
            return result
        
        # 比较关键属性
        differences = self.compare_states(from_state, to_state)
        result['differences'] = differences
        
        # 检查是否有显著差异
        significant_diffs = []
        for prop, diff in differences.items():
            if self.is_significant_difference(prop, diff):
                significant_diffs.append({
                    'property': prop,
                    'from_value': diff['from'],
                    'to_value': diff['to'],
                    'difference': diff['diff']
                })
        
        if significant_diffs:
            result['status'] = 'conflict'
            result['issues'] = significant_diffs
        
        return result
    
    def compare_states(self, state1: ElementState, state2: ElementState) -> Dict[str, Any]:
        """比较两个状态的差异"""
        differences = {}
        
        # 比较transform属性
        for prop in ['translateX', 'translateY', 'rotateZ', 'scaleX', 'scaleY']:
            val1 = state1.transform.get(prop, 0)
            val2 = state2.transform.get(prop, 0)
            
            if val1 != val2:
                differences[f'transform.{prop}'] = {
                    'from': val1,
                    'to': val2,
                    'diff': abs(float(val1) - float(val2)) if isinstance(val1, (int, float)) and isinstance(val2, (int, float)) else None
                }
        
        # 比较visual属性
        for prop in ['opacity', 'color', 'backgroundColor']:
            val1 = state1.visual.get(prop)
            val2 = state2.visual.get(prop)
            
            if val1 != val2:
                differences[f'visual.{prop}'] = {
                    'from': val1,
                    'to': val2,
                    'diff': None
                }
        
        return differences
    
    def is_significant_difference(self, property_name: str, diff_data: Dict) -> bool:
        """判断差异是否显著"""
        if diff_data['diff'] is None:
            return True  # 非数值差异都认为是显著的
        
        diff_value = diff_data['diff']
        
        # 根据属性类型判断
        if 'translateX' in property_name or 'translateY' in property_name:
            return diff_value > self.tolerance_settings['position']
        elif 'rotate' in property_name:
            return diff_value > self.tolerance_settings['rotation']
        elif 'scale' in property_name:
            return diff_value > self.tolerance_settings['scale']
        elif 'opacity' in property_name:
            return diff_value > self.tolerance_settings['opacity']
        
        return diff_value > 0  # 默认任何差异都是显著的
    
    def create_transition(self, from_segment: str, to_segment: str, 
                         element_id: str) -> Optional[StateTransition]:
        """创建状态转换"""
        from_state = self.get_element_state(element_id, from_segment)
        to_state = self.get_element_state(element_id, to_segment)
        
        if not from_state or not to_state:
            logger.warning(f"无法创建转换，缺少状态: {element_id}")
            return None
        
        # 验证转换
        validation = self.validate_element_continuity(element_id, from_state, to_state)
        
        transition = StateTransition(
            from_segment=from_segment,
            to_segment=to_segment,
            element_id=element_id,
            start_state=from_state,
            end_state=to_state,
            validation_result=validation
        )
        
        self.transitions.append(transition)
        return transition
    
    def auto_fix_state_inconsistency(self, element_id: str, 
                                   from_segment: str, to_segment: str) -> Dict[str, Any]:
        """自动修复状态不一致"""
        result = {
            'success': False,
            'method': None,
            'fixed_state': None,
            'message': ''
        }
        
        try:
            from_state = self.get_element_state(element_id, from_segment)
            to_state = self.get_element_state(element_id, to_segment)
            
            if not from_state or not to_state:
                result['message'] = "缺少必要的状态数据"
                return result
            
            # 策略1: 使用from_state的结束状态作为to_state的开始状态
            if from_state.source == "live_captured":
                # 如果from_state是实时捕获的，优先使用它
                fixed_state = self.create_interpolated_state(from_state, to_state)
                result['method'] = 'interpolation'
                result['fixed_state'] = fixed_state
                result['success'] = True
                result['message'] = '使用插值方法修复状态'
            
            # 策略2: 创建平滑过渡
            else:
                fixed_state = self.create_smooth_transition(from_state, to_state)
                result['method'] = 'smooth_transition'
                result['fixed_state'] = fixed_state
                result['success'] = True
                result['message'] = '创建平滑过渡'
            
        except Exception as e:
            result['message'] = f"自动修复失败: {str(e)}"
            logger.error(f"自动修复状态失败: {e}")
        
        return result
    
    def create_interpolated_state(self, state1: ElementState, state2: ElementState) -> ElementState:
        """创建插值状态"""
        # 简单的线性插值
        interpolated_transform = {}
        
        for prop in ['translateX', 'translateY', 'rotateZ', 'scaleX', 'scaleY']:
            val1 = float(state1.transform.get(prop, 0))
            val2 = float(state2.transform.get(prop, 0))
            interpolated_transform[prop] = (val1 + val2) / 2
        
        return ElementState(
            element_id=state1.element_id,
            timestamp=time.time(),
            segment_id=f"{state1.segment_id}_to_{state2.segment_id}",
            transform=interpolated_transform,
            visual=state1.visual.copy(),
            layout=state1.layout.copy(),
            animation=state1.animation.copy(),
            custom_properties=state1.custom_properties.copy(),
            source="auto_fixed",
            confidence=0.8
        )
    
    def create_smooth_transition(self, state1: ElementState, state2: ElementState) -> ElementState:
        """创建平滑过渡状态"""
        # 使用state1的结束状态作为基础
        return ElementState(
            element_id=state1.element_id,
            timestamp=time.time(),
            segment_id=f"{state1.segment_id}_smooth",
            transform=state1.transform.copy(),
            visual=state1.visual.copy(),
            layout=state1.layout.copy(),
            animation=state1.animation.copy(),
            custom_properties=state1.custom_properties.copy(),
            source="smooth_transition",
            confidence=0.9
        )
    
    def export_states(self, file_path: str):
        """导出状态数据"""
        try:
            export_data = {
                'element_states': {},
                'transitions': [],
                'tolerance_settings': self.tolerance_settings,
                'export_time': time.time()
            }
            
            # 导出元素状态
            for element_id, states in self.element_states.items():
                export_data['element_states'][element_id] = [
                    asdict(state) for state in states
                ]
            
            # 导出转换
            for transition in self.transitions:
                export_data['transitions'].append({
                    'from_segment': transition.from_segment,
                    'to_segment': transition.to_segment,
                    'element_id': transition.element_id,
                    'start_state': asdict(transition.start_state),
                    'end_state': asdict(transition.end_state),
                    'transition_type': transition.transition_type,
                    'validation_result': transition.validation_result
                })
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"状态数据已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"导出状态数据失败: {e}")
            raise
    
    def import_states(self, file_path: str):
        """导入状态数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 导入元素状态
            self.element_states.clear()
            for element_id, states_data in import_data.get('element_states', {}).items():
                self.element_states[element_id] = [
                    ElementState(**state_data) for state_data in states_data
                ]
            
            # 导入容差设置
            if 'tolerance_settings' in import_data:
                self.tolerance_settings.update(import_data['tolerance_settings'])
            
            logger.info(f"状态数据已从 {file_path} 导入")
            
        except Exception as e:
            logger.error(f"导入状态数据失败: {e}")
            raise
    
    def clear_states(self):
        """清空所有状态"""
        self.element_states.clear()
        self.transitions.clear()
        logger.info("所有状态数据已清空")

    # ========== 核心状态管理方法 ==========

    def update_state(self, element_id: str, segment_id: str, state_data: Dict[str, Any]) -> bool:
        """更新元素状态"""
        try:
            state = self.get_element_state(element_id, segment_id)
            if state:
                # 更新现有状态
                if 'transform' in state_data:
                    state.transform.update(state_data['transform'])
                if 'visual' in state_data:
                    state.visual.update(state_data['visual'])
                if 'layout' in state_data:
                    state.layout.update(state_data['layout'])
                if 'animation' in state_data:
                    state.animation.update(state_data['animation'])
                if 'custom_properties' in state_data:
                    state.custom_properties.update(state_data['custom_properties'])

                state.timestamp = time.time()

                # 发射更新信号
                self.state_changed.emit(element_id, asdict(state))
                self.notify_subscribers('state_changed', element_id, asdict(state))

                logger.info(f"状态已更新: {element_id} @ {segment_id}")
                return True
            else:
                # 创建新状态
                self.record_element_state(element_id, segment_id, state_data)
                return True

        except Exception as e:
            logger.error(f"更新状态失败: {e}")
            return False

    def subscribe(self, event_type: str, callback: Callable) -> bool:
        """订阅状态变化事件"""
        try:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                logger.info(f"已订阅事件: {event_type}")
                return True
            return False

        except Exception as e:
            logger.error(f"订阅事件失败: {e}")
            return False

    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """取消订阅状态变化事件"""
        try:
            if event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.info(f"已取消订阅事件: {event_type}")
                return True
            return False

        except Exception as e:
            logger.error(f"取消订阅事件失败: {e}")
            return False

    def notify_subscribers(self, event_type: str, *args, **kwargs):
        """通知订阅者"""
        try:
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        callback(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"通知订阅者失败: {e}")

        except Exception as e:
            logger.error(f"通知订阅者失败: {e}")

    def get_current_state(self, element_id: str) -> Optional[Dict[str, Any]]:
        """获取元素当前状态"""
        try:
            latest_state = self.get_latest_state(element_id)
            if latest_state:
                return asdict(latest_state)
            return None

        except Exception as e:
            logger.error(f"获取当前状态失败: {e}")
            return None

    def set_state(self, element_id: str, segment_id: str, state_data: Dict[str, Any]) -> bool:
        """设置元素状态"""
        try:
            return self.update_state(element_id, segment_id, state_data)

        except Exception as e:
            logger.error(f"设置状态失败: {e}")
            return False
