"""
AI Animation Studio - 增强方案管理器
提供方案生成、评分、收藏、版本控制、可视化预览等功能
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

from core.data_structures import AnimationSolution, TechStack
from core.logger import get_logger

logger = get_logger("enhanced_solution_manager")


class SolutionQuality(Enum):
    """方案质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


class SolutionCategory(Enum):
    """方案分类"""
    ENTRANCE = "entrance"      # 入场动画
    EXIT = "exit"             # 退场动画
    TRANSITION = "transition"  # 过渡动画
    INTERACTION = "interaction" # 交互动画
    EFFECT = "effect"         # 特效动画
    COMPOSITE = "composite"   # 复合动画


@dataclass
class SolutionMetrics:
    """方案评估指标"""
    quality_score: float = 0.0          # 质量分数 (0-100)
    performance_score: float = 0.0      # 性能分数 (0-100)
    creativity_score: float = 0.0       # 创意分数 (0-100)
    usability_score: float = 0.0        # 易用性分数 (0-100)
    compatibility_score: float = 0.0    # 兼容性分数 (0-100)
    overall_score: float = 0.0          # 综合分数 (0-100)
    
    def calculate_overall_score(self):
        """计算综合分数"""
        weights = {
            "quality": 0.3,
            "performance": 0.25,
            "creativity": 0.2,
            "usability": 0.15,
            "compatibility": 0.1
        }
        
        self.overall_score = (
            self.quality_score * weights["quality"] +
            self.performance_score * weights["performance"] +
            self.creativity_score * weights["creativity"] +
            self.usability_score * weights["usability"] +
            self.compatibility_score * weights["compatibility"]
        )


@dataclass
class EnhancedAnimationSolution:
    """增强动画方案"""
    # 基础信息
    solution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "未命名方案"
    description: str = ""
    category: SolutionCategory = SolutionCategory.EFFECT
    
    # 代码和技术
    html_code: str = ""
    css_code: str = ""
    js_code: str = ""
    tech_stack: TechStack = TechStack.CSS_ANIMATION
    
    # 评估指标
    metrics: SolutionMetrics = field(default_factory=SolutionMetrics)
    quality_level: SolutionQuality = SolutionQuality.AVERAGE
    
    # 用户交互
    user_rating: float = 0.0             # 用户评分 (0-5)
    rating_count: int = 0                # 评分人数
    favorite_count: int = 0              # 收藏次数
    usage_count: int = 0                 # 使用次数
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = "AI生成"
    tags: List[str] = field(default_factory=list)
    
    # 版本控制
    version: str = "1.0.0"
    parent_solution_id: Optional[str] = None
    child_solutions: List[str] = field(default_factory=list)
    
    # 预览数据
    thumbnail_path: Optional[str] = None
    preview_gif_path: Optional[str] = None
    
    def add_user_rating(self, rating: float):
        """添加用户评分"""
        if not 0 <= rating <= 5:
            raise ValueError("评分必须在0-5之间")
        
        total_score = self.user_rating * self.rating_count
        self.rating_count += 1
        self.user_rating = (total_score + rating) / self.rating_count
        self.updated_at = datetime.now()
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def add_to_favorites(self):
        """添加到收藏"""
        self.favorite_count += 1
        self.updated_at = datetime.now()


