"""
AI Animation Studio - 技术架构评估系统
评估代码结构、扩展性、稳定性、性能优化等方面
"""

import os
import json
import time
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import subprocess

from core.logger import get_logger

logger = get_logger("technical_architecture_assessment")


class ArchitectureQuality(Enum):
    """架构质量级别枚举"""
    POOR = "poor"                          # 差
    BASIC = "basic"                        # 基础
    GOOD = "good"                          # 良好
    EXCELLENT = "excellent"                # 优秀
    ENTERPRISE = "enterprise"              # 企业级


class PerformanceLevel(Enum):
    """性能级别枚举"""
    CRITICAL = "critical"                  # 严重问题
    POOR = "poor"                          # 性能差
    ACCEPTABLE = "acceptable"              # 可接受
    GOOD = "good"                          # 良好
    EXCELLENT = "excellent"                # 优秀


@dataclass
class CodeStructureMetrics:
    """代码结构指标"""
    total_files: int = 0
    total_lines: int = 0
    total_classes: int = 0
    total_functions: int = 0
    average_file_size: float = 0.0
    average_function_complexity: float = 0.0
    code_duplication_rate: float = 0.0
    documentation_coverage: float = 0.0
    type_annotation_coverage: float = 0.0
    test_coverage: float = 0.0


@dataclass
class ExtensibilityMetrics:
    """扩展性指标"""
    interface_abstraction_score: float = 0.0
    plugin_architecture_score: float = 0.0
    configuration_flexibility_score: float = 0.0
    api_design_score: float = 0.0
    dependency_injection_score: float = 0.0
    modular_design_score: float = 0.0


@dataclass
class StabilityMetrics:
    """稳定性指标"""
    error_handling_coverage: float = 0.0
    exception_safety_score: float = 0.0
    resource_management_score: float = 0.0
    thread_safety_score: float = 0.0
    memory_safety_score: float = 0.0
    graceful_degradation_score: float = 0.0


@dataclass
class PerformanceMetrics:
    """性能指标"""
    startup_time_score: float = 0.0
    memory_efficiency_score: float = 0.0
    cpu_efficiency_score: float = 0.0
    io_efficiency_score: float = 0.0
    algorithm_complexity_score: float = 0.0
    caching_strategy_score: float = 0.0
    async_programming_score: float = 0.0


@dataclass
class TechnicalArchitectureReport:
    """技术架构评估报告"""
    analysis_date: datetime = field(default_factory=datetime.now)
    
    # 四大评估维度
    code_structure_quality: ArchitectureQuality = ArchitectureQuality.BASIC
    extensibility_quality: ArchitectureQuality = ArchitectureQuality.BASIC
    stability_quality: ArchitectureQuality = ArchitectureQuality.BASIC
    performance_quality: PerformanceLevel = PerformanceLevel.ACCEPTABLE
    
    # 详细指标
    code_structure_metrics: CodeStructureMetrics = field(default_factory=CodeStructureMetrics)
    extensibility_metrics: ExtensibilityMetrics = field(default_factory=ExtensibilityMetrics)
    stability_metrics: StabilityMetrics = field(default_factory=StabilityMetrics)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    
    # 综合评分
    overall_architecture_score: float = 0.0
    overall_architecture_quality: ArchitectureQuality = ArchitectureQuality.BASIC
    
    # 关键发现
    architecture_strengths: List[str] = field(default_factory=list)
    architecture_weaknesses: List[str] = field(default_factory=list)
    performance_bottlenecks: List[str] = field(default_factory=list)
    scalability_concerns: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    
    # 改进建议
    immediate_actions: List[str] = field(default_factory=list)
    short_term_improvements: List[str] = field(default_factory=list)
    long_term_optimizations: List[str] = field(default_factory=list)


