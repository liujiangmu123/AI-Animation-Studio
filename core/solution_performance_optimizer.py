"""
AI Animation Studio - 方案性能优化器
自动分析和优化动画方案的性能，提供优化建议和自动优化功能
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from core.enhanced_solution_manager import EnhancedAnimationSolution
from core.logger import get_logger

logger = get_logger("solution_performance_optimizer")


class OptimizationType(Enum):
    """优化类型"""
    PERFORMANCE = "performance"      # 性能优化
    COMPATIBILITY = "compatibility" # 兼容性优化
    ACCESSIBILITY = "accessibility" # 可访问性优化
    CODE_QUALITY = "code_quality"   # 代码质量优化


@dataclass
class OptimizationRule:
    """优化规则"""
    rule_id: str
    name: str
    description: str
    optimization_type: OptimizationType
    pattern: str                    # 匹配模式
    replacement: str                # 替换内容
    impact_score: float            # 影响分数 (0-10)
    difficulty: str                # 难度等级 (easy, medium, hard)
    auto_applicable: bool = True   # 是否可自动应用


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        # 性能优化规则
        self.performance_rules = [
            OptimizationRule(
                rule_id="perf_001",
                name="使用transform代替position",
                description="将left/top属性改为transform，提升GPU加速性能",
                optimization_type=OptimizationType.PERFORMANCE,
                pattern=r"(left|top)\s*:\s*([^;]+);",
                replacement="transform: translate({value});",
                impact_score=8.0,
                difficulty="easy"
            ),
            OptimizationRule(
                rule_id="perf_002", 
                name="添加will-change属性",
                description="为动画元素添加will-change属性，优化渲染性能",
                optimization_type=OptimizationType.PERFORMANCE,
                pattern=r"(\.[\w-]+\s*{[^}]*)(transform|opacity)([^}]*})",
                replacement=r"\1will-change: \2;\2\3",
                impact_score=6.0,
                difficulty="easy"
            ),
            OptimizationRule(
                rule_id="perf_003",
                name="使用transform3d强制GPU加速",
                description="将2D变换改为3D变换，强制启用GPU加速",
                optimization_type=OptimizationType.PERFORMANCE,
                pattern=r"transform\s*:\s*translate\(([^)]+)\)",
                replacement=r"transform: translate3d(\1, 0)",
                impact_score=7.0,
                difficulty="easy"
            ),
            OptimizationRule(
                rule_id="perf_004",
                name="优化动画时长",
                description="调整过长的动画时长，提升用户体验",
                optimization_type=OptimizationType.PERFORMANCE,
                pattern=r"(animation-duration|transition-duration)\s*:\s*([5-9]|\d{2,})s",
                replacement=r"\1: 3s",
                impact_score=5.0,
                difficulty="easy"
            ),
            OptimizationRule(
                rule_id="perf_005",
                name="使用requestAnimationFrame",
                description="将setInterval/setTimeout改为requestAnimationFrame",
                optimization_type=OptimizationType.PERFORMANCE,
                pattern=r"setInterval\s*\(\s*([^,]+),\s*(\d+)\s*\)",
                replacement="requestAnimationFrame(\\1)",
                impact_score=9.0,
                difficulty="medium"
            )
        ]
        
        # 兼容性优化规则
        self.compatibility_rules = [
            OptimizationRule(
                rule_id="compat_001",
                name="添加浏览器前缀",
                description="为CSS属性添加浏览器前缀，提升兼容性",
                optimization_type=OptimizationType.COMPATIBILITY,
                pattern=r"(transform|transition|animation)\s*:",
                replacement=r"-webkit-\1:\n-moz-\1:\n-ms-\1:\n\1:",
                impact_score=7.0,
                difficulty="easy"
            ),
            OptimizationRule(
                rule_id="compat_002",
                name="提供降级方案",
                description="为现代CSS特性提供降级方案",
                optimization_type=OptimizationType.COMPATIBILITY,
                pattern=r"display\s*:\s*grid",
                replacement="display: -ms-grid;\ndisplay: grid",
                impact_score=6.0,
                difficulty="medium"
            )
        ]
        
        # 代码质量优化规则
        self.quality_rules = [
            OptimizationRule(
                rule_id="quality_001",
                name="添加代码注释",
                description="为关键动画代码添加注释，提升可维护性",
                optimization_type=OptimizationType.CODE_QUALITY,
                pattern=r"(@keyframes\s+[\w-]+\s*{)",
                replacement=r"/* 关键帧动画定义 */\n\1",
                impact_score=4.0,
                difficulty="easy"
            ),
            OptimizationRule(
                rule_id="quality_002",
                name="优化CSS选择器",
                description="简化复杂的CSS选择器，提升性能",
                optimization_type=OptimizationType.CODE_QUALITY,
                pattern=r"([\w\s>+~:]+){4,}",
                replacement="/* 建议简化选择器 */",
                impact_score=5.0,
                difficulty="medium",
                auto_applicable=False
            )
        ]
        
        # 合并所有规则
        self.all_rules = (
            self.performance_rules + 
            self.compatibility_rules + 
            self.quality_rules
        )
    
    def analyze_solution_performance(self, solution: EnhancedAnimationSolution) -> Dict[str, Any]:
        """分析方案性能"""
        analysis = {
            "performance_issues": [],
            "optimization_opportunities": [],
            "compatibility_issues": [],
            "quality_issues": [],
            "overall_performance_score": 0,
            "optimization_potential": 0
        }
        
        try:
            # 分析CSS性能
            css_issues = self.analyze_css_performance(solution.css_code)
            analysis["performance_issues"].extend(css_issues)
            
            # 分析JavaScript性能
            js_issues = self.analyze_js_performance(solution.js_code)
            analysis["performance_issues"].extend(js_issues)
            
            # 查找优化机会
            optimization_opportunities = self.find_optimization_opportunities(solution)
            analysis["optimization_opportunities"] = optimization_opportunities
            
            # 计算性能分数
            analysis["overall_performance_score"] = self.calculate_performance_score(analysis)
            
            # 计算优化潜力
            analysis["optimization_potential"] = len(optimization_opportunities) * 10
            
        except Exception as e:
            logger.error(f"分析方案性能失败: {e}")
        
        return analysis
    
    def analyze_css_performance(self, css_code: str) -> List[Dict[str, Any]]:
        """分析CSS性能"""
        issues = []
        
        if not css_code:
            return issues
        
        try:
            # 检查低性能属性
            low_perf_props = ["left", "top", "width", "height", "margin-left", "margin-top"]
            for prop in low_perf_props:
                if re.search(rf"{prop}\s*:", css_code):
                    issues.append({
                        "type": "performance",
                        "severity": "medium",
                        "message": f"使用了低性能属性 '{prop}'，建议改用transform",
                        "property": prop,
                        "suggestion": f"将 {prop} 改为 transform"
                    })
            
            # 检查动画时长
            duration_matches = re.findall(r"(animation-duration|transition-duration)\s*:\s*(\d+(?:\.\d+)?)(s|ms)", css_code)
            for match in duration_matches:
                prop, value, unit = match
                duration_ms = float(value) * (1000 if unit == "s" else 1)
                
                if duration_ms > 5000:  # 超过5秒
                    issues.append({
                        "type": "performance",
                        "severity": "low",
                        "message": f"动画时长过长 ({value}{unit})，可能影响用户体验",
                        "property": prop,
                        "suggestion": "考虑缩短动画时长到3秒以内"
                    })
            
            # 检查复杂选择器
            complex_selectors = re.findall(r"([^{]+{)", css_code)
            for selector in complex_selectors:
                if selector.count(" ") > 4 or selector.count(">") > 2:
                    issues.append({
                        "type": "performance",
                        "severity": "low",
                        "message": "选择器过于复杂，可能影响CSS解析性能",
                        "selector": selector.strip(),
                        "suggestion": "简化选择器结构"
                    })
            
        except Exception as e:
            logger.error(f"分析CSS性能失败: {e}")
        
        return issues
    
    def analyze_js_performance(self, js_code: str) -> List[Dict[str, Any]]:
        """分析JavaScript性能"""
        issues = []
        
        if not js_code:
            return issues
        
        try:
            # 检查定时器使用
            if "setInterval" in js_code:
                issues.append({
                    "type": "performance",
                    "severity": "high",
                    "message": "使用setInterval可能导致性能问题",
                    "suggestion": "改用requestAnimationFrame实现动画"
                })
            
            # 检查DOM查询
            dom_queries = re.findall(r"(getElementById|querySelector|getElementsBy\w+)", js_code)
            if len(dom_queries) > 5:
                issues.append({
                    "type": "performance",
                    "severity": "medium",
                    "message": "频繁的DOM查询可能影响性能",
                    "suggestion": "缓存DOM元素引用"
                })
            
            # 检查循环中的DOM操作
            loop_patterns = [r"for\s*\([^)]*\)\s*{[^}]*(?:getElementById|querySelector)", 
                           r"while\s*\([^)]*\)\s*{[^}]*(?:getElementById|querySelector)"]
            
            for pattern in loop_patterns:
                if re.search(pattern, js_code, re.DOTALL):
                    issues.append({
                        "type": "performance",
                        "severity": "high",
                        "message": "在循环中进行DOM操作会严重影响性能",
                        "suggestion": "将DOM操作移出循环或使用文档片段"
                    })
            
        except Exception as e:
            logger.error(f"分析JavaScript性能失败: {e}")
        
        return issues
    
    def find_optimization_opportunities(self, solution: EnhancedAnimationSolution) -> List[Dict[str, Any]]:
        """查找优化机会"""
        opportunities = []
        
        try:
            # 检查所有优化规则
            for rule in self.all_rules:
                # 检查CSS代码
                if solution.css_code and re.search(rule.pattern, solution.css_code):
                    opportunities.append({
                        "rule": rule,
                        "code_type": "css",
                        "matches": re.findall(rule.pattern, solution.css_code),
                        "estimated_improvement": rule.impact_score
                    })
                
                # 检查JavaScript代码
                if solution.js_code and re.search(rule.pattern, solution.js_code):
                    opportunities.append({
                        "rule": rule,
                        "code_type": "js",
                        "matches": re.findall(rule.pattern, solution.js_code),
                        "estimated_improvement": rule.impact_score
                    })
            
            # 按影响分数排序
            opportunities.sort(key=lambda x: x["estimated_improvement"], reverse=True)
            
        except Exception as e:
            logger.error(f"查找优化机会失败: {e}")
        
        return opportunities
    
    def calculate_performance_score(self, analysis: Dict[str, Any]) -> float:
        """计算性能分数"""
        base_score = 80.0  # 基础分数
        
        # 根据问题数量扣分
        performance_issues = analysis.get("performance_issues", [])
        
        for issue in performance_issues:
            severity = issue.get("severity", "low")
            if severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 8
            else:  # low
                base_score -= 3
        
        return max(0, min(100, base_score))
    
    def auto_optimize_solution(self, solution: EnhancedAnimationSolution, 
                              optimization_types: List[OptimizationType] = None) -> EnhancedAnimationSolution:
        """自动优化方案"""
        try:
            if optimization_types is None:
                optimization_types = [OptimizationType.PERFORMANCE]
            
            # 创建优化后的方案副本
            optimized_solution = self.copy_solution(solution)
            optimized_solution.name += " (优化版)"
            optimized_solution.version = self.increment_version(solution.version)
            
            # 应用优化规则
            applied_optimizations = []
            
            for rule in self.all_rules:
                if rule.optimization_type in optimization_types and rule.auto_applicable:
                    # 优化CSS代码
                    if optimized_solution.css_code:
                        original_css = optimized_solution.css_code
                        optimized_css = self.apply_optimization_rule(original_css, rule)
                        
                        if optimized_css != original_css:
                            optimized_solution.css_code = optimized_css
                            applied_optimizations.append(rule.name)
                    
                    # 优化JavaScript代码
                    if optimized_solution.js_code:
                        original_js = optimized_solution.js_code
                        optimized_js = self.apply_optimization_rule(original_js, rule)
                        
                        if optimized_js != original_js:
                            optimized_solution.js_code = optimized_js
                            applied_optimizations.append(rule.name)
            
            # 更新描述
            if applied_optimizations:
                optimized_solution.description += f"\n\n已应用优化: {', '.join(applied_optimizations)}"
            
            logger.info(f"自动优化完成，应用了 {len(applied_optimizations)} 个优化")
            
            return optimized_solution
            
        except Exception as e:
            logger.error(f"自动优化方案失败: {e}")
            return solution
    
    def apply_optimization_rule(self, code: str, rule: OptimizationRule) -> str:
        """应用优化规则"""
        try:
            # 简化的规则应用逻辑
            if rule.rule_id == "perf_001":
                # left/top 转 transform
                code = re.sub(r"left\s*:\s*([^;]+);", r"transform: translateX(\1);", code)
                code = re.sub(r"top\s*:\s*([^;]+);", r"transform: translateY(\1);", code)
            
            elif rule.rule_id == "perf_002":
                # 添加will-change
                code = re.sub(
                    r"(\.[\w-]+\s*{[^}]*)(transform|opacity)([^}]*})",
                    r"\1will-change: \2;\n  \2\3",
                    code
                )
            
            elif rule.rule_id == "perf_003":
                # 2D转3D变换
                code = re.sub(
                    r"transform\s*:\s*translate\(([^)]+)\)",
                    r"transform: translate3d(\1, 0)",
                    code
                )
            
            elif rule.rule_id == "perf_004":
                # 优化动画时长
                code = re.sub(
                    r"(animation-duration|transition-duration)\s*:\s*[5-9]s",
                    r"\1: 3s",
                    code
                )
            
            elif rule.rule_id == "perf_005":
                # setInterval转requestAnimationFrame
                code = re.sub(
                    r"setInterval\s*\(\s*([^,]+),\s*\d+\s*\)",
                    r"requestAnimationFrame(\1)",
                    code
                )
            
            elif rule.rule_id == "compat_001":
                # 添加浏览器前缀
                for prop in ["transform", "transition", "animation"]:
                    pattern = rf"({prop}\s*:[^;]+;)"
                    replacement = rf"-webkit-\1\n-moz-\1\n-ms-\1\n\1"
                    code = re.sub(pattern, replacement, code)
            
            return code
            
        except Exception as e:
            logger.error(f"应用优化规则失败: {e}")
            return code
    
    def copy_solution(self, solution: EnhancedAnimationSolution) -> EnhancedAnimationSolution:
        """复制方案"""
        import copy
        return copy.deepcopy(solution)
    
    def increment_version(self, version: str) -> str:
        """递增版本号"""
        try:
            parts = version.split(".")
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                return f"{major}.{minor}.{patch + 1}"
            else:
                return "1.0.1"
        except:
            return "1.0.1"
    
    def generate_optimization_report(self, original_solution: EnhancedAnimationSolution,
                                   optimized_solution: EnhancedAnimationSolution) -> Dict[str, Any]:
        """生成优化报告"""
        try:
            # 分析原始方案
            original_analysis = self.analyze_solution_performance(original_solution)
            
            # 分析优化后方案
            optimized_analysis = self.analyze_solution_performance(optimized_solution)
            
            # 计算改进
            performance_improvement = (
                optimized_analysis["overall_performance_score"] - 
                original_analysis["overall_performance_score"]
            )
            
            # 代码大小对比
            original_size = len(original_solution.css_code) + len(original_solution.js_code)
            optimized_size = len(optimized_solution.css_code) + len(optimized_solution.js_code)
            size_change = optimized_size - original_size
            
            report = {
                "optimization_summary": {
                    "performance_improvement": performance_improvement,
                    "code_size_change": size_change,
                    "issues_fixed": len(original_analysis["performance_issues"]) - len(optimized_analysis["performance_issues"]),
                    "optimization_count": len(original_analysis["optimization_opportunities"])
                },
                "before": {
                    "performance_score": original_analysis["overall_performance_score"],
                    "issues_count": len(original_analysis["performance_issues"]),
                    "code_size": original_size
                },
                "after": {
                    "performance_score": optimized_analysis["overall_performance_score"],
                    "issues_count": len(optimized_analysis["performance_issues"]),
                    "code_size": optimized_size
                },
                "applied_optimizations": [],
                "recommendations": []
            }
            
            # 添加建议
            if performance_improvement > 10:
                report["recommendations"].append("优化效果显著，建议采用优化版本")
            elif performance_improvement > 0:
                report["recommendations"].append("优化有一定效果，可以考虑采用")
            else:
                report["recommendations"].append("当前方案已经较为优化")
            
            return report
            
        except Exception as e:
            logger.error(f"生成优化报告失败: {e}")
            return {}
    
    def get_optimization_suggestions(self, solution: EnhancedAnimationSolution) -> List[Dict[str, Any]]:
        """获取优化建议"""
        suggestions = []
        
        try:
            # 查找优化机会
            opportunities = self.find_optimization_opportunities(solution)
            
            for opportunity in opportunities:
                rule = opportunity["rule"]
                
                suggestion = {
                    "id": rule.rule_id,
                    "title": rule.name,
                    "description": rule.description,
                    "type": rule.optimization_type.value,
                    "impact": rule.impact_score,
                    "difficulty": rule.difficulty,
                    "auto_applicable": rule.auto_applicable,
                    "code_type": opportunity["code_type"],
                    "matches_count": len(opportunity["matches"])
                }
                
                suggestions.append(suggestion)
            
            # 按影响分数排序
            suggestions.sort(key=lambda x: x["impact"], reverse=True)
            
        except Exception as e:
            logger.error(f"获取优化建议失败: {e}")
        
        return suggestions
    
    def apply_specific_optimization(self, solution: EnhancedAnimationSolution, 
                                  rule_id: str) -> EnhancedAnimationSolution:
        """应用特定优化"""
        try:
            # 查找对应规则
            rule = None
            for r in self.all_rules:
                if r.rule_id == rule_id:
                    rule = r
                    break
            
            if not rule:
                logger.warning(f"未找到优化规则: {rule_id}")
                return solution
            
            # 创建优化后的方案
            optimized_solution = self.copy_solution(solution)
            
            # 应用规则
            if optimized_solution.css_code:
                optimized_solution.css_code = self.apply_optimization_rule(
                    optimized_solution.css_code, rule
                )
            
            if optimized_solution.js_code:
                optimized_solution.js_code = self.apply_optimization_rule(
                    optimized_solution.js_code, rule
                )
            
            # 更新元数据
            optimized_solution.description += f"\n应用优化: {rule.name}"
            optimized_solution.version = self.increment_version(solution.version)
            
            logger.info(f"应用优化规则: {rule.name}")
            
            return optimized_solution
            
        except Exception as e:
            logger.error(f"应用特定优化失败: {e}")
            return solution
    
    def batch_optimize_solutions(self, solutions: List[EnhancedAnimationSolution],
                               optimization_types: List[OptimizationType] = None) -> List[EnhancedAnimationSolution]:
        """批量优化方案"""
        optimized_solutions = []
        
        try:
            for solution in solutions:
                optimized = self.auto_optimize_solution(solution, optimization_types)
                optimized_solutions.append(optimized)
            
            logger.info(f"批量优化完成，处理了 {len(solutions)} 个方案")
            
        except Exception as e:
            logger.error(f"批量优化失败: {e}")
        
        return optimized_solutions
    
    def validate_optimization(self, original_solution: EnhancedAnimationSolution,
                            optimized_solution: EnhancedAnimationSolution) -> Dict[str, Any]:
        """验证优化效果"""
        validation = {
            "is_valid": True,
            "issues": [],
            "improvements": [],
            "warnings": []
        }
        
        try:
            # 检查代码语法
            if not self.validate_css_syntax(optimized_solution.css_code):
                validation["is_valid"] = False
                validation["issues"].append("优化后的CSS代码存在语法错误")
            
            if not self.validate_js_syntax(optimized_solution.js_code):
                validation["is_valid"] = False
                validation["issues"].append("优化后的JavaScript代码存在语法错误")
            
            # 检查功能完整性
            if len(optimized_solution.css_code) < len(original_solution.css_code) * 0.5:
                validation["warnings"].append("优化后代码大幅减少，请检查功能完整性")
            
            # 记录改进
            original_analysis = self.analyze_solution_performance(original_solution)
            optimized_analysis = self.analyze_solution_performance(optimized_solution)
            
            performance_improvement = (
                optimized_analysis["overall_performance_score"] - 
                original_analysis["overall_performance_score"]
            )
            
            if performance_improvement > 0:
                validation["improvements"].append(f"性能提升 {performance_improvement:.1f} 分")
            
        except Exception as e:
            logger.error(f"验证优化效果失败: {e}")
            validation["issues"].append(f"验证过程出错: {str(e)}")
        
        return validation
    
    def validate_css_syntax(self, css_code: str) -> bool:
        """验证CSS语法"""
        if not css_code:
            return True
        
        try:
            # 简单的CSS语法检查
            open_braces = css_code.count("{")
            close_braces = css_code.count("}")
            
            return open_braces == close_braces
            
        except Exception as e:
            logger.error(f"验证CSS语法失败: {e}")
            return False
    
    def validate_js_syntax(self, js_code: str) -> bool:
        """验证JavaScript语法"""
        if not js_code:
            return True
        
        try:
            # 简单的JavaScript语法检查
            open_parens = js_code.count("(")
            close_parens = js_code.count(")")
            open_braces = js_code.count("{")
            close_braces = js_code.count("}")
            
            return (open_parens == close_parens and open_braces == close_braces)
            
        except Exception as e:
            logger.error(f"验证JavaScript语法失败: {e}")
            return False
