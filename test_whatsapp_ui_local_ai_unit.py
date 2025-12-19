"""
Unit Tests for WhatsApp Chat UI - Local AI Mode

This module contains unit tests for the core functionality of the WhatsApp Chat UI
with special focus on Local AI mode (LLaMA3 self-hosted support) and the intelligent
fallback hierarchy.

Test Coverage:
- Local LLM detection and availability checking
- LLaMA3 response generation
- Service monitoring and health checks
- Fallback mechanism testing
- API endpoint functionality
- Environment configuration
"""

import unittest
import json
import time
from unittest.mock import patch, Mock, MagicMock
import requests
from datetime import datetime

# Import the Flask app and test client
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.ui_views import (
    check_local_llm_availability,
    get_local_llm_response,
    get_enhanced_response,
    get_service_status,
    categorize_query,
    DEMO_RESPONSES
)

class TestLocalLLMDetection(unittest.TestCase):
    """Test cases for local LLM availability detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Reset global state for testing
        import app.ui_views
        app.ui_views.LOCAL_LLM_AVAILABLE = None
        app.ui_views.LOCAL_LLM_LAST_CHECK = 0
    
    @patch('app.ui_views.requests.get')
    def test_ollama_available_with_llama3(self, mock_get):
        """Test when Ollama is available and LLaMA3 model is installed"""
        # Mock successful response with LLaMA3 model
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3:latest"},
                {"name": "codellama:latest"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Test the function
        result = check_local_llm_availability()
        self.assertTrue(result)
        
        # Verify the API was called correctly
        mock_get.assert_called_once_with("http://127.0.0.1:11434/api/tags", timeout=5)
    
    @patch('app.ui_views.requests.get')
    def test_ollama_available_without_llama3(self, mock_get):
        """Test when Ollama is available but no LLaMA3 model"""
        # Mock successful response without LLaMA3 model
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "codellama:latest"},
                {"name": "mistral:latest"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Test the function
        result = check_local_llm_availability()
        self.assertFalse(result)
    
    @patch('app.ui_views.requests.get')
    def test_ollama_connection_error(self, mock_get):
        """Test when Ollama is not running"""
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        # Test the function
        result = check_local_llm_availability()
        self.assertFalse(result)
    
    @patch('app.ui_views.requests.get')
    def test_ollama_timeout(self, mock_get):
        """Test when Ollama request times out"""
        # Mock timeout error
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Test the function
        result = check_local_llm_availability()
        self.assertFalse(result)
    
    @patch('app.ui_views.requests.get')
    def test_ollama_caching(self, mock_get):
        """Test that availability checking is cached"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3:latest"}]
        }
        mock_get.return_value = mock_response
        
        # Reset global state
        import app.ui_views
        app.ui_views.LOCAL_LLM_AVAILABLE = None
        app.ui_views.LOCAL_LLM_LAST_CHECK = 0
        
        # First call should make API request
        result1 = check_local_llm_availability()
        self.assertTrue(result1)
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call within cache window should use cached result
        result2 = check_local_llm_availability()
        self.assertTrue(result2)
        self.assertEqual(mock_get.call_count, 1)  # Still 1 because of caching

class TestLocalLLMResponse(unittest.TestCase):
    """Test cases for LLaMA3 response generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('requests.post')
    def test_successful_llama3_response(self, mock_post):
        """Test successful LLaMA3 response generation"""
        # Mock successful Ollama response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": "I can help you with MSPSDC services. Please let me know what specific information you need."
            }
        }
        mock_post.return_value = mock_response
        
        # Test the function
        result = get_local_llm_response(
            "Hello, I need help with MSPSDC services",
            [{"type": "user", "message": "Hello"}]
        )
        
        self.assertIsNotNone(result)
        self.assertIn("MSPSDC services", result)
        
        # Verify the API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['model'], 'llama3')
        self.assertEqual(call_args[1]['json']['stream'], False)
    
    @patch('requests.post')
    def test_llama3_timeout(self, mock_post):
        """Test LLaMA3 response timeout handling"""
        # Mock timeout error
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Test the function
        result = get_local_llm_response("Hello", [])
        
        # Should return None on timeout
        self.assertIsNone(result)
    
    @patch('requests.post')
    def test_llama3_connection_error(self, mock_post):
        """Test LLaMA3 connection error handling"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        # Test the function
        result = get_local_llm_response("Hello", [])
        
        # Should return None on connection error
        self.assertIsNone(result)
    
    @patch('requests.post')
    def test_llama3_api_error(self, mock_post):
        """Test LLaMA3 API error handling"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test the function
        result = get_local_llm_response("Hello", [])
        
        # Should return None on API error
        self.assertIsNone(result)
    
    def test_mspsdc_context_in_prompt(self):
        """Test that MSPSDC context is included in the prompt"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "Test response"}
            }
            mock_post.return_value = mock_response
            
            get_local_llm_response("Hello", [])
            
            # Check that the first message has MSPSDC context
            call_args = mock_post.call_args
            messages = call_args[1]['json']['messages']
            self.assertEqual(len(messages), 2)  # System message + user message
            
            system_message = messages[0]
            self.assertEqual(system_message['role'], 'system')
            self.assertIn("Meghalaya State Public Services Delivery Commission", system_message['content'])
            self.assertIn("MSPSDC", system_message['content'])

