"""
Mock Service Implementations for Testing

This module provides mock implementations of external services (Ollama, main LLM service)
for testing purposes without requiring actual service dependencies.
"""

import json
import time
import threading
from unittest.mock import Mock, patch
import requests
from datetime import datetime

class MockOllamaServer:
    """Mock Ollama server for testing"""
    
    def __init__(self, port=11434, available_models=None):
        self.port = port
        self.available = True
        self.models = available_models or ['llama3:latest', 'llama3.1:latest']
        self.call_log = []
        self.request_count = 0
        
    def start(self):
        """Start mock server (simulation)"""
        self.available = True
        
    def stop(self):
        """Stop mock server"""
        self.available = False
        
    def add_model(self, model_name):
        """Add a model to available models"""
        if model_name not in self.models:
            self.models.append(model_name)
            
    def remove_model(self, model_name):
        """Remove a model from available models"""
        if model_name in self.models:
            self.models.remove(model_name)
    
    def simulate_availability_check(self):
        """Simulate availability check"""
        self.request_count += 1
        self.call_log.append({
            'method': 'GET',
            'endpoint': '/api/tags',
            'timestamp': datetime.now().isoformat(),
            'available': self.available
        })
        
        if not self.available:
            raise requests.exceptions.ConnectionError("Connection refused")
        
        return {
            "models": [{"name": model} for model in self.models]
        }
    
    def simulate_chat_completion(self, model, messages, stream=False):
        """Simulate chat completion"""
        self.request_count += 1
        self.call_log.append({
            'method': 'POST',
            'endpoint': '/api/chat',
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'message_count': len(messages),
            'stream': stream
        })
        
        if not self.available:
            raise requests.exceptions.ConnectionError("Connection refused")
        
        if model not in self.models:
            raise Exception(f"Model {model} not found")
        
        # Generate contextual response based on messages
        system_message = ""
        user_message = ""
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            elif msg['role'] == 'user':
                user_message = msg['content']
        
        # Generate appropriate response
        response = self._generate_response(user_message, system_message)
        
        return {
            "message": {
                "content": response,
                "role": "assistant"
            },
            "model": model,
            "created_at": datetime.now().isoformat(),
            "done": True
        }
    
    def _generate_response(self, user_message, system_message):
        """Generate contextual response"""
        message_lower = user_message.lower()
        
        # MSPSDC-specific responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your local AI assistant for MSPSDC (Meghalaya State Public Services Delivery Commission). I can help you with information about public services, document applications, welfare schemes, and procedures. How may I assist you today?"
        
        elif any(word in message_lower for word in ['service', 'services']):
            return "MSPSDC provides various public services including document verification, certificate issuance (birth, caste, income, domicile), application processing, and citizen support services. You can apply for most services online through our digital platform. What specific service do you need assistance with?"
        
        elif any(word in message_lower for word in ['document', 'certificate', 'birth', 'caste', 'income', 'domicile']):
            return "For document-related services, you can apply for:\n\n• Birth Certificate - Required documents: Parents' ID, Address proof\n• Caste Certificate - Required documents: Community certificate, Income proof\n• Income Certificate - Required documents: Income statements, Address proof\n• Domicile Certificate - Required documents: Residence proof, Family details\n\nAll applications can be submitted online. Would you like details about any specific document?"
        
        elif any(word in message_lower for word in ['scheme', 'schemes', 'welfare', 'benefits', 'program']):
            return "Meghalaya offers various welfare schemes:\n\n• Healthcare: Ayushman Bharat, Chief Minister's Health Insurance\n• Education: Scholarship schemes, Mid-day meal program\n• Livelihood: MGNREGA, Self-help group support\n• Social Security: Pension schemes, Disability benefits\n\nSpecific eligibility criteria and application processes vary. Which scheme interests you?"
        
        elif any(word in message_lower for word in ['application', 'apply', 'process', 'procedure']):
            return "The application process typically involves:\n\n1. Visit MSPSDC portal or service center\n2. Fill online application form\n3. Upload required documents\n4. Pay applicable fees (if any)\n5. Track application status online\n6. Collect certificate/ documents upon approval\n\nProcessing time varies by service type. Most certificates are issued within 7-15 working days. Do you need help with a specific application?"
        
        else:
            return "As your MSPSDC AI assistant, I'm here to help with information about:\n\n• Public services and procedures\n• Document applications and requirements  \n• Welfare schemes and benefits\n• Online application processes\n• Status tracking and support\n\nCould you please specify what information you need about Meghalaya State Public Services?"

