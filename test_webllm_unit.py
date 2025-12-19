"""
Unit Tests for WebLLM Client-Side Inference

This module contains unit tests for the WebLLM service and its components,
including model configuration, inference requests/responses, and metrics tracking.

Test Coverage:
- Model configuration management
- Inference request validation
- Response generation and tracking
- Performance metrics calculation
- API endpoint functionality
"""

import unittest
import json
import time
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
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


class TestWebLLMConfig(unittest.TestCase):
    """Test WebLLM configuration management"""
    
    def test_supported_models_count(self):
        """Test that expected number of models are supported"""
        models = WebLLMConfig.get_all_models()
        self.assertGreater(len(models), 0)
        self.assertIn('microsoft/phi-2', [m['model_id'] for m in models])
    
    def test_get_recommended_models(self):
        """Test getting only recommended models"""
        models = WebLLMConfig.get_recommended_models()
        self.assertGreater(len(models), 0)
        
        # All should have recommended flag
        for model in models:
            self.assertTrue(model.get('recommended', False))
    
    def test_get_model_info(self):
        """Test getting information about a specific model"""
        info = WebLLMConfig.get_model_info(ModelType.MISTRAL.value)
        self.assertIsNotNone(info)
        self.assertIn('model_id', info)
        self.assertIn('size_gb', info)
        self.assertIn('vram_required_gb', info)
    
    def test_invalid_model_info(self):
        """Test getting info for invalid model"""
        info = WebLLMConfig.get_model_info('invalid_model')
        self.assertIsNone(info)
    
    def test_default_config_values(self):
        """Test default configuration values"""
        self.assertEqual(WebLLMConfig.DEFAULT_TEMPERATURE, 0.7)
        self.assertEqual(WebLLMConfig.DEFAULT_MAX_TOKENS, 512)
        self.assertEqual(WebLLMConfig.DEFAULT_TOP_P, 0.9)
        self.assertIsNotNone(WebLLMConfig.DEFAULT_MODEL)


class TestModelConfig(unittest.TestCase):
    """Test model configuration"""
    
    def test_model_config_creation(self):
        """Test creating a model configuration"""
        config = ModelConfig(
            model_id="test_model",
            model_type=ModelType.MISTRAL,
            temperature=0.5,
            max_tokens=256
        )
        
        self.assertEqual(config.model_id, "test_model")
        self.assertEqual(config.model_type, ModelType.MISTRAL)
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 256)
    
    def test_model_config_to_dict(self):
        """Test converting model config to dictionary"""
        config = ModelConfig(
            model_id="test_model",
            model_type=ModelType.LLAMA3,
            temperature=0.8
        )
        
        config_dict = config.to_dict()
        self.assertEqual(config_dict['model_id'], "test_model")
        self.assertEqual(config_dict['temperature'], 0.8)
        self.assertIsInstance(config_dict['model_type'], str)


class TestInferenceRequest(unittest.TestCase):
    """Test inference request handling"""
    
    def test_inference_request_creation(self):
        """Test creating an inference request"""
        request = InferenceRequest(
            prompt="Test prompt",
            model_id="test_model"
        )
        
        self.assertEqual(request.prompt, "Test prompt")
        self.assertEqual(request.model_id, "test_model")
        self.assertIsNotNone(request.timestamp)
    
    def test_inference_request_with_params(self):
        """Test creating request with parameters"""
        request = InferenceRequest(
            prompt="Test",
            model_id="model",
            temperature=0.5,
            max_tokens=256,
            top_p=0.8,
            top_k=40
        )
        
        self.assertEqual(request.temperature, 0.5)
        self.assertEqual(request.max_tokens, 256)
        self.assertEqual(request.top_p, 0.8)
        self.assertEqual(request.top_k, 40)
    
    def test_inference_request_to_dict(self):
        """Test converting request to dictionary"""
        request = InferenceRequest(
            prompt="Test prompt",
            model_id="test_model",
            temperature=0.7
        )
        
        req_dict = request.to_dict()
        self.assertEqual(req_dict['prompt'], "Test prompt")
        self.assertEqual(req_dict['model_id'], "test_model")
        self.assertIn('timestamp', req_dict)


