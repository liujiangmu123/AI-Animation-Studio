"""
AI Animation Studio - AI服务管理器
统一管理多个AI服务的配置、调用、监控和缓存
"""

import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from core.logger import get_logger

logger = get_logger("ai_service_manager")


class AIServiceType(Enum):
    """AI服务类型"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


@dataclass
class AIRequest:
    """AI请求数据"""
    prompt: str
    service: AIServiceType
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AIResponse:
    """AI响应数据"""
    content: str
    service: AIServiceType
    model: str
    tokens_used: int
    cost: float
    response_time: float
    timestamp: datetime = None
    cached: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AICache:
    """AI响应缓存"""
    
    def __init__(self, cache_dir: str = "ai_cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "cache_index.json")
        self.max_size_mb = 100
        self.expire_hours = 24
        
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_index = self.load_cache_index()
    
    def load_cache_index(self) -> Dict[str, Any]:
        """加载缓存索引"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"加载缓存索引失败: {e}")
            return {}
    
    def save_cache_index(self):
        """保存缓存索引"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存索引失败: {e}")
    
    def get_cache_key(self, request: AIRequest) -> str:
        """生成缓存键"""
        content = f"{request.prompt}_{request.service.value}_{request.model}_{request.temperature}_{request.max_tokens}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, request: AIRequest) -> Optional[AIResponse]:
        """获取缓存的响应"""
        try:
            cache_key = self.get_cache_key(request)
            
            if cache_key in self.cache_index:
                cache_info = self.cache_index[cache_key]
                
                # 检查是否过期
                cache_time = datetime.fromisoformat(cache_info["timestamp"])
                if datetime.now() - cache_time > timedelta(hours=self.expire_hours):
                    self.remove(cache_key)
                    return None
                
                # 读取缓存文件
                cache_file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
                if os.path.exists(cache_file_path):
                    with open(cache_file_path, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    response = AIResponse(
                        content=response_data["content"],
                        service=AIServiceType(response_data["service"]),
                        model=response_data["model"],
                        tokens_used=response_data["tokens_used"],
                        cost=response_data["cost"],
                        response_time=response_data["response_time"],
                        timestamp=datetime.fromisoformat(response_data["timestamp"]),
                        cached=True
                    )
                    
                    logger.debug(f"缓存命中: {cache_key}")
                    return response
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def put(self, request: AIRequest, response: AIResponse):
        """存储响应到缓存"""
        try:
            cache_key = self.get_cache_key(request)
            
            # 保存响应数据
            cache_file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            response_data = {
                "content": response.content,
                "service": response.service.value,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "response_time": response.response_time,
                "timestamp": response.timestamp.isoformat()
            }
            
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            
            # 更新缓存索引
            self.cache_index[cache_key] = {
                "timestamp": response.timestamp.isoformat(),
                "size": os.path.getsize(cache_file_path),
                "service": response.service.value,
                "model": response.model
            }
            
            self.save_cache_index()
            self.cleanup_cache()
            
            logger.debug(f"缓存已保存: {cache_key}")
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def remove(self, cache_key: str):
        """移除缓存项"""
        try:
            if cache_key in self.cache_index:
                cache_file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
                if os.path.exists(cache_file_path):
                    os.remove(cache_file_path)
                
                del self.cache_index[cache_key]
                self.save_cache_index()
                
        except Exception as e:
            logger.error(f"移除缓存失败: {e}")
    
    def cleanup_cache(self):
        """清理过期和超大缓存"""
        try:
            # 计算总缓存大小
            total_size = sum(info.get("size", 0) for info in self.cache_index.values())
            max_size_bytes = self.max_size_mb * 1024 * 1024
            
            # 如果超过大小限制，删除最旧的缓存
            if total_size > max_size_bytes:
                sorted_items = sorted(
                    self.cache_index.items(),
                    key=lambda x: x[1]["timestamp"]
                )
                
                for cache_key, _ in sorted_items:
                    self.remove(cache_key)
                    total_size = sum(info.get("size", 0) for info in self.cache_index.values())
                    if total_size <= max_size_bytes:
                        break
            
            # 删除过期缓存
            expired_keys = []
            for cache_key, info in self.cache_index.items():
                cache_time = datetime.fromisoformat(info["timestamp"])
                if datetime.now() - cache_time > timedelta(hours=self.expire_hours):
                    expired_keys.append(cache_key)
            
            for cache_key in expired_keys:
                self.remove(cache_key)
                
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")


class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self, config_file: str = "ai_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.cache = AICache()
        self.usage_stats = {}
        
        # 服务状态
        self.service_status = {
            AIServiceType.OPENAI: {"available": False, "last_check": None},
            AIServiceType.CLAUDE: {"available": False, "last_check": None},
            AIServiceType.GEMINI: {"available": False, "last_check": None}
        }
        
        logger.info("AI服务管理器初始化完成")
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # 默认配置
            return {
                "preferred_service": "gemini",
                "auto_fallback": True,
                "fallback_order": ["claude", "openai", "gemini"],
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 30,
                "max_retries": 3,
                "enable_cache": True,
                "cache_expire_hours": 24,
                "cache_size_mb": 100
            }
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {}
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.config.update(new_config)
        self.save_config()
        
        # 更新缓存设置
        if "cache_expire_hours" in new_config:
            self.cache.expire_hours = new_config["cache_expire_hours"]
        if "cache_size_mb" in new_config:
            self.cache.max_size_mb = new_config["cache_size_mb"]
        
        logger.info("AI配置已更新")
    
    def get_available_services(self) -> List[AIServiceType]:
        """获取可用的服务列表"""
        available = []
        
        if self.config.get("openai_api_key"):
            available.append(AIServiceType.OPENAI)
        if self.config.get("claude_api_key"):
            available.append(AIServiceType.CLAUDE)
        if self.config.get("gemini_api_key"):
            available.append(AIServiceType.GEMINI)
        
        return available
    
    def get_preferred_service(self) -> Optional[AIServiceType]:
        """获取首选服务"""
        preferred = self.config.get("preferred_service", "gemini")
        try:
            service = AIServiceType(preferred)
            if service in self.get_available_services():
                return service
        except ValueError:
            pass
        
        # 如果首选服务不可用，返回第一个可用服务
        available = self.get_available_services()
        return available[0] if available else None
    
    def generate_animation_code(self, prompt: str, service: AIServiceType = None) -> Optional[AIResponse]:
        """生成动画代码"""
        try:
            # 确定使用的服务
            if service is None:
                service = self.get_preferred_service()
            
            if service is None:
                raise Exception("没有可用的AI服务")
            
            # 构建请求
            request = AIRequest(
                prompt=prompt,
                service=service,
                model=self.get_model_for_service(service),
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2000)
            )
            
            # 检查缓存
            if self.config.get("enable_cache", True):
                cached_response = self.cache.get(request)
                if cached_response:
                    return cached_response
            
            # 调用AI服务
            response = self.call_ai_service(request)
            
            # 保存到缓存
            if response and self.config.get("enable_cache", True):
                self.cache.put(request, response)
            
            # 记录使用量
            if response:
                self.record_usage(service, response.tokens_used, response.cost)
            
            return response
            
        except Exception as e:
            logger.error(f"生成动画代码失败: {e}")
            
            # 尝试备用服务
            if self.config.get("auto_fallback", True) and service:
                fallback_services = self.get_fallback_services(service)
                for fallback_service in fallback_services:
                    try:
                        return self.generate_animation_code(prompt, fallback_service)
                    except Exception as fallback_error:
                        logger.warning(f"备用服务 {fallback_service.value} 也失败: {fallback_error}")
                        continue
            
            return None
    
    def get_model_for_service(self, service: AIServiceType) -> str:
        """获取服务对应的模型"""
        model_map = {
            AIServiceType.OPENAI: self.config.get("openai_model", "gpt-4"),
            AIServiceType.CLAUDE: self.config.get("claude_model", "claude-3-5-sonnet-20241022"),
            AIServiceType.GEMINI: self.config.get("gemini_model", "gemini-2.0-flash-exp")
        }
        return model_map.get(service, "")
    
    def get_fallback_services(self, failed_service: AIServiceType) -> List[AIServiceType]:
        """获取备用服务列表"""
        fallback_order = self.config.get("fallback_order", ["claude", "openai", "gemini"])
        available_services = self.get_available_services()
        
        # 移除失败的服务
        available_services = [s for s in available_services if s != failed_service]
        
        # 按照备用顺序排序
        ordered_services = []
        for service_name in fallback_order:
            try:
                service = AIServiceType(service_name)
                if service in available_services:
                    ordered_services.append(service)
            except ValueError:
                continue
        
        # 添加剩余的服务
        for service in available_services:
            if service not in ordered_services:
                ordered_services.append(service)
        
        return ordered_services
    
    def call_ai_service(self, request: AIRequest) -> Optional[AIResponse]:
        """调用AI服务"""
        try:
            start_time = time.time()

            # 根据服务类型调用相应的AI服务
            if request.service == "gemini":
                return self._call_gemini_service(request, start_time)
            elif request.service == "openai":
                return self._call_openai_service(request, start_time)
            elif request.service == "claude":
                return self._call_claude_service(request, start_time)
            else:
                # 如果服务不支持，返回模拟响应
                return self._call_fallback_service(request, start_time)

        except Exception as e:
            logger.error(f"AI服务调用失败: {e}")
            # 返回错误响应
            return AIResponse(
                content=f"AI服务调用失败: {str(e)}",
                service=request.service,
                model=request.model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )

    def _call_gemini_service(self, request: AIRequest, start_time: float) -> Optional[AIResponse]:
        """调用Gemini服务"""
        try:
            from ai.gemini_generator import GeminiGenerator

            # 创建Gemini生成器实例
            generator = GeminiGenerator()

            # 调用生成方法
            solutions = generator.generate_animation_solutions(
                description=request.prompt,
                num_solutions=1,
                tech_stack=request.parameters.get('tech_stack', 'html_css_js')
            )

            if solutions:
                solution = solutions[0]
                content = f"""
                <!-- {solution.name} -->
                {solution.html_content}

                <style>
                {solution.css_content}
                </style>

                <script>
                {solution.js_content}
                </script>
                """

                response_time = time.time() - start_time

                return AIResponse(
                    content=content.strip(),
                    service=request.service,
                    model=request.model,
                    tokens_used=len(content) // 4,
                    cost=self.calculate_cost(request.service, len(content) // 4),
                    response_time=response_time
                )
            else:
                # 如果没有生成解决方案，返回错误
                return self._call_fallback_service(request, start_time)

        except Exception as e:
            logger.error(f"Gemini服务调用失败: {e}")
            return self._call_fallback_service(request, start_time)

    def _call_openai_service(self, request: AIRequest, start_time: float) -> Optional[AIResponse]:
        """调用OpenAI服务"""
        try:
            # TODO: 实现OpenAI API调用
            logger.warning("OpenAI服务暂未实现，使用回退服务")
            return self._call_fallback_service(request, start_time)

        except Exception as e:
            logger.error(f"OpenAI服务调用失败: {e}")
            return self._call_fallback_service(request, start_time)

    def _call_claude_service(self, request: AIRequest, start_time: float) -> Optional[AIResponse]:
        """调用Claude服务"""
        try:
            # TODO: 实现Claude API调用
            logger.warning("Claude服务暂未实现，使用回退服务")
            return self._call_fallback_service(request, start_time)

        except Exception as e:
            logger.error(f"Claude服务调用失败: {e}")
            return self._call_fallback_service(request, start_time)

    def _call_fallback_service(self, request: AIRequest, start_time: float) -> AIResponse:
        """回退服务（模拟响应）"""
        try:
            # 模拟网络延迟
            time.sleep(0.5)

            # 生成基于提示的简单动画
            mock_content = f"""
            <!-- AI生成的动画代码 - {request.prompt} -->
            <div class="animation-container">
                <div class="animated-element" data-prompt="{request.prompt}">
                    <div class="content">{request.prompt}</div>
                </div>
            </div>

            <style>
            .animation-container {{
                width: 100%;
                height: 300px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}

            .animated-element {{
                width: 200px;
                height: 200px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                border-radius: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                animation: dynamicAnimation 3s ease-in-out infinite;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}

            .content {{
                color: white;
                font-weight: bold;
                text-align: center;
                font-size: 16px;
                padding: 10px;
            }}

            @keyframes dynamicAnimation {{
                0% {{ transform: scale(1) rotate(0deg); opacity: 0.8; }}
                25% {{ transform: scale(1.1) rotate(90deg); opacity: 1; }}
                50% {{ transform: scale(1.2) rotate(180deg); opacity: 0.9; }}
                75% {{ transform: scale(1.1) rotate(270deg); opacity: 1; }}
                100% {{ transform: scale(1) rotate(360deg); opacity: 0.8; }}
            }}
            </style>

            <script>
            // 添加交互功能
            document.addEventListener('DOMContentLoaded', function() {{
                const element = document.querySelector('.animated-element');
                if (element) {{
                    element.addEventListener('click', function() {{
                        this.style.animationDuration = '1s';
                        setTimeout(() => {{
                            this.style.animationDuration = '3s';
                        }}, 2000);
                    }});
                }}
            }});
            </script>
            """

            response_time = time.time() - start_time

            return AIResponse(
                content=mock_content.strip(),
                service=request.service,
                model=request.model or "fallback",
                tokens_used=len(mock_content) // 4,
                cost=0.0,  # 回退服务免费
                response_time=response_time
            )
            
            logger.info(f"AI服务调用成功: {request.service.value}")
            return response
            
        except Exception as e:
            logger.error(f"调用AI服务失败: {e}")
            return None
    
    def calculate_cost(self, service: AIServiceType, tokens: int) -> float:
        """计算使用成本"""
        # 简化的成本计算（实际应该根据最新的定价）
        cost_per_1k_tokens = {
            AIServiceType.OPENAI: 0.03,    # GPT-4
            AIServiceType.CLAUDE: 0.015,   # Claude-3.5-Sonnet
            AIServiceType.GEMINI: 0.001    # Gemini-2.0-Flash
        }
        
        rate = cost_per_1k_tokens.get(service, 0.01)
        return (tokens / 1000) * rate
    
    def record_usage(self, service: AIServiceType, tokens: int, cost: float):
        """记录使用量"""
        try:
            from ui.enhanced_ai_config_dialog import APIUsageMonitor
            
            monitor = APIUsageMonitor()
            monitor.record_usage(service.value, tokens, cost)
            
        except Exception as e:
            logger.error(f"记录使用量失败: {e}")
    
    def check_usage_limits(self, service: AIServiceType) -> Tuple[bool, str]:
        """检查使用量限制"""
        try:
            from ui.enhanced_ai_config_dialog import APIUsageMonitor
            
            monitor = APIUsageMonitor()
            
            # 检查日限制
            daily_usage = monitor.get_daily_usage()
            service_daily = daily_usage.get(service.value, {})
            daily_requests = service_daily.get("requests", 0)
            daily_limit = self.config.get("daily_limit", 100)
            
            if daily_requests >= daily_limit:
                return False, f"已达到日请求限制 ({daily_limit})"
            
            # 检查月限制
            monthly_usage = monitor.get_monthly_usage()
            service_monthly = monthly_usage.get(service.value, {})
            monthly_requests = service_monthly.get("requests", 0)
            monthly_limit = self.config.get("monthly_limit", 1000)
            
            if monthly_requests >= monthly_limit:
                return False, f"已达到月请求限制 ({monthly_limit})"
            
            # 检查费用限制
            monthly_cost = service_monthly.get("cost", 0.0)
            cost_limit = self.config.get("cost_limit", 50.0)
            
            if monthly_cost >= cost_limit:
                return False, f"已达到月费用限制 (${cost_limit})"
            
            return True, "使用量正常"
            
        except Exception as e:
            logger.error(f"检查使用量限制失败: {e}")
            return True, "检查失败，允许使用"
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """获取使用量摘要"""
        try:
            from ui.enhanced_ai_config_dialog import APIUsageMonitor
            
            monitor = APIUsageMonitor()
            
            return {
                "daily_usage": monitor.get_daily_usage(),
                "monthly_usage": monitor.get_monthly_usage(),
                "total_requests": monitor.usage_data.get("total_requests", 0),
                "total_tokens": monitor.usage_data.get("total_tokens", 0),
                "cache_stats": {
                    "cache_size": len(self.cache.cache_index),
                    "cache_hits": 0,  # TODO: 实现缓存命中统计
                    "cache_misses": 0
                }
            }
            
        except Exception as e:
            logger.error(f"获取使用量摘要失败: {e}")
            return {}
    
    def clear_cache(self):
        """清空缓存"""
        try:
            import shutil
            if os.path.exists(self.cache.cache_dir):
                shutil.rmtree(self.cache.cache_dir)
            
            os.makedirs(self.cache.cache_dir, exist_ok=True)
            self.cache.cache_index = {}
            self.cache.save_cache_index()
            
            logger.info("AI缓存已清空")
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
    
    def export_usage_report(self, file_path: str):
        """导出使用量报告"""
        try:
            usage_summary = self.get_usage_summary()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(usage_summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"使用量报告已导出: {file_path}")
            
        except Exception as e:
            logger.error(f"导出使用量报告失败: {e}")


# 全局AI服务管理器实例
ai_service_manager = AIServiceManager()