class MockMainLLMService:
    """Mock main LLM service for testing"""
    
    def __init__(self, port=5000):
        self.port = port
        self.available = True
        self.call_log = []
        self.request_count = 0
        
    def start(self):
        """Start mock service"""
        self.available = True
        
    def stop(self):
        """Stop mock service"""
        self.available = False
    
    def simulate_query(self, query_data):
        """Simulate main LLM query"""
        self.request_count += 1
        self.call_log.append({
            'timestamp': datetime.now().isoformat(),
            'query': query_data.get('query'),
            'query_type': query_data.get('query_type'),
            'message_history_length': len(query_data.get('message_history', []))
        })
        
        if not self.available:
            raise Exception("Main LLM service unavailable")
        
        # Simulate processing delay
        time.sleep(0.1)
        
        query = query_data.get('query', '')
        query_type = query_data.get('query_type', 'general')
        
        # Generate more sophisticated response for main LLM
        response = self._generate_advanced_response(query, query_type)
        
        return {
            "response": response,
            "query_type": query_type,
            "processing_time": 0.1,
            "model": "main-llm-service",
            "confidence": 0.95
        }
    
    def _generate_advanced_response(self, query, query_type):
        """Generate advanced response from main LLM"""
        query_lower = query.lower()
        
        if 'hello' in query_lower or 'hi' in query_lower or 'greetings' in query_lower:
            return "Hello! I'm the main AI assistant for MSPSDC, powered by advanced language models. I'm here to provide comprehensive information about Meghalaya State Public Services Delivery Commission. How can I assist you with your government service needs today?"
        
        elif 'service' in query_lower or 'services' in query_lower:
            return "MSPSDC offers a comprehensive suite of digital public services including:\n\n📋 **Document Services**: Birth certificates, caste certificates, income certificates, domicile certificates\n🏥 **Healthcare Services**: Medical facility registrations, health scheme enrollments\n🎓 **Education Services**: Scholarship applications, educational certificate verifications\n💼 **Employment Services**: Job registration, skill development program enrollments\n🏛️ **Administrative Services**: Grievance redressal, public service complaints\n\nAll services are integrated into our unified digital platform for seamless citizen experience. What specific service area interests you?"
        
        elif 'document' in query_lower or 'certificate' in query_lower:
            return "**Document Services at MSPSDC:**\n\n**Available Documents:**\n• Birth Certificate - Proof of birth and age\n• Caste Certificate - Social category verification  \n• Income Certificate - Financial status proof\n• Domicile Certificate - Permanent residence proof\n• Character Certificate - Background verification\n• Marriage Certificate - Marital status proof\n\n**Application Process:**\n1. Online application through MSPSDC portal\n2. Document upload and verification\n3. Payment processing (where applicable)\n4. Status tracking and updates\n5. Digital certificate delivery\n\n**Processing Time:** 3-7 working days for most certificates\n\nWhich document do you need assistance with?"
        
        elif 'scheme' in query_lower or 'welfare' in query_lower or 'benefit' in query_lower:
            return "**Welfare Schemes in Meghalaya:**\n\n**Healthcare Schemes:**\n• Pradhan Mantri Jan Arogya Yojana (PMJAY)\n• Chief Minister's Universal Health Insurance Scheme\n• National Health Mission programs\n\n**Education Schemes:**  \n• Post-Matric Scholarship for SC/ST students\n• Merit-based scholarships\n• Mid-day meal program\n\n**Livelihood Schemes:**\n• Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)\n• Self-help group support programs\n• Rural development initiatives\n\n**Social Security:**\n• Old age pension schemes\n• Disability benefits\n• Widow pension programs\n\nDetailed eligibility criteria and application processes vary by scheme. Which scheme would you like to know more about?"
        
        elif 'application' in query_lower or 'apply' in query_lower:
            return "**Online Application Process:**\n\n**Step-by-Step Guide:**\n1. **Registration**: Create account on MSPSDC portal\n2. **Service Selection**: Choose required service from catalog\n3. **Form Filling**: Complete online application with accurate details\n4. **Document Upload**: Upload all required documents in specified formats\n5. **Fee Payment**: Pay applicable fees through secure online payment gateway\n6. **Submission**: Submit application and note reference number\n7. **Tracking**: Monitor application status through your dashboard\n8. **Delivery**: Receive digital certificates via email or collect physical copies\n\n**Important Notes:**\n• All information must be accurate and verifiable\n• Document formats and sizes must meet specifications\n• Processing times vary by service complexity\n• Most services are free or have nominal fees\n\nNeed help with a specific application? I can guide you through the process."
        
        elif 'status' in query_lower or 'track' in query_lower or 'progress' in query_lower:
            return "**Application Status Tracking:**\n\n**Methods to Check Status:**\n• **Online Portal**: Login to your MSPSDC account\n• **Reference Number**: Use application ID for quick lookup\n• **SMS Notifications**: Receive updates via registered mobile number\n• **Email Alerts**: Get status updates in registered email\n\n**Status Stages:**\n• **Submitted**: Application received and under initial review\n• **Under Process**: Documents verified and application processing\n• **Pending**: Additional documents or information required\n• **Approved**: Application approved, certificate in preparation  \n• **Ready for Collection**: Certificate ready for pickup or delivery\n• **Delivered**: Certificate successfully delivered\n\nFor immediate assistance, contact MSPSDC helpline at 1800-345-xxxx. What's your application reference number?"
        
        else:
            return "I'm here to help with comprehensive information about MSPSDC services. I can assist you with:\n\n• **Service Information**: Detailed explanations of available public services\n• **Application Guidance**: Step-by-step help with online applications  \n• **Document Requirements**: Specific document lists for different services\n• **Scheme Details**: Welfare program information and eligibility criteria\n• **Process Clarification**: Explanation of government procedures and timelines\n• **Status Updates**: Help tracking your application progress\n\nCould you please provide more specific details about what MSPSDC service or information you need? This will help me provide you with the most accurate and relevant assistance."

