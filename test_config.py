"""
Test Configuration and Fixtures for WhatsApp Chat UI Local AI Tests

This module provides shared test configuration, fixtures, and utilities
for the WhatsApp Chat UI Local AI testing suite.
"""

import os
import tempfile
import json
from unittest.mock import Mock, patch
import requests

# Test Configuration
TEST_CONFIG = {
    'TESTING': True,
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-secret-key',
    'SESSION_TYPE': 'filesystem',
    'DATABASE_URL': 'sqlite:///:memory:',
    'LLM_SERVICE_URL': 'http://127.0.0.1:5000/query/',
    'OLLAMA_BASE_URL': 'http://127.0.0.1:11434',
    'OLLAMA_MODEL': 'llama3',
    'USE_ENHANCED_MODE': False
}

# Mock Service Responses
MOCK_OLLAMA_RESPONSE = {
    "models": [
        {"name": "llama3:latest"},
        {"name": "llama3.1:latest"},
        {"name": "codellama:latest"}
    ]
}

MOCK_LLM_SUCCESS_RESPONSE = {
    "response": "This is a response from the main LLM service for MSPSDC assistance."
}

MOCK_LOCAL_LLM_SUCCESS_RESPONSE = {
    "message": {
        "content": "I can help you with MSPSDC services. As your local AI assistant, I have access to information about Meghalaya State Public Services Delivery Commission and can assist with queries about documents, schemes, and procedures."
    }
}

# Test Messages for Different Scenarios
TEST_MESSAGES = {
    'greeting': [
        "Hello",
        "Hi there",
        "Hey",
        "Good morning",
        "Greetings"
    ],
    'services': [
        "What services do you offer?",
        "Tell me about MSPSDC services",
        "I need help with government services",
        "What public services are available?"
    ],
    'documents': [
        "I need a birth certificate",
        "How do I apply for a caste certificate?",
        "What documents are required for certificate?",
        "Document verification process"
    ],
    'schemes': [
        "What welfare schemes are available?",
        "Tell me about government schemes",
        "Healthcare schemes in Meghalaya",
        "Education scholarships"
    ],
    'complex_queries': [
        "I am a farmer from Meghalaya and I need information about agricultural subsidies and how to apply for them through MSPSDC",
        "What is the complete process for getting a domicile certificate in Meghalaya including required documents and timeline?",
        "Can you help me understand the eligibility criteria for the Pradhan Mantri Jan Dhan Yojana as implemented in Meghalaya?"
    ]
}

# Expected Response Categories
EXPECTED_RESPONSE_TYPES = {
    'greeting': [
        "Hello! Welcome to MSPSDC Chat Assistant",
        "Hi there! I'm here to assist you",
        "Greetings! I'm your AI assistant"
    ],
    'services': [
        "MSPSDC offers various public services",
        "We provide comprehensive public services",
        "Our main services include"
    ],
    'documents': [
        "For document-related services",
        "Document services include",
        "You can apply for birth certificates"
    ],
    'schemes': [
        "Meghalaya has several welfare schemes",
        "Our state offers various social welfare schemes",
        "I can provide information about healthcare schemes"
    ]
}

class MockOllamaService:
    """Mock Ollama service for testing"""
    
    def __init__(self, available=True, models_available=True):
        self.available = available
        self.models_available = models_available
        self.call_count = 0
    
    def check_availability(self, *args, **kwargs):
        """Mock availability check"""
        self.call_count += 1
        if not self.available:
            raise requests.exceptions.ConnectionError("Ollama not available")
        
        if not self.models_available:
            return False
        
        return True
    
    def get_models(self, *args, **kwargs):
        """Mock getting models"""
        if not self.available:
            raise requests.exceptions.ConnectionError("Ollama not available")
        
        return MOCK_OLLAMA_RESPONSE
    
    def chat_completion(self, *args, **kwargs):
        """Mock chat completion"""
        if not self.available:
            raise requests.exceptions.ConnectionError("Ollama not available")
        
        return MOCK_LOCAL_LLM_SUCCESS_RESPONSE

class MockMainLLMService:
    """Mock main LLM service for testing"""
    
    def __init__(self, available=True, success=True):
        self.available = available
        self.success = success
        self.call_count = 0
    
    def query(self, *args, **kwargs):
        """Mock main LLM query"""
        self.call_count += 1
        if not self.available:
            raise requests.exceptions.ConnectionError("Main LLM not available")
        
        if not self.success:
            return {"error": "API Error"}
        
        return MOCK_LLM_SUCCESS_RESPONSE