class SolutionEvaluator:
    """方案评估器"""
    
    def __init__(self):
        # 评估规则
        self.evaluation_rules = {
            "quality": {
                "code_structure": 0.3,      # 代码结构
                "animation_smoothness": 0.3, # 动画流畅度
                "visual_appeal": 0.4        # 视觉吸引力
            },
            "performance": {
                "code_efficiency": 0.4,     # 代码效率
                "resource_usage": 0.3,      # 资源使用
                "browser_compatibility": 0.3 # 浏览器兼容性
            },
            "creativity": {
                "uniqueness": 0.5,          # 独特性
                "innovation": 0.3,          # 创新性
                "artistic_value": 0.2       # 艺术价值
            }
        }
    
    def evaluate_solution(self, solution: EnhancedAnimationSolution) -> SolutionMetrics:
        """评估方案"""
        try:
            metrics = SolutionMetrics()
            
            # 质量评估
            metrics.quality_score = self.evaluate_quality(solution)
            
            # 性能评估
            metrics.performance_score = self.evaluate_performance(solution)
            
            # 创意评估
            metrics.creativity_score = self.evaluate_creativity(solution)
            
            # 易用性评估
            metrics.usability_score = self.evaluate_usability(solution)
            
            # 兼容性评估
            metrics.compatibility_score = self.evaluate_compatibility(solution)
            
            # 计算综合分数
            metrics.calculate_overall_score()
            
            return metrics
            
        except Exception as e:
            logger.error(f"评估方案失败: {e}")
            return SolutionMetrics()
    
    def evaluate_quality(self, solution: EnhancedAnimationSolution) -> float:
        """评估质量"""
        score = 0.0
        
        try:
            # 代码结构评估
            code_structure_score = self.analyze_code_structure(solution.html_code, solution.css_code, solution.js_code)
            score += code_structure_score * self.evaluation_rules["quality"]["code_structure"]
            
            # 动画流畅度评估
            smoothness_score = self.analyze_animation_smoothness(solution.css_code, solution.js_code)
            score += smoothness_score * self.evaluation_rules["quality"]["animation_smoothness"]
            
            # 视觉吸引力评估
            visual_score = self.analyze_visual_appeal(solution.html_code, solution.css_code)
            score += visual_score * self.evaluation_rules["quality"]["visual_appeal"]
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
        
        return min(100, max(0, score))
    
    def evaluate_performance(self, solution: EnhancedAnimationSolution) -> float:
        """评估性能"""
        score = 0.0
        
        try:
            # 代码效率
            efficiency_score = self.analyze_code_efficiency(solution.css_code, solution.js_code)
            score += efficiency_score * self.evaluation_rules["performance"]["code_efficiency"]
            
            # 资源使用
            resource_score = self.analyze_resource_usage(solution.html_code, solution.css_code)
            score += resource_score * self.evaluation_rules["performance"]["resource_usage"]
            
            # 浏览器兼容性
            compatibility_score = self.analyze_browser_compatibility(solution.css_code, solution.js_code)
            score += compatibility_score * self.evaluation_rules["performance"]["browser_compatibility"]
            
        except Exception as e:
            logger.error(f"性能评估失败: {e}")
        
        return min(100, max(0, score))
    
    def evaluate_creativity(self, solution: EnhancedAnimationSolution) -> float:
        """评估创意"""
        score = 50.0  # 基础分数
        
        try:
            # 独特性分析
            uniqueness_score = self.analyze_uniqueness(solution.css_code, solution.js_code)
            score += (uniqueness_score - 50) * self.evaluation_rules["creativity"]["uniqueness"]
            
            # 创新性分析
            innovation_score = self.analyze_innovation(solution.tech_stack, solution.css_code)
            score += (innovation_score - 50) * self.evaluation_rules["creativity"]["innovation"]
            
            # 艺术价值分析
            artistic_score = self.analyze_artistic_value(solution.html_code, solution.css_code)
            score += (artistic_score - 50) * self.evaluation_rules["creativity"]["artistic_value"]
            
        except Exception as e:
            logger.error(f"创意评估失败: {e}")
        
        return min(100, max(0, score))
    
    def evaluate_usability(self, solution: EnhancedAnimationSolution) -> float:
        """评估易用性"""
        score = 70.0  # 基础分数
        
        try:
            # 代码可读性
            if solution.html_code and "<!--" in solution.html_code:
                score += 10  # 有注释加分
            
            # 代码长度合理性
            total_length = len(solution.html_code) + len(solution.css_code) + len(solution.js_code)
            if 500 <= total_length <= 2000:
                score += 10  # 长度适中加分
            elif total_length > 3000:
                score -= 10  # 过长扣分
            
            # 技术栈简单性
            if solution.tech_stack == TechStack.CSS_ANIMATION:
                score += 10  # CSS动画更易用
            elif solution.tech_stack == TechStack.THREE_JS:
                score -= 5   # 3D动画较复杂
            
        except Exception as e:
            logger.error(f"易用性评估失败: {e}")
        
        return min(100, max(0, score))
    
    def evaluate_compatibility(self, solution: EnhancedAnimationSolution) -> float:
        """评估兼容性"""
        score = 80.0  # 基础分数
        
        try:
            # 检查现代CSS特性使用
            modern_features = ["grid", "flexbox", "transform", "transition", "animation"]
            css_code = solution.css_code.lower()
            
            for feature in modern_features:
                if feature in css_code:
                    score += 2  # 使用现代特性加分
            
            # 检查浏览器前缀
            prefixes = ["-webkit-", "-moz-", "-ms-", "-o-"]
            prefix_count = sum(1 for prefix in prefixes if prefix in css_code)
            score += prefix_count * 3  # 有前缀加分
            
            # 检查JavaScript兼容性
            if solution.js_code:
                if "const " in solution.js_code or "let " in solution.js_code:
                    score += 5  # 使用现代JS语法
                if "querySelector" in solution.js_code:
                    score += 3  # 使用标准API
            
        except Exception as e:
            logger.error(f"兼容性评估失败: {e}")
        
        return min(100, max(0, score))
    
    # 具体分析方法
    def analyze_code_structure(self, html: str, css: str, js: str) -> float:
        """分析代码结构"""
        score = 50.0
        
        # HTML结构分析
        if html:
            if "<div" in html and "class=" in html:
                score += 10  # 良好的HTML结构
            if "id=" in html:
                score += 5   # 有ID标识
        
        # CSS结构分析
        if css:
            if "@keyframes" in css:
                score += 15  # 使用关键帧动画
            if "transition" in css:
                score += 10  # 使用过渡效果
            if "{" in css and "}" in css:
                score += 5   # 基本CSS语法
        
        return min(100, score)
    
    def analyze_animation_smoothness(self, css: str, js: str) -> float:
        """分析动画流畅度"""
        score = 60.0
        
        # 检查缓动函数
        easing_functions = ["ease", "ease-in", "ease-out", "ease-in-out", "cubic-bezier"]
        for easing in easing_functions:
            if easing in css.lower():
                score += 8
                break
        
        # 检查帧率优化
        if "transform" in css.lower():
            score += 15  # transform属性性能更好
        
        if "will-change" in css.lower():
            score += 10  # 明确指定will-change
        
        return min(100, score)
    
    def analyze_visual_appeal(self, html: str, css: str) -> float:
        """分析视觉吸引力"""
        score = 50.0
        
        # 颜色使用
        color_keywords = ["color", "background", "gradient", "shadow"]
        for keyword in color_keywords:
            if keyword in css.lower():
                score += 5
        
        # 视觉效果
        effects = ["shadow", "gradient", "opacity", "blur", "scale"]
        for effect in effects:
            if effect in css.lower():
                score += 6
        
        return min(100, score)
    
    def analyze_code_efficiency(self, css: str, js: str) -> float:
        """分析代码效率"""
        score = 70.0
        
        # CSS效率
        if css:
            # 检查是否使用了高性能属性
            efficient_props = ["transform", "opacity", "filter"]
            for prop in efficient_props:
                if prop in css.lower():
                    score += 5
            
            # 检查是否避免了低性能属性
            inefficient_props = ["left", "top", "width", "height"]
            for prop in inefficient_props:
                if f"{prop}:" in css.lower():
                    score -= 3
        
        return min(100, max(0, score))
    
    def analyze_resource_usage(self, html: str, css: str) -> float:
        """分析资源使用"""
        score = 80.0
        
        # 代码大小分析
        total_size = len(html) + len(css)
        
        if total_size < 1000:
            score += 10  # 代码简洁
        elif total_size > 5000:
            score -= 10  # 代码过长
        
        # 外部资源检查
        if "http://" in html or "https://" in html:
            score -= 5   # 依赖外部资源
        
        return min(100, max(0, score))
    
    def analyze_browser_compatibility(self, css: str, js: str) -> float:
        """分析浏览器兼容性"""
        score = 75.0
        
        # 检查CSS兼容性
        if css:
            # 现代CSS特性
            modern_features = ["grid", "flexbox", "calc("]
            for feature in modern_features:
                if feature in css.lower():
                    score += 3
            
            # 浏览器前缀
            if "-webkit-" in css or "-moz-" in css:
                score += 5
        
        return min(100, score)
    
    def analyze_uniqueness(self, css: str, js: str) -> float:
        """分析独特性"""
        score = 50.0
        
        # 检查创新的动画属性组合
        advanced_features = ["clip-path", "mask", "filter", "backdrop-filter"]
        for feature in advanced_features:
            if feature in css.lower():
                score += 10
        
        return min(100, score)
    
    def analyze_innovation(self, tech_stack: TechStack, css: str) -> float:
        """分析创新性"""
        score = 50.0
        
        # 技术栈创新性
        if tech_stack == TechStack.THREE_JS:
            score += 20  # 3D动画更创新
        elif tech_stack == TechStack.GSAP:
            score += 15  # GSAP较创新
        elif tech_stack == TechStack.CSS_ANIMATION:
            score += 5   # CSS动画基础
        
        return min(100, score)
    
    def analyze_artistic_value(self, html: str, css: str) -> float:
        """分析艺术价值"""
        score = 50.0
        
        # 视觉元素丰富度
        visual_elements = ["gradient", "shadow", "border-radius", "opacity"]
        for element in visual_elements:
            if element in css.lower():
                score += 5
        
        return min(100, score)