class TestInferenceResponse(unittest.TestCase):
    """Test inference response handling"""
    
    def test_inference_response_creation(self):
        """Test creating an inference response"""
        response = InferenceResponse(
            request_id="req_123",
            text="Response text",
            tokens_generated=50,
            inference_time_ms=150.5,
            mode=InferenceMode.CLIENT_SIDE.value,
            model_id="test_model"
        )
        
        self.assertEqual(response.request_id, "req_123")
        self.assertEqual(response.text, "Response text")
        self.assertEqual(response.tokens_generated, 50)
        self.assertTrue(response.success)
        self.assertIsNone(response.error)
    
    def test_inference_response_with_error(self):
        """Test creating error response"""
        response = InferenceResponse(
            request_id="req_123",
            text="",
            tokens_generated=0,
            inference_time_ms=0,
            mode=InferenceMode.SERVER_SIDE.value,
            model_id="test_model",
            success=False,
            error="Model failed to load"
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Model failed to load")
    
    def test_inference_response_to_dict(self):
        """Test converting response to dictionary"""
        response = InferenceResponse(
            request_id="req_123",
            text="Test response",
            tokens_generated=25,
            inference_time_ms=100.0,
            mode=InferenceMode.CLIENT_SIDE.value,
            model_id="test_model"
        )
        
        resp_dict = response.to_dict()
        self.assertEqual(resp_dict['request_id'], "req_123")
        self.assertEqual(resp_dict['text'], "Test response")
        self.assertIn('timestamp', resp_dict)


class TestWebLLMManager(unittest.TestCase):
    """Test WebLLM manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = WebLLMManager()
    
    def test_manager_initialization(self):
        """Test manager initializes correctly"""
        self.assertEqual(len(self.manager.loaded_models), 0)
        self.assertEqual(len(self.manager.model_configs), 0)
        self.assertEqual(self.manager.performance_metrics['total_inferences'], 0)
    
    def test_add_model_config(self):
        """Test adding model configuration"""
        config = ModelConfig(
            model_id="test_model",
            model_type=ModelType.MISTRAL
        )
        
        self.manager.add_model_config("mistral", config)
        
        self.assertIn("mistral", self.manager.model_configs)
        self.assertEqual(self.manager.get_model_config("mistral"), config)
    
    def test_validate_empty_prompt(self):
        """Test validation with empty prompt"""
        request = InferenceRequest(
            prompt="",
            model_id="test"
        )
        
        valid, error = self.manager.validate_inference_request(request)
        self.assertFalse(valid)
        self.assertIn("empty", error.lower())
    
    def test_validate_long_prompt(self):
        """Test validation with prompt exceeding max length"""
        request = InferenceRequest(
            prompt="x" * 2500,
            model_id="test"
        )
        
        valid, error = self.manager.validate_inference_request(request)
        self.assertFalse(valid)
        self.assertIn("length", error.lower())
    
    def test_validate_invalid_temperature(self):
        """Test validation with invalid temperature"""
        request = InferenceRequest(
            prompt="Test",
            model_id="test",
            temperature=3.0
        )
        
        valid, error = self.manager.validate_inference_request(request)
        self.assertFalse(valid)
        self.assertIn("temperature", error.lower())
    
    def test_validate_invalid_max_tokens(self):
        """Test validation with invalid max tokens"""
        request = InferenceRequest(
            prompt="Test",
            model_id="test",
            max_tokens=3000
        )
        
        valid, error = self.manager.validate_inference_request(request)
        self.assertFalse(valid)
        self.assertIn("tokens", error.lower())
    
    def test_validate_valid_request(self):
        """Test validation with valid request"""
        request = InferenceRequest(
            prompt="Valid test prompt",
            model_id="test",
            temperature=0.7,
            max_tokens=512
        )
        
        valid, error = self.manager.validate_inference_request(request)
        self.assertTrue(valid)
        self.assertIsNone(error)
    
    def test_record_inference(self):
        """Test recording inference metrics"""
        response = InferenceResponse(
            request_id="req_1",
            text="Test",
            tokens_generated=50,
            inference_time_ms=100.0,
            mode=InferenceMode.CLIENT_SIDE.value,
            model_id="test"
        )
        
        self.manager.record_inference(response)
        
        self.assertEqual(self.manager.performance_metrics['total_inferences'], 1)
        self.assertEqual(self.manager.performance_metrics['total_tokens'], 50)
        self.assertEqual(self.manager.performance_metrics['total_time_ms'], 100.0)
        self.assertEqual(self.manager.performance_metrics['client_side_count'], 1)
    
    def test_record_multiple_inferences(self):
        """Test recording multiple inferences"""
        for i in range(5):
            response = InferenceResponse(
                request_id=f"req_{i}",
                text="Test",
                tokens_generated=50 + i * 10,
                inference_time_ms=100.0 + i * 10,
                mode=InferenceMode.CLIENT_SIDE.value if i % 2 == 0 else InferenceMode.SERVER_SIDE.value,
                model_id="test"
            )
            self.manager.record_inference(response)
        
        metrics = self.manager.performance_metrics
        self.assertEqual(metrics['total_inferences'], 5)
        self.assertEqual(metrics['client_side_count'], 3)
        self.assertEqual(metrics['server_side_count'], 2)
        self.assertGreater(metrics['average_inference_time'], 0)
    
    def test_get_inference_history(self):
        """Test retrieving inference history"""
        for i in range(3):
            response = InferenceResponse(
                request_id=f"req_{i}",
                text=f"Test {i}",
                tokens_generated=50,
                inference_time_ms=100.0,
                mode=InferenceMode.CLIENT_SIDE.value,
                model_id="test"
            )
            self.manager.record_inference(response)
        
        history = self.manager.get_inference_history(limit=2)
        self.assertEqual(len(history), 2)
    
    def test_clear_history(self):
        """Test clearing history"""
        response = InferenceResponse(
            request_id="req_1",
            text="Test",
            tokens_generated=50,
            inference_time_ms=100.0,
            mode=InferenceMode.CLIENT_SIDE.value,
            model_id="test"
        )
        self.manager.record_inference(response)
        
        self.assertEqual(self.manager.performance_metrics['total_inferences'], 1)
        
        self.manager.clear_history()
        
        self.assertEqual(self.manager.performance_metrics['total_inferences'], 0)
        self.assertEqual(len(self.manager.inference_history), 0)


class TestWebLLMAPIEndpoints(unittest.TestCase):
    """Test WebLLM API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_webllm_interface_loads(self):
        """Test that WebLLM interface loads"""
        response = self.client.get('/webllm/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'webllm', response.data.lower())
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/webllm/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'webllm')
    
    def test_get_models(self):
        """Test getting available models"""
        response = self.client.get('/webllm/api/models')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('models', data)
        self.assertGreater(data['count'], 0)
        self.assertIn('default_model', data)
    
    def test_get_recommended_models(self):
        """Test getting recommended models"""
        response = self.client.get('/webllm/api/models?recommended=true')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertGreater(data['count'], 0)
    
    def test_get_model_info(self):
        """Test getting model information"""
        response = self.client.get(f'/webllm/api/models/info?model={ModelType.MISTRAL.value}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('model_id', data)
        self.assertIn('size_gb', data)
    
    def test_get_invalid_model_info(self):
        """Test getting info for invalid model"""
        response = self.client.get('/webllm/api/models/info?model=invalid_model')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.webllm_views.get_llm_response')
    def test_inference_endpoint_valid(self, mock_llm):
        """Test inference endpoint with valid input"""
        # Mock the LLM response
        mock_llm.return_value = ("This is an AI response about artificial intelligence.", 10, 150.0)
        
        response = self.client.post('/webllm/api/infer',
            json={
                'prompt': 'What is AI?',
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('request_id', data)
        self.assertIn('text', data)
        self.assertIn('inference_time_ms', data)
        self.assertEqual(data['text'], "This is an AI response about artificial intelligence.")
    
    def test_inference_endpoint_missing_prompt(self):
        """Test inference endpoint with missing prompt"""
        response = self.client.post('/webllm/api/infer',
            json={
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_inference_endpoint_empty_prompt(self):
        """Test inference endpoint with empty prompt"""
        response = self.client.post('/webllm/api/infer',
            json={
                'prompt': '',
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    @patch('app.webllm_views.get_llm_response')
    def test_batch_inference_endpoint(self, mock_llm):
        """Test batch inference endpoint"""
        # Mock the LLM response
        mock_llm.return_value = ("Test response from LLM", 5, 100.0)
        
        response = self.client.post('/webllm/api/infer/batch',
            json={
                'prompts': ['Prompt 1', 'Prompt 2', 'Prompt 3'],
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_prompts'], 3)
        self.assertEqual(data['successful'], 3)
    
    def test_batch_inference_too_many_prompts(self):
        """Test batch inference with too many prompts"""
        prompts = [f'Prompt {i}' for i in range(150)]
        
        response = self.client.post('/webllm/api/infer/batch',
            json={
                'prompts': prompts,
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_set_model_config(self):
        """Test setting model configuration"""
        response = self.client.post('/webllm/api/config/models',
            json={
                'model_type': 'mistral',
                'temperature': 0.5,
                'max_tokens': 256
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'configured')
    
    def test_get_metrics(self):
        """Test getting performance metrics"""
        # Add some metrics first
        self.client.post('/webllm/api/infer',
            json={'prompt': 'Test', 'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        
        response = self.client.get('/webllm/api/metrics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('metrics', data)
        self.assertGreater(data['metrics']['total_inferences'], 0)
    
    def test_get_history(self):
        """Test getting inference history"""
        response = self.client.get('/webllm/api/history')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('history', data)
        self.assertIn('count', data)
    
    def test_clear_endpoint(self):
        """Test clear endpoint"""
        response = self.client.post('/webllm/api/clear',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'cleared')
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = self.client.get('/webllm/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'operational')
        self.assertIn('total_inferences', data)


if __name__ == '__main__':
    unittest.main()
