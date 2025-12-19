"""
Integration Tests for WebLLM Client-Side Inference

This module contains integration tests for the complete WebLLM workflow,
including browser-to-server communication, model loading, inference execution,
and performance under various conditions.

Test Coverage:
- End-to-end chat workflow
- Multiple sequential and concurrent inferences
- Model switching and configuration changes
- Error handling and recovery
- Performance and stress testing
- Client-side vs server-side inference modes
"""

import unittest
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.webllm_service import (
    WebLLMManager,
    ModelType,
    InferenceMode
)


class TestWebLLMWorkflow(unittest.TestCase):
    """Test complete WebLLM workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Clear data before each test
        self.client.post('/webllm/api/clear', content_type='application/json')
    
    def test_simple_chat_flow(self):
        """Test simple chat message flow"""
        # 1. Get available models
        models_resp = self.client.get('/webllm/api/models')
        self.assertEqual(models_resp.status_code, 200)
        models = json.loads(models_resp.data)
        self.assertGreater(models['count'], 0)
        
        # 2. Send inference request
        infer_resp = self.client.post('/webllm/api/infer',
            json={
                'prompt': 'Hello, what is machine learning?',
                'model_id': models['default_model']
            },
            content_type='application/json'
        )
        self.assertEqual(infer_resp.status_code, 200)
        result = json.loads(infer_resp.data)
        self.assertIn('request_id', result)
        self.assertIn('text', result)
        
        # 3. Get history
        history_resp = self.client.get('/webllm/api/history')
        self.assertEqual(history_resp.status_code, 200)
        history = json.loads(history_resp.data)
        self.assertGreater(history['count'], 0)
        
        # 4. Check metrics
        metrics_resp = self.client.get('/webllm/api/metrics')
        self.assertEqual(metrics_resp.status_code, 200)
        metrics = json.loads(metrics_resp.data)
        self.assertEqual(metrics['metrics']['total_inferences'], 1)
    
    def test_multi_turn_conversation(self):
        """Test multiple turn conversation"""
        prompts = [
            'What is Python?',
            'How do I install it?',
            'Can I use it for web development?',
            'What frameworks are available?'
        ]
        
        for prompt in prompts:
            response = self.client.post('/webllm/api/infer',
                json={'prompt': prompt, 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Verify all conversations recorded
        history_resp = self.client.get('/webllm/api/history?limit=10')
        history = json.loads(history_resp.data)
        self.assertEqual(history['count'], 4)
    
    def test_configuration_changes_during_chat(self):
        """Test changing configuration between requests"""
        # First request with default temperature
        resp1 = self.client.post('/webllm/api/infer',
            json={
                'prompt': 'First prompt',
                'model_id': ModelType.MISTRAL.value,
                'temperature': 0.3
            },
            content_type='application/json'
        )
        self.assertEqual(resp1.status_code, 200)
        
        # Change configuration
        config_resp = self.client.post('/webllm/api/config/models',
            json={
                'model_type': 'mistral',
                'temperature': 0.9,
                'max_tokens': 1024
            },
            content_type='application/json'
        )
        self.assertEqual(config_resp.status_code, 200)
        
        # Second request with new temperature
        resp2 = self.client.post('/webllm/api/infer',
            json={
                'prompt': 'Second prompt',
                'model_id': ModelType.MISTRAL.value,
                'temperature': 0.9
            },
            content_type='application/json'
        )
        self.assertEqual(resp2.status_code, 200)
    
    def test_inference_mode_switching(self):
        """Test switching between inference modes"""
        modes = [
            InferenceMode.CLIENT_SIDE.value,
            InferenceMode.SERVER_SIDE.value,
            InferenceMode.HYBRID.value
        ]
        
        for mode in modes:
            response = self.client.post('/webllm/api/infer',
                json={
                    'prompt': f'Test prompt in {mode}',
                    'model_id': ModelType.MISTRAL.value,
                    'mode': mode
                },
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['mode'], mode)
    
    def test_batch_and_sequential_mix(self):
        """Test mixing batch and sequential inference"""
        # Sequential requests
        for i in range(3):
            resp = self.client.post('/webllm/api/infer',
                json={'prompt': f'Sequential {i}', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
            self.assertEqual(resp.status_code, 200)
        
        # Batch request
        batch_resp = self.client.post('/webllm/api/infer/batch',
            json={
                'prompts': ['Batch 1', 'Batch 2', 'Batch 3'],
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        self.assertEqual(batch_resp.status_code, 200)
        batch_data = json.loads(batch_resp.data)
        self.assertEqual(batch_data['total_prompts'], 3)
        
        # Verify total
        metrics_resp = self.client.get('/webllm/api/metrics')
        metrics = json.loads(metrics_resp.data)
        self.assertEqual(metrics['metrics']['total_inferences'], 6)


class TestWebLLMErrorHandling(unittest.TestCase):
    """Test error handling and recovery"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear data before each test
        self.client.post('/webllm/api/clear', content_type='application/json')
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON"""
        response = self.client.post('/webllm/api/infer',
            data='not valid json',
            content_type='application/json'
        )
        
        self.assertNotEqual(response.status_code, 200)
    
    def test_invalid_temperature_handling(self):
        """Test invalid temperature values"""
        invalid_temps = [-1, 3.0, 'invalid']
        
        for temp in invalid_temps[:2]:  # Skip string for now
            response = self.client.post('/webllm/api/infer',
                json={
                    'prompt': 'Test',
                    'model_id': ModelType.MISTRAL.value,
                    'temperature': temp
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
    
    def test_empty_batch_handling(self):
        """Test handling of empty batch"""
        response = self.client.post('/webllm/api/infer/batch',
            json={
                'prompts': [],
                'model_id': ModelType.MISTRAL.value
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        # Missing prompt
        resp1 = self.client.post('/webllm/api/infer',
            json={'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        self.assertEqual(resp1.status_code, 400)
        
        # Missing prompts in batch
        resp2 = self.client.post('/webllm/api/infer/batch',
            json={'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        self.assertEqual(resp2.status_code, 400)
    
    def test_recovery_after_error(self):
        """Test system recovery after error"""
        # Send invalid request
        invalid_resp = self.client.post('/webllm/api/infer',
            json={'prompt': ''},
            content_type='application/json'
        )
        self.assertEqual(invalid_resp.status_code, 400)
        
        # System should recover and handle valid request
        valid_resp = self.client.post('/webllm/api/infer',
            json={'prompt': 'Valid prompt', 'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        self.assertEqual(valid_resp.status_code, 200)


class TestWebLLMPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear data before each test
        self.client.post('/webllm/api/clear', content_type='application/json')
    
    def test_sequential_requests_performance(self):
        """Test performance of sequential requests"""
        num_requests = 10
        times = []
        
        start_time = time.time()
        for i in range(num_requests):
            req_start = time.time()
            response = self.client.post('/webllm/api/infer',
                json={'prompt': f'Test {i}', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
            req_time = time.time() - req_start
            times.append(req_time)
            self.assertEqual(response.status_code, 200)
        
        total_time = time.time() - start_time
        avg_time = total_time / num_requests
        
        # Metrics should be recorded
        metrics_resp = self.client.get('/webllm/api/metrics')
        metrics = json.loads(metrics_resp.data)
        self.assertEqual(metrics['metrics']['total_inferences'], num_requests)
    
    def test_batch_vs_sequential_efficiency(self):
        """Test batch inference vs sequential performance"""
        prompts = [f'Prompt {i}' for i in range(10)]
        
        # Batch inference
        batch_start = time.time()
        batch_resp = self.client.post('/webllm/api/infer/batch',
            json={'prompts': prompts, 'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        batch_time = time.time() - batch_start
        self.assertEqual(batch_resp.status_code, 200)
        
        # Clear for fresh test
        self.client.post('/webllm/api/clear', content_type='application/json')
        
        # Sequential inference
        seq_start = time.time()
        for prompt in prompts:
            self.client.post('/webllm/api/infer',
                json={'prompt': prompt, 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
        seq_time = time.time() - seq_start
        
        # Batch should be reasonably comparable (might be faster)
        self.assertGreater(seq_time, batch_time * 0.5)
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        num_concurrent = 5
        
        def make_request(i):
            return self.client.post('/webllm/api/infer',
                json={'prompt': f'Concurrent {i}', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
        
        # Use threading to simulate concurrent requests
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # All should succeed
        for result in results:
            self.assertEqual(result.status_code, 200)
        
        # Verify metrics
        metrics_resp = self.client.get('/webllm/api/metrics')
        metrics = json.loads(metrics_resp.data)
        self.assertEqual(metrics['metrics']['total_inferences'], num_concurrent)
    
    def test_response_time_metrics(self):
        """Test response time metrics tracking"""
        # Send several requests
        for i in range(5):
            self.client.post('/webllm/api/infer',
                json={'prompt': f'Test {i}', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
        
        # Check metrics
        metrics_resp = self.client.get('/webllm/api/metrics')
        metrics = json.loads(metrics_resp.data)
        
        self.assertGreater(metrics['metrics']['average_inference_time'], 0)
        self.assertGreater(metrics['metrics']['total_time_ms'], 0)
    
    def test_memory_efficiency_with_history(self):
        """Test memory efficiency with large history"""
        # Generate history
        for i in range(50):
            self.client.post('/webllm/api/infer',
                json={'prompt': f'Test {i}', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
        
        # Retrieve history in chunks
        history1 = self.client.get('/webllm/api/history?limit=10')
        self.assertEqual(history1.status_code, 200)
        data1 = json.loads(history1.data)
        self.assertEqual(data1['count'], 10)
        
        history2 = self.client.get('/webllm/api/history?limit=25')
        self.assertEqual(history2.status_code, 200)
        data2 = json.loads(history2.data)
        self.assertEqual(data2['count'], 25)


class TestWebLLMStress(unittest.TestCase):
    """Test WebLLM under stress conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear data before each test
        self.client.post('/webllm/api/clear', content_type='application/json')
    
    def test_high_volume_requests(self):
        """Test handling high volume of requests"""
        num_requests = 50
        success_count = 0
        
        for i in range(num_requests):
            response = self.client.post('/webllm/api/infer',
                json={'prompt': f'Request {i}', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
            if response.status_code == 200:
                success_count += 1
        
        # Should maintain high success rate
        success_rate = success_count / num_requests
        self.assertGreater(success_rate, 0.9)
    
    def test_maximum_batch_size(self):
        """Test with maximum batch size"""
        # Create 100 prompts (max allowed)
        prompts = [f'Prompt {i}' for i in range(100)]
        
        response = self.client.post('/webllm/api/infer/batch',
            json={'prompts': prompts, 'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_prompts'], 100)
    
    def test_maximum_prompt_length(self):
        """Test with maximum prompt length"""
        # Create 2000 character prompt (max allowed)
        long_prompt = 'a' * 2000
        
        response = self.client.post('/webllm/api/infer',
            json={'prompt': long_prompt, 'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_sustained_load(self):
        """Test sustained load over time"""
        duration_seconds = 5
        requests_made = 0
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            response = self.client.post('/webllm/api/infer',
                json={'prompt': f'Load test', 'model_id': ModelType.MISTRAL.value},
                content_type='application/json'
            )
            if response.status_code == 200:
                requests_made += 1
        
        # Should handle sustained load
        self.assertGreater(requests_made, 0)
        
        # Verify system still responsive
        health_resp = self.client.get('/webllm/api/health')
        self.assertEqual(health_resp.status_code, 200)


class TestWebLLMIntegrationWithChat(unittest.TestCase):
    """Test WebLLM integration with chat UI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear data before each test
        self.client.post('/webllm/api/clear', content_type='application/json')
    
    def test_webllm_interface_accessibility(self):
        """Test WebLLM interface is accessible"""
        response = self.client.get('/webllm/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WebLLM', response.data)
    
    def test_webllm_and_whatsapp_coexistence(self):
        """Test WebLLM and WhatsApp chat UI can coexist"""
        # WebLLM should be accessible
        webllm_resp = self.client.get('/webllm/')
        self.assertEqual(webllm_resp.status_code, 200)
        
        # Chat UI should still be accessible
        chat_resp = self.client.get('/')
        self.assertEqual(chat_resp.status_code, 200)
        
        # Both should have independent inference endpoints
        webllm_infer = self.client.post('/webllm/api/infer',
            json={'prompt': 'WebLLM test', 'model_id': ModelType.MISTRAL.value},
            content_type='application/json'
        )
        self.assertEqual(webllm_infer.status_code, 200)
        
        # Chat UI inference might use different endpoint
        # This depends on chat UI implementation


if __name__ == '__main__':
    unittest.main()