class TestServiceStatus(unittest.TestCase):
    """Test cases for service status monitoring"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('app.ui_views.check_llm_service')
    @patch('app.ui_views.check_local_llm_availability')
    def test_all_services_available(self, mock_local_llm, mock_main_llm):
        """Test when all services are available"""
        # Mock both services as available
        mock_main_llm.return_value = True
        mock_local_llm.return_value = True
        
        # Set enhanced mode
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            status = get_service_status()
            
            self.assertTrue(status['main_llm_available'])
            self.assertTrue(status['local_llm_available'])
            self.assertEqual(status['active_service'], 'main_llm')
            self.assertEqual(status['service_status'], 'enhanced')
    
    @patch('app.ui_views.check_llm_service')
    @patch('app.ui_views.check_local_llm_availability')
    def test_only_local_llm_available(self, mock_local_llm, mock_main_llm):
        """Test when only local LLM is available"""
        # Mock only local LLM as available
        mock_main_llm.return_value = False
        mock_local_llm.return_value = True
        
        status = get_service_status()
        
        self.assertFalse(status['main_llm_available'])
        self.assertTrue(status['local_llm_available'])
        self.assertEqual(status['active_service'], 'local_llm')
        self.assertEqual(status['service_status'], 'local_enhanced')
    
    @patch('app.ui_views.check_llm_service')
    @patch('app.ui_views.check_local_llm_availability')
    def test_no_services_available(self, mock_local_llm, mock_main_llm):
        """Test when no services are available"""
        # Mock both services as unavailable
        mock_main_llm.return_value = False
        mock_local_llm.return_value = False
        
        status = get_service_status()
        
        self.assertFalse(status['main_llm_available'])
        self.assertFalse(status['local_llm_available'])
        self.assertEqual(status['active_service'], 'demo')
        self.assertEqual(status['service_status'], 'demo')

class TestEnhancedResponse(unittest.TestCase):
    """Test cases for enhanced response generation with fallback hierarchy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('requests.post')
    def test_main_llm_success(self, mock_post):
        """Test successful response from main LLM service"""
        # Mock main LLM service success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is a response from the main LLM service"
        }
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            result = get_enhanced_response("Hello", [])
        
        self.assertIn("main LLM service", result)
    
    @patch('requests.post')
    @patch('app.ui_views.check_local_llm_availability', return_value=True)
    @patch('app.ui_views.get_local_llm_response')
    def test_fallback_to_local_llm(self, mock_local_response, mock_local_available, mock_post):
        """Test fallback to local LLM when main LLM fails"""
        # Mock main LLM failure
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Mock local LLM success
        mock_local_response.return_value = "This is a response from local LLaMA3"
        
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            result = get_enhanced_response("Hello", [])
        
        self.assertIn("local LLaMA3", result)
        mock_local_response.assert_called_once()
    
    @patch('requests.post')
    @patch('app.ui_views.check_local_llm_availability', return_value=False)
    def test_fallback_to_demo(self, mock_local_available, mock_post):
        """Test fallback to demo responses when no LLM services available"""
        # Mock main LLM failure
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            result = get_enhanced_response("Hello", [])
        
        # Should get a demo response
        self.assertIn(result, [
            response for responses in DEMO_RESPONSES.values() 
            for response in responses
        ])
    
    def test_demo_mode_response(self):
        """Test demo mode response generation"""
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'false'}):
            result = get_enhanced_response("Hello", [])
        
        # Should get a demo response
        self.assertIn(result, [
            response for responses in DEMO_RESPONSES.values() 
            for response in responses
        ])
    
    def test_query_categorization(self):
        """Test that queries are properly categorized"""
        # Test greeting
        result = get_enhanced_response("Hello there", [])
        self.assertIn(result, DEMO_RESPONSES['greeting'])
        
        # Test service query
        result = get_enhanced_response("What services do you offer?", [])
        self.assertIn(result, DEMO_RESPONSES['services'])
        
        # Test scheme query
        result = get_enhanced_response("Tell me about welfare schemes", [])
        self.assertIn(result, DEMO_RESPONSES['schemes'])
        
        # Test document query
        result = get_enhanced_response("I need a birth certificate", [])
        self.assertIn(result, DEMO_RESPONSES['documents'])

