"""
WebLLM Flask Blueprint

Provides REST API endpoints for WebLLM client-side inference,
model management, and performance monitoring.
"""

import logging
import json
import uuid
import time
from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import os
import requests

from app.services.webllm_service import (
    WebLLMManager,
    WebLLMConfig,
    ModelConfig,
    ModelType,
    InferenceRequest,
    InferenceResponse,
    InferenceMode,
    get_webllm_manager
)

webllm_blueprint = Blueprint("webllm", __name__, template_folder="templates", url_prefix="/webllm")
logger = logging.getLogger(__name__)

# Initialize WebLLM manager
manager = get_webllm_manager()

# LLM Service Configuration
LLM_SERVICE_URL = os.getenv('LLM_SERVICE_URL', 'http://127.0.0.1:5000/query/')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"


def get_llm_response(prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> tuple:
    """
    Get response from actual LLM service.
    
    Returns: (response_text, tokens_used, inference_time_ms)
    """
    try:
        # Try Ollama first (local inference)
        start_time = time.time()
        
        ollama_payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Provide concise, informative responses."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(
            OLLAMA_CHAT_ENDPOINT,
            json=ollama_payload,
            timeout=120
        )
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('message', {}).get('content', '').strip()
            
            # Estimate token count (rough approximation: 1 token ≈ 4 characters)
            tokens_used = len(response_text.split()) * 1.3
            
            logger.info(f"Ollama inference successful: {len(response_text)} chars in {inference_time:.1f}ms")
            return response_text, int(tokens_used), inference_time
        else:
            logger.warning(f"Ollama returned status {response.status_code}")
            
    except requests.exceptions.Timeout:
        logger.warning("Ollama request timed out")
    except requests.exceptions.ConnectionError:
        logger.warning(f"Could not connect to Ollama at {OLLAMA_CHAT_ENDPOINT}")
    except Exception as e:
        logger.warning(f"Error calling Ollama: {e}")
    
    # Fallback to main LLM service
    try:
        start_time = time.time()
        
        json_message = {
            "query": prompt,
            "message_history": [],
            "query_type": "general"
        }
        
        response = requests.post(
            LLM_SERVICE_URL,
            data=json.dumps(json_message),
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        inference_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get('response', '').strip()
            tokens_used = len(response_text.split()) * 1.3
            
            logger.info(f"Main LLM service inference successful: {len(response_text)} chars in {inference_time:.1f}ms")
            return response_text, int(tokens_used), inference_time
            
    except Exception as e:
        logger.warning(f"Main LLM service failed: {e}")
    
    # Fallback response if all services fail
    logger.warning("All LLM services failed, using fallback response")
    fallback_text = "I apologize, but I'm unable to connect to the AI service at the moment. Please try again later or contact support."
    return fallback_text, 15, 0


@webllm_blueprint.route("/", methods=["GET"])
def webllm_interface():
    """Serve WebLLM interface"""
    try:
        return render_template("webllm.html")
    except Exception as e:
        logger.error(f"Error serving WebLLM interface: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "webllm",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": len(manager.loaded_models)
    }), 200


