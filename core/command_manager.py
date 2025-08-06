"""
AI Animation Studio - 命令管理器
实现撤销重做功能的命令模式
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from datetime import datetime
import uuid

from core.logger import get_logger

logger = get_logger("command_manager")


class Command(ABC):
    """命令基类"""
    
    def __init__(self, description: str = ""):
        self.id = str(uuid.uuid4())
        self.description = description
        self.timestamp = datetime.now()
        self.executed = False
    
    @abstractmethod
    def execute(self) -> bool:
        """执行命令"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """撤销命令"""
        pass
    
    def can_merge_with(self, other: 'Command') -> bool:
        """检查是否可以与另一个命令合并"""
        return False
    
    def merge_with(self, other: 'Command') -> 'Command':
        """与另一个命令合并"""
        return self
    
    def __str__(self):
        return f"{self.description} ({self.timestamp.strftime('%H:%M:%S')})"


class CommandGroup(Command):
    """命令组 - 用于批量操作"""
    
    def __init__(self, commands: List[Command], description: str = "批量操作"):
        super().__init__(description)
        self.commands = commands
    
    def execute(self) -> bool:
        """执行所有命令"""
        try:
            for command in self.commands:
                if not command.execute():
                    # 如果有命令失败，撤销已执行的命令
                    self._rollback()
                    return False
            self.executed = True
            return True
        except Exception as e:
            logger.error(f"命令组执行失败: {e}")
            self._rollback()
            return False
    
    def undo(self) -> bool:
        """撤销所有命令（逆序）"""
        try:
            for command in reversed(self.commands):
                if command.executed:
                    command.undo()
            self.executed = False
            return True
        except Exception as e:
            logger.error(f"命令组撤销失败: {e}")
            return False
    
    def _rollback(self):
        """回滚已执行的命令"""
        for command in reversed(self.commands):
            if command.executed:
                command.undo()


class CommandManager:
    """命令管理器 - 管理撤销重做历史"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.auto_merge = True
        self.merge_timeout = 2.0  # 2秒内的相似操作可以合并
        
        logger.info(f"命令管理器初始化，最大历史记录: {max_history}")
    
    def execute_command(self, command: Command) -> bool:
        """执行命令并添加到历史记录"""
        try:
            # 尝试与最近的命令合并
            if self.auto_merge and self.undo_stack:
                last_command = self.undo_stack[-1]
                time_diff = (command.timestamp - last_command.timestamp).total_seconds()
                
                if time_diff <= self.merge_timeout and last_command.can_merge_with(command):
                    logger.info(f"合并命令: {last_command.description} + {command.description}")
                    merged_command = last_command.merge_with(command)
                    self.undo_stack[-1] = merged_command
                    return merged_command.execute()
            
            # 执行命令
            if command.execute():
                # 清空重做栈
                self.redo_stack.clear()
                
                # 添加到撤销栈
                self.undo_stack.append(command)
                
                # 限制历史记录大小
                if len(self.undo_stack) > self.max_history:
                    removed = self.undo_stack.pop(0)
                    logger.debug(f"移除旧命令: {removed.description}")
                
                logger.info(f"命令执行成功: {command.description}")
                return True
            else:
                logger.warning(f"命令执行失败: {command.description}")
                return False
                
        except Exception as e:
            logger.error(f"执行命令时发生错误: {e}")
            return False
    
    def undo(self) -> bool:
        """撤销最后一个命令"""
        if not self.undo_stack:
            logger.info("没有可撤销的命令")
            return False
        
        try:
            command = self.undo_stack.pop()
            if command.undo():
                self.redo_stack.append(command)
                logger.info(f"撤销成功: {command.description}")
                return True
            else:
                # 撤销失败，重新放回栈中
                self.undo_stack.append(command)
                logger.warning(f"撤销失败: {command.description}")
                return False
                
        except Exception as e:
            logger.error(f"撤销命令时发生错误: {e}")
            return False
    
    def redo(self) -> bool:
        """重做最后一个撤销的命令"""
        if not self.redo_stack:
            logger.info("没有可重做的命令")
            return False
        
        try:
            command = self.redo_stack.pop()
            if command.execute():
                self.undo_stack.append(command)
                logger.info(f"重做成功: {command.description}")
                return True
            else:
                # 重做失败，重新放回栈中
                self.redo_stack.append(command)
                logger.warning(f"重做失败: {command.description}")
                return False
                
        except Exception as e:
            logger.error(f"重做命令时发生错误: {e}")
            return False
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return len(self.redo_stack) > 0
    
    def get_undo_description(self) -> Optional[str]:
        """获取下一个撤销操作的描述"""
        if self.undo_stack:
            return self.undo_stack[-1].description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """获取下一个重做操作的描述"""
        if self.redo_stack:
            return self.redo_stack[-1].description
        return None
    
    def get_history(self) -> List[str]:
        """获取历史记录"""
        history = []
        for command in self.undo_stack:
            history.append(f"✅ {command}")
        for command in reversed(self.redo_stack):
            history.append(f"⏳ {command}")
        return history
    
    def clear_history(self):
        """清空历史记录"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        logger.info("历史记录已清空")
    
    def has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        # 如果有撤销栈中的命令，说明有未保存的更改
        return len(self.undo_stack) > 0

    def mark_saved(self):
        """标记为已保存状态"""
        # 可以在这里实现保存状态标记逻辑
        # 目前简单实现，实际可以更复杂
        logger.info("项目已标记为保存状态")

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "undo_count": len(self.undo_stack),
            "redo_count": len(self.redo_stack),
            "total_operations": len(self.undo_stack) + len(self.redo_stack),
            "max_history": self.max_history,
            "auto_merge": self.auto_merge
        }

    # ==================== 高级撤销重做功能 ====================

    def undo_multiple(self, count: int) -> int:
        """批量撤销多个命令"""
        undone_count = 0
        for _ in range(count):
            if self.undo():
                undone_count += 1
            else:
                break

        logger.info(f"批量撤销完成，成功撤销 {undone_count}/{count} 个命令")
        return undone_count

    def redo_multiple(self, count: int) -> int:
        """批量重做多个命令"""
        redone_count = 0
        for _ in range(count):
            if self.redo():
                redone_count += 1
            else:
                break

        logger.info(f"批量重做完成，成功重做 {redone_count}/{count} 个命令")
        return redone_count

    def undo_to_checkpoint(self, checkpoint_id: str) -> bool:
        """撤销到指定检查点"""
        try:
            # 查找检查点位置
            checkpoint_index = -1
            for i, command in enumerate(self.undo_stack):
                if hasattr(command, 'checkpoint_id') and command.checkpoint_id == checkpoint_id:
                    checkpoint_index = i
                    break

            if checkpoint_index == -1:
                logger.warning(f"未找到检查点: {checkpoint_id}")
                return False

            # 撤销到检查点
            undo_count = len(self.undo_stack) - checkpoint_index
            return self.undo_multiple(undo_count) == undo_count

        except Exception as e:
            logger.error(f"撤销到检查点失败: {e}")
            return False

    def create_checkpoint(self, name: str = "") -> str:
        """创建检查点"""
        try:
            import uuid
            checkpoint_id = str(uuid.uuid4())

            # 创建检查点命令
            checkpoint_command = CheckpointCommand(checkpoint_id, name)
            self.execute_command(checkpoint_command)

            logger.info(f"创建检查点: {name} ({checkpoint_id})")
            return checkpoint_id

        except Exception as e:
            logger.error(f"创建检查点失败: {e}")
            return ""

    def get_checkpoints(self) -> List[dict]:
        """获取所有检查点"""
        checkpoints = []
        for i, command in enumerate(self.undo_stack):
            if hasattr(command, 'checkpoint_id'):
                checkpoints.append({
                    "id": command.checkpoint_id,
                    "name": command.checkpoint_name,
                    "index": i,
                    "timestamp": command.timestamp,
                    "description": command.description
                })
        return checkpoints

    def selective_undo(self, command_id: str) -> bool:
        """选择性撤销指定命令"""
        try:
            # 查找命令
            command_index = -1
            for i, command in enumerate(self.undo_stack):
                if command.id == command_id:
                    command_index = i
                    break

            if command_index == -1:
                logger.warning(f"未找到命令: {command_id}")
                return False

            # 检查是否可以选择性撤销
            target_command = self.undo_stack[command_index]
            if not self._can_selective_undo(target_command, command_index):
                logger.warning(f"命令不能选择性撤销: {target_command.description}")
                return False

            # 执行选择性撤销
            if target_command.undo():
                # 从栈中移除命令
                self.undo_stack.pop(command_index)
                logger.info(f"选择性撤销成功: {target_command.description}")
                return True
            else:
                logger.error(f"选择性撤销失败: {target_command.description}")
                return False

        except Exception as e:
            logger.error(f"选择性撤销异常: {e}")
            return False

    def _can_selective_undo(self, command, command_index: int) -> bool:
        """检查命令是否可以选择性撤销"""
        # 检查是否有依赖关系
        for i in range(command_index + 1, len(self.undo_stack)):
            later_command = self.undo_stack[i]
            if self._has_dependency(command, later_command):
                return False

        return True

    def _has_dependency(self, command1, command2) -> bool:
        """检查两个命令之间是否有依赖关系"""
        # 简单的依赖检查逻辑
        # 实际实现中可以更复杂
        if hasattr(command1, 'element_id') and hasattr(command2, 'element_id'):
            return command1.element_id == command2.element_id

        return False

    def get_command_by_id(self, command_id: str) -> Optional['Command']:
        """根据ID获取命令"""
        for command in self.undo_stack + self.redo_stack:
            if command.id == command_id:
                return command
        return None

    def get_command_dependencies(self, command_id: str) -> List[str]:
        """获取命令的依赖关系"""
        dependencies = []
        target_command = self.get_command_by_id(command_id)

        if not target_command:
            return dependencies

        # 查找依赖的命令
        for command in self.undo_stack:
            if command.id != command_id and self._has_dependency(target_command, command):
                dependencies.append(command.id)

        return dependencies


class CheckpointCommand(Command):
    """检查点命令"""

    def __init__(self, checkpoint_id: str, name: str = ""):
        super().__init__(f"检查点: {name or checkpoint_id[:8]}")
        self.checkpoint_id = checkpoint_id
        self.checkpoint_name = name

    def execute(self) -> bool:
        """检查点不需要执行任何操作"""
        self.executed = True
        return True

    def undo(self) -> bool:
        """检查点不需要撤销任何操作"""
        self.executed = False
        return True