class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
        self.assertIn('services', data)
        self.assertIn('main_llm', data['services'])
        self.assertIn('local_llm', data['services'])
    
    def test_llm_status_endpoint(self):
        """Test the LLM status endpoint"""
        response = self.client.get('/api/llm/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('main_llm_available', data)
        self.assertIn('local_llm_available', data)
        self.assertIn('recommendation', data)
    
    def test_ollama_setup_endpoint(self):
        """Test the Ollama setup information endpoint"""
        response = self.client.get('/api/ollama/setup')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('setup_instructions', data)
        self.assertIn('environment_variables', data)
        self.assertIn('benefits', data)
    
    def test_chat_send_endpoint(self):
        """Test the chat send endpoint"""
        response = self.client.post('/api/chat/send',
            json={'message': 'Hello'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('bot_response', data)
        self.assertIn('chat_history', data)
    
    def test_chat_send_empty_message(self):
        """Test chat send with empty message"""
        response = self.client.post('/api/chat/send',
            json={'message': ''},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_chat_send_invalid_json(self):
        """Test chat send with invalid JSON"""
        response = self.client.post('/api/chat/send',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_chat_history_endpoint(self):
        """Test the chat history endpoint"""
        response = self.client.get('/api/chat/history')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('chat_history', data)
    
    def test_chat_clear_endpoint(self):
        """Test the chat clear endpoint"""
        response = self.client.post('/api/chat/clear')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])

class TestModeSwitching(unittest.TestCase):
    """Test cases for mode switching functionality"""
    
    def setUp(self):
        """setUp method is abstract"""
        pass
    
    @patch('app.ui_views.get_service_status')
    def test_switch_to_demo_mode(self, mock_service_status):
        """Test switching to demo mode"""
        app = create_app()[0]
        app.config['TESTING'] = True
        client = app.test_client()
        
        response = client.post('/api/mode/demo')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['mode'], 'demo')
    
    @patch('app.ui_views.get_service_status')
    def test_switch_to_enhanced_mode_no_services(self, mock_service_status):
        """Test switching to enhanced mode when no services available"""
        app = create_app()[0]
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Mock no services available
        mock_service_status.return_value = {
            'main_llm_available': False,
            'local_llm_available': False
        }
        
        response = client.post('/api/mode/enhanced')
        self.assertEqual(response.status_code, 503)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('setup_instructions', data)

class TestEnvironmentConfiguration(unittest.TestCase):
    """Test cases for environment configuration"""
    
    def test_default_configuration(self):
        """Test default environment configuration"""
        from app.ui_views import LLM_SERVICE_URL, USE_ENHANCED_MODE, OLLAMA_BASE_URL, OLLAMA_MODEL
        
        self.assertEqual(LLM_SERVICE_URL, 'http://127.0.0.1:5000/query/')
        self.assertFalse(USE_ENHANCED_MODE)
        self.assertEqual(OLLAMA_BASE_URL, 'http://127.0.0.1:11434')
        self.assertEqual(OLLAMA_MODEL, 'llama3')
    
    @patch.dict(os.environ, {
        'LLM_SERVICE_URL': 'http://custom-llm:5000/query/',
        'USE_ENHANCED_MODE': 'true',
        'OLLAMA_BASE_URL': 'http://custom-ollama:11434',
        'OLLAMA_MODEL': 'llama3.1'
    })
    def test_custom_configuration(self):
        """Test custom environment configuration"""
        # Import after setting environment
        from app.ui_views import LLM_SERVICE_URL, USE_ENHANCED_MODE, OLLAMA_BASE_URL, OLLAMA_MODEL
        
        self.assertEqual(LLM_SERVICE_URL, 'http://custom-llm:5000/query/')
        self.assertTrue(USE_ENHANCED_MODE)
        self.assertEqual(OLLAMA_BASE_URL, 'http://custom-ollama:11434')
        self.assertEqual(OLLAMA_MODEL, 'llama3.1')

if __name__ == '__main__':
    # Set up test environment
    os.environ['FLASK_ENV'] = 'testing'
    
    # Run the tests
    unittest.main(verbosity=2)