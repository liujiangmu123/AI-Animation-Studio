"""
AI Animation Studio - 具体命令实现
实现各种具体的撤销重做命令
"""

from typing import Any, Dict, Optional
from core.command_manager import Command
from core.logger import get_logger

logger = get_logger("commands")


class AddElementCommand(Command):
    """添加元素命令"""
    
    def __init__(self, project_manager, element):
        super().__init__(f"添加元素: {element.name}")
        self.project_manager = project_manager
        self.element = element
        self.element_id = element.element_id
    
    def execute(self) -> bool:
        try:
            self.project_manager.add_element(self.element)
            self.executed = True
            return True
        except Exception as e:
            logger.error(f"添加元素失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            self.project_manager.remove_element(self.element_id)
            self.executed = False
            return True
        except Exception as e:
            logger.error(f"撤销添加元素失败: {e}")
            return False


class RemoveElementCommand(Command):
    """删除元素命令"""
    
    def __init__(self, project_manager, element_id: str):
        self.project_manager = project_manager
        self.element_id = element_id
        self.element = None  # 将在执行时保存
        super().__init__(f"删除元素: {element_id}")
    
    def execute(self) -> bool:
        try:
            # 保存元素以便撤销
            self.element = self.project_manager.get_element(self.element_id)
            if self.element:
                self.description = f"删除元素: {self.element.name}"
                self.project_manager.remove_element(self.element_id)
                self.executed = True
                return True
            return False
        except Exception as e:
            logger.error(f"删除元素失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            if self.element:
                self.project_manager.add_element(self.element)
                self.executed = False
                return True
            return False
        except Exception as e:
            logger.error(f"撤销删除元素失败: {e}")
            return False


class ModifyElementCommand(Command):
    """修改元素属性命令"""
    
    def __init__(self, project_manager, element_id: str, property_name: str, 
                 old_value: Any, new_value: Any):
        super().__init__(f"修改 {property_name}: {old_value} → {new_value}")
        self.project_manager = project_manager
        self.element_id = element_id
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
    
    def execute(self) -> bool:
        try:
            element = self.project_manager.get_element(self.element_id)
            if element:
                setattr(element, self.property_name, self.new_value)
                self.project_manager.update_element(element)
                self.executed = True
                return True
            return False
        except Exception as e:
            logger.error(f"修改元素属性失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            element = self.project_manager.get_element(self.element_id)
            if element:
                setattr(element, self.property_name, self.old_value)
                self.project_manager.update_element(element)
                self.executed = False
                return True
            return False
        except Exception as e:
            logger.error(f"撤销修改元素属性失败: {e}")
            return False
    
    def can_merge_with(self, other: Command) -> bool:
        """检查是否可以与另一个修改命令合并"""
        if not isinstance(other, ModifyElementCommand):
            return False
        
        return (self.element_id == other.element_id and 
                self.property_name == other.property_name)
    
    def merge_with(self, other: Command) -> Command:
        """与另一个修改命令合并"""
        if isinstance(other, ModifyElementCommand):
            # 创建新的合并命令，保持原始值，使用新的目标值
            return ModifyElementCommand(
                self.project_manager,
                self.element_id,
                self.property_name,
                self.old_value,  # 保持最初的值
                other.new_value  # 使用最新的值
            )
        return self


class MoveElementCommand(Command):
    """移动元素命令"""
    
    def __init__(self, project_manager, element_id: str, old_position: Dict, new_position: Dict):
        super().__init__(f"移动元素: ({old_position['x']},{old_position['y']}) → ({new_position['x']},{new_position['y']})")
        self.project_manager = project_manager
        self.element_id = element_id
        self.old_position = old_position
        self.new_position = new_position
    
    def execute(self) -> bool:
        try:
            element = self.project_manager.get_element(self.element_id)
            if element:
                element.position = self.new_position.copy()
                self.project_manager.update_element(element)
                self.executed = True
                return True
            return False
        except Exception as e:
            logger.error(f"移动元素失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            element = self.project_manager.get_element(self.element_id)
            if element:
                element.position = self.old_position.copy()
                self.project_manager.update_element(element)
                self.executed = False
                return True
            return False
        except Exception as e:
            logger.error(f"撤销移动元素失败: {e}")
            return False
    
    def can_merge_with(self, other: Command) -> bool:
        """检查是否可以与另一个移动命令合并"""
        if not isinstance(other, MoveElementCommand):
            return False
        return self.element_id == other.element_id
    
    def merge_with(self, other: Command) -> Command:
        """与另一个移动命令合并"""
        if isinstance(other, MoveElementCommand):
            return MoveElementCommand(
                self.project_manager,
                self.element_id,
                self.old_position,  # 保持最初的位置
                other.new_position  # 使用最新的位置
            )
        return self


class AddTimeSegmentCommand(Command):
    """添加时间段命令"""
    
    def __init__(self, project_manager, time_segment):
        super().__init__(f"添加时间段: {time_segment.start_time}s-{time_segment.end_time}s")
        self.project_manager = project_manager
        self.time_segment = time_segment
        self.segment_id = time_segment.segment_id
    
    def execute(self) -> bool:
        try:
            self.project_manager.add_time_segment(self.time_segment)
            self.executed = True
            return True
        except Exception as e:
            logger.error(f"添加时间段失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            self.project_manager.remove_time_segment(self.segment_id)
            self.executed = False
            return True
        except Exception as e:
            logger.error(f"撤销添加时间段失败: {e}")
            return False


class ApplyAnimationSolutionCommand(Command):
    """应用动画方案命令"""
    
    def __init__(self, project_manager, solution, segment_id: str):
        super().__init__(f"应用动画方案: {solution.name}")
        self.project_manager = project_manager
        self.solution = solution
        self.segment_id = segment_id
        self.old_solution = None
    
    def execute(self) -> bool:
        try:
            # 保存旧方案以便撤销
            segment = self.project_manager.get_time_segment(self.segment_id)
            if segment:
                self.old_solution = segment.animation_solution
                segment.animation_solution = self.solution
                self.project_manager.update_time_segment(segment)
                self.executed = True
                return True
            return False
        except Exception as e:
            logger.error(f"应用动画方案失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            segment = self.project_manager.get_time_segment(self.segment_id)
            if segment:
                segment.animation_solution = self.old_solution
                self.project_manager.update_time_segment(segment)
                self.executed = False
                return True
            return False
        except Exception as e:
            logger.error(f"撤销应用动画方案失败: {e}")
            return False


class ChangeLayerOrderCommand(Command):
    """改变图层顺序命令"""
    
    def __init__(self, project_manager, element_id: str, old_z_index: int, new_z_index: int):
        super().__init__(f"改变图层顺序: {old_z_index} → {new_z_index}")
        self.project_manager = project_manager
        self.element_id = element_id
        self.old_z_index = old_z_index
        self.new_z_index = new_z_index
    
    def execute(self) -> bool:
        try:
            element = self.project_manager.get_element(self.element_id)
            if element:
                element.z_index = self.new_z_index
                self.project_manager.update_element(element)
                self.executed = True
                return True
            return False
        except Exception as e:
            logger.error(f"改变图层顺序失败: {e}")
            return False
    
    def undo(self) -> bool:
        try:
            element = self.project_manager.get_element(self.element_id)
            if element:
                element.z_index = self.old_z_index
                self.project_manager.update_element(element)
                self.executed = False
                return True
            return False
        except Exception as e:
            logger.error(f"撤销改变图层顺序失败: {e}")
            return False
