"""
AI Animation Studio - 方案智能推荐引擎
基于用户行为、方案质量、相似度等因素提供智能方案推荐
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

from core.enhanced_solution_manager import EnhancedAnimationSolution, SolutionCategory
from core.data_structures import TechStack
from core.logger import get_logger

logger = get_logger("solution_recommendation")


@dataclass
class UserPreference:
    """用户偏好"""
    preferred_categories: Dict[SolutionCategory, float]  # 分类偏好权重
    preferred_tech_stacks: Dict[TechStack, float]        # 技术栈偏好权重
    quality_threshold: float                             # 质量阈值
    complexity_preference: float                         # 复杂度偏好 (0-1)
    novelty_preference: float                           # 新颖性偏好 (0-1)
    
    def __post_init__(self):
        if not hasattr(self, 'preferred_categories') or not self.preferred_categories:
            self.preferred_categories = {category: 1.0 for category in SolutionCategory}
        if not hasattr(self, 'preferred_tech_stacks') or not self.preferred_tech_stacks:
            self.preferred_tech_stacks = {tech: 1.0 for tech in TechStack}


@dataclass
class RecommendationScore:
    """推荐分数"""
    solution_id: str
    total_score: float
    quality_score: float
    preference_score: float
    popularity_score: float
    novelty_score: float
    similarity_score: float
    explanation: str


class UserBehaviorTracker:
    """用户行为跟踪器"""
    
    def __init__(self):
        self.user_actions = []
        self.solution_interactions = defaultdict(list)
        self.category_usage = defaultdict(int)
        self.tech_stack_usage = defaultdict(int)
    
    def track_solution_view(self, solution: EnhancedAnimationSolution):
        """跟踪方案查看"""
        self.user_actions.append({
            "action": "view",
            "solution_id": solution.solution_id,
            "category": solution.category.value,
            "tech_stack": solution.tech_stack.value,
            "timestamp": datetime.now().isoformat()
        })
        
        self.solution_interactions[solution.solution_id].append("view")
        self.category_usage[solution.category] += 1
        self.tech_stack_usage[solution.tech_stack] += 1
    
    def track_solution_apply(self, solution: EnhancedAnimationSolution):
        """跟踪方案应用"""
        self.user_actions.append({
            "action": "apply",
            "solution_id": solution.solution_id,
            "category": solution.category.value,
            "tech_stack": solution.tech_stack.value,
            "timestamp": datetime.now().isoformat()
        })
        
        self.solution_interactions[solution.solution_id].append("apply")
        self.category_usage[solution.category] += 3  # 应用权重更高
        self.tech_stack_usage[solution.tech_stack] += 3
    
    def track_solution_favorite(self, solution: EnhancedAnimationSolution):
        """跟踪方案收藏"""
        self.user_actions.append({
            "action": "favorite",
            "solution_id": solution.solution_id,
            "category": solution.category.value,
            "tech_stack": solution.tech_stack.value,
            "timestamp": datetime.now().isoformat()
        })
        
        self.solution_interactions[solution.solution_id].append("favorite")
        self.category_usage[solution.category] += 2
        self.tech_stack_usage[solution.tech_stack] += 2
    
    def track_solution_rating(self, solution: EnhancedAnimationSolution, rating: float):
        """跟踪方案评分"""
        self.user_actions.append({
            "action": "rate",
            "solution_id": solution.solution_id,
            "category": solution.category.value,
            "tech_stack": solution.tech_stack.value,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        })
        
        # 根据评分调整偏好
        weight = rating / 5.0  # 转换为0-1权重
        self.category_usage[solution.category] += int(weight * 5)
        self.tech_stack_usage[solution.tech_stack] += int(weight * 5)
    
    def get_user_preferences(self) -> UserPreference:
        """获取用户偏好"""
        try:
            # 计算分类偏好
            total_category_usage = sum(self.category_usage.values())
            category_preferences = {}
            
            for category in SolutionCategory:
                usage = self.category_usage.get(category, 0)
                preference = usage / max(1, total_category_usage)
                category_preferences[category] = preference
            
            # 计算技术栈偏好
            total_tech_usage = sum(self.tech_stack_usage.values())
            tech_preferences = {}
            
            for tech in TechStack:
                usage = self.tech_stack_usage.get(tech, 0)
                preference = usage / max(1, total_tech_usage)
                tech_preferences[tech] = preference
            
            # 分析其他偏好
            quality_threshold = self.analyze_quality_threshold()
            complexity_preference = self.analyze_complexity_preference()
            novelty_preference = self.analyze_novelty_preference()
            
            return UserPreference(
                preferred_categories=category_preferences,
                preferred_tech_stacks=tech_preferences,
                quality_threshold=quality_threshold,
                complexity_preference=complexity_preference,
                novelty_preference=novelty_preference
            )
            
        except Exception as e:
            logger.error(f"获取用户偏好失败: {e}")
            return UserPreference(
                preferred_categories={},
                preferred_tech_stacks={},
                quality_threshold=0.6,
                complexity_preference=0.5,
                novelty_preference=0.5
            )
    
    def analyze_quality_threshold(self) -> float:
        """分析质量阈值偏好"""
        # 分析用户应用的方案的平均质量
        applied_actions = [a for a in self.user_actions if a["action"] == "apply"]
        
        if not applied_actions:
            return 0.6  # 默认阈值
        
        # 这里需要获取方案的质量分数，简化实现
        return 0.7  # 假设用户偏好较高质量
    
    def analyze_complexity_preference(self) -> float:
        """分析复杂度偏好"""
        # 基于用户选择的技术栈推断复杂度偏好
        tech_weights = {
            TechStack.CSS_ANIMATION: 0.3,
            TechStack.JAVASCRIPT: 0.5,
            TechStack.GSAP: 0.7,
            TechStack.THREE_JS: 0.9,
            TechStack.SVG_ANIMATION: 0.6
        }
        
        total_weight = 0
        weighted_complexity = 0
        
        for tech, usage in self.tech_stack_usage.items():
            if usage > 0:
                weight = tech_weights.get(tech, 0.5)
                total_weight += usage
                weighted_complexity += weight * usage
        
        return weighted_complexity / max(1, total_weight)
    
    def analyze_novelty_preference(self) -> float:
        """分析新颖性偏好"""
        # 分析用户是否倾向于选择新创建的方案
        recent_actions = [
            a for a in self.user_actions 
            if (datetime.now() - datetime.fromisoformat(a["timestamp"])).days <= 7
        ]
        
        if len(recent_actions) > len(self.user_actions) * 0.7:
            return 0.8  # 偏好新颖性
        else:
            return 0.4  # 偏好稳定性


class SimilarityCalculator:
    """相似度计算器"""
    
    def __init__(self):
        # 特征权重
        self.feature_weights = {
            "category": 0.3,
            "tech_stack": 0.25,
            "complexity": 0.2,
            "style": 0.15,
            "duration": 0.1
        }
    
    def calculate_solution_similarity(self, solution1: EnhancedAnimationSolution,
                                    solution2: EnhancedAnimationSolution) -> float:
        """计算方案相似度"""
        try:
            similarity_scores = {}
            
            # 分类相似度
            similarity_scores["category"] = 1.0 if solution1.category == solution2.category else 0.0
            
            # 技术栈相似度
            similarity_scores["tech_stack"] = 1.0 if solution1.tech_stack == solution2.tech_stack else 0.3
            
            # 复杂度相似度
            complexity1 = solution1.metrics.overall_score
            complexity2 = solution2.metrics.overall_score
            complexity_diff = abs(complexity1 - complexity2) / 100.0
            similarity_scores["complexity"] = 1.0 - complexity_diff
            
            # 风格相似度（基于代码特征）
            similarity_scores["style"] = self.calculate_style_similarity(solution1, solution2)
            
            # 时长相似度（基于CSS动画时长）
            similarity_scores["duration"] = self.calculate_duration_similarity(solution1, solution2)
            
            # 计算加权相似度
            total_similarity = sum(
                score * self.feature_weights[feature]
                for feature, score in similarity_scores.items()
            )
            
            return total_similarity
            
        except Exception as e:
            logger.error(f"计算方案相似度失败: {e}")
            return 0.0
    
    def calculate_style_similarity(self, solution1: EnhancedAnimationSolution,
                                 solution2: EnhancedAnimationSolution) -> float:
        """计算风格相似度"""
        try:
            # 提取CSS特征
            features1 = self.extract_css_features(solution1.css_code)
            features2 = self.extract_css_features(solution2.css_code)
            
            # 计算特征重叠度
            common_features = set(features1).intersection(set(features2))
            total_features = set(features1).union(set(features2))
            
            if not total_features:
                return 0.0
            
            return len(common_features) / len(total_features)
            
        except Exception as e:
            logger.error(f"计算风格相似度失败: {e}")
            return 0.0
    
    def extract_css_features(self, css_code: str) -> List[str]:
        """提取CSS特征"""
        features = []
        
        if not css_code:
            return features
        
        # 提取动画属性
        animation_props = ["transform", "opacity", "scale", "rotate", "translate"]
        for prop in animation_props:
            if prop in css_code.lower():
                features.append(f"uses_{prop}")
        
        # 提取视觉效果
        visual_effects = ["shadow", "gradient", "blur", "brightness"]
        for effect in visual_effects:
            if effect in css_code.lower():
                features.append(f"has_{effect}")
        
        # 提取缓动函数
        if "ease-in" in css_code:
            features.append("easing_ease_in")
        elif "ease-out" in css_code:
            features.append("easing_ease_out")
        elif "ease-in-out" in css_code:
            features.append("easing_ease_in_out")
        
        return features
    
    def calculate_duration_similarity(self, solution1: EnhancedAnimationSolution,
                                    solution2: EnhancedAnimationSolution) -> float:
        """计算时长相似度"""
        try:
            # 提取动画时长
            duration1 = self.extract_animation_duration(solution1.css_code)
            duration2 = self.extract_animation_duration(solution2.css_code)
            
            if duration1 is None or duration2 is None:
                return 0.5  # 无法比较时返回中性值
            
            # 计算时长差异
            duration_diff = abs(duration1 - duration2)
            max_duration = max(duration1, duration2)
            
            if max_duration == 0:
                return 1.0
            
            similarity = 1.0 - (duration_diff / max_duration)
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"计算时长相似度失败: {e}")
            return 0.5
    
    def extract_animation_duration(self, css_code: str) -> Optional[float]:
        """提取动画时长"""
        if not css_code:
            return None
        
        # 查找动画时长
        duration_patterns = [
            r"animation-duration\s*:\s*(\d+(?:\.\d+)?)(s|ms)",
            r"transition-duration\s*:\s*(\d+(?:\.\d+)?)(s|ms)"
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, css_code)
            if matches:
                value, unit = matches[0]
                duration = float(value)
                if unit == "ms":
                    duration /= 1000  # 转换为秒
                return duration
        
        return None


class SolutionRecommendationEngine:
    """方案推荐引擎"""
    
    def __init__(self):
        self.behavior_tracker = UserBehaviorTracker()
        self.similarity_calculator = SimilarityCalculator()
        self.recommendation_cache = {}
        self.cache_expiry = timedelta(hours=1)
        
        logger.info("方案推荐引擎初始化完成")
    
    def get_recommendations(self, solutions: List[EnhancedAnimationSolution],
                          context: Dict[str, Any] = None,
                          limit: int = 10) -> List[RecommendationScore]:
        """获取推荐方案"""
        try:
            # 检查缓存
            cache_key = self.generate_cache_key(solutions, context, limit)
            if cache_key in self.recommendation_cache:
                cached_result, cache_time = self.recommendation_cache[cache_key]
                if datetime.now() - cache_time < self.cache_expiry:
                    return cached_result
            
            # 获取用户偏好
            user_preferences = self.behavior_tracker.get_user_preferences()
            
            # 计算推荐分数
            recommendation_scores = []
            
            for solution in solutions:
                score = self.calculate_recommendation_score(
                    solution, user_preferences, solutions, context
                )
                recommendation_scores.append(score)
            
            # 排序并限制数量
            recommendation_scores.sort(key=lambda x: x.total_score, reverse=True)
            top_recommendations = recommendation_scores[:limit]
            
            # 缓存结果
            self.recommendation_cache[cache_key] = (top_recommendations, datetime.now())
            
            logger.info(f"生成 {len(top_recommendations)} 个推荐方案")
            
            return top_recommendations
            
        except Exception as e:
            logger.error(f"获取推荐方案失败: {e}")
            return []
    
    def calculate_recommendation_score(self, solution: EnhancedAnimationSolution,
                                     user_preferences: UserPreference,
                                     all_solutions: List[EnhancedAnimationSolution],
                                     context: Dict[str, Any] = None) -> RecommendationScore:
        """计算推荐分数"""
        try:
            # 质量分数 (0-1)
            quality_score = solution.metrics.overall_score / 100.0
            
            # 偏好匹配分数 (0-1)
            preference_score = self.calculate_preference_score(solution, user_preferences)
            
            # 流行度分数 (0-1)
            popularity_score = self.calculate_popularity_score(solution, all_solutions)
            
            # 新颖性分数 (0-1)
            novelty_score = self.calculate_novelty_score(solution)
            
            # 相似度分数 (0-1) - 基于上下文
            similarity_score = self.calculate_context_similarity_score(solution, context)
            
            # 权重配置
            weights = {
                "quality": 0.3,
                "preference": 0.25,
                "popularity": 0.2,
                "novelty": 0.15,
                "similarity": 0.1
            }
            
            # 计算总分
            total_score = (
                quality_score * weights["quality"] +
                preference_score * weights["preference"] +
                popularity_score * weights["popularity"] +
                novelty_score * weights["novelty"] +
                similarity_score * weights["similarity"]
            )
            
            # 生成解释
            explanation = self.generate_recommendation_explanation(
                solution, quality_score, preference_score, popularity_score, novelty_score
            )
            
            return RecommendationScore(
                solution_id=solution.solution_id,
                total_score=total_score,
                quality_score=quality_score,
                preference_score=preference_score,
                popularity_score=popularity_score,
                novelty_score=novelty_score,
                similarity_score=similarity_score,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"计算推荐分数失败: {e}")
            return RecommendationScore(
                solution_id=solution.solution_id,
                total_score=0.0,
                quality_score=0.0,
                preference_score=0.0,
                popularity_score=0.0,
                novelty_score=0.0,
                similarity_score=0.0,
                explanation="计算失败"
            )
    
    def calculate_preference_score(self, solution: EnhancedAnimationSolution,
                                 user_preferences: UserPreference) -> float:
        """计算偏好匹配分数"""
        try:
            # 分类偏好
            category_preference = user_preferences.preferred_categories.get(solution.category, 0.5)
            
            # 技术栈偏好
            tech_preference = user_preferences.preferred_tech_stacks.get(solution.tech_stack, 0.5)
            
            # 质量阈值匹配
            quality_match = 1.0 if solution.metrics.overall_score >= user_preferences.quality_threshold * 100 else 0.5
            
            # 复杂度匹配
            solution_complexity = solution.metrics.overall_score / 100.0
            complexity_diff = abs(solution_complexity - user_preferences.complexity_preference)
            complexity_match = 1.0 - complexity_diff
            
            # 加权平均
            preference_score = (
                category_preference * 0.4 +
                tech_preference * 0.3 +
                quality_match * 0.2 +
                complexity_match * 0.1
            )
            
            return preference_score
            
        except Exception as e:
            logger.error(f"计算偏好分数失败: {e}")
            return 0.5
    
    def calculate_popularity_score(self, solution: EnhancedAnimationSolution,
                                 all_solutions: List[EnhancedAnimationSolution]) -> float:
        """计算流行度分数"""
        try:
            if not all_solutions:
                return 0.5
            
            # 使用次数排名
            usage_counts = [s.usage_count for s in all_solutions]
            max_usage = max(usage_counts) if usage_counts else 1
            usage_score = solution.usage_count / max(1, max_usage)
            
            # 评分排名
            ratings = [s.user_rating for s in all_solutions if s.rating_count > 0]
            max_rating = max(ratings) if ratings else 5.0
            rating_score = solution.user_rating / max_rating if solution.rating_count > 0 else 0.5
            
            # 收藏排名
            favorite_counts = [s.favorite_count for s in all_solutions]
            max_favorites = max(favorite_counts) if favorite_counts else 1
            favorite_score = solution.favorite_count / max(1, max_favorites)
            
            # 综合流行度
            popularity_score = (usage_score * 0.5 + rating_score * 0.3 + favorite_score * 0.2)
            
            return popularity_score
            
        except Exception as e:
            logger.error(f"计算流行度分数失败: {e}")
            return 0.5
    
    def calculate_novelty_score(self, solution: EnhancedAnimationSolution) -> float:
        """计算新颖性分数"""
        try:
            # 基于创建时间的新颖性
            now = datetime.now()
            age_days = (now - solution.created_at).days
            
            # 新颖性衰减函数
            if age_days <= 7:
                time_novelty = 1.0
            elif age_days <= 30:
                time_novelty = 0.8
            elif age_days <= 90:
                time_novelty = 0.5
            else:
                time_novelty = 0.2
            
            # 基于使用次数的新颖性（使用少的更新颖）
            usage_novelty = 1.0 / (1.0 + math.log(solution.usage_count + 1))
            
            # 综合新颖性
            novelty_score = (time_novelty * 0.7 + usage_novelty * 0.3)
            
            return novelty_score
            
        except Exception as e:
            logger.error(f"计算新颖性分数失败: {e}")
            return 0.5
    
    def calculate_context_similarity_score(self, solution: EnhancedAnimationSolution,
                                         context: Dict[str, Any] = None) -> float:
        """计算上下文相似度分数"""
        if not context:
            return 0.5
        
        try:
            similarity_score = 0.5  # 基础分数
            
            # 如果上下文中有目标分类
            if "target_category" in context:
                target_category = context["target_category"]
                if solution.category.value == target_category:
                    similarity_score += 0.3
            
            # 如果上下文中有技术栈偏好
            if "preferred_tech" in context:
                preferred_tech = context["preferred_tech"]
                if solution.tech_stack.value == preferred_tech:
                    similarity_score += 0.2
            
            # 如果上下文中有关键词
            if "keywords" in context:
                keywords = context["keywords"]
                description_lower = solution.description.lower()
                
                matching_keywords = sum(1 for kw in keywords if kw.lower() in description_lower)
                keyword_score = matching_keywords / max(1, len(keywords))
                similarity_score += keyword_score * 0.3
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"计算上下文相似度失败: {e}")
            return 0.5
    
    def generate_recommendation_explanation(self, solution: EnhancedAnimationSolution,
                                          quality_score: float, preference_score: float,
                                          popularity_score: float, novelty_score: float) -> str:
        """生成推荐解释"""
        explanations = []
        
        try:
            # 质量解释
            if quality_score > 0.8:
                explanations.append("高质量方案")
            elif quality_score > 0.6:
                explanations.append("质量良好")
            
            # 偏好解释
            if preference_score > 0.7:
                explanations.append("符合您的偏好")
            
            # 流行度解释
            if popularity_score > 0.7:
                explanations.append("用户热门选择")
            elif solution.usage_count > 10:
                explanations.append("经过验证的方案")
            
            # 新颖性解释
            if novelty_score > 0.8:
                explanations.append("新颖创意")
            
            # 技术栈解释
            tech_descriptions = {
                TechStack.CSS_ANIMATION: "纯CSS实现，简单易用",
                TechStack.JAVASCRIPT: "JavaScript增强，功能丰富",
                TechStack.GSAP: "GSAP动画库，专业级效果",
                TechStack.THREE_JS: "3D动画效果，视觉震撼",
                TechStack.SVG_ANIMATION: "矢量动画，缩放无损"
            }
            
            tech_desc = tech_descriptions.get(solution.tech_stack, "")
            if tech_desc:
                explanations.append(tech_desc)
            
            return "，".join(explanations) if explanations else "推荐方案"
            
        except Exception as e:
            logger.error(f"生成推荐解释失败: {e}")
            return "推荐方案"
    
    def generate_cache_key(self, solutions: List[EnhancedAnimationSolution],
                          context: Dict[str, Any], limit: int) -> str:
        """生成缓存键"""
        try:
            # 基于方案ID列表、上下文和限制生成键
            solution_ids = sorted([s.solution_id for s in solutions])
            context_str = json.dumps(context or {}, sort_keys=True)
            
            key_data = f"{len(solution_ids)}_{hash(tuple(solution_ids))}_{hash(context_str)}_{limit}"
            return key_data
            
        except Exception as e:
            logger.error(f"生成缓存键失败: {e}")
            return f"default_{len(solutions)}_{limit}"
    
    def get_similar_solutions(self, target_solution: EnhancedAnimationSolution,
                            candidate_solutions: List[EnhancedAnimationSolution],
                            limit: int = 5) -> List[Tuple[EnhancedAnimationSolution, float]]:
        """获取相似方案"""
        try:
            similarities = []
            
            for candidate in candidate_solutions:
                if candidate.solution_id != target_solution.solution_id:
                    similarity = self.similarity_calculator.calculate_solution_similarity(
                        target_solution, candidate
                    )
                    similarities.append((candidate, similarity))
            
            # 按相似度排序
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"获取相似方案失败: {e}")
            return []
    
    def get_trending_solutions(self, solutions: List[EnhancedAnimationSolution],
                             time_window_days: int = 7,
                             limit: int = 10) -> List[EnhancedAnimationSolution]:
        """获取趋势方案"""
        try:
            # 计算趋势分数
            trending_scores = []
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
            
            for solution in solutions:
                # 基于最近的使用情况计算趋势
                recent_usage = 0
                if solution.updated_at >= cutoff_date:
                    recent_usage = solution.usage_count
                
                # 基于评分增长
                rating_trend = solution.user_rating * solution.rating_count
                
                # 基于收藏增长
                favorite_trend = solution.favorite_count
                
                # 综合趋势分数
                trend_score = recent_usage * 0.5 + rating_trend * 0.3 + favorite_trend * 0.2
                
                trending_scores.append((solution, trend_score))
            
            # 排序并返回
            trending_scores.sort(key=lambda x: x[1], reverse=True)
            trending_solutions = [solution for solution, _ in trending_scores[:limit]]
            
            return trending_solutions
            
        except Exception as e:
            logger.error(f"获取趋势方案失败: {e}")
            return []
    
    def get_personalized_recommendations(self, solutions: List[EnhancedAnimationSolution],
                                       user_id: str = None,
                                       limit: int = 10) -> List[RecommendationScore]:
        """获取个性化推荐"""
        try:
            # 获取用户偏好
            user_preferences = self.behavior_tracker.get_user_preferences()
            
            # 过滤符合偏好的方案
            filtered_solutions = []
            
            for solution in solutions:
                # 质量过滤
                if solution.metrics.overall_score >= user_preferences.quality_threshold * 100:
                    # 分类偏好过滤
                    category_preference = user_preferences.preferred_categories.get(solution.category, 0)
                    if category_preference > 0.3:  # 偏好阈值
                        filtered_solutions.append(solution)
            
            # 如果过滤后方案太少，放宽条件
            if len(filtered_solutions) < limit:
                filtered_solutions = solutions
            
            # 获取推荐
            recommendations = self.get_recommendations(filtered_solutions, limit=limit)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取个性化推荐失败: {e}")
            return []
    
    def update_user_behavior(self, action: str, solution: EnhancedAnimationSolution, **kwargs):
        """更新用户行为"""
        try:
            if action == "view":
                self.behavior_tracker.track_solution_view(solution)
            elif action == "apply":
                self.behavior_tracker.track_solution_apply(solution)
            elif action == "favorite":
                self.behavior_tracker.track_solution_favorite(solution)
            elif action == "rate":
                rating = kwargs.get("rating", 0)
                self.behavior_tracker.track_solution_rating(solution, rating)
            
            # 清除缓存
            self.recommendation_cache.clear()
            
        except Exception as e:
            logger.error(f"更新用户行为失败: {e}")
    
    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """获取推荐统计"""
        try:
            user_preferences = self.behavior_tracker.get_user_preferences()
            
            stats = {
                "total_actions": len(self.behavior_tracker.user_actions),
                "category_preferences": {
                    cat.value: pref for cat, pref in user_preferences.preferred_categories.items()
                },
                "tech_preferences": {
                    tech.value: pref for tech, pref in user_preferences.preferred_tech_stacks.items()
                },
                "quality_threshold": user_preferences.quality_threshold,
                "complexity_preference": user_preferences.complexity_preference,
                "novelty_preference": user_preferences.novelty_preference,
                "cache_size": len(self.recommendation_cache)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取推荐统计失败: {e}")
            return {}
    
    def export_user_preferences(self, file_path: str):
        """导出用户偏好"""
        try:
            preferences = self.behavior_tracker.get_user_preferences()
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "user_actions": self.behavior_tracker.user_actions,
                "category_usage": dict(self.behavior_tracker.category_usage),
                "tech_stack_usage": dict(self.behavior_tracker.tech_stack_usage),
                "preferences": {
                    "categories": {cat.value: pref for cat, pref in preferences.preferred_categories.items()},
                    "tech_stacks": {tech.value: pref for tech, pref in preferences.preferred_tech_stacks.items()},
                    "quality_threshold": preferences.quality_threshold,
                    "complexity_preference": preferences.complexity_preference,
                    "novelty_preference": preferences.novelty_preference
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户偏好已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"导出用户偏好失败: {e}")
    
    def import_user_preferences(self, file_path: str):
        """导入用户偏好"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复用户行为
            if "user_actions" in data:
                self.behavior_tracker.user_actions = data["user_actions"]
            
            if "category_usage" in data:
                self.behavior_tracker.category_usage = defaultdict(int, data["category_usage"])
            
            if "tech_stack_usage" in data:
                self.behavior_tracker.tech_stack_usage = defaultdict(int, data["tech_stack_usage"])
            
            logger.info(f"用户偏好已从 {file_path} 导入")
            
        except Exception as e:
            logger.error(f"导入用户偏好失败: {e}")
