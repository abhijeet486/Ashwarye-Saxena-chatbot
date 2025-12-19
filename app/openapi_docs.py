"""
OpenAPI/Swagger Documentation for WhatsApp Chat UI

This module provides comprehensive API documentation using OpenAPI 3.0
and Swagger UI for the WhatsApp Chat UI with Local AI mode.
"""

from flask_restx import Api, Resource, fields, Namespace
from flask import request, jsonify
import os
import json

# Create API instance
api = Api(
    version='1.0',
    title='WhatsApp Chat UI API',
    description='''
    WhatsApp Chat UI with Local AI Mode - Comprehensive API Documentation
    
    This API provides a complete chat interface with intelligent fallback capabilities:
    
    ## Features
    - **Chat Interface**: Send and receive messages with AI-powered responses
    - **Local AI Support**: Integration with self-hosted LLaMA3 via Ollama
    - **Intelligent Fallback**: Main LLM → Local LLM → Demo responses
    - **Service Monitoring**: Real-time status of all services
    - **Mode Switching**: Runtime switching between Demo and Enhanced modes
    - **MSPSDC Integration**: Specialized responses for Meghalaya State Public Services
    
    ## Service Architecture
    - **Demo Mode**: Predefined responses for testing and development
    - **Enhanced Mode**: Real AI responses via main LLM service
    - **Local AI Mode**: Self-hosted LLaMA3 via Ollama (when available)
    
    ## Authentication
    Currently no authentication required. In production, implement appropriate
    authentication mechanisms as needed.
    ''',
    contact='MSPSDC Development Team',
    license='MIT License',
    doc='/docs',  # Swagger UI will be available at this endpoint
    prefix='/api'
)

# Create namespaces for better organization
chat_ns = Namespace('Chat', description='Chat messaging operations')
service_ns = Namespace('Service', description='Service monitoring and status')
mode_ns = Namespace('Mode', description='Mode switching and configuration')

# Add namespaces to API
api.add_namespace(chat_ns, path='/chat')
api.add_namespace(service_ns, path='/service')
api.add_namespace(mode_ns, path='/mode')

# Define API models

# Chat Message Model
chat_message_model = api.model('ChatMessage', {
    'message': fields.String(required=True, description='User message content', 
                            example='Hello, I need help with MSPSDC services'),
    'timestamp': fields.String(description='Message timestamp (ISO format)',
                              example='2025-12-19T10:30:00.000000')
})

# Chat History Model
chat_history_model = api.model('ChatHistory', {
    'type': fields.String(required=True, description='Message type', 
                         enum=['user', 'bot', 'system'],
                         example='user'),
    'message': fields.String(required=True, description='Message content',
                           example='Hello, I need help with MSPSDC services'),
    'timestamp': fields.String(required=True, description='Message timestamp',
                             example='2025-12-19T10:30:00.000000')
})

# Send Message Request Model
send_message_request = api.model('SendMessageRequest', {
    'message': fields.String(required=True, description='Message to send',
                           example='What documents do I need for a caste certificate?')
})

# Send Message Response Model
send_message_response = api.model('SendMessageResponse', {
    'success': fields.Boolean(description='Operation success status', example=True),
    'bot_response': fields.String(description='AI response from the system',
                                 example='For document-related services, you can apply for...'),
    'chat_history': fields.List(fields.Nested(chat_history_model), 
                               description='Complete conversation history')
})

# Chat History Response Model
chat_history_response = api.model('ChatHistoryResponse', {
    'success': fields.Boolean(description='Operation success status', example=True),
    'chat_history': fields.List(fields.Nested(chat_history_model),
                               description='Conversation history')
})

# Service Status Model
service_status_model = api.model('ServiceStatus', {
    'available': fields.Boolean(description='Service availability status', example=True),
    'url': fields.String(description='Service endpoint URL',
                        example='http://127.0.0.1:5000/query/'),
    'model': fields.String(description='AI model name (for local LLM)',
                          example='llama3')
})

# Health Check Response Model
health_response = api.model('HealthResponse', {
    'status': fields.String(description='Service health status', example='healthy'),
    'timestamp': fields.String(description='Response timestamp',
                             example='2025-12-19T10:30:00.000000'),
    'service': fields.String(description='Service name', example='WhatsApp Chat UI'),
    'mode': fields.String(description='Current operational mode', example='demo'),
    'enhanced_mode': fields.Boolean(description='Enhanced mode enabled', example=False),
    'services': fields.Nested(api.model('ServicesStatus', {
        'main_llm': fields.Nested(service_status_model),
        'local_llm': fields.Nested(service_status_model)
    })),
    'active_service': fields.String(description='Currently active service',
                                  example='demo'),
    'service_status': fields.String(description='Overall service status',
                                   example='demo')
})