@webllm_blueprint.route("/api/models", methods=["GET"])
def get_models():
    """Get available models for WebLLM"""
    try:
        recommended_only = request.args.get("recommended", "false").lower() == "true"
        
        if recommended_only:
            models = WebLLMConfig.get_recommended_models()
        else:
            models = WebLLMConfig.get_all_models()
        
        return jsonify({
            "models": models,
            "default_model": WebLLMConfig.DEFAULT_MODEL,
            "count": len(models)
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving models: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/models/info", methods=["GET"])
def get_model_info():
    """Get information about a specific model"""
    try:
        model_type = request.args.get("model")
        if not model_type:
            return jsonify({"error": "Missing 'model' query parameter"}), 400
        
        info = WebLLMConfig.get_model_info(model_type)
        if not info:
            return jsonify({"error": f"Model {model_type} not found"}), 404
        
        return jsonify(info), 200
    except Exception as e:
        logger.error(f"Error retrieving model info: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/infer", methods=["POST"])
def run_inference():
    """
    Run inference with actual LLM service.
    
    Expected JSON:
    {
        "prompt": "Your prompt here",
        "model_id": "model-name",
        "temperature": 0.7,
        "max_tokens": 512,
        "mode": "client_side"
    }
    """
    try:
        data = request.get_json()
        
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing required field: prompt"}), 400
        
        # Create inference request
        inf_request = InferenceRequest(
            prompt=data.get("prompt"),
            model_id=data.get("model_id", WebLLMConfig.DEFAULT_MODEL),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
            top_p=data.get("top_p"),
            top_k=data.get("top_k"),
            mode=data.get("mode", InferenceMode.CLIENT_SIDE.value)
        )
        
        # Validate request
        valid, error_msg = manager.validate_inference_request(inf_request)
        if not valid:
            return jsonify({"error": error_msg}), 400
        
        # Get actual LLM response
        response_text, tokens_generated, inference_time = get_llm_response(
            prompt=inf_request.prompt,
            temperature=inf_request.temperature or WebLLMConfig.DEFAULT_TEMPERATURE,
            max_tokens=inf_request.max_tokens or WebLLMConfig.DEFAULT_MAX_TOKENS
        )
        
        # Create response with actual data
        request_id = str(uuid.uuid4())
        response = InferenceResponse(
            request_id=request_id,
            text=response_text,
            tokens_generated=tokens_generated,
            inference_time_ms=inference_time,
            mode=inf_request.mode,
            model_id=inf_request.model_id
        )
        
        # Record inference metrics
        manager.record_inference(response)
        
        return jsonify({
            "request_id": response.request_id,
            "text": response.text,
            "tokens_generated": response.tokens_generated,
            "inference_time_ms": response.inference_time_ms,
            "mode": response.mode,
            "model_id": response.model_id,
            "timestamp": response.timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/infer/batch", methods=["POST"])
def batch_inference():
    """
    Run batch inference on multiple prompts with actual LLM service
    
    Expected JSON:
    {
        "prompts": ["prompt1", "prompt2"],
        "model_id": "model-name",
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json()
        
        if not data or "prompts" not in data:
            return jsonify({"error": "Missing required field: prompts"}), 400
        
        prompts = data.get("prompts", [])
        if not isinstance(prompts, list) or len(prompts) == 0:
            return jsonify({"error": "Prompts must be a non-empty list"}), 400
        
        if len(prompts) > 100:
            return jsonify({"error": "Maximum 100 prompts per batch"}), 400
        
        model_id = data.get("model_id", WebLLMConfig.DEFAULT_MODEL)
        temperature = data.get("temperature", WebLLMConfig.DEFAULT_TEMPERATURE)
        max_tokens = data.get("max_tokens", WebLLMConfig.DEFAULT_MAX_TOKENS)
        
        results = []
        total_time = 0
        total_tokens = 0
        successful_count = 0
        
        for prompt in prompts:
            inf_request = InferenceRequest(
                prompt=prompt,
                model_id=model_id,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            valid, error_msg = manager.validate_inference_request(inf_request)
            if not valid:
                results.append({
                    "error": error_msg,
                    "prompt": prompt
                })
                continue
            
            # Get actual LLM response
            try:
                response_text, tokens, inference_time = get_llm_response(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                request_id = str(uuid.uuid4())
                
                response = InferenceResponse(
                    request_id=request_id,
                    text=response_text,
                    tokens_generated=tokens,
                    inference_time_ms=inference_time,
                    mode=InferenceMode.CLIENT_SIDE.value,
                    model_id=model_id
                )
                
                manager.record_inference(response)
                
                total_time += inference_time
                total_tokens += tokens
                successful_count += 1
                
                results.append({
                    "request_id": response.request_id,
                    "text": response.text,
                    "tokens_generated": response.tokens_generated,
                    "inference_time_ms": response.inference_time_ms
                })
                
            except Exception as e:
                logger.error(f"Error processing prompt in batch: {e}")
                results.append({
                    "error": str(e),
                    "prompt": prompt
                })
        
        return jsonify({
            "results": results,
            "total_prompts": len(prompts),
            "successful": successful_count,
            "total_time_ms": total_time,
            "total_tokens": total_tokens
        }), 200
        
    except Exception as e:
        logger.error(f"Error during batch inference: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/config/models", methods=["POST"])
def set_model_config():
    """
    Configure a model
    
    Expected JSON:
    {
        "model_type": "mistral",
        "temperature": 0.7,
        "max_tokens": 512
    }
    """
    try:
        data = request.get_json()
        
        model_type = data.get("model_type")
        if not model_type:
            return jsonify({"error": "Missing model_type"}), 400
        
        config = ModelConfig(
            model_id=model_type,
            model_type=ModelType.MISTRAL,
            temperature=data.get("temperature", WebLLMConfig.DEFAULT_TEMPERATURE),
            max_tokens=data.get("max_tokens", WebLLMConfig.DEFAULT_MAX_TOKENS),
            top_p=data.get("top_p", WebLLMConfig.DEFAULT_TOP_P),
            top_k=data.get("top_k", WebLLMConfig.DEFAULT_TOP_K)
        )
        
        manager.add_model_config(model_type, config)
        
        return jsonify({
            "status": "configured",
            "model_type": model_type,
            "config": config.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error configuring model: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/config/models/<model_type>", methods=["GET"])
def get_model_config(model_type):
    """Get configuration for a specific model"""
    try:
        config = manager.get_model_config(model_type)
        if not config:
            return jsonify({"error": f"No configuration for model {model_type}"}), 404
        
        return jsonify(config.to_dict()), 200
    except Exception as e:
        logger.error(f"Error retrieving model config: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Get performance metrics"""
    try:
        metrics = manager.get_performance_metrics()
        
        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "inference_history_count": len(manager.inference_history)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/history", methods=["GET"])
def get_history():
    """Get inference history"""
    try:
        limit = request.args.get("limit", 10, type=int)
        if limit > 100:
            limit = 100
        
        history = manager.get_inference_history(limit)
        
        return jsonify({
            "count": len(history),
            "history": [h.to_dict() for h in history]
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/clear", methods=["POST"])
def clear_data():
    """Clear history and reset metrics"""
    try:
        manager.clear_history()
        
        return jsonify({
            "status": "cleared",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        return jsonify({"error": str(e)}), 500


@webllm_blueprint.route("/api/status", methods=["GET"])
def get_status():
    """Get overall WebLLM status"""
    try:
        metrics = manager.get_performance_metrics()
        
        return jsonify({
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "webllm",
            "models_configured": len(manager.model_configs),
            "models_loaded": len(manager.loaded_models),
            "total_inferences": metrics.get("total_inferences", 0),
            "average_inference_time_ms": metrics.get("average_inference_time", 0)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving status: {e}")
        return jsonify({"error": str(e)}), 500