# Test Scenarios with Mock Services
TEST_SCENARIOS = {
    'ollama_available': {
        'ollama_available': True,
        'ollama_models': ['llama3:latest'],
        'main_llm_available': False,
        'expected_service': 'local_llm',
        'description': 'Test when Ollama is available but main LLM is not'
    },
    
    'main_llm_available': {
        'ollama_available': False,
        'main_llm_available': True,
        'enhanced_mode': True,
        'expected_service': 'main_llm', 
        'description': 'Test when main LLM is available in enhanced mode'
    },
    
    'all_services_available': {
        'ollama_available': True,
        'ollama_models': ['llama3:latest'],
        'main_llm_available': True,
        'enhanced_mode': True,
        'expected_service': 'main_llm',
        'description': 'Test when all services are available (should prefer main LLM)'
    },
    
    'no_services_available': {
        'ollama_available': False,
        'main_llm_available': False,
        'enhanced_mode': True,
        'expected_service': 'demo',
        'description': 'Test fallback to demo when no services available'
    },
    
    'ollama_connection_error': {
        'ollama_connection_error': True,
        'main_llm_available': False,
        'expected_service': 'demo',
        'description': 'Test handling of Ollama connection errors'
    },
    
    'main_llm_timeout': {
        'main_llm_timeout': True,
        'ollama_available': True,
        'enhanced_mode': True,
        'expected_service': 'local_llm',
        'description': 'Test fallback to local LLM when main LLM times out'
    }
}

