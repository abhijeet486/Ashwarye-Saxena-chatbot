"""
WebLLM Swagger/OpenAPI Documentation

Provides comprehensive OpenAPI 3.0 specification and Swagger UI
for the WebLLM browser-based inference API.
"""

from flask_restx import Api, Resource, fields, Namespace

# Create WebLLM API namespace
webllm_ns = Namespace(
    'WebLLM',
    description='Browser-based client-side LLM inference API',
    doc='/webllm/docs'
)

# Define Models for WebLLM

# Model Definition
model_info_model = {
    'model_id': fields.String(
        required=True,
        description='Model identifier',
        example='mistralai/Mistral-7B-Instruct-v0.2'
    ),
    'size_gb': fields.Float(
        required=True,
        description='Model size in gigabytes',
        example=14.0
    ),
    'vram_required_gb': fields.Integer(
        required=True,
        description='VRAM required for inference',
        example=6
    ),
    'recommended': fields.Boolean(
        description='Whether model is recommended for browser inference',
        example=True
    )
}

# Inference Request Model
inference_request_model = {
    'prompt': fields.String(
        required=True,
        description='The input prompt for the model',
        example='What is machine learning?',
        min_length=1,
        max_length=2000
    ),
    'model_id': fields.String(
        required=True,
        description='Model identifier to use for inference',
        example='mistralai/Mistral-7B-Instruct-v0.2'
    ),
    'temperature': fields.Float(
        description='Sampling temperature (0.0-2.0). Higher = more creative',
        example=0.7,
        min=0.0,
        max=2.0
    ),
    'max_tokens': fields.Integer(
        description='Maximum number of tokens to generate (1-2048)',
        example=512,
        min=1,
        max=2048
    ),
    'top_p': fields.Float(
        description='Nucleus sampling parameter (0.0-1.0)',
        example=0.9,
        min=0.0,
        max=1.0
    ),
    'top_k': fields.Integer(
        description='Top-k sampling parameter',
        example=50,
        min=1
    ),
    'mode': fields.String(
        description='Inference execution mode',
        example='client_side',
        enum=['client_side', 'server_side', 'hybrid']
    )
}

# Inference Response Model
inference_response_model = {
    'request_id': fields.String(
        required=True,
        description='Unique request identifier',
        example='550e8400-e29b-41d4-a716-446655440000'
    ),
    'text': fields.String(
        required=True,
        description='Generated response text from the model',
        example='Machine learning is a subset of artificial intelligence...'
    ),
    'tokens_generated': fields.Integer(
        required=True,
        description='Approximate number of tokens generated',
        example=45
    ),
    'inference_time_ms': fields.Float(
        required=True,
        description='Time taken for inference in milliseconds',
        example=234.5
    ),
    'mode': fields.String(
        required=True,
        description='Execution mode used',
        example='client_side'
    ),
    'model_id': fields.String(
        required=True,
        description='Model that was used',
        example='mistralai/Mistral-7B-Instruct-v0.2'
    ),
    'timestamp': fields.String(
        required=True,
        description='ISO format timestamp',
        example='2024-01-15T10:30:00.000000'
    )
}

# Batch Inference Request Model
batch_inference_request_model = {
    'prompts': fields.List(
        fields.String(min_length=1, max_length=2000),
        required=True,
        description='List of prompts for batch inference (max 100)',
        example=['What is AI?', 'What is ML?', 'What is DL?']
    ),
    'model_id': fields.String(
        required=True,
        description='Model identifier to use',
        example='mistralai/Mistral-7B-Instruct-v0.2'
    ),
    'temperature': fields.Float(
        description='Sampling temperature',
        example=0.7
    ),
    'max_tokens': fields.Integer(
        description='Maximum tokens per prompt',
        example=512
    )
}

# Batch Inference Result
batch_inference_result_model = {
    'request_id': fields.String(
        required=True,
        description='Request identifier',
        example='550e8400-e29b-41d4-a716-446655440000'
    ),
    'text': fields.String(
        required=True,
        description='Response text',
        example='AI is artificial intelligence...'
    ),
    'tokens_generated': fields.Integer(
        required=True,
        description='Tokens in this response',
        example=35
    ),
    'inference_time_ms': fields.Float(
        required=True,
        description='Inference time for this prompt',
        example=200.0
    )
}

# Batch Inference Response Model
batch_inference_response_model = {
    'results': fields.List(
        fields.Raw(description='Individual inference results'),
        required=True,
        description='Array of inference results'
    ),
    'total_prompts': fields.Integer(
        required=True,
        description='Total prompts in batch',
        example=3
    ),
    'successful': fields.Integer(
        required=True,
        description='Number of successful inferences',
        example=3
    ),
    'total_time_ms': fields.Float(
        required=True,
        description='Total time for all inferences',
        example=645.0
    ),
    'total_tokens': fields.Integer(
        required=True,
        description='Total tokens generated',
        example=117
    )
}

# Model Configuration Request
model_config_request_model = {
    'model_type': fields.String(
        required=True,
        description='Model type/identifier',
        example='mistral'
    ),
    'temperature': fields.Float(
        description='Default temperature',
        example=0.7
    ),
    'max_tokens': fields.Integer(
        description='Default max tokens',
        example=512
    ),
    'top_p': fields.Float(
        description='Default top_p value',
        example=0.9
    ),
    'top_k': fields.Integer(
        description='Default top_k value',
        example=50
    )
}

