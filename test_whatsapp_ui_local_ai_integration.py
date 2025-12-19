"""
Integration Tests for WhatsApp Chat UI - Local AI Mode

This module contains integration tests for the WhatsApp Chat UI with Local AI mode,
testing the complete system functionality including web interface, API integration,
and end-to-end workflows.

Test Coverage:
- Complete chat workflows
- Service integration testing
- UI interaction simulation
- Error handling and recovery
- Performance and reliability testing
- Real-world usage scenarios
"""

import unittest
import json
import time
import threading
from unittest.mock import patch, Mock
import requests
from flask import url_for
import os
import sys

# Import the Flask app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

class TestChatWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete chat workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_basic_chat_workflow(self):
        """Test basic chat workflow from UI to response"""
        # Simulate sending a message through the API
        response = self.client.post('/api/chat/send',
            json={'message': 'Hello, I need help with MSPSDC services'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('bot_response', data)
        self.assertIn('chat_history', data)
        self.assertEqual(len(data['chat_history']), 2)  # User + Bot message
        
        # Verify chat history structure
        user_message = data['chat_history'][0]
        bot_message = data['chat_history'][1]
        
        self.assertEqual(user_message['type'], 'user')
        self.assertEqual(user_message['message'], 'Hello, I need help with MSPSDC services')
        self.assertIn('timestamp', user_message)
        
        self.assertEqual(bot_message['type'], 'bot')
        self.assertIn('timestamp', bot_message)
    
    def test_conversation_history_persistence(self):
        """Test that conversation history persists across requests"""
        # Send first message
        response1 = self.client.post('/api/chat/send',
            json={'message': 'Hello'},
            content_type='application/json'
        )
        
        self.assertEqual(response1.status_code, 200)
        history1 = json.loads(response1.data)['chat_history']
        
        # Send second message
        response2 = self.client.post('/api/chat/send',
            json={'message': 'Tell me about services'},
            content_type='application/json'
        )
        
        self.assertEqual(response2.status_code, 200)
        history2 = json.loads(response2.data)['chat_history']
        
        # Should have accumulated messages
        self.assertEqual(len(history2), 4)  # 2 previous + 2 new
        self.assertEqual(history2[0]['message'], 'Hello')
        self.assertEqual(history2[2]['message'], 'Tell me about services')
    
    def test_chat_clear_functionality(self):
        """Test chat history clearing"""
        # Add some messages first
        self.client.post('/api/chat/send',
            json={'message': 'Test message'},
            content_type='application/json'
        )
        
        # Verify messages exist
        response = self.client.get('/api/chat/history')
        self.assertEqual(response.status_code, 200)
        history = json.loads(response.data)['chat_history']
        self.assertGreater(len(history), 0)
        
        # Clear chat
        response = self.client.post('/api/chat/clear')
        self.assertEqual(response.status_code, 200)
        
        # Verify messages are cleared
        response = self.client.get('/api/chat/history')
        self.assertEqual(response.status_code, 200)
        history = json.loads(response.data)['chat_history']
        self.assertEqual(len(history), 0)
    
    def test_error_handling_invalid_message(self):
        """Test error handling for invalid messages"""
        # Test empty message
        response = self.client.post('/api/chat/send',
            json={'message': ''},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test missing message field
        response = self.client.post('/api/chat/send',
            json={},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test invalid JSON
        response = self.client.post('/api/chat/send',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

class TestServiceIntegration(unittest.TestCase):
    """Integration tests for service monitoring and integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_service_status_monitoring(self):
        """Test service status monitoring across all endpoints"""
        # Test health endpoint
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        health_data = json.loads(response.data)
        
        self.assertIn('active_service', health_data)
        self.assertIn('services', health_data)
        self.assertIn('main_llm', health_data['services'])
        self.assertIn('local_llm', health_data['services'])
        
        # Test LLM status endpoint
        response = self.client.get('/api/llm/status')
        self.assertEqual(response.status_code, 200)
        llm_data = json.loads(response.data)
        
        self.assertIn('main_llm_available', llm_data)
        self.assertIn('local_llm_available', llm_data)
        self.assertIn('recommendation', llm_data)
        
        # Test Ollama setup endpoint
        response = self.client.get('/api/ollama/setup')
        self.assertEqual(response.status_code, 200)
        setup_data = json.loads(response.data)
        
        self.assertIn('setup_instructions', setup_data)
        self.assertIn('environment_variables', setup_data)
        self.assertIn('benefits', setup_data)
    
    @patch('requests.get')
    @patch('requests.post')
    def test_intelligent_fallback_integration(self, mock_post, mock_get):
        """Test the complete fallback hierarchy integration"""
        # Mock Ollama as available
        mock_ollama_response = Mock()
        mock_ollama_response.status_code = 200
        mock_ollama_response.json.return_value = {
            "models": [{"name": "llama3:latest"}]
        }
        mock_get.return_value = mock_ollama_response
        
        # Mock main LLM as unavailable
        mock_post.side_effect = requests.exceptions.ConnectionError("Main LLM unavailable")
        
        # Mock local LLM success
        mock_local_response = Mock()
        mock_local_response.status_code = 200
        mock_local_response.json.return_value = {
            "message": {"content": "This is a response from local LLaMA3"}
        }
        mock_post.return_value = mock_local_response
        
        # Set enhanced mode
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            # Send a message that should trigger fallback to local LLM
            response = self.client.post('/api/chat/send',
                json={'message': 'Hello from integration test'},
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('local LLaMA3', data['bot_response'])
    
    def test_ui_interface_accessibility(self):
        """Test that the UI interface is accessible"""
        # Test main chat interface
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MSPSDC Chat Assistant', response.data)
        self.assertIn(b'chat-container', response.data)
        
        # Verify key UI elements are present
        self.assertIn(b'chat-messages', response.data)
        self.assertIn(b'chat-input', response.data)
        self.assertIn(b'send-button', response.data)
        self.assertIn(b'mode-badge', response.data)

class TestPerformanceAndReliability(unittest.TestCase):
    """Integration tests for performance and reliability"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        def send_message(message):
            return self.client.post('/api/chat/send',
                json={'message': message},
                content_type='application/json'
            )
        
        # Create multiple concurrent requests
        threads = []
        messages = [f"Message {i}" for i in range(10)]
        
        for message in messages:
            thread = threading.Thread(target=send_message, args=(message,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests completed successfully
        # (In a real scenario, we'd check specific responses)
        # This is a basic check that the system didn't crash
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
    
    def test_response_time_performance(self):
        """Test response time performance"""
        start_time = time.time()
        
        response = self.client.post('/api/chat/send',
            json={'message': 'Performance test message'},
            content_type='application/json'
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5.0)  # Should respond within 5 seconds
    
    def test_memory_usage_with_large_history(self):
        """Test system behavior with large conversation history"""
        # Send many messages to build up history
        for i in range(100):
            response = self.client.post('/api/chat/send',
                json={'message': f'Long conversation message {i}'},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Verify system still responds
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        # Verify chat still works
        response = self.client.post('/api/chat/send',
            json={'message': 'Final test message'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

class TestRealWorldScenarios(unittest.TestCase):
    """Integration tests for real-world usage scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_mspsdc_service_inquiry_workflow(self):
        """Test typical MSPSDC service inquiry workflow"""
        workflow_messages = [
            "Hello, I need help with government services",
            "What documents do I need for a caste certificate?",
            "How long does the application process take?",
            "Can I apply online or do I need to visit in person?",
            "Thank you for the information"
        ]
        
        responses = []
        for message in workflow_messages:
            response = self.client.post('/api/chat/send',
                json={'message': message},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            responses.append(data['bot_response'])
        
        # Verify responses are contextually appropriate
        self.assertIn('MSPSDC', responses[0])
        self.assertIn('document', responses[1].lower())
        self.assertIn('application', responses[2].lower())
    
    def test_error_recovery_workflow(self):
        """Test system recovery from various error conditions"""
        # Test 1: Empty message
        response = self.client.post('/api/chat/send',
            json={'message': ''},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test 2: Invalid JSON
        response = self.client.post('/api/chat/send',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test 3: Recovery - valid message should still work
        response = self.client.post('/api/chat/send',
            json={'message': 'System recovery test'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_session_isolation(self):
        """Test that sessions are properly isolated"""
        # Create two different clients to simulate different users
        client1 = self.app.test_client()
        client2 = self.app.test_client()
        
        # User 1 sends a message
        response1 = client1.post('/api/chat/send',
            json={'message': 'Message from user 1'},
            content_type='application/json'
        )
        
        # User 2 sends a message
        response2 = client2.post('/api/chat/send',
            json={'message': 'Message from user 2'},
            content_type='application/json'
        )
        
        # Verify both got responses
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Verify histories are separate
        # (Note: In production, you'd want more sophisticated session management)
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        # Each should have their own conversation
        user1_messages = [msg['message'] for msg in data1['chat_history']]
        user2_messages = [msg['message'] for msg in data2['chat_history']]
        
        self.assertIn('Message from user 1', user1_messages)
        self.assertIn('Message from user 2', user2_messages)

class TestEnvironmentIntegration(unittest.TestCase):
    """Integration tests for environment configuration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Store original environment
        self.original_env = dict(os.environ)
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_enhanced_mode_environment_integration(self):
        """Test integration with enhanced mode environment variable"""
        # Test with enhanced mode enabled
        os.environ['USE_ENHANCED_MODE'] = 'true'
        
        app = create_app()[0]
        client = app.test_client()
        
        # Test that enhanced mode is recognized
        response = client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['enhanced_mode'])
    
    def test_ollama_configuration_integration(self):
        """Test integration with Ollama environment configuration"""
        # Test with custom Ollama configuration
        os.environ['OLLAMA_BASE_URL'] = 'http://custom-ollama:11434'
        os.environ['OLLAMA_MODEL'] = 'llama3.1'
        
        app = create_app()[0]
        client = app.test_client()
        
        # Test that custom configuration is reflected
        response = client.get('/api/ollama/setup')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(
            data['environment_variables']['OLLAMA_MODEL']['current'],
            'llama3.1'
        )
    
    def test_main_llm_service_configuration_integration(self):
        """Test integration with main LLM service configuration"""
        # Test with custom main LLM service configuration
        os.environ['LLM_SERVICE_URL'] = 'http://custom-llm:5000/query/'
        
        app = create_app()[0]
        client = app.test_client()
        
        # Test that custom configuration is reflected
        response = client.get('/api/llm/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(
            data['main_service_url'],
            'http://custom-llm:5000/query/'
        )

class TestFallbackMechanismIntegration(unittest.TestCase):
    """Integration tests for the complete fallback mechanism"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    @patch('requests.get')
    @patch('requests.post')
    def test_complete_fallback_chain(self, mock_post, mock_get):
        """Test complete fallback chain: Main LLM -> Local LLM -> Demo"""
        # Scenario 1: All services unavailable -> Demo fallback
        mock_get.side_effect = requests.exceptions.ConnectionError("No Ollama")
        mock_post.side_effect = requests.exceptions.ConnectionError("No Main LLM")
        
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            response = self.client.post('/api/chat/send',
                json={'message': 'Test fallback to demo'},
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Should get a demo response (not LLM response)
        demo_responses = []
        for category in DEMO_RESPONSES.values():
            demo_responses.extend(category)
        self.assertIn(data['bot_response'], demo_responses)
    
    @patch('requests.get')
    @patch('requests.post')
    def test_partial_service_recovery(self, mock_post, mock_get):
        """Test system behavior when services become available"""
        # Initial state: No services
        mock_get.side_effect = requests.exceptions.ConnectionError("No Ollama")
        mock_post.side_effect = requests.exceptions.ConnectionError("No Main LLM")
        
        with patch.dict(os.environ, {'USE_ENHANCED_MODE': 'true'}):
            # Test initial fallback
            response1 = self.client.post('/api/chat/send',
                json={'message': 'Initial message'},
                content_type='application/json'
            )
            
            # Simulate Ollama becoming available
            mock_ollama_response = Mock()
            mock_ollama_response.status_code = 200
            mock_ollama_response.json.return_value = {
                "models": [{"name": "llama3:latest"}]
            }
            mock_get.return_value = mock_ollama_response
            
            # Mock local LLM success
            mock_local_response = Mock()
            mock_local_response.status_code = 200
            mock_local_response.json.return_value = {
                "message": {"content": "Now using local LLaMA3"}
            }
            mock_post.return_value = mock_local_response
            
            # Test recovery
            response2 = self.client.post('/api/chat/send',
                json={'message': 'Recovery message'},
                content_type='application/json'
            )
        
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        self.assertIn("local LLaMA3", data2['bot_response'])

if __name__ == '__main__':
    # Set up test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    # Run the tests with verbose output
    unittest.main(verbosity=2, buffer=True)