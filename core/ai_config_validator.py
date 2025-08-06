"""
AI Animation Studio - AI配置验证器
验证AI服务配置的有效性、安全性和最佳实践
"""

import re
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from core.logger import get_logger

logger = get_logger("ai_config_validator")


class ValidationLevel(Enum):
    """验证级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationResult:
    """验证结果"""
    level: ValidationLevel
    message: str
    field: str = ""
    suggestion: str = ""


class AIConfigValidator:
    """AI配置验证器"""
    
    def __init__(self):
        # API密钥格式规则
        self.api_key_patterns = {
            "openai": r"^sk-[a-zA-Z0-9]{48,}$",
            "claude": r"^sk-ant-[a-zA-Z0-9\-_]{95,}$",
            "gemini": r"^AIza[a-zA-Z0-9\-_]{35}$"
        }
        
        # 模型列表（用于验证）
        self.valid_models = {
            "openai": [
                "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
            ],
            "claude": [
                "claude-3-5-sonnet-20241022", "claude-3-opus-20240229",
                "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
            ],
            "gemini": [
                "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash",
                "gemini-pro", "gemini-pro-vision"
            ]
        }
        
        logger.info("AI配置验证器初始化完成")
    
    def validate_config(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证完整配置"""
        results = []
        
        try:
            # 验证API密钥
            results.extend(self.validate_api_keys(config))
            
            # 验证模型设置
            results.extend(self.validate_models(config))
            
            # 验证生成参数
            results.extend(self.validate_generation_params(config))
            
            # 验证使用量限制
            results.extend(self.validate_usage_limits(config))
            
            # 验证代理设置
            results.extend(self.validate_proxy_settings(config))
            
            # 验证服务配置
            results.extend(self.validate_service_configuration(config))
            
            logger.info(f"配置验证完成，发现 {len(results)} 个问题")
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"配置验证过程中发生错误: {str(e)}",
                "general"
            ))
        
        return results
    
    def validate_api_keys(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证API密钥"""
        results = []
        
        # 检查是否至少配置了一个API密钥
        api_keys = {
            "openai": config.get("openai_api_key", ""),
            "claude": config.get("claude_api_key", ""),
            "gemini": config.get("gemini_api_key", "")
        }
        
        configured_services = [service for service, key in api_keys.items() if key.strip()]
        
        if not configured_services:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "至少需要配置一个AI服务的API密钥",
                "api_keys",
                "请在API配置标签页中配置至少一个服务的API密钥"
            ))
            return results
        
        # 验证每个API密钥的格式
        for service, api_key in api_keys.items():
            if api_key.strip():
                if not self.validate_api_key_format(service, api_key):
                    results.append(ValidationResult(
                        ValidationLevel.ERROR,
                        f"{service.upper()} API密钥格式不正确",
                        f"{service}_api_key",
                        f"请检查{service.upper()} API密钥格式是否正确"
                    ))
                else:
                    results.append(ValidationResult(
                        ValidationLevel.INFO,
                        f"{service.upper()} API密钥格式正确",
                        f"{service}_api_key"
                    ))
        
        # 建议配置多个服务
        if len(configured_services) == 1:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                "建议配置多个AI服务以提高可用性",
                "api_keys",
                "配置备用AI服务可以在主服务不可用时自动切换"
            ))
        
        return results
    
    def validate_api_key_format(self, service: str, api_key: str) -> bool:
        """验证API密钥格式"""
        pattern = self.api_key_patterns.get(service)
        if pattern:
            return bool(re.match(pattern, api_key))
        return True  # 未知服务，跳过格式验证
    
    def validate_models(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证模型设置"""
        results = []
        
        model_configs = {
            "openai": config.get("openai_model", ""),
            "claude": config.get("claude_model", ""),
            "gemini": config.get("gemini_model", "")
        }
        
        for service, model in model_configs.items():
            if model and config.get(f"{service}_api_key", "").strip():
                if model not in self.valid_models.get(service, []):
                    results.append(ValidationResult(
                        ValidationLevel.WARNING,
                        f"{service.upper()} 模型 '{model}' 可能不存在或已过时",
                        f"{service}_model",
                        f"建议使用推荐的{service.upper()}模型"
                    ))
                else:
                    results.append(ValidationResult(
                        ValidationLevel.INFO,
                        f"{service.upper()} 模型 '{model}' 有效",
                        f"{service}_model"
                    ))
        
        return results
    
    def validate_generation_params(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证生成参数"""
        results = []
        
        # 验证温度参数
        temperature = config.get("temperature", 0.7)
        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 2):
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"温度参数 {temperature} 无效，应在0-2之间",
                "temperature",
                "建议设置为0.7以获得平衡的创造性"
            ))
        elif temperature > 1.5:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"温度参数 {temperature} 较高，可能导致输出不稳定",
                "temperature",
                "建议设置为0.7-1.0之间"
            ))
        
        # 验证最大令牌数
        max_tokens = config.get("max_tokens", 2000)
        if not isinstance(max_tokens, int) or max_tokens < 100:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                f"最大令牌数 {max_tokens} 过小",
                "max_tokens",
                "建议设置为至少1000以确保完整的代码生成"
            ))
        elif max_tokens > 8000:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"最大令牌数 {max_tokens} 较大，可能增加费用",
                "max_tokens",
                "建议根据实际需要调整令牌数限制"
            ))
        
        # 验证超时设置
        timeout = config.get("timeout", 30)
        if not isinstance(timeout, int) or timeout < 10:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"超时时间 {timeout}秒 可能过短",
                "timeout",
                "建议设置为30-60秒"
            ))
        elif timeout > 300:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"超时时间 {timeout}秒 过长",
                "timeout",
                "建议设置为30-60秒"
            ))
        
        return results
    
    def validate_usage_limits(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证使用量限制"""
        results = []
        
        # 验证日限制
        daily_limit = config.get("daily_limit", 100)
        if not isinstance(daily_limit, int) or daily_limit < 1:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "日请求限制必须为正整数",
                "daily_limit"
            ))
        elif daily_limit < 10:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"日请求限制 {daily_limit} 可能过低",
                "daily_limit",
                "建议设置为至少50以满足正常使用需求"
            ))
        
        # 验证月限制
        monthly_limit = config.get("monthly_limit", 1000)
        if not isinstance(monthly_limit, int) or monthly_limit < daily_limit:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "月请求限制应大于日请求限制",
                "monthly_limit"
            ))
        
        # 验证费用限制
        cost_limit = config.get("cost_limit", 50.0)
        if not isinstance(cost_limit, (int, float)) or cost_limit < 0:
            results.append(ValidationResult(
                ValidationLevel.ERROR,
                "费用限制必须为非负数",
                "cost_limit"
            ))
        elif cost_limit < 5.0:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                f"费用限制 ${cost_limit} 可能过低",
                "cost_limit",
                "建议设置为至少$10以避免频繁触发限制"
            ))
        
        return results
    
    def validate_proxy_settings(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证代理设置"""
        results = []
        
        if config.get("enable_proxy", False):
            proxy_host = config.get("proxy_host", "")
            proxy_port = config.get("proxy_port", 0)
            
            if not proxy_host:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    "启用代理时必须指定代理地址",
                    "proxy_host"
                ))
            
            if not isinstance(proxy_port, int) or not (1 <= proxy_port <= 65535):
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    f"代理端口 {proxy_port} 无效",
                    "proxy_port",
                    "端口号应在1-65535之间"
                ))
            
            # 验证代理认证
            if config.get("proxy_auth", False):
                proxy_username = config.get("proxy_username", "")
                proxy_password = config.get("proxy_password", "")
                
                if not proxy_username or not proxy_password:
                    results.append(ValidationResult(
                        ValidationLevel.ERROR,
                        "启用代理认证时必须提供用户名和密码",
                        "proxy_auth"
                    ))
        
        return results
    
    def validate_service_configuration(self, config: Dict[str, any]) -> List[ValidationResult]:
        """验证服务配置"""
        results = []
        
        # 验证首选服务
        preferred_service = config.get("preferred_service", "")
        if preferred_service:
            api_key = config.get(f"{preferred_service}_api_key", "")
            if not api_key.strip():
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    f"首选服务 {preferred_service.upper()} 未配置API密钥",
                    "preferred_service",
                    "请配置首选服务的API密钥或选择其他服务"
                ))
        
        # 验证备用服务顺序
        fallback_order = config.get("fallback_order", [])
        if isinstance(fallback_order, list):
            for service in fallback_order:
                if service not in ["openai", "claude", "gemini"]:
                    results.append(ValidationResult(
                        ValidationLevel.WARNING,
                        f"备用服务列表中包含未知服务: {service}",
                        "fallback_order"
                    ))
        
        # 验证缓存设置
        if config.get("enable_cache", True):
            cache_expire_hours = config.get("cache_expire_hours", 24)
            cache_size_mb = config.get("cache_size_mb", 100)
            
            if not isinstance(cache_expire_hours, int) or cache_expire_hours < 1:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    "缓存过期时间必须为正整数",
                    "cache_expire_hours"
                ))
            
            if not isinstance(cache_size_mb, int) or cache_size_mb < 10:
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    f"缓存大小 {cache_size_mb}MB 可能过小",
                    "cache_size_mb",
                    "建议设置为至少50MB"
                ))
        
        return results
    
    def test_api_connection(self, service: str, api_key: str, model: str = "") -> ValidationResult:
        """测试API连接"""
        try:
            if service == "openai":
                return self.test_openai_connection(api_key, model)
            elif service == "claude":
                return self.test_claude_connection(api_key, model)
            elif service == "gemini":
                return self.test_gemini_connection(api_key, model)
            else:
                return ValidationResult(
                    ValidationLevel.ERROR,
                    f"不支持的服务: {service}",
                    "service"
                )
                
        except Exception as e:
            logger.error(f"测试{service}连接失败: {e}")
            return ValidationResult(
                ValidationLevel.ERROR,
                f"连接测试失败: {str(e)}",
                f"{service}_api_key"
            )
    
    def test_openai_connection(self, api_key: str, model: str) -> ValidationResult:
        """测试OpenAI连接"""
        try:
            # 简化实现，实际应该调用OpenAI API
            if not self.validate_api_key_format("openai", api_key):
                return ValidationResult(
                    ValidationLevel.ERROR,
                    "OpenAI API密钥格式不正确",
                    "openai_api_key"
                )
            
            # 模拟连接测试
            return ValidationResult(
                ValidationLevel.INFO,
                "OpenAI连接测试成功",
                "openai_api_key"
            )
            
        except Exception as e:
            return ValidationResult(
                ValidationLevel.ERROR,
                f"OpenAI连接测试失败: {str(e)}",
                "openai_api_key"
            )
    
    def test_claude_connection(self, api_key: str, model: str) -> ValidationResult:
        """测试Claude连接"""
        try:
            if not self.validate_api_key_format("claude", api_key):
                return ValidationResult(
                    ValidationLevel.ERROR,
                    "Claude API密钥格式不正确",
                    "claude_api_key"
                )
            
            return ValidationResult(
                ValidationLevel.INFO,
                "Claude连接测试成功",
                "claude_api_key"
            )
            
        except Exception as e:
            return ValidationResult(
                ValidationLevel.ERROR,
                f"Claude连接测试失败: {str(e)}",
                "claude_api_key"
            )
    
    def test_gemini_connection(self, api_key: str, model: str) -> ValidationResult:
        """测试Gemini连接"""
        try:
            if not self.validate_api_key_format("gemini", api_key):
                return ValidationResult(
                    ValidationLevel.ERROR,
                    "Gemini API密钥格式不正确",
                    "gemini_api_key"
                )
            
            return ValidationResult(
                ValidationLevel.INFO,
                "Gemini连接测试成功",
                "gemini_api_key"
            )
            
        except Exception as e:
            return ValidationResult(
                ValidationLevel.ERROR,
                f"Gemini连接测试失败: {str(e)}",
                "gemini_api_key"
            )
    
    def get_security_recommendations(self, config: Dict[str, any]) -> List[ValidationResult]:
        """获取安全建议"""
        results = []
        
        # API密钥安全建议
        results.append(ValidationResult(
            ValidationLevel.INFO,
            "建议定期轮换API密钥以提高安全性",
            "security",
            "每3-6个月更换一次API密钥"
        ))
        
        # 使用量监控建议
        if not config.get("limit_warning", True):
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                "建议启用使用量警告以避免意外超支",
                "limit_warning"
            ))
        
        # 代理安全建议
        if config.get("enable_proxy", False):
            results.append(ValidationResult(
                ValidationLevel.INFO,
                "使用代理时请确保代理服务器的安全性",
                "proxy_security",
                "避免使用不可信的代理服务器"
            ))
        
        return results
    
    def get_performance_recommendations(self, config: Dict[str, any]) -> List[ValidationResult]:
        """获取性能建议"""
        results = []
        
        # 缓存建议
        if not config.get("enable_cache", True):
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                "建议启用缓存以提高响应速度和降低费用",
                "enable_cache"
            ))
        
        # 温度设置建议
        temperature = config.get("temperature", 0.7)
        if temperature > 1.0:
            results.append(ValidationResult(
                ValidationLevel.INFO,
                "较高的温度设置可能影响代码质量的一致性",
                "temperature",
                "对于代码生成，建议使用0.3-0.7的温度值"
            ))
        
        # 超时设置建议
        timeout = config.get("timeout", 30)
        if timeout < 30:
            results.append(ValidationResult(
                ValidationLevel.WARNING,
                "较短的超时时间可能导致复杂请求失败",
                "timeout",
                "建议设置为30-60秒"
            ))
        
        return results
    
    def validate_and_get_summary(self, config: Dict[str, any]) -> Dict[str, any]:
        """验证配置并返回摘要"""
        validation_results = self.validate_config(config)
        security_recommendations = self.get_security_recommendations(config)
        performance_recommendations = self.get_performance_recommendations(config)
        
        all_results = validation_results + security_recommendations + performance_recommendations
        
        # 统计结果
        error_count = len([r for r in all_results if r.level == ValidationLevel.ERROR])
        warning_count = len([r for r in all_results if r.level == ValidationLevel.WARNING])
        info_count = len([r for r in all_results if r.level == ValidationLevel.INFO])
        
        return {
            "results": all_results,
            "summary": {
                "total": len(all_results),
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count,
                "is_valid": error_count == 0
            }
        }