# Model Configuration Response
model_config_response_model = {
    'status': fields.String(
        required=True,
        description='Configuration status',
        example='configured'
    ),
    'model_type': fields.String(
        required=True,
        description='Configured model type',
        example='mistral'
    ),
    'config': fields.Raw(
        required=True,
        description='Full configuration object'
    )
}

# Performance Metrics Model
performance_metrics_model = {
    'total_inferences': fields.Integer(
        required=True,
        description='Total number of inferences',
        example=42
    ),
    'total_tokens': fields.Integer(
        required=True,
        description='Total tokens generated',
        example=1840
    ),
    'total_time_ms': fields.Float(
        required=True,
        description='Total inference time in milliseconds',
        example=8450.5
    ),
    'average_inference_time': fields.Float(
        required=True,
        description='Average inference time',
        example=201.2
    ),
    'client_side_count': fields.Integer(
        required=True,
        description='Number of client-side inferences',
        example=35
    ),
    'server_side_count': fields.Integer(
        required=True,
        description='Number of server-side inferences',
        example=7
    )
}

# Metrics Response Model
metrics_response_model = {
    'timestamp': fields.String(
        required=True,
        description='Response timestamp',
        example='2024-01-15T10:30:00.000000'
    ),
    'metrics': fields.Nested(
        performance_metrics_model,
        required=True,
        description='Performance metrics'
    ),
    'inference_history_count': fields.Integer(
        required=True,
        description='Number of inferences in history',
        example=42
    )
}

# History Response Model
history_response_model = {
    'count': fields.Integer(
        required=True,
        description='Number of history records returned',
        example=10
    ),
    'history': fields.List(
        fields.Raw(description='Inference record'),
        required=True,
        description='Array of inference history records'
    )
}

# Status Response Model
status_response_model = {
    'status': fields.String(
        required=True,
        description='System status',
        example='operational',
        enum=['operational', 'degraded', 'offline']
    ),
    'timestamp': fields.String(
        required=True,
        description='Status timestamp',
        example='2024-01-15T10:30:00.000000'
    ),
    'service': fields.String(
        required=True,
        description='Service name',
        example='webllm'
    ),
    'models_configured': fields.Integer(
        required=True,
        description='Number of configured models',
        example=2
    ),
    'models_loaded': fields.Integer(
        required=True,
        description='Number of loaded models',
        example=1
    ),
    'total_inferences': fields.Integer(
        required=True,
        description='Total inferences performed',
        example=42
    ),
    'average_inference_time_ms': fields.Float(
        required=True,
        description='Average inference time',
        example=201.2
    )
}

# Health Check Response Model
health_response_model = {
    'status': fields.String(
        required=True,
        description='Health status',
        example='healthy',
        enum=['healthy', 'degraded', 'unhealthy']
    ),
    'service': fields.String(
        required=True,
        description='Service name',
        example='webllm'
    ),
    'timestamp': fields.String(
        required=True,
        description='Check timestamp',
        example='2024-01-15T10:30:00.000000'
    ),
    'models_loaded': fields.Integer(
        required=True,
        description='Number of loaded models',
        example=0
    )
}

# Error Response Model
error_response_model = {
    'error': fields.String(
        required=True,
        description='Error message',
        example='Missing required field: prompt'
    ),
    'code': fields.String(
        description='Error code',
        example='VALIDATION_ERROR'
    ),
    'timestamp': fields.String(
        description='Error timestamp',
        example='2024-01-15T10:30:00.000000'
    )
}

# Models List Response
models_list_response_model = {
    'models': fields.List(
        fields.Raw(description='Model information'),
        required=True,
        description='List of available models'
    ),
    'default_model': fields.String(
        required=True,
        description='Default model identifier',
        example='mistralai/Mistral-7B-Instruct-v0.2'
    ),
    'count': fields.Integer(
        required=True,
        description='Number of models',
        example=7
    )
}

# Consolidated WebLLM API Models Dictionary
webllm_models = {
    'ModelInfo': model_info_model,
    'InferenceRequest': inference_request_model,
    'InferenceResponse': inference_response_model,
    'BatchInferenceRequest': batch_inference_request_model,
    'BatchInferenceResult': batch_inference_result_model,
    'BatchInferenceResponse': batch_inference_response_model,
    'ModelConfigRequest': model_config_request_model,
    'ModelConfigResponse': model_config_response_model,
    'PerformanceMetrics': performance_metrics_model,
    'MetricsResponse': metrics_response_model,
    'HistoryResponse': history_response_model,
    'StatusResponse': status_response_model,
    'HealthResponse': health_response_model,
    'ErrorResponse': error_response_model,
    'ModelsListResponse': models_list_response_model
}


def register_webllm_models(api_instance):
    """
    Register all WebLLM models with the Flask-RESTX API instance.
    
    Args:
        api_instance: Flask-RESTX Api instance
    """
    for model_name, model_def in webllm_models.items():
        api_instance.model(model_name, model_def)


def get_webllm_namespace():
    """Get the WebLLM namespace for use in Flask app."""
    return webllm_ns