class SolutionVersionManager:
    """方案版本管理器"""
    
    def __init__(self):
        self.version_history: Dict[str, List[EnhancedAnimationSolution]] = {}
    
    def create_version(self, solution: EnhancedAnimationSolution, 
                      changes_description: str = "") -> str:
        """创建新版本"""
        try:
            # 生成新版本号
            if solution.solution_id not in self.version_history:
                self.version_history[solution.solution_id] = []
                new_version = "1.0.0"
            else:
                versions = self.version_history[solution.solution_id]
                last_version = versions[-1].version if versions else "1.0.0"
                new_version = self.increment_version(last_version)
            
            # 创建新版本的方案
            new_solution = self.copy_solution(solution)
            new_solution.version = new_version
            new_solution.updated_at = datetime.now()
            
            # 添加到版本历史
            self.version_history[solution.solution_id].append(new_solution)
            
            logger.info(f"创建方案版本: {solution.solution_id} v{new_version}")
            
            return new_version
            
        except Exception as e:
            logger.error(f"创建版本失败: {e}")
            return solution.version
    
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
    
    def copy_solution(self, solution: EnhancedAnimationSolution) -> EnhancedAnimationSolution:
        """复制方案"""
        # 创建深拷贝
        solution_dict = asdict(solution)
        solution_dict["solution_id"] = str(uuid.uuid4())  # 新ID
        solution_dict["created_at"] = datetime.now()
        solution_dict["updated_at"] = datetime.now()
        
        return EnhancedAnimationSolution(**solution_dict)
    
    def get_version_history(self, solution_id: str) -> List[EnhancedAnimationSolution]:
        """获取版本历史"""
        return self.version_history.get(solution_id, [])
    
    def rollback_to_version(self, solution_id: str, version: str) -> Optional[EnhancedAnimationSolution]:
        """回滚到指定版本"""
        try:
            versions = self.version_history.get(solution_id, [])
            for solution in versions:
                if solution.version == version:
                    return self.copy_solution(solution)
            
            return None
            
        except Exception as e:
            logger.error(f"回滚版本失败: {e}")
            return None


