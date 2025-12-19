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
    Run inference on the browser.
    
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
        
        # Create response (simulated for testing)
        request_id = str(uuid.uuid4())
        response = InferenceResponse(
            request_id=request_id,
            text=f"Response to: {inf_request.prompt[:50]}...",
            tokens_generated=50,
            inference_time_ms=150.5,
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
    Run batch inference on multiple prompts
    
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
        temperature = data.get("temperature")
        
        results = []
        total_time = 0
        total_tokens = 0
        
        for prompt in prompts:
            inf_request = InferenceRequest(
                prompt=prompt,
                model_id=model_id,
                temperature=temperature
            )
            
            valid, error_msg = manager.validate_inference_request(inf_request)
            if not valid:
                results.append({
                    "error": error_msg,
                    "prompt": prompt
                })
                continue
            
            # Simulated inference
            request_id = str(uuid.uuid4())
            inference_time = 100 + len(prompt) * 0.5
            tokens = len(prompt.split()) * 2
            
            response = InferenceResponse(
                request_id=request_id,
                text=f"Response to: {prompt[:50]}...",
                tokens_generated=tokens,
                inference_time_ms=inference_time,
                mode=InferenceMode.CLIENT_SIDE.value,
                model_id=model_id
            )
            
            manager.record_inference(response)
            
            total_time += inference_time
            total_tokens += tokens
            
            results.append({
                "request_id": response.request_id,
                "text": response.text,
                "tokens_generated": response.tokens_generated,
                "inference_time_ms": response.inference_time_ms
            })
        
        return jsonify({
            "results": results,
            "total_prompts": len(prompts),
            "successful": len(results),
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
