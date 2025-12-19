"""
WebLLM Service Module

This module provides integration with WebLLM for client-side browser-based LLM inference.
WebLLM allows running large language models directly in the browser using WebGPU.

Features:
- Model loading and management
- Inference execution
- Caching and optimization
- Fallback to server-side inference
- Performance monitoring
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types for WebLLM"""
    LLAMA2 = "Llama-2-7b-chat-hf"
    LLAMA2_13B = "Llama-2-13b-chat-hf"
    LLAMA3 = "meta-llama/Llama-3-8b-chat-hf"
    MISTRAL = "mistralai/Mistral-7B-Instruct-v0.2"
    PHI2 = "microsoft/phi-2"
    STABLELM = "stabilityai/stablelm-zephyr-3b"
    VICUNA = "lmsys/vicuna-7b-v1.5"
    REDPAJAMA = "togethercomputer/RedPajama-INCITE-7B-Chat"


class InferenceMode(Enum):
    """Inference execution modes"""
    CLIENT_SIDE = "client_side"
    SERVER_SIDE = "server_side"
    HYBRID = "hybrid"


@dataclass
class ModelConfig:
    """Configuration for WebLLM model"""
    model_id: str
    model_type: ModelType
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9
    top_k: int = 50
    repeat_penalty: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['model_type'] = self.model_type.value
        return data


@dataclass
class InferenceRequest:
    """Inference request model"""
    prompt: str
    model_id: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    mode: str = InferenceMode.CLIENT_SIDE.value
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class InferenceResponse:
    """Inference response model"""
    request_id: str
    text: str
    tokens_generated: int
    inference_time_ms: float
    mode: str
    model_id: str
    success: bool = True
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class WebLLMConfig:
    """WebLLM configuration management"""
    
    # Supported models with their sizes and approximate resource requirements
    SUPPORTED_MODELS = {
        ModelType.LLAMA2.value: {
            "model_id": "meta-llama/Llama-2-7b-chat-hf",
            "size_gb": 13.5,
            "vram_required_gb": 6,
            "recommended": True
        },
        ModelType.LLAMA2_13B.value: {
            "model_id": "meta-llama/Llama-2-13b-chat-hf",
            "size_gb": 26,
            "vram_required_gb": 10,
            "recommended": False
        },
        ModelType.LLAMA3.value: {
            "model_id": "meta-llama/Llama-3-8b-chat-hf",
            "size_gb": 15,
            "vram_required_gb": 8,
            "recommended": True
        },
        ModelType.MISTRAL.value: {
            "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
            "size_gb": 14,
            "vram_required_gb": 6,
            "recommended": True
        },
        ModelType.PHI2.value: {
            "model_id": "microsoft/phi-2",
            "size_gb": 5.5,
            "vram_required_gb": 4,
            "recommended": True
        },
        ModelType.STABLELM.value: {
            "model_id": "stabilityai/stablelm-zephyr-3b",
            "size_gb": 6,
            "vram_required_gb": 3,
            "recommended": True
        }
    }
    
    # Default configuration
    DEFAULT_MODEL = ModelType.MISTRAL.value
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 512
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 50
    
    @classmethod
    def get_model_info(cls, model_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a supported model"""
        return cls.SUPPORTED_MODELS.get(model_type)
    
    @classmethod
    def get_all_models(cls) -> List[Dict[str, Any]]:
        """Get all supported models"""
        return list(cls.SUPPORTED_MODELS.values())
    
    @classmethod
    def get_recommended_models(cls) -> List[Dict[str, Any]]:
        """Get recommended models for browser inference"""
        return [m for m in cls.SUPPORTED_MODELS.values() if m.get("recommended")]


class WebLLMManager:
    """
    Manages WebLLM operations including model loading,
    caching, and inference execution.
    """
    
    def __init__(self):
        """Initialize WebLLM manager"""
        self.logger = logger
        self.loaded_models: Dict[str, Any] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.inference_history: List[InferenceResponse] = []
        self.performance_metrics: Dict[str, Any] = {
            "total_inferences": 0,
            "total_tokens": 0,
            "total_time_ms": 0,
            "average_inference_time": 0,
            "client_side_count": 0,
            "server_side_count": 0
        }
    
    def add_model_config(self, model_type: str, config: ModelConfig) -> None:
        """Add or update model configuration"""
        self.model_configs[model_type] = config
        self.logger.info(f"Model config added for {model_type}")
    
    def get_model_config(self, model_type: str) -> Optional[ModelConfig]:
        """Get model configuration"""
        return self.model_configs.get(model_type)
    
    def get_all_model_configs(self) -> Dict[str, ModelConfig]:
        """Get all model configurations"""
        return self.model_configs.copy()
    
    def validate_inference_request(self, request: InferenceRequest) -> tuple:
        """Validate inference request"""
        if not request.prompt or len(request.prompt.strip()) == 0:
            return False, "Prompt cannot be empty"
        
        if len(request.prompt) > 2000:
            return False, "Prompt exceeds maximum length of 2000 characters"
        
        if request.temperature is not None:
            if not (0 <= request.temperature <= 2):
                return False, "Temperature must be between 0 and 2"
        
        if request.max_tokens is not None:
            if not (1 <= request.max_tokens <= 2048):
                return False, "Max tokens must be between 1 and 2048"
        
        if request.top_p is not None:
            if not (0 < request.top_p <= 1):
                return False, "Top P must be between 0 and 1"
        
        return True, None
    
    def record_inference(self, response: InferenceResponse) -> None:
        """Record inference for metrics tracking"""
        self.inference_history.append(response)
        self.performance_metrics["total_inferences"] += 1
        self.performance_metrics["total_tokens"] += response.tokens_generated
        self.performance_metrics["total_time_ms"] += response.inference_time_ms
        
        if response.mode == InferenceMode.CLIENT_SIDE.value:
            self.performance_metrics["client_side_count"] += 1
        elif response.mode == InferenceMode.SERVER_SIDE.value:
            self.performance_metrics["server_side_count"] += 1
        
        # Update average
        if self.performance_metrics["total_inferences"] > 0:
            self.performance_metrics["average_inference_time"] = (
                self.performance_metrics["total_time_ms"] / 
                self.performance_metrics["total_inferences"]
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    def get_inference_history(self, limit: int = 10) -> List[InferenceResponse]:
        """Get recent inference history"""
        return self.inference_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear inference history and reset metrics"""
        self.inference_history.clear()
        self.performance_metrics = {
            "total_inferences": 0,
            "total_tokens": 0,
            "total_time_ms": 0,
            "average_inference_time": 0,
            "client_side_count": 0,
            "server_side_count": 0
        }


# Global WebLLM manager instance
webllm_manager = WebLLMManager()


def get_webllm_manager() -> WebLLMManager:
    """Get global WebLLM manager instance"""
    return webllm_manager


def initialize_webllm_config(app) -> None:
    """Initialize WebLLM configuration from app config"""
    logger.info("WebLLM configuration initialized")
