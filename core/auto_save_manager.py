"""
AI Animation Studio - 自动保存管理器
提供自动保存、版本历史、崩溃恢复等功能
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from core.logger import get_logger

logger = get_logger("auto_save_manager")


class AutoSaveManager(QObject):
    """自动保存管理器"""
    
    # 信号定义
    auto_save_triggered = pyqtSignal()
    auto_save_completed = pyqtSignal(bool, str)  # 成功状态, 消息
    recovery_data_found = pyqtSignal(str)  # 恢复数据路径
    
    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        
        # 自动保存设置
        self.enabled = True
        self.interval_minutes = 5
        self.operation_threshold = 10
        self.trigger_mode = "time"  # "time", "operations", "changes", "mixed"
        
        # 状态跟踪
        self.operation_count = 0
        self.last_auto_save = None
        self.last_manual_save = None
        self.has_unsaved_changes = False
        
        # 定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.perform_auto_save)
        
        # 目录设置
        self.auto_save_dir = Path("auto_saves")
        self.recovery_dir = Path("recovery")
        self.version_dir = Path("versions")
        
        self._ensure_directories()
        
        logger.info("自动保存管理器初始化完成")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.auto_save_dir, self.recovery_dir, self.version_dir]:
            directory.mkdir(exist_ok=True)
    
    def start_auto_save(self):
        """启动自动保存"""
        if not self.enabled:
            return
        
        if self.trigger_mode in ["time", "mixed"]:
            interval_ms = self.interval_minutes * 60 * 1000
            self.auto_save_timer.start(interval_ms)
            logger.info(f"自动保存已启动，间隔: {self.interval_minutes} 分钟")
    
    def stop_auto_save(self):
        """停止自动保存"""
        self.auto_save_timer.stop()
        logger.info("自动保存已停止")
    
    def configure(self, **kwargs):
        """配置自动保存参数"""
        if 'enabled' in kwargs:
            self.enabled = kwargs['enabled']
        if 'interval_minutes' in kwargs:
            self.interval_minutes = kwargs['interval_minutes']
        if 'operation_threshold' in kwargs:
            self.operation_threshold = kwargs['operation_threshold']
        if 'trigger_mode' in kwargs:
            self.trigger_mode = kwargs['trigger_mode']
        
        # 重新启动定时器
        if self.enabled:
            self.stop_auto_save()
            self.start_auto_save()
        
        logger.info(f"自动保存配置已更新: {kwargs}")
    
    def record_operation(self):
        """记录操作（用于操作计数触发）"""
        self.operation_count += 1
        self.has_unsaved_changes = True
        
        # 检查是否需要触发自动保存
        if self.trigger_mode in ["operations", "mixed"]:
            if self.operation_count >= self.operation_threshold:
                self.perform_auto_save()
    
    def record_manual_save(self):
        """记录手动保存"""
        self.last_manual_save = datetime.now()
        self.operation_count = 0
        self.has_unsaved_changes = False
        logger.debug("记录手动保存")
    
    def perform_auto_save(self):
        """执行自动保存"""
        try:
            if not self.project_manager or not self.project_manager.current_project:
                return
            
            if not self.has_unsaved_changes:
                logger.debug("没有未保存的更改，跳过自动保存")
                return
            
            # 发出自动保存信号
            self.auto_save_triggered.emit()
            
            # 生成自动保存文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = self.project_manager.current_project.name
            auto_save_file = self.auto_save_dir / f"{project_name}_auto_{timestamp}.aas"
            
            # 执行保存
            success = self.project_manager.save_project(
                file_path=auto_save_file,
                create_backup=False,
                incremental=True
            )
            
            if success:
                self.last_auto_save = datetime.now()
                self.operation_count = 0
                self.has_unsaved_changes = False
                
                # 清理旧的自动保存文件
                self._cleanup_auto_saves()
                
                message = f"自动保存完成: {auto_save_file.name}"
                logger.info(message)
                self.auto_save_completed.emit(True, message)
            else:
                message = "自动保存失败"
                logger.error(message)
                self.auto_save_completed.emit(False, message)
                
        except Exception as e:
            message = f"自动保存异常: {e}"
            logger.error(message)
            self.auto_save_completed.emit(False, message)
    
    def _cleanup_auto_saves(self, max_files: int = 10):
        """清理旧的自动保存文件"""
        try:
            auto_save_files = list(self.auto_save_dir.glob("*_auto_*.aas"))
            auto_save_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # 删除超出数量限制的文件
            for file_to_delete in auto_save_files[max_files:]:
                file_to_delete.unlink()
                logger.debug(f"删除旧的自动保存文件: {file_to_delete.name}")
                
        except Exception as e:
            logger.error(f"清理自动保存文件失败: {e}")
    
    def create_recovery_point(self):
        """创建恢复点"""
        try:
            if not self.project_manager or not self.project_manager.current_project:
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = self.project_manager.current_project.name
            recovery_file = self.recovery_dir / f"{project_name}_recovery_{timestamp}.aas"
            
            success = self.project_manager.save_project(
                file_path=recovery_file,
                create_backup=False,
                incremental=False
            )
            
            if success:
                # 保存恢复点元数据
                metadata = {
                    "timestamp": timestamp,
                    "project_name": project_name,
                    "file_path": str(recovery_file),
                    "created_at": datetime.now().isoformat()
                }
                
                metadata_file = recovery_file.with_suffix('.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                logger.info(f"恢复点创建成功: {recovery_file.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"创建恢复点失败: {e}")
            return False
    
    def check_for_recovery_data(self) -> Optional[str]:
        """检查是否有恢复数据"""
        try:
            recovery_files = list(self.recovery_dir.glob("*_recovery_*.aas"))
            if not recovery_files:
                return None
            
            # 找到最新的恢复文件
            latest_recovery = max(recovery_files, key=lambda f: f.stat().st_mtime)
            
            # 检查恢复文件是否比较新（比如1小时内）
            file_time = datetime.fromtimestamp(latest_recovery.stat().st_mtime)
            if datetime.now() - file_time < timedelta(hours=1):
                logger.info(f"发现恢复数据: {latest_recovery.name}")
                self.recovery_data_found.emit(str(latest_recovery))
                return str(latest_recovery)
            
            return None
            
        except Exception as e:
            logger.error(f"检查恢复数据失败: {e}")
            return None
    
    def restore_from_recovery(self, recovery_file: str) -> bool:
        """从恢复文件恢复"""
        try:
            recovery_path = Path(recovery_file)
            if not recovery_path.exists():
                logger.error(f"恢复文件不存在: {recovery_file}")
                return False
            
            # 加载恢复文件
            success = self.project_manager.load_project(recovery_path)
            
            if success:
                logger.info(f"从恢复文件恢复成功: {recovery_file}")
                return True
            else:
                logger.error(f"从恢复文件恢复失败: {recovery_file}")
                return False
                
        except Exception as e:
            logger.error(f"恢复过程异常: {e}")
            return False
    
    def create_version_backup(self, description: str = "") -> bool:
        """创建版本备份"""
        try:
            if not self.project_manager or not self.project_manager.current_project:
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = self.project_manager.current_project.name
            version_file = self.version_dir / f"{project_name}_v{timestamp}.aas"
            
            success = self.project_manager.save_project(
                file_path=version_file,
                create_backup=False,
                incremental=False
            )
            
            if success:
                # 保存版本元数据
                metadata = {
                    "timestamp": timestamp,
                    "project_name": project_name,
                    "description": description,
                    "file_path": str(version_file),
                    "created_at": datetime.now().isoformat(),
                    "version": self._get_next_version_number()
                }
                
                metadata_file = version_file.with_suffix('.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                logger.info(f"版本备份创建成功: {version_file.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"创建版本备份失败: {e}")
            return False
    
    def _get_next_version_number(self) -> int:
        """获取下一个版本号"""
        try:
            version_files = list(self.version_dir.glob("*.json"))
            if not version_files:
                return 1
            
            max_version = 0
            for version_file in version_files:
                try:
                    with open(version_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        version = metadata.get('version', 0)
                        max_version = max(max_version, version)
                except:
                    continue
            
            return max_version + 1
            
        except Exception as e:
            logger.error(f"获取版本号失败: {e}")
            return 1
    
    def get_version_history(self) -> List[Dict]:
        """获取版本历史"""
        try:
            version_files = list(self.version_dir.glob("*.json"))
            versions = []
            
            for version_file in version_files:
                try:
                    with open(version_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        versions.append(metadata)
                except:
                    continue
            
            # 按版本号排序
            versions.sort(key=lambda v: v.get('version', 0), reverse=True)
            return versions
            
        except Exception as e:
            logger.error(f"获取版本历史失败: {e}")
            return []
    
    def get_status(self) -> Dict:
        """获取自动保存状态"""
        return {
            "enabled": self.enabled,
            "interval_minutes": self.interval_minutes,
            "operation_threshold": self.operation_threshold,
            "trigger_mode": self.trigger_mode,
            "operation_count": self.operation_count,
            "last_auto_save": self.last_auto_save.isoformat() if self.last_auto_save else None,
            "last_manual_save": self.last_manual_save.isoformat() if self.last_manual_save else None,
            "has_unsaved_changes": self.has_unsaved_changes,
            "timer_active": self.auto_save_timer.isActive()
        }