# LLM Status Response Model
llm_status_response = api.model('LLMStatusResponse', {
    'main_llm_available': fields.Boolean(description='Main LLM service availability', example=False),
    'main_llm_test': fields.Boolean(description='Main LLM service test result', example=False),
    'local_llm_available': fields.Boolean(description='Local LLM service availability', example=True),
    'local_llm_test': fields.Boolean(description='Local LLM service test result', example=True),
    'enhanced_mode_enabled': fields.Boolean(description='Enhanced mode status', example=False),
    'main_service_url': fields.String(description='Main LLM service URL',
                                    example='http://127.0.0.1:5000/query/'),
    'local_service_url': fields.String(description='Local LLM service URL',
                                     example='http://127.0.0.1:11434'),
    'local_model': fields.String(description='Local LLM model name', example='llama3'),
    'active_service': fields.String(description='Currently active service', example='local_llm'),
    'recommendation': fields.String(description='System recommendation',
                                  example='Local LLM (LLaMA3) available for enhanced responses')
})

# Mode Switch Response Model
mode_switch_response = api.model('ModeSwitchResponse', {
    'success': fields.Boolean(description='Operation success status', example=True),
    'mode': fields.String(description='New operational mode', example='enhanced'),
    'message': fields.String(description='Status message',
                           example='Switched to enhanced mode with main LLM service'),
    'error': fields.String(description='Error message (if operation failed)',
                          example='LLM service not available'),
    'details': fields.String(description='Additional operation details',
                           example='Using llama3 via Ollama at http://127.0.0.1:11434'),
    'setup_instructions': fields.Raw(description='Setup instructions (if applicable)')
})

# Ollama Setup Response Model
ollama_setup_response = api.model('OllamaSetupResponse', {
    'setup_instructions': fields.Raw(description='Setup instructions for Ollama installation',
                                   example={
                                       'install_ollama': {
                                           'command': 'curl -fsSL https://ollama.ai/install.sh | sh',
                                           'description': 'Install Ollama on Linux/macOS'
                                       }
                                   }),
    'environment_variables': fields.Raw(description='Environment variable configuration',
                                      example={
                                          'OLLAMA_BASE_URL': {
                                              'current': 'http://127.0.0.1:11434',
                                              'description': 'URL of Ollama server'
                                          }
                                      }),
    'benefits': fields.List(fields.String, description='Benefits of local LLaMA3',
                          example=[
                              'No API costs - completely free local inference',
                              'Works offline once model is downloaded',
                              'Full conversation context and memory'
                          ])
})

# Error Response Model
error_response = api.model('ErrorResponse', {
    'error': fields.String(description='Error message', example='Invalid request'),
    'details': fields.String(description='Detailed error information',
                            example='Message field is required'),
    'code': fields.Integer(description='HTTP status code', example=400)
})

# Add API decorators for documentation
@api.errorhandler
def handle_error(error):
    """Global error handler"""
    return {'error': str(error)}, getattr(error, 'code', 500)

# Chat Endpoints
@chat_ns.route('/send')
class SendMessage(Resource):
    @chat_ns.expect(send_message_request)
    @chat_ns.marshal_with(send_message_response)
    @chat_ns.response(200, 'Message sent successfully')
    @chat_ns.response(400, 'Invalid request', error_response)
    @chat_ns.response(500, 'Internal server error', error_response)
    def post(self):
        """
        Send a message to the chat system
        
        Sends a user message and receives an AI response. The system uses
        intelligent fallback to provide the best available response:
        1. Main LLM service (if enhanced mode enabled and available)
        2. Local LLaMA3 via Ollama (if available)
        3. Demo responses (always available fallback)
        
        The conversation history is maintained per session for context-aware responses.
        """
        try:
            # Get the request data
            data = request.get_json()
            if not data or 'message' not in data:
                return {'error': 'Message field is required'}, 400
                
            message = data['message'].strip()
            if not message:
                return {'error': 'Message cannot be empty'}, 400
            
            # Create a minimal Flask request context
            from flask import Flask
            app = Flask(__name__)
            
            with app.test_request_context(json={'message': message}, content_type='application/json'):
                from app.ui_views import send_message
                response = send_message()
                if hasattr(response, 'get_json'):
                    return response.get_json()
                else:
                    return response
                
        except Exception as e:
            return {'error': str(e)}, 500

@chat_ns.route('/history')
class ChatHistory(Resource):
    @chat_ns.marshal_with(chat_history_response)
    @chat_ns.response(200, 'Chat history retrieved successfully')
    @chat_ns.response(500, 'Internal server error', error_response)
    def get(self):
        """
        Get chat history for current session
        
        Retrieves the complete conversation history for the current user session,
        including both user messages and bot responses with timestamps.
        """
        try:
            from app.ui_views import get_chat_history
            
            response = get_chat_history()
            if hasattr(response, 'get_json'):
                return response.get_json()
            else:
                return response
                
        except Exception as e:
            return {'error': str(e)}, 500

@chat_ns.route('/clear')
class ClearChat(Resource):
    @api.marshal_with(api.model('ClearChatResponse', {
        'success': fields.Boolean(description='Operation success status'),
        'message': fields.String(description='Status message')
    }))
    @chat_ns.response(200, 'Chat history cleared successfully')
    @chat_ns.response(500, 'Internal server error', error_response)
    def post(self):
        """
        Clear chat history for current session
        
        Removes all messages from the conversation history for the current session.
        This action cannot be undone.
        """
        try:
            from app.ui_views import clear_chat
            
            response = clear_chat()
            if hasattr(response, 'get_json'):
                return response.get_json()
            else:
                return response
                
        except Exception as e:
            return {'error': str(e)}, 500