class EnhancedSolutionManager:
    """增强方案管理器"""
    
    def __init__(self, storage_path: str = "solutions"):
        self.storage_path = storage_path
        self.solutions: Dict[str, EnhancedAnimationSolution] = {}
        self.favorites: List[str] = []
        self.evaluator = SolutionEvaluator()
        self.version_manager = SolutionVersionManager()
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 加载现有方案
        self.load_solutions()
        
        logger.info(f"增强方案管理器初始化完成，加载了 {len(self.solutions)} 个方案")
    
    def add_solution(self, solution: EnhancedAnimationSolution, 
                    auto_evaluate: bool = True) -> str:
        """添加方案"""
        try:
            # 自动评估
            if auto_evaluate:
                solution.metrics = self.evaluator.evaluate_solution(solution)
                solution.quality_level = self.determine_quality_level(solution.metrics.overall_score)
            
            # 存储方案
            self.solutions[solution.solution_id] = solution
            
            # 保存到文件
            self.save_solution(solution)
            
            logger.info(f"添加方案: {solution.name} (ID: {solution.solution_id})")
            
            return solution.solution_id
            
        except Exception as e:
            logger.error(f"添加方案失败: {e}")
            return ""
    
    def determine_quality_level(self, overall_score: float) -> SolutionQuality:
        """确定质量等级"""
        if overall_score >= 85:
            return SolutionQuality.EXCELLENT
        elif overall_score >= 70:
            return SolutionQuality.GOOD
        elif overall_score >= 50:
            return SolutionQuality.AVERAGE
        else:
            return SolutionQuality.POOR
    
    def get_solutions_by_category(self, category: SolutionCategory) -> List[EnhancedAnimationSolution]:
        """按分类获取方案"""
        return [s for s in self.solutions.values() if s.category == category]
    
    def get_solutions_by_quality(self, quality: SolutionQuality) -> List[EnhancedAnimationSolution]:
        """按质量获取方案"""
        return [s for s in self.solutions.values() if s.quality_level == quality]
    
    def get_top_rated_solutions(self, limit: int = 10) -> List[EnhancedAnimationSolution]:
        """获取评分最高的方案"""
        solutions = list(self.solutions.values())
        solutions.sort(key=lambda x: x.user_rating, reverse=True)
        return solutions[:limit]
    
    def get_most_used_solutions(self, limit: int = 10) -> List[EnhancedAnimationSolution]:
        """获取使用最多的方案"""
        solutions = list(self.solutions.values())
        solutions.sort(key=lambda x: x.usage_count, reverse=True)
        return solutions[:limit]
    
    def search_solutions(self, query: str, filters: Dict[str, Any] = None) -> List[EnhancedAnimationSolution]:
        """搜索方案"""
        results = []
        query_lower = query.lower()
        
        try:
            for solution in self.solutions.values():
                # 文本匹配
                if (query_lower in solution.name.lower() or
                    query_lower in solution.description.lower() or
                    any(query_lower in tag.lower() for tag in solution.tags)):
                    
                    # 应用过滤器
                    if self.apply_filters(solution, filters):
                        results.append(solution)
            
            # 按相关性排序
            results.sort(key=lambda x: self.calculate_relevance(x, query), reverse=True)
            
        except Exception as e:
            logger.error(f"搜索方案失败: {e}")
        
        return results
    
    def apply_filters(self, solution: EnhancedAnimationSolution, filters: Dict[str, Any]) -> bool:
        """应用过滤器"""
        if not filters:
            return True
        
        try:
            # 分类过滤
            if "category" in filters and solution.category != filters["category"]:
                return False
            
            # 技术栈过滤
            if "tech_stack" in filters and solution.tech_stack != filters["tech_stack"]:
                return False
            
            # 质量过滤
            if "min_quality" in filters and solution.metrics.overall_score < filters["min_quality"]:
                return False
            
            # 评分过滤
            if "min_rating" in filters and solution.user_rating < filters["min_rating"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"应用过滤器失败: {e}")
            return True
    
    def calculate_relevance(self, solution: EnhancedAnimationSolution, query: str) -> float:
        """计算相关性分数"""
        score = 0.0
        query_lower = query.lower()
        
        # 名称匹配
        if query_lower in solution.name.lower():
            score += 10
        
        # 描述匹配
        if query_lower in solution.description.lower():
            score += 5
        
        # 标签匹配
        for tag in solution.tags:
            if query_lower in tag.lower():
                score += 3
        
        # 质量加权
        score *= (1 + solution.metrics.overall_score / 100)
        
        return score
    
    def add_to_favorites(self, solution_id: str) -> bool:
        """添加到收藏"""
        try:
            if solution_id in self.solutions and solution_id not in self.favorites:
                self.favorites.append(solution_id)
                self.solutions[solution_id].add_to_favorites()
                self.save_favorites()
                
                logger.info(f"方案已添加到收藏: {solution_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"添加收藏失败: {e}")
            return False
    
    def remove_from_favorites(self, solution_id: str) -> bool:
        """从收藏中移除"""
        try:
            if solution_id in self.favorites:
                self.favorites.remove(solution_id)
                if solution_id in self.solutions:
                    self.solutions[solution_id].favorite_count = max(0, self.solutions[solution_id].favorite_count - 1)
                self.save_favorites()
                
                logger.info(f"方案已从收藏中移除: {solution_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"移除收藏失败: {e}")
            return False
    
    def get_favorite_solutions(self) -> List[EnhancedAnimationSolution]:
        """获取收藏的方案"""
        return [self.solutions[sid] for sid in self.favorites if sid in self.solutions]
    
    def save_solution(self, solution: EnhancedAnimationSolution):
        """保存方案到文件"""
        try:
            file_path = os.path.join(self.storage_path, f"{solution.solution_id}.json")
            
            # 转换为字典
            solution_dict = asdict(solution)
            
            # 处理datetime对象
            solution_dict["created_at"] = solution.created_at.isoformat()
            solution_dict["updated_at"] = solution.updated_at.isoformat()
            
            # 处理枚举
            solution_dict["category"] = solution.category.value
            solution_dict["quality_level"] = solution.quality_level.value
            solution_dict["tech_stack"] = solution.tech_stack.value
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(solution_dict, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存方案失败: {e}")
    
    def load_solutions(self):
        """加载所有方案"""
        try:
            if not os.path.exists(self.storage_path):
                return
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json') and filename != 'favorites.json':
                    file_path = os.path.join(self.storage_path, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            solution_dict = json.load(f)
                        
                        # 转换枚举和datetime
                        solution_dict["category"] = SolutionCategory(solution_dict.get("category", "effect"))
                        solution_dict["quality_level"] = SolutionQuality(solution_dict.get("quality_level", "average"))
                        solution_dict["tech_stack"] = TechStack(solution_dict.get("tech_stack", "css_animation"))
                        
                        if "created_at" in solution_dict:
                            solution_dict["created_at"] = datetime.fromisoformat(solution_dict["created_at"])
                        if "updated_at" in solution_dict:
                            solution_dict["updated_at"] = datetime.fromisoformat(solution_dict["updated_at"])
                        
                        # 创建方案对象
                        solution = EnhancedAnimationSolution(**solution_dict)
                        self.solutions[solution.solution_id] = solution
                        
                    except Exception as e:
                        logger.warning(f"加载方案文件失败 {filename}: {e}")
            
            # 加载收藏列表
            self.load_favorites()
            
            logger.info(f"成功加载 {len(self.solutions)} 个方案")
            
        except Exception as e:
            logger.error(f"加载方案失败: {e}")
    
    def save_favorites(self):
        """保存收藏列表"""
        try:
            favorites_path = os.path.join(self.storage_path, "favorites.json")
            with open(favorites_path, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存收藏列表失败: {e}")
    
    def load_favorites(self):
        """加载收藏列表"""
        try:
            favorites_path = os.path.join(self.storage_path, "favorites.json")
            if os.path.exists(favorites_path):
                with open(favorites_path, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
                    
        except Exception as e:
            logger.error(f"加载收藏列表失败: {e}")
            self.favorites = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            if not self.solutions:
                return {}
            
            solutions = list(self.solutions.values())
            
            # 基本统计
            total_solutions = len(solutions)
            total_favorites = len(self.favorites)
            total_usage = sum(s.usage_count for s in solutions)
            
            # 质量分布
            quality_distribution = {}
            for quality in SolutionQuality:
                count = sum(1 for s in solutions if s.quality_level == quality)
                quality_distribution[quality.value] = count
            
            # 分类分布
            category_distribution = {}
            for category in SolutionCategory:
                count = sum(1 for s in solutions if s.category == category)
                category_distribution[category.value] = count
            
            # 技术栈分布
            tech_distribution = {}
            for tech in TechStack:
                count = sum(1 for s in solutions if s.tech_stack == tech)
                tech_distribution[tech.value] = count
            
            # 平均分数
            avg_quality = sum(s.metrics.overall_score for s in solutions) / total_solutions
            avg_rating = sum(s.user_rating for s in solutions if s.rating_count > 0) / max(1, sum(1 for s in solutions if s.rating_count > 0))
            
            return {
                "total_solutions": total_solutions,
                "total_favorites": total_favorites,
                "total_usage": total_usage,
                "quality_distribution": quality_distribution,
                "category_distribution": category_distribution,
                "tech_distribution": tech_distribution,
                "average_quality": avg_quality,
                "average_rating": avg_rating,
                "top_solution": max(solutions, key=lambda x: x.metrics.overall_score) if solutions else None
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