def create_mock_response_scenario(scenario_name):
    """Create mock responses for a specific scenario"""
    scenario = TEST_SCENARIOS.get(scenario_name, {})
    
    def mock_ollama_get(*args, **kwargs):
        """Mock Ollama GET request"""
        if scenario.get('ollama_available'):
            if scenario.get('ollama_connection_error'):
                raise requests.exceptions.ConnectionError("Connection failed")
            
            return Mock(
                status_code=200,
                json=lambda: {
                    "models": [{"name": model} for model in scenario.get('ollama_models', ['llama3:latest'])]
                }
            )
        else:
            raise requests.exceptions.ConnectionError("Ollama not available")
    
    def mock_ollama_post(*args, **kwargs):
        """Mock Ollama POST request"""
        if not scenario.get('ollama_available'):
            raise requests.exceptions.ConnectionError("Ollama not available")
        
        if scenario.get('ollama_connection_error'):
            raise requests.exceptions.ConnectionError("Connection failed")
        
        # Simulate response based on messages
        data = kwargs.get('json', {})
        messages = data.get('messages', [])
        
        # Generate response based on last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        response_content = f"This is a response from local LLaMA3 regarding: {user_message[:50]}..."
        
        return Mock(
            status_code=200,
            json=lambda: {
                "message": {
                    "content": response_content,
                    "role": "assistant"
                }
            }
        )
    
    def mock_main_llm_post(*args, **kwargs):
        """Mock main LLM POST request"""
        if scenario.get('main_llm_timeout'):
            raise requests.exceptions.Timeout("Request timed out")
        
        if not scenario.get('main_llm_available'):
            raise requests.exceptions.ConnectionError("Main LLM not available")
        
        # Simulate successful response
        return Mock(
            status_code=200,
            json=lambda: {
                "response": "This is a response from the main LLM service with advanced AI capabilities."
            }
        )
    
    return {
        'mock_ollama_get': mock_ollama_get,
        'mock_ollama_post': mock_ollama_post,
        'mock_main_llm_post': mock_main_llm_post,
        'scenario': scenario
    }

# Utility functions for testing
def simulate_ollama_startup():
    """Simulate Ollama service startup"""
    mock_server = MockOllamaServer()
    mock_server.start()
    return mock_server

def simulate_ollama_shutdown():
    """Simulate Ollama service shutdown"""
    mock_server = MockOllamaServer()
    mock_server.stop()
    return mock_server

def create_test_conversation():
    """Create a test conversation for testing"""
    return [
        {"role": "user", "content": "Hello, I need help with MSPSDC services"},
        {"role": "assistant", "content": "Hello! I'm here to help you with MSPSDC services. What specific assistance do you need?"},
        {"role": "user", "content": "I need information about birth certificate application"},
        {"role": "assistant", "content": "For birth certificate application, you need to provide parent identification documents and address proof. You can apply online through the MSPSDC portal."}
    ]

def generate_load_test_messages(count=100):
    """Generate messages for load testing"""
    messages = []
    base_messages = [
        "Hello, I need help with MSPSDC services",
        "What documents do I need for a birth certificate?",
        "Tell me about welfare schemes in Meghalaya",
        "How do I track my application status?",
        "What is the process for getting a caste certificate?",
        "Can you help me understand the online application process?",
        "What are the working hours of MSPSDC centers?",
        "How do I contact MSPSDC support?",
        "What documents are required for income certificate?",
        "Tell me about education scholarship schemes"
    ]
    
    for i in range(count):
        base_message = base_messages[i % len(base_messages)]
        messages.append({
            "role": "user",
            "content": f"{base_message} (Test message {i+1})",
            "timestamp": f"2025-12-18T12:{i//60:02d}:{i%60:02d}.000000"
        })
    
    return messages

# Performance testing utilities
class PerformanceMonitor:
    """Monitor performance metrics during testing"""
    
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'request_counts': {}
        }
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
    
    def record_response_time(self, endpoint, response_time):
        """Record response time for an endpoint"""
        if endpoint not in self.metrics['response_times']:
            self.metrics['response_times'][endpoint] = []
        self.metrics['response_times'][endpoint].append(response_time)
    
    def get_average_response_time(self, endpoint):
        """Get average response time for an endpoint"""
        times = self.metrics['response_times'].get(endpoint, [])
        return sum(times) / len(times) if times else 0
    
    def generate_performance_report(self):
        """Generate performance report"""
        total_time = time.time() - self.start_time
        
        report = {
            'total_duration': total_time,
            'average_response_times': {},
            'total_requests': 0,
            'requests_per_second': 0
        }
        
        for endpoint, times in self.metrics['response_times'].items():
            report['average_response_times'][endpoint] = sum(times) / len(times)
            report['total_requests'] += len(times)
        
        if total_time > 0:
            report['requests_per_second'] = report['total_requests'] / total_time
        
        return report