# Service Endpoints
@service_ns.route('/health')
class HealthCheck(Resource):
    @service_ns.marshal_with(health_response)
    @service_ns.response(200, 'Service is healthy')
    def get(self):
        """
        Health check endpoint
        
        Provides comprehensive health status of all services including:
        - Current operational mode
        - Service availability status
        - Active service information
        - System timestamps
        """
        try:
            from app.ui_views import health_check
            
            response = health_check()
            if hasattr(response, 'get_json'):
                return response.get_json()
            else:
                return response
                
        except Exception as e:
            return {'error': str(e)}, 500

@service_ns.route('/llm/status')
class LLMStatus(Resource):
    @service_ns.marshal_with(llm_status_response)
    @service_ns.response(200, 'LLM service status retrieved')
    def get(self):
        """
        Get LLM service status
        
        Provides detailed status information for all LLM services:
        - Main LLM service availability and testing
        - Local LLM (Ollama) availability and testing
        - Current configuration and recommendations
        - Service URLs and model information
        """
        try:
            from app.ui_views import llm_status
            
            response = llm_status()
            if hasattr(response, 'get_json'):
                return response.get_json()
            else:
                return response
                
        except Exception as e:
            return {'error': str(e)}, 500

@service_ns.route('/ollama/setup')
class OllamaSetup(Resource):
    @service_ns.marshal_with(ollama_setup_response)
    @service_ns.response(200, 'Ollama setup information retrieved')
    def get(self):
        """
        Get Ollama setup information
        
        Provides complete setup instructions for installing and configuring
        Ollama with LLaMA3 for local AI mode. Includes:
        - Installation commands
        - Environment variable configuration
        - Benefits of local processing
        - API usage examples
        """
        try:
            from app.ui_views import ollama_setup_info
            
            response = ollama_setup_info()
            if hasattr(response, 'get_json'):
                return response.get_json()
            else:
                return response
                
        except Exception as e:
            return {'error': str(e)}, 500

# Mode Endpoints
@mode_ns.route('/demo')
class SwitchToDemo(Resource):
    @mode_ns.marshal_with(mode_switch_response)
    @mode_ns.response(200, 'Switched to demo mode successfully')
    @mode_ns.response(500, 'Internal server error', error_response)
    def post(self):
        """
        Switch to demo mode
        
        Switches the chat system to demo mode, which uses predefined responses
        for testing and development purposes. This mode does not require any
        external LLM services.
        """
        try:
            from app.ui_views import switch_to_demo
            
            response = switch_to_demo()
            if hasattr(response, 'get_json'):
                return response.get_json()
            else:
                return response
                
        except Exception as e:
            return {'error': str(e)}, 500

@mode_ns.route('/enhanced')
class SwitchToEnhanced(Resource):
    @mode_ns.marshal_with(mode_switch_response)
    @api.expect(api.model('EnhancedModeRequest', {
        'force': fields.Boolean(description='Force switch even if services unavailable', 
                               example=False, default=False)
    }))
    @api.response(200, 'Switched to enhanced mode successfully')
    @api.response(503, 'Service unavailable', mode_switch_response)
    @api.response(500, 'Internal server error', error_response)
    def post(self):
        """
        Switch to enhanced mode
        
        Attempts to switch to enhanced mode, which uses real AI services.
        The system will use the best available service:
        1. Main LLM service (preferred)
        2. Local LLaMA3 via Ollama (fallback)
        
        If no services are available, returns setup instructions.
        """
        try:
            from app.ui_views import switch_to_enhanced
            
            response = switch_to_enhanced()
            response_data = response.get_json()
            
            # Check if this is an error response (503 status)
            if 'error' in response_data:
                return response_data, 503
            return response_data
                
        except Exception as e:
            return {'error': str(e)}, 500

# Additional documentation endpoints
@api.route('/')
class APIDocumentation(Resource):
    def get(self):
        """
        API Documentation Index
        
        Redirects to the interactive Swagger UI documentation
        """
        return {
            'message': 'Welcome to WhatsApp Chat UI API',
            'documentation': '/docs',
            'openapi_spec': '/api/spec',
            'version': '1.0',
            'endpoints': {
                'chat': '/api/chat',
                'service': '/api/service', 
                'mode': '/api/mode'
            }
        }

# Error handling for the documentation
@api.errorhandler(ValueError)
def handle_value_error(error):
    """Handle value errors in API documentation"""
    return {'error': str(error)}, 400

@api.errorhandler(AttributeError)
def handle_attribute_error(error):
    """Handle attribute errors in API documentation"""
    return {'error': 'Invalid request format'}, 400

print("✅ OpenAPI/Swagger documentation configured")
print("📚 Interactive API docs available at: http://localhost:8000/docs")
print("🔧 OpenAPI spec available at: http://localhost:8000/api/spec")