class TechnicalArchitectureAssessor:
    """技术架构评估器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.python_files = []
        self.analysis_cache = {}
        
        # 扫描Python文件
        self.scan_python_files()
        
        logger.info("技术架构评估器初始化完成")
    
    def scan_python_files(self):
        """扫描Python文件"""
        try:
            self.python_files = list(self.project_root.rglob("*.py"))
            logger.info(f"发现 {len(self.python_files)} 个Python文件")
            
        except Exception as e:
            logger.error(f"扫描Python文件失败: {e}")
    
    def assess_technical_architecture(self) -> TechnicalArchitectureReport:
        """评估技术架构"""
        try:
            logger.info("开始技术架构评估")
            
            report = TechnicalArchitectureReport()
            
            # 评估代码结构
            self.assess_code_structure(report)
            
            # 评估扩展性
            self.assess_extensibility(report)
            
            # 评估稳定性
            self.assess_stability(report)
            
            # 评估性能
            self.assess_performance(report)
            
            # 计算综合评分
            self.calculate_overall_score(report)
            
            # 生成关键发现和建议
            self.generate_findings_and_recommendations(report)
            
            logger.info("技术架构评估完成")
            return report
            
        except Exception as e:
            logger.error(f"技术架构评估失败: {e}")
            return TechnicalArchitectureReport()
    
    def assess_code_structure(self, report: TechnicalArchitectureReport):
        """评估代码结构"""
        try:
            metrics = report.code_structure_metrics
            
            # 基础统计
            metrics.total_files = len(self.python_files)
            
            total_lines = 0
            total_classes = 0
            total_functions = 0
            documented_items = 0
            type_annotated_items = 0
            
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = len(content.split('\n'))
                    total_lines += lines
                    
                    # 解析AST
                    try:
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                total_classes += 1
                                if ast.get_docstring(node):
                                    documented_items += 1
                            elif isinstance(node, ast.FunctionDef):
                                total_functions += 1
                                if ast.get_docstring(node):
                                    documented_items += 1
                                # 检查类型注解
                                if node.returns or any(arg.annotation for arg in node.args.args):
                                    type_annotated_items += 1
                    
                    except SyntaxError:
                        logger.warning(f"语法错误，跳过文件: {file_path}")
                        continue
                
                except Exception as e:
                    logger.warning(f"读取文件失败 {file_path}: {e}")
                    continue
            
            metrics.total_lines = total_lines
            metrics.total_classes = total_classes
            metrics.total_functions = total_functions
            metrics.average_file_size = total_lines / max(metrics.total_files, 1)
            
            # 文档覆盖率
            total_items = total_classes + total_functions
            metrics.documentation_coverage = documented_items / max(total_items, 1)
            
            # 类型注解覆盖率
            metrics.type_annotation_coverage = type_annotated_items / max(total_functions, 1)
            
            # 代码重复率（简化计算）
            metrics.code_duplication_rate = self.estimate_code_duplication()
            
            # 确定代码结构质量
            structure_score = (
                min(1.0, metrics.documentation_coverage * 2) * 0.3 +
                min(1.0, metrics.type_annotation_coverage * 2) * 0.3 +
                (1.0 - min(1.0, metrics.code_duplication_rate * 2)) * 0.2 +
                min(1.0, 1.0 - metrics.average_file_size / 1000) * 0.2
            )
            
            if structure_score >= 0.9:
                report.code_structure_quality = ArchitectureQuality.ENTERPRISE
            elif structure_score >= 0.75:
                report.code_structure_quality = ArchitectureQuality.EXCELLENT
            elif structure_score >= 0.6:
                report.code_structure_quality = ArchitectureQuality.GOOD
            elif structure_score >= 0.4:
                report.code_structure_quality = ArchitectureQuality.BASIC
            else:
                report.code_structure_quality = ArchitectureQuality.POOR
            
        except Exception as e:
            logger.error(f"评估代码结构失败: {e}")
    
    def assess_extensibility(self, report: TechnicalArchitectureReport):
        """评估扩展性"""
        try:
            metrics = report.extensibility_metrics
            
            # 接口抽象评分
            metrics.interface_abstraction_score = self.evaluate_interface_abstraction()
            
            # 插件架构评分
            metrics.plugin_architecture_score = self.evaluate_plugin_architecture()
            
            # 配置灵活性评分
            metrics.configuration_flexibility_score = self.evaluate_configuration_flexibility()
            
            # API设计评分
            metrics.api_design_score = self.evaluate_api_design()
            
            # 依赖注入评分
            metrics.dependency_injection_score = self.evaluate_dependency_injection()
            
            # 模块化设计评分
            metrics.modular_design_score = self.evaluate_modular_design()
            
            # 计算综合扩展性评分
            extensibility_score = (
                metrics.interface_abstraction_score * 0.2 +
                metrics.plugin_architecture_score * 0.15 +
                metrics.configuration_flexibility_score * 0.15 +
                metrics.api_design_score * 0.2 +
                metrics.dependency_injection_score * 0.15 +
                metrics.modular_design_score * 0.15
            )
            
            if extensibility_score >= 0.9:
                report.extensibility_quality = ArchitectureQuality.ENTERPRISE
            elif extensibility_score >= 0.75:
                report.extensibility_quality = ArchitectureQuality.EXCELLENT
            elif extensibility_score >= 0.6:
                report.extensibility_quality = ArchitectureQuality.GOOD
            elif extensibility_score >= 0.4:
                report.extensibility_quality = ArchitectureQuality.BASIC
            else:
                report.extensibility_quality = ArchitectureQuality.POOR
            
        except Exception as e:
            logger.error(f"评估扩展性失败: {e}")
    
    def assess_stability(self, report: TechnicalArchitectureReport):
        """评估稳定性"""
        try:
            metrics = report.stability_metrics
            
            # 错误处理覆盖率
            metrics.error_handling_coverage = self.evaluate_error_handling_coverage()
            
            # 异常安全性评分
            metrics.exception_safety_score = self.evaluate_exception_safety()
            
            # 资源管理评分
            metrics.resource_management_score = self.evaluate_resource_management()
            
            # 线程安全性评分
            metrics.thread_safety_score = self.evaluate_thread_safety()
            
            # 内存安全性评分
            metrics.memory_safety_score = self.evaluate_memory_safety()
            
            # 优雅降级评分
            metrics.graceful_degradation_score = self.evaluate_graceful_degradation()
            
            # 计算综合稳定性评分
            stability_score = (
                metrics.error_handling_coverage * 0.25 +
                metrics.exception_safety_score * 0.2 +
                metrics.resource_management_score * 0.15 +
                metrics.thread_safety_score * 0.15 +
                metrics.memory_safety_score * 0.15 +
                metrics.graceful_degradation_score * 0.1
            )
            
            if stability_score >= 0.9:
                report.stability_quality = ArchitectureQuality.ENTERPRISE
            elif stability_score >= 0.75:
                report.stability_quality = ArchitectureQuality.EXCELLENT
            elif stability_score >= 0.6:
                report.stability_quality = ArchitectureQuality.GOOD
            elif stability_score >= 0.4:
                report.stability_quality = ArchitectureQuality.BASIC
            else:
                report.stability_quality = ArchitectureQuality.POOR
            
        except Exception as e:
            logger.error(f"评估稳定性失败: {e}")
    
    def assess_performance(self, report: TechnicalArchitectureReport):
        """评估性能"""
        try:
            metrics = report.performance_metrics
            
            # 启动时间评分
            metrics.startup_time_score = self.evaluate_startup_time()
            
            # 内存效率评分
            metrics.memory_efficiency_score = self.evaluate_memory_efficiency()
            
            # CPU效率评分
            metrics.cpu_efficiency_score = self.evaluate_cpu_efficiency()
            
            # I/O效率评分
            metrics.io_efficiency_score = self.evaluate_io_efficiency()
            
            # 算法复杂度评分
            metrics.algorithm_complexity_score = self.evaluate_algorithm_complexity()
            
            # 缓存策略评分
            metrics.caching_strategy_score = self.evaluate_caching_strategy()
            
            # 异步编程评分
            metrics.async_programming_score = self.evaluate_async_programming()
            
            # 计算综合性能评分
            performance_score = (
                metrics.startup_time_score * 0.15 +
                metrics.memory_efficiency_score * 0.2 +
                metrics.cpu_efficiency_score * 0.2 +
                metrics.io_efficiency_score * 0.15 +
                metrics.algorithm_complexity_score * 0.15 +
                metrics.caching_strategy_score * 0.1 +
                metrics.async_programming_score * 0.05
            )
            
            if performance_score >= 0.9:
                report.performance_quality = PerformanceLevel.EXCELLENT
            elif performance_score >= 0.75:
                report.performance_quality = PerformanceLevel.GOOD
            elif performance_score >= 0.6:
                report.performance_quality = PerformanceLevel.ACCEPTABLE
            elif performance_score >= 0.4:
                report.performance_quality = PerformanceLevel.POOR
            else:
                report.performance_quality = PerformanceLevel.CRITICAL
            
        except Exception as e:
            logger.error(f"评估性能失败: {e}")
    
    def estimate_code_duplication(self) -> float:
        """估算代码重复率"""
        try:
            # 简化的重复代码检测
            function_signatures = []
            
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取函数签名
                    function_matches = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
                    function_signatures.extend(function_matches)
                
                except Exception:
                    continue
            
            if not function_signatures:
                return 0.0
            
            # 计算重复函数名的比例
            unique_functions = set(function_signatures)
            duplication_rate = 1.0 - len(unique_functions) / len(function_signatures)
            
            return min(1.0, duplication_rate)

        except Exception as e:
            logger.error(f"估算代码重复率失败: {e}")
            return 0.0

    def evaluate_interface_abstraction(self) -> float:
        """评估接口抽象程度"""
        try:
            abstract_patterns = 0
            total_classes = 0

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查抽象基类
                    if 'ABC' in content or 'abstractmethod' in content:
                        abstract_patterns += 1

                    # 检查协议/接口
                    if 'Protocol' in content or 'interface' in content.lower():
                        abstract_patterns += 1

                    # 统计类数量
                    total_classes += content.count('class ')

                except Exception:
                    continue

            if total_classes == 0:
                return 0.5

            return min(1.0, abstract_patterns / total_classes * 2)

        except Exception as e:
            logger.error(f"评估接口抽象程度失败: {e}")
            return 0.0

    def evaluate_plugin_architecture(self) -> float:
        """评估插件架构"""
        try:
            plugin_indicators = 0

            # 检查插件相关文件和目录
            plugin_paths = [
                "plugins", "extensions", "addons", "modules"
            ]

            for path_name in plugin_paths:
                if (self.project_root / path_name).exists():
                    plugin_indicators += 1

            # 检查插件加载机制
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    plugin_keywords = [
                        'load_plugin', 'register_plugin', 'plugin_manager',
                        'extension_point', 'hook', 'entry_point'
                    ]

                    for keyword in plugin_keywords:
                        if keyword in content.lower():
                            plugin_indicators += 1
                            break

                except Exception:
                    continue

            return min(1.0, plugin_indicators / 5)

        except Exception as e:
            logger.error(f"评估插件架构失败: {e}")
            return 0.0

    def evaluate_configuration_flexibility(self) -> float:
        """评估配置灵活性"""
        try:
            config_score = 0

            # 检查配置文件
            config_files = [
                "config.py", "settings.py", "app_config.py",
                "config.json", "config.yaml", "config.toml"
            ]

            for config_file in config_files:
                if list(self.project_root.rglob(config_file)):
                    config_score += 0.2

            # 检查环境变量支持
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'os.environ' in content or 'getenv' in content:
                        config_score += 0.2
                        break

                except Exception:
                    continue

            # 检查配置类
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'Config' in content and 'class' in content:
                        config_score += 0.2
                        break

                except Exception:
                    continue

            return min(1.0, config_score)

        except Exception as e:
            logger.error(f"评估配置灵活性失败: {e}")
            return 0.0

    def evaluate_api_design(self) -> float:
        """评估API设计"""
        try:
            api_score = 0

            # 检查API相关模式
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查RESTful API
                    if any(method in content for method in ['@app.route', '@api.route', 'FastAPI', 'Flask']):
                        api_score += 0.3

                    # 检查API版本控制
                    if 'v1' in content or 'version' in content.lower():
                        api_score += 0.2

                    # 检查API文档
                    if 'swagger' in content.lower() or 'openapi' in content.lower():
                        api_score += 0.2

                    # 检查错误处理
                    if 'HTTPException' in content or 'APIError' in content:
                        api_score += 0.2

                    # 检查数据验证
                    if 'pydantic' in content or 'marshmallow' in content:
                        api_score += 0.1

                except Exception:
                    continue

            return min(1.0, api_score)

        except Exception as e:
            logger.error(f"评估API设计失败: {e}")
            return 0.0

    def evaluate_dependency_injection(self) -> float:
        """评估依赖注入"""
        try:
            di_score = 0

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查依赖注入模式
                    di_patterns = [
                        '__init__', 'inject', 'dependency', 'container',
                        'provider', 'factory', 'singleton'
                    ]

                    pattern_count = sum(1 for pattern in di_patterns if pattern in content.lower())
                    di_score += min(0.2, pattern_count * 0.05)

                except Exception:
                    continue

            return min(1.0, di_score)

        except Exception as e:
            logger.error(f"评估依赖注入失败: {e}")
            return 0.0

    def evaluate_modular_design(self) -> float:
        """评估模块化设计"""
        try:
            # 计算模块化指标
            total_files = len(self.python_files)
            if total_files == 0:
                return 0.0

            # 检查目录结构
            directories = set()
            for file_path in self.python_files:
                directories.add(file_path.parent)

            # 模块化评分基于目录层次和文件分布
            directory_depth = max(len(d.parts) - len(self.project_root.parts) for d in directories)
            files_per_directory = total_files / len(directories)

            # 理想的模块化：适中的目录深度，合理的文件分布
            depth_score = min(1.0, directory_depth / 5)  # 5层以内为好
            distribution_score = min(1.0, 1.0 / max(1, files_per_directory / 10))  # 每目录10个文件以内

            return (depth_score + distribution_score) / 2

        except Exception as e:
            logger.error(f"评估模块化设计失败: {e}")
            return 0.0

    def evaluate_error_handling_coverage(self) -> float:
        """评估错误处理覆盖率"""
        try:
            total_functions = 0
            functions_with_error_handling = 0

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 统计函数数量
                    function_count = content.count('def ')
                    total_functions += function_count

                    # 统计有错误处理的函数
                    try_count = content.count('try:')
                    except_count = content.count('except')

                    # 估算有错误处理的函数数量
                    functions_with_error_handling += min(function_count, try_count)

                except Exception:
                    continue

            if total_functions == 0:
                return 0.0

            return functions_with_error_handling / total_functions

        except Exception as e:
            logger.error(f"评估错误处理覆盖率失败: {e}")
            return 0.0

    def evaluate_exception_safety(self) -> float:
        """评估异常安全性"""
        try:
            safety_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0

                    # 检查finally块
                    if 'finally:' in content:
                        file_score += 0.3

                    # 检查上下文管理器
                    if 'with ' in content:
                        file_score += 0.3

                    # 检查异常链
                    if 'raise' in content and 'from' in content:
                        file_score += 0.2

                    # 检查日志记录
                    if 'logger' in content and 'except' in content:
                        file_score += 0.2

                    safety_score += min(1.0, file_score)

                except Exception:
                    continue

            return safety_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估异常安全性失败: {e}")
            return 0.0

    def evaluate_resource_management(self) -> float:
        """评估资源管理"""
        try:
            resource_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0

                    # 检查文件操作的正确关闭
                    if 'with open(' in content:
                        file_score += 0.4
                    elif 'close()' in content:
                        file_score += 0.2

                    # 检查数据库连接管理
                    if 'connection' in content.lower() and ('close' in content or 'with' in content):
                        file_score += 0.3

                    # 检查内存管理
                    if 'del ' in content or '__del__' in content:
                        file_score += 0.2

                    # 检查缓存清理
                    if 'cache' in content.lower() and 'clear' in content:
                        file_score += 0.1

                    resource_score += min(1.0, file_score)

                except Exception:
                    continue

            return resource_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估资源管理失败: {e}")
            return 0.0

    def evaluate_thread_safety(self) -> float:
        """评估线程安全性"""
        try:
            thread_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0

                    # 检查线程同步机制
                    if any(keyword in content for keyword in ['Lock()', 'RLock()', 'Semaphore()', 'threading']):
                        file_score += 0.4

                    # 检查队列使用
                    if 'Queue' in content or 'queue' in content:
                        file_score += 0.3

                    # 检查原子操作
                    if 'atomic' in content.lower():
                        file_score += 0.2

                    # 检查线程局部存储
                    if 'threading.local' in content:
                        file_score += 0.1

                    thread_score += min(1.0, file_score)

                except Exception:
                    continue

            return thread_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估线程安全性失败: {e}")
            return 0.0

    def evaluate_memory_safety(self) -> float:
        """评估内存安全性"""
        try:
            memory_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0.7  # Python默认内存安全

                    # 检查内存泄漏预防
                    if 'weakref' in content:
                        file_score += 0.1

                    # 检查循环引用处理
                    if 'gc.collect' in content:
                        file_score += 0.1

                    # 检查大对象处理
                    if any(keyword in content for keyword in ['__slots__', 'generator', 'yield']):
                        file_score += 0.1

                    memory_score += min(1.0, file_score)

                except Exception:
                    continue

            return memory_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估内存安全性失败: {e}")
            return 0.0

    def evaluate_graceful_degradation(self) -> float:
        """评估优雅降级"""
        try:
            degradation_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0

                    # 检查降级策略
                    if 'fallback' in content.lower():
                        file_score += 0.3

                    # 检查默认值处理
                    if 'default' in content.lower() and ('=' in content or 'get(' in content):
                        file_score += 0.3

                    # 检查可选依赖处理
                    if 'ImportError' in content or 'ModuleNotFoundError' in content:
                        file_score += 0.2

                    # 检查配置验证
                    if 'validate' in content.lower() or 'check' in content.lower():
                        file_score += 0.2

                    degradation_score += min(1.0, file_score)

                except Exception:
                    continue

            return degradation_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估优雅降级失败: {e}")
            return 0.0

    def evaluate_startup_time(self) -> float:
        """评估启动时间"""
        try:
            # 基于导入复杂度估算启动时间
            import_complexity = 0

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 统计导入语句
                    import_count = content.count('import ') + content.count('from ')
                    import_complexity += import_count

                except Exception:
                    continue

            # 基于导入复杂度评分（越少越好）
            if import_complexity < 50:
                return 1.0
            elif import_complexity < 100:
                return 0.8
            elif import_complexity < 200:
                return 0.6
            elif import_complexity < 400:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.error(f"评估启动时间失败: {e}")
            return 0.5

    def evaluate_memory_efficiency(self) -> float:
        """评估内存效率"""
        try:
            efficiency_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0.5  # 基础分

                    # 检查内存优化技术
                    if '__slots__' in content:
                        file_score += 0.2

                    if 'generator' in content or 'yield' in content:
                        file_score += 0.2

                    if 'cache' in content.lower():
                        file_score += 0.1

                    efficiency_score += min(1.0, file_score)

                except Exception:
                    continue

            return efficiency_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估内存效率失败: {e}")
            return 0.0

    def evaluate_cpu_efficiency(self) -> float:
        """评估CPU效率"""
        try:
            efficiency_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0.5  # 基础分

                    # 检查性能优化
                    if 'async' in content or 'await' in content:
                        file_score += 0.2

                    if 'multiprocessing' in content or 'threading' in content:
                        file_score += 0.2

                    if 'numpy' in content or 'pandas' in content:
                        file_score += 0.1

                    efficiency_score += min(1.0, file_score)

                except Exception:
                    continue

            return efficiency_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估CPU效率失败: {e}")
            return 0.0

    def evaluate_io_efficiency(self) -> float:
        """评估I/O效率"""
        try:
            efficiency_score = 0
            total_files = len(self.python_files)

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_score = 0.5  # 基础分

                    # 检查异步I/O
                    if 'aiofiles' in content or 'asyncio' in content:
                        file_score += 0.3

                    # 检查批量操作
                    if 'batch' in content.lower():
                        file_score += 0.2

                    efficiency_score += min(1.0, file_score)

                except Exception:
                    continue

            return efficiency_score / max(total_files, 1)

        except Exception as e:
            logger.error(f"评估I/O效率失败: {e}")
            return 0.0

    def evaluate_algorithm_complexity(self) -> float:
        """评估算法复杂度"""
        try:
            complexity_score = 0.7  # 默认良好分数

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查嵌套循环（可能的O(n²)复杂度）
                    nested_loops = len(re.findall(r'for.*:\s*\n.*for.*:', content, re.MULTILINE))
                    if nested_loops > 3:
                        complexity_score -= 0.1

                    # 检查递归（可能的指数复杂度）
                    recursive_calls = content.count('def ') - content.count('return')
                    if recursive_calls > 5:
                        complexity_score -= 0.1

                except Exception:
                    continue

            return max(0.0, min(1.0, complexity_score))

        except Exception as e:
            logger.error(f"评估算法复杂度失败: {e}")
            return 0.5

    def evaluate_caching_strategy(self) -> float:
        """评估缓存策略"""
        try:
            caching_score = 0

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查缓存实现
                    if 'cache' in content.lower():
                        caching_score += 0.3

                    if 'lru_cache' in content or '@cache' in content:
                        caching_score += 0.4

                    if 'redis' in content.lower() or 'memcached' in content.lower():
                        caching_score += 0.3

                except Exception:
                    continue

            return min(1.0, caching_score)

        except Exception as e:
            logger.error(f"评估缓存策略失败: {e}")
            return 0.0

    def evaluate_async_programming(self) -> float:
        """评估异步编程"""
        try:
            async_score = 0
            total_files = len(self.python_files)
            files_with_async = 0

            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'async def' in content or 'await' in content:
                        files_with_async += 1

                except Exception:
                    continue

            if total_files > 0:
                async_score = files_with_async / total_files

            return async_score

        except Exception as e:
            logger.error(f"评估异步编程失败: {e}")
            return 0.0

    def calculate_overall_score(self, report: TechnicalArchitectureReport):
        """计算综合评分"""
        try:
            # 四大维度权重
            weights = {
                "code_structure": 0.25,
                "extensibility": 0.25,
                "stability": 0.25,
                "performance": 0.25
            }

            # 将质量级别转换为数值
            quality_scores = {
                ArchitectureQuality.POOR: 0.2,
                ArchitectureQuality.BASIC: 0.4,
                ArchitectureQuality.GOOD: 0.6,
                ArchitectureQuality.EXCELLENT: 0.8,
                ArchitectureQuality.ENTERPRISE: 1.0
            }

            performance_scores = {
                PerformanceLevel.CRITICAL: 0.1,
                PerformanceLevel.POOR: 0.3,
                PerformanceLevel.ACCEPTABLE: 0.5,
                PerformanceLevel.GOOD: 0.7,
                PerformanceLevel.EXCELLENT: 0.9
            }

            # 计算加权平均分
            overall_score = (
                quality_scores[report.code_structure_quality] * weights["code_structure"] +
                quality_scores[report.extensibility_quality] * weights["extensibility"] +
                quality_scores[report.stability_quality] * weights["stability"] +
                performance_scores[report.performance_quality] * weights["performance"]
            )

            report.overall_architecture_score = overall_score

            # 确定整体架构质量
            if overall_score >= 0.9:
                report.overall_architecture_quality = ArchitectureQuality.ENTERPRISE
            elif overall_score >= 0.75:
                report.overall_architecture_quality = ArchitectureQuality.EXCELLENT
            elif overall_score >= 0.6:
                report.overall_architecture_quality = ArchitectureQuality.GOOD
            elif overall_score >= 0.4:
                report.overall_architecture_quality = ArchitectureQuality.BASIC
            else:
                report.overall_architecture_quality = ArchitectureQuality.POOR

        except Exception as e:
            logger.error(f"计算综合评分失败: {e}")

    def generate_findings_and_recommendations(self, report: TechnicalArchitectureReport):
        """生成关键发现和建议"""
        try:
            # 架构优势
            if report.code_structure_quality in [ArchitectureQuality.EXCELLENT, ArchitectureQuality.ENTERPRISE]:
                report.architecture_strengths.append("代码结构优秀，具备良好的可维护性")

            if report.extensibility_quality in [ArchitectureQuality.EXCELLENT, ArchitectureQuality.ENTERPRISE]:
                report.architecture_strengths.append("系统扩展性强，支持插件和模块化开发")

            if report.stability_quality in [ArchitectureQuality.EXCELLENT, ArchitectureQuality.ENTERPRISE]:
                report.architecture_strengths.append("系统稳定性高，错误处理完善")

            if report.performance_quality in [PerformanceLevel.GOOD, PerformanceLevel.EXCELLENT]:
                report.architecture_strengths.append("性能表现良好，优化措施得当")

            # 架构弱点
            if report.code_structure_quality == ArchitectureQuality.POOR:
                report.architecture_weaknesses.append("代码结构需要重构，可维护性差")

            if report.extensibility_quality == ArchitectureQuality.POOR:
                report.architecture_weaknesses.append("系统扩展性不足，难以添加新功能")

            if report.stability_quality == ArchitectureQuality.POOR:
                report.architecture_weaknesses.append("系统稳定性问题严重，错误处理不足")

            if report.performance_quality in [PerformanceLevel.CRITICAL, PerformanceLevel.POOR]:
                report.performance_bottlenecks.append("性能问题严重，需要立即优化")

            # 立即行动建议
            if report.overall_architecture_score < 0.5:
                report.immediate_actions.append("立即进行架构重构，解决关键质量问题")

            if report.stability_quality == ArchitectureQuality.POOR:
                report.immediate_actions.append("完善错误处理机制，提升系统稳定性")

            if report.performance_quality == PerformanceLevel.CRITICAL:
                report.immediate_actions.append("紧急修复性能瓶颈，优化关键路径")

            # 短期改进建议
            if report.code_structure_metrics.documentation_coverage < 0.6:
                report.short_term_improvements.append("提升文档覆盖率，完善代码注释")

            if report.code_structure_metrics.type_annotation_coverage < 0.5:
                report.short_term_improvements.append("添加类型注解，提升代码质量")

            if report.extensibility_metrics.modular_design_score < 0.6:
                report.short_term_improvements.append("改进模块化设计，降低耦合度")

            # 长期优化建议
            if report.extensibility_metrics.plugin_architecture_score < 0.5:
                report.long_term_optimizations.append("设计插件架构，支持第三方扩展")

            if report.performance_metrics.caching_strategy_score < 0.5:
                report.long_term_optimizations.append("实现缓存策略，提升系统性能")

            if report.performance_metrics.async_programming_score < 0.3:
                report.long_term_optimizations.append("引入异步编程，提升并发性能")

        except Exception as e:
            logger.error(f"生成关键发现和建议失败: {e}")

    def generate_html_report(self, report: TechnicalArchitectureReport) -> str:
        """生成HTML报告"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AI Animation Studio - 技术架构评估报告</title>
                <style>
                    body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                    .section {{ margin: 25px 0; padding: 20px; border-left: 4px solid #3498db; background: #f8f9fa; border-radius: 5px; }}
                    .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .metric-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .score {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                    .excellent {{ color: #27ae60; }}
                    .good {{ color: #2ecc71; }}
                    .acceptable {{ color: #f39c12; }}
                    .poor {{ color: #e74c3c; }}
                    .critical {{ color: #c0392b; }}
                    .progress-bar {{ width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
                    .progress-fill {{ height: 100%; transition: width 0.3s ease; }}
                    .strengths {{ color: #27ae60; }}
                    .weaknesses {{ color: #e74c3c; }}
                    .recommendations {{ color: #3498db; }}
                    .immediate {{ background: #ffebee; border-left: 4px solid #f44336; }}
                    .short-term {{ background: #fff3e0; border-left: 4px solid #ff9800; }}
                    .long-term {{ background: #e8f5e8; border-left: 4px solid #4caf50; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏗️ AI Animation Studio 技术架构评估报告</h1>
                        <p>评估时间: {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <div class="score {self.get_score_class(report.overall_architecture_score)}">
                            综合评分: {report.overall_architecture_score:.1%} ({report.overall_architecture_quality.value})
                        </div>
                    </div>

                    <div class="section">
                        <h2>📊 四大维度评估</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h3>代码结构质量</h3>
                                <div class="score {self.get_quality_class(report.code_structure_quality)}">{report.code_structure_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_quality_class(report.code_structure_quality)}"
                                         style="width: {self.quality_to_percentage(report.code_structure_quality)}%"></div>
                                </div>
                                <p>文件数: {report.code_structure_metrics.total_files}</p>
                                <p>代码行数: {report.code_structure_metrics.total_lines}</p>
                                <p>文档覆盖率: {report.code_structure_metrics.documentation_coverage:.1%}</p>
                            </div>

                            <div class="metric-card">
                                <h3>扩展性质量</h3>
                                <div class="score {self.get_quality_class(report.extensibility_quality)}">{report.extensibility_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_quality_class(report.extensibility_quality)}"
                                         style="width: {self.quality_to_percentage(report.extensibility_quality)}%"></div>
                                </div>
                                <p>模块化设计: {report.extensibility_metrics.modular_design_score:.1%}</p>
                                <p>API设计: {report.extensibility_metrics.api_design_score:.1%}</p>
                                <p>配置灵活性: {report.extensibility_metrics.configuration_flexibility_score:.1%}</p>
                            </div>

                            <div class="metric-card">
                                <h3>稳定性质量</h3>
                                <div class="score {self.get_quality_class(report.stability_quality)}">{report.stability_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_quality_class(report.stability_quality)}"
                                         style="width: {self.quality_to_percentage(report.stability_quality)}%"></div>
                                </div>
                                <p>错误处理覆盖率: {report.stability_metrics.error_handling_coverage:.1%}</p>
                                <p>异常安全性: {report.stability_metrics.exception_safety_score:.1%}</p>
                                <p>资源管理: {report.stability_metrics.resource_management_score:.1%}</p>
                            </div>

                            <div class="metric-card">
                                <h3>性能质量</h3>
                                <div class="score {self.get_performance_class(report.performance_quality)}">{report.performance_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_performance_class(report.performance_quality)}"
                                         style="width: {self.performance_to_percentage(report.performance_quality)}%"></div>
                                </div>
                                <p>内存效率: {report.performance_metrics.memory_efficiency_score:.1%}</p>
                                <p>CPU效率: {report.performance_metrics.cpu_efficiency_score:.1%}</p>
                                <p>缓存策略: {report.performance_metrics.caching_strategy_score:.1%}</p>
                            </div>
                        </div>
                    </div>

                    <div class="section">
                        <h2>💪 架构优势</h2>
                        <ul class="strengths">
            """

            for strength in report.architecture_strengths:
                html += f"<li>✅ {strength}</li>"

            html += """
                        </ul>
                    </div>

                    <div class="section">
                        <h2>⚠️ 架构弱点</h2>
                        <ul class="weaknesses">
            """

            for weakness in report.architecture_weaknesses:
                html += f"<li>❌ {weakness}</li>"

            html += """
                        </ul>
                    </div>

                    <div class="section immediate">
                        <h2>🚨 立即行动建议</h2>
                        <ul class="recommendations">
            """

            for action in report.immediate_actions:
                html += f"<li>🔥 {action}</li>"

            html += """
                        </ul>
                    </div>

                    <div class="section short-term">
                        <h2>📅 短期改进建议</h2>
                        <ul class="recommendations">
            """

            for improvement in report.short_term_improvements:
                html += f"<li>⚡ {improvement}</li>"

            html += """
                        </ul>
                    </div>

                    <div class="section long-term">
                        <h2>🎯 长期优化建议</h2>
                        <ul class="recommendations">
            """

            for optimization in report.long_term_optimizations:
                html += f"<li>🚀 {optimization}</li>"

            html += """
                        </ul>
                    </div>

                    <div class="section">
                        <h2>📈 详细指标</h2>
                        <h3>代码结构指标</h3>
                        <p>总文件数: {report.code_structure_metrics.total_files}</p>
                        <p>总代码行数: {report.code_structure_metrics.total_lines}</p>
                        <p>总类数: {report.code_structure_metrics.total_classes}</p>
                        <p>总函数数: {report.code_structure_metrics.total_functions}</p>
                        <p>平均文件大小: {report.code_structure_metrics.average_file_size:.1f} 行</p>
                        <p>文档覆盖率: {report.code_structure_metrics.documentation_coverage:.1%}</p>
                        <p>类型注解覆盖率: {report.code_structure_metrics.type_annotation_coverage:.1%}</p>
                        <p>代码重复率: {report.code_structure_metrics.code_duplication_rate:.1%}</p>

                        <h3>扩展性指标</h3>
                        <p>接口抽象评分: {report.extensibility_metrics.interface_abstraction_score:.1%}</p>
                        <p>插件架构评分: {report.extensibility_metrics.plugin_architecture_score:.1%}</p>
                        <p>配置灵活性评分: {report.extensibility_metrics.configuration_flexibility_score:.1%}</p>
                        <p>API设计评分: {report.extensibility_metrics.api_design_score:.1%}</p>
                        <p>依赖注入评分: {report.extensibility_metrics.dependency_injection_score:.1%}</p>
                        <p>模块化设计评分: {report.extensibility_metrics.modular_design_score:.1%}</p>

                        <h3>稳定性指标</h3>
                        <p>错误处理覆盖率: {report.stability_metrics.error_handling_coverage:.1%}</p>
                        <p>异常安全性评分: {report.stability_metrics.exception_safety_score:.1%}</p>
                        <p>资源管理评分: {report.stability_metrics.resource_management_score:.1%}</p>
                        <p>线程安全性评分: {report.stability_metrics.thread_safety_score:.1%}</p>
                        <p>内存安全性评分: {report.stability_metrics.memory_safety_score:.1%}</p>
                        <p>优雅降级评分: {report.stability_metrics.graceful_degradation_score:.1%}</p>

                        <h3>性能指标</h3>
                        <p>启动时间评分: {report.performance_metrics.startup_time_score:.1%}</p>
                        <p>内存效率评分: {report.performance_metrics.memory_efficiency_score:.1%}</p>
                        <p>CPU效率评分: {report.performance_metrics.cpu_efficiency_score:.1%}</p>
                        <p>I/O效率评分: {report.performance_metrics.io_efficiency_score:.1%}</p>
                        <p>算法复杂度评分: {report.performance_metrics.algorithm_complexity_score:.1%}</p>
                        <p>缓存策略评分: {report.performance_metrics.caching_strategy_score:.1%}</p>
                        <p>异步编程评分: {report.performance_metrics.async_programming_score:.1%}</p>
                    </div>
                </div>
            </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return f"<html><body><h1>报告生成失败: {e}</h1></body></html>"

    def get_score_class(self, score: float) -> str:
        """获取评分样式类"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.75:
            return "good"
        elif score >= 0.6:
            return "acceptable"
        elif score >= 0.4:
            return "poor"
        else:
            return "critical"

    def get_quality_class(self, quality: ArchitectureQuality) -> str:
        """获取质量样式类"""
        quality_classes = {
            ArchitectureQuality.ENTERPRISE: "excellent",
            ArchitectureQuality.EXCELLENT: "excellent",
            ArchitectureQuality.GOOD: "good",
            ArchitectureQuality.BASIC: "acceptable",
            ArchitectureQuality.POOR: "poor"
        }
        return quality_classes.get(quality, "poor")

    def get_performance_class(self, performance: PerformanceLevel) -> str:
        """获取性能样式类"""
        performance_classes = {
            PerformanceLevel.EXCELLENT: "excellent",
            PerformanceLevel.GOOD: "good",
            PerformanceLevel.ACCEPTABLE: "acceptable",
            PerformanceLevel.POOR: "poor",
            PerformanceLevel.CRITICAL: "critical"
        }
        return performance_classes.get(performance, "poor")

    def quality_to_percentage(self, quality: ArchitectureQuality) -> int:
        """将质量级别转换为百分比"""
        quality_percentages = {
            ArchitectureQuality.ENTERPRISE: 100,
            ArchitectureQuality.EXCELLENT: 85,
            ArchitectureQuality.GOOD: 70,
            ArchitectureQuality.BASIC: 50,
            ArchitectureQuality.POOR: 25
        }
        return quality_percentages.get(quality, 25)

    def performance_to_percentage(self, performance: PerformanceLevel) -> int:
        """将性能级别转换为百分比"""
        performance_percentages = {
            PerformanceLevel.EXCELLENT: 95,
            PerformanceLevel.GOOD: 80,
            PerformanceLevel.ACCEPTABLE: 60,
            PerformanceLevel.POOR: 35,
            PerformanceLevel.CRITICAL: 15
        }
        return performance_percentages.get(performance, 35)