# Pytest Fixtures (Converted to regular functions for unittest)
def create_app():
    """Create a test Flask application"""
    from app import create_app
    
    app = create_app()[0]
    app.config.update(TEST_CONFIG)
    
    return app

def create_test_client(app):
    """Create a test client"""
    return app.test_client()

def mock_ollama():
    """Mock Ollama service"""
    with patch('app.ui_views.requests.get') as mock_get, \
         patch('app.ui_views.requests.post') as mock_post:
        
        # Mock availability check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_OLLAMA_RESPONSE
        mock_get.return_value = mock_response
        
        # Mock chat completion
        mock_chat_response = Mock()
        mock_chat_response.status_code = 200
        mock_chat_response.json.return_value = MOCK_LOCAL_LLM_SUCCESS_RESPONSE
        mock_post.return_value = mock_chat_response
        
        yield {
            'available': True,
            'mock_get': mock_get,
            'mock_post': mock_post,
            'response': mock_response
        }

def mock_main_llm():
    """Mock main LLM service"""
    with patch('app.ui_views.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_LLM_SUCCESS_RESPONSE
        mock_post.return_value = mock_response
        
        yield {
            'available': True,
            'mock_post': mock_post,
            'response': mock_response
        }

def mock_services_unavailable():
    """Mock when all services are unavailable"""
    with patch('app.ui_views.requests.get') as mock_get, \
         patch('app.ui_views.requests.post') as mock_post:
        
        # Both services unavailable
        mock_get.side_effect = requests.exceptions.ConnectionError("Service unavailable")
        mock_post.side_effect = requests.exceptions.ConnectionError("Service unavailable")
        
        yield {
            'main_unavailable': True,
            'local_unavailable': True,
            'mock_get': mock_get,
            'mock_post': mock_post
        }

def sample_chat_history():
    """Sample chat history for testing"""
    return [
        {
            "type": "user",
            "message": "Hello, I need help with MSPSDC services",
            "timestamp": "2025-12-18T12:00:00.000000"
        },
        {
            "type": "bot", 
            "message": "Hello! I'm here to assist you with Meghalaya State Public Services. What can I help you with?",
            "timestamp": "2025-12-18T12:00:01.000000"
        },
        {
            "type": "user",
            "message": "I need information about document services",
            "timestamp": "2025-12-18T12:00:05.000000"
        }
    ]

def test_environment():
    """Set up test environment variables"""
    original_env = dict(os.environ)
    
    # Set test environment variables
    os.environ.update({
        'FLASK_ENV': 'testing',
        'DATABASE_URL': 'sqlite:///:memory:',
        'USE_ENHANCED_MODE': 'false',
        'OLLAMA_BASE_URL': 'http://127.0.0.1:11434',
        'OLLAMA_MODEL': 'llama3',
        'LLM_SERVICE_URL': 'http://127.0.0.1:5000/query/'
    })
    
    def cleanup():
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
    
    # Return cleanup function for use in test teardown
    return cleanup

# Utility Functions for Testing
def assert_response_structure(response_data, expected_keys):
    """Assert that response has expected structure"""
    for key in expected_keys:
        assert key in response_data, f"Missing key: {key}"

def assert_chat_history_structure(chat_history):
    """Assert that chat history has correct structure"""
    for message in chat_history:
        assert 'type' in message, "Message missing 'type' field"
        assert 'message' in message, "Message missing 'message' field"
        assert 'timestamp' in message, "Message missing 'timestamp' field"
        assert message['type'] in ['user', 'bot', 'system'], f"Invalid message type: {message['type']}"

def create_test_message(message_type, content, timestamp=None):
    """Create a test message"""
    return {
        'type': message_type,
        'message': content,
        'timestamp': timestamp or "2025-12-18T12:00:00.000000"
    }

def verify_service_status_response(data):
    """Verify service status response structure"""
    assert 'main_llm_available' in data
    assert 'local_llm_available' in data
    assert 'active_service' in data
    assert 'service_status' in data
    assert 'recommendation' in data

def verify_health_response(data):
    """Verify health check response structure"""
    assert data['status'] == 'healthy'
    assert 'service' in data
    assert 'mode' in data
    assert 'services' in data
    assert 'main_llm' in data['services']
    assert 'local_llm' in data['services']

def verify_ollama_setup_response(data):
    """Verify Ollama setup response structure"""
    assert 'setup_instructions' in data
    assert 'environment_variables' in data
    assert 'benefits' in data
    
    setup_instructions = data['setup_instructions']
    required_steps = ['install_ollama', 'start_ollama', 'install_llama3', 'verify_installation']
    for step in required_steps:
        assert step in setup_instructions, f"Missing setup step: {step}"

# Test Data Generators
def generate_conversation_history(num_exchanges=5):
    """Generate a conversation history for testing"""
    history = []
    for i in range(num_exchanges):
        # Add user message
        history.append(create_test_message(
            'user', 
            f"User question {i+1}",
            f"2025-12-18T12:00:{i*2:02d}.000000"
        ))
        
        # Add bot response
        history.append(create_test_message(
            'bot',
            f"Bot response {i+1}",
            f"2025-12-18T12:00:{i*2+1:02d}.000000"
        ))
    
    return history

def generate_stress_test_messages(count=50):
    """Generate messages for stress testing"""
    messages = []
    message_templates = [
        "Hello, I need help with {service}",
        "What documents do I need for {document}?",
        "Tell me about {scheme}",
        "How do I apply for {service}?",
        "What is the process for {document}?",
        "Can you explain {scheme}?",
        "I need information about {service}",
        "Help me understand {document} requirements"
    ]
    
    services = ["birth certificate", "caste certificate", "income certificate", "domicile certificate"]
    documents = ["birth certificate", "caste certificate", "income certificate", "domicile certificate", "character certificate"]
    schemes = ["PM Jan Dhan Yojana", "Ayushman Bharat", "Mahatma Gandhi National Rural Employment Guarantee Act"]
    
    for i in range(count):
        template = message_templates[i % len(message_templates)]
        
        if '{service}' in template:
            content = template.format(service=services[i % len(services)])
        elif '{document}' in template:
            content = template.format(document=documents[i % len(documents)])
        elif '{scheme}' in template:
            content = template.format(scheme=schemes[i % len(schemes)])
        else:
            content = template
        
        messages.append({
            'message': content,
            'expected_category': categorize_test_message(content)
        })
    
    return messages

def categorize_test_message(message):
    """Categorize test message for validation"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return 'greeting'
    elif any(word in message_lower for word in ['service', 'services', 'help', 'assistance']):
        return 'services'
    elif any(word in message_lower for word in ['document', 'certificate', 'documents', 'certificates']):
        return 'documents'
    elif any(word in message_lower for word in ['scheme', 'schemes', 'welfare', 'benefits', 'program']):
        return 'schemes'
    else:
        return 'default'

# Configuration for different test scenarios
SCENARIO_CONFIGS = {
    'basic_functionality': {
        'main_llm_available': False,
        'local_llm_available': False,
        'enhanced_mode': False,
        'expected_service': 'demo'
    },
    'enhanced_mode': {
        'main_llm_available': True,
        'local_llm_available': True,
        'enhanced_mode': True,
        'expected_service': 'main_llm'
    },
    'local_ai_mode': {
        'main_llm_available': False,
        'local_llm_available': True,
        'enhanced_mode': False,
        'expected_service': 'local_llm'
    },
    'fallback_mode': {
        'main_llm_available': True,
        'local_llm_available': False,
        'enhanced_mode': True,
        'expected_service': 'main_llm'
    },
    'all_unavailable': {
        'main_llm_available': False,
        'local_llm_available': False,
        'enhanced_mode': True,
        'expected_service': 'demo'
    }
}

# Performance Test Parameters
PERFORMANCE_THRESHOLDS = {
    'response_time_max': 5.0,  # seconds
    'concurrent_requests': 10,
    'memory_messages': 100,
    'stress_test_messages': 50
}

# Error Scenarios for Testing
ERROR_SCENARIOS = {
    'invalid_json': {
        'data': 'invalid json',
        'content_type': 'application/json',
        'expected_status': 400
    },
    'empty_message': {
        'data': {'message': ''},
        'content_type': 'application/json',
        'expected_status': 400
    },
    'missing_message_field': {
        'data': {},
        'content_type': 'application/json',
        'expected_status': 400
    },
    'wrong_content_type': {
        'data': {'message': 'test'},
        'content_type': 'text/plain',
        'expected_status': 415
    }
}