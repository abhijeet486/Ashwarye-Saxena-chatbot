import json
import logging
from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import random
import requests
import os
import time

ui_blueprint = Blueprint("ui", __name__, template_folder="templates")

# Configuration
LLM_SERVICE_URL = os.getenv('LLM_SERVICE_URL', 'http://127.0.0.1:5000/query/')
USE_ENHANCED_MODE = os.getenv('USE_ENHANCED_MODE', 'false').lower() == 'true'
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

# Self-hosted LLaMA3 service availability
LOCAL_LLM_AVAILABLE = None
LOCAL_LLM_LAST_CHECK = 0

# Predefined responses for demo
DEMO_RESPONSES = {
    'greeting': [
        "Hello! Welcome to MSPSDC Chat Assistant. How can I help you today?",
        "Hi there! I'm here to assist you with Meghalaya State Public Services. What can I help you with?",
        "Greetings! I'm your AI assistant for MSPSDC. How may I assist you?"
    ],
    'services': [
        "MSPSDC offers various public services including document verification, certificate issuance, and citizen support. Which specific service are you interested in?",
        "We provide comprehensive public services through our digital platform. Our main services include document verification, application processing, and citizen grievance handling."
    ],
    'schemes': [
        "Meghalaya has several welfare schemes for citizens including healthcare, education, and livelihood support programs. Would you like to know about any specific scheme?",
        "Our state offers various social welfare schemes. I can provide information about healthcare schemes, education scholarships, and livelihood programs."
    ],
    'documents': [
        "For document-related services, you can apply for birth certificates, caste certificates, income certificates, and other important documents through our portal.",
        "Document services include application for various certificates and verifications. You can submit applications online and track their status."
    ],
    'default': [
        "I understand you're asking about MSPSDC services. Could you please be more specific about what information you need?",
        "That's a great question about our services. Let me help you with information on that topic.",
        "I'd be happy to assist you with MSPSDC-related queries. Could you provide more details about what you're looking for?",
        "Thank you for your question. For more detailed information, you might want to visit our official website or contact our helpdesk."
    ]
}

def categorize_query(query):
    """Simple query categorization for demo"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return 'greeting'
    elif any(word in query_lower for word in ['service', 'services', 'help', 'assistance']):
        return 'services'
    elif any(word in query_lower for word in ['scheme', 'schemes', 'welfare', 'benefits', 'program']):
        return 'schemes'
    elif any(word in query_lower for word in ['document', 'certificate', 'documents', 'certificates']):
        return 'documents'
    else:
        return 'default'

@ui_blueprint.route('/')
def chat_interface():
    """Main chat interface"""
    return render_template('chat.html')

def get_llm_response(query, message_history=None, query_type="general"):
    """Get response from LLM service with fallback to demo responses"""
    try:
        if message_history is None:
            message_history = []
        
        json_message = {
            "query": query,
            "message_history": message_history,
            "query_type": query_type
        }
        query_json = json.dumps(json_message)
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            LLM_SERVICE_URL,
            data=query_json,
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('response', 'Sorry, I could not process your request.')
        else:
            logging.error(f"LLM service returned status {response.status_code}")
            return get_fallback_response(query)
            
    except requests.exceptions.Timeout:
        logging.warning("LLM service timed out, using fallback")
        return get_fallback_response(query)
    except requests.exceptions.ConnectionError:
        logging.warning("Could not connect to LLM service, using fallback")
        return get_fallback_response(query)
    except Exception as e:
        logging.error(f"Error calling LLM service: {e}")
        return get_fallback_response(query)

def get_fallback_response(query):
    """Get demo response as fallback"""
    category = categorize_query(query)
    responses = DEMO_RESPONSES.get(category, DEMO_RESPONSES['default'])
    return random.choice(responses)

def check_local_llm_availability():
    """Check if local LLM (Ollama) is available"""
    global LOCAL_LLM_AVAILABLE, LOCAL_LLM_LAST_CHECK
    
    # Cache result for 30 seconds to avoid repeated calls
    current_time = time.time()
    if current_time - LOCAL_LLM_LAST_CHECK < 30 and LOCAL_LLM_AVAILABLE is not None:
        return LOCAL_LLM_AVAILABLE
    
    try:
        # Check if Ollama is running and accessible
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            # Check if Llama3 model is available
            model_names = [model.get('name', '') for model in models.get('models', [])]
            llama_available = any('llama3' in name.lower() for name in model_names)
            
            LOCAL_LLM_AVAILABLE = llama_available
            LOCAL_LLM_LAST_CHECK = current_time
            
            logging.info(f"Ollama availability check: {llama_available}, models: {model_names}")
            return llama_available
        else:
            LOCAL_LLM_AVAILABLE = False
            LOCAL_LLM_LAST_CHECK = current_time
            return False
    except Exception as e:
        logging.warning(f"Ollama availability check failed: {e}")
        LOCAL_LLM_AVAILABLE = False
        LOCAL_LLM_LAST_CHECK = current_time
        return False

def get_local_llm_response(query, message_history=None):
    """Get response from local LLM (Ollama/LLaMA3)"""
    try:
        if message_history is None:
            message_history = []
        
        # Prepare the conversation context
        messages = []
        
        # Add system message for MSPSDC context
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant for Meghalaya State Public Services Delivery Commission (MSPSDC). You help citizens with information about public services, schemes, documents, and procedures. Be concise, helpful, and informative."
        })
        
        # Add conversation history
        for msg in message_history[-5:]:  # Last 5 messages for context
            if msg.get('type') == 'user':
                messages.append({"role": "user", "content": msg.get('message', '')})
            elif msg.get('type') == 'bot':
                messages.append({"role": "assistant", "content": msg.get('message', '')})
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Prepare request to Ollama
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60  # 60 second timeout for LLM generation
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('message', {}).get('content', '').strip()
        else:
            logging.error(f"Ollama API returned status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logging.warning("Ollama request timed out")
        return None
    except requests.exceptions.ConnectionError:
        logging.warning("Could not connect to Ollama")
        return None
    except Exception as e:
        logging.error(f"Error calling Ollama: {e}")
        return None

def get_enhanced_response(query, message_history=None):
    """Get response with intelligent fallback hierarchy"""
    # Try main LLM service first (for enhanced mode)
    if USE_ENHANCED_MODE:
        try:
            json_message = {
                "query": query,
                "message_history": message_history or [],
                "query_type": "general"
            }
            query_json = json.dumps(json_message)
            
            response = requests.post(
                LLM_SERVICE_URL,
                data=query_json,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get('response', '')
                
        except Exception as e:
            logging.warning(f"Main LLM service failed: {e}")
    
    # Try local LLM (LLaMA3 via Ollama) as secondary option
    if check_local_llm_availability():
        local_response = get_local_llm_response(query, message_history)
        if local_response:
            logging.info("Using local LLaMA3 response")
            return local_response
    
    # Fallback to demo responses
    logging.info("Using demo fallback response")
    return get_fallback_response(query)

@ui_blueprint.route('/api/chat/send', methods=['POST'])
def send_message():
    """Handle chat message sending with enhanced or demo responses"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create session
        session_id = session.get('session_id')
        if not session_id:
            session_id = datetime.now().isoformat()
            session['session_id'] = session_id
        
        # Initialize or get chat history
        chat_history = session.get('chat_history', [])
        
        # Add user message to history
        chat_history.append({
            'type': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get response using enhanced fallback hierarchy
        bot_response = get_enhanced_response(message, chat_history[:-1])
        
        # Add bot response to history
        chat_history.append({
            'type': 'bot',
            'message': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update session
        session['chat_history'] = chat_history
        
        return jsonify({
            'success': True,
            'bot_response': bot_response,
            'chat_history': chat_history
        })
        
    except Exception as e:
        logging.error(f"Error in send_message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ui_blueprint.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for current session"""
    try:
        chat_history = session.get('chat_history', [])
        return jsonify({
            'success': True,
            'chat_history': chat_history
        })
    except Exception as e:
        logging.error(f"Error in get_chat_history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@ui_blueprint.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for current session"""
    try:
        session.pop('chat_history', None)
        session.pop('session_id', None)
        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        logging.error(f"Error in clear_chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def check_llm_service():
    """Check if main LLM service is available"""
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        return True
    except:
        return False

def get_service_status():
    """Get comprehensive service status"""
    main_llm_available = check_llm_service()
    local_llm_available = check_local_llm_availability()
    
    # Determine which service is being used
    if USE_ENHANCED_MODE and main_llm_available:
        active_service = "main_llm"
        service_status = "enhanced"
    elif local_llm_available:
        active_service = "local_llm"
        service_status = "local_enhanced"
    else:
        active_service = "demo"
        service_status = "demo"
    
    return {
        'main_llm_available': main_llm_available,
        'local_llm_available': local_llm_available,
        'active_service': active_service,
        'service_status': service_status,
        'ollama_base_url': OLLAMA_BASE_URL,
        'ollama_model': OLLAMA_MODEL
    }

@ui_blueprint.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    service_status = get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'WhatsApp Chat UI',
        'mode': 'enhanced' if USE_ENHANCED_MODE else 'demo',
        'enhanced_mode': USE_ENHANCED_MODE,
        'services': {
            'main_llm': {
                'available': service_status['main_llm_available'],
                'url': LLM_SERVICE_URL
            },
            'local_llm': {
                'available': service_status['local_llm_available'],
                'url': service_status['ollama_base_url'],
                'model': service_status['ollama_model']
            }
        },
        'active_service': service_status['active_service'],
        'service_status': service_status['service_status']
    })

@ui_blueprint.route('/api/llm/status', methods=['GET'])
def llm_status():
    """Check LLM service status"""
    service_status = get_service_status()
    
    # Test main LLM service
    main_llm_test = False
    if service_status['main_llm_available']:
        try:
            test_response = requests.post(
                LLM_SERVICE_URL,
                json={"query": "hello", "query_type": "greeting"},
                timeout=10
            )
            main_llm_test = test_response.status_code == 200
        except:
            main_llm_test = False
    
    # Test local LLM service
    local_llm_test = False
    if service_status['local_llm_available']:
        try:
            test_response = requests.post(
                f"{service_status['ollama_base_url']}/api/chat",
                json={
                    "model": service_status['ollama_model'],
                    "messages": [{"role": "user", "content": "Hello"}],
                    "stream": False
                },
                timeout=30
            )
            local_llm_test = test_response.status_code == 200
        except:
            local_llm_test = False
    
    # Generate recommendation
    if service_status['main_llm_available'] and main_llm_test:
        recommendation = "Enhanced mode ready with main LLM"
    elif service_status['local_llm_available'] and local_llm_test:
        recommendation = "Local LLM (LLaMA3) available for enhanced responses"
    else:
        recommendation = "Using demo responses - install and run Ollama with LLaMA3 for enhanced mode"
    
    return jsonify({
        'main_llm_available': service_status['main_llm_available'],
        'main_llm_test': main_llm_test,
        'local_llm_available': service_status['local_llm_available'],
        'local_llm_test': local_llm_test,
        'enhanced_mode_enabled': USE_ENHANCED_MODE,
        'main_service_url': LLM_SERVICE_URL,
        'local_service_url': service_status['ollama_base_url'],
        'local_model': service_status['ollama_model'],
        'active_service': service_status['active_service'],
        'recommendation': recommendation
    })

@ui_blueprint.route('/api/mode/demo', methods=['POST'])
def switch_to_demo():
    """Switch to demo mode"""
    os.environ['USE_ENHANCED_MODE'] = 'false'
    return jsonify({'success': True, 'mode': 'demo', 'message': 'Switched to demo mode'})

@ui_blueprint.route('/api/mode/enhanced', methods=['POST'])
def switch_to_enhanced():
    """Switch to enhanced mode (if LLM service is available)"""
    service_status = get_service_status()
    
    # Check if we have any LLM service available
    if not (service_status['main_llm_available'] or service_status['local_llm_available']):
        return jsonify({
            'error': 'No LLM service available. Cannot switch to enhanced mode.',
            'details': 'Install and run Ollama with LLaMA3 model or start the main LLM service.',
            'setup_instructions': {
                'ollama_install': 'curl -fsSL https://ollama.ai/install.sh | sh',
                'ollama_start': 'ollama serve',
                'ollama_model': f'ollama pull {OLLAMA_MODEL}',
                'alternative': 'Start the main LLM service on port 5000'
            }
        }), 503
    
    # Check if main LLM service is available (preferred)
    if service_status['main_llm_available']:
        os.environ['USE_ENHANCED_MODE'] = 'true'
        return jsonify({
            'success': True, 
            'mode': 'enhanced', 
            'message': 'Switched to enhanced mode with main LLM service'
        })
    
    # Check if local LLM is available
    if service_status['local_llm_available']:
        # For local LLM, we don't need to change USE_ENHANCED_MODE
        # as it will be used automatically when available
        return jsonify({
            'success': True, 
            'mode': 'local_enhanced', 
            'message': f'Enhanced mode active with local LLM ({OLLAMA_MODEL})',
            'details': f'Using {OLLAMA_MODEL} via Ollama at {OLLAMA_BASE_URL}'
        })
    
    return jsonify({'error': 'Unknown error checking LLM services'}), 500

@ui_blueprint.route('/api/ollama/setup', methods=['GET'])
def ollama_setup_info():
    """Get Ollama setup instructions"""
    return jsonify({
        'setup_instructions': {
            'install_ollama': {
                'command': 'curl -fsSL https://ollama.ai/install.sh | sh',
                'description': 'Install Ollama on Linux/macOS'
            },
            'start_ollama': {
                'command': 'ollama serve',
                'description': 'Start Ollama server (runs on port 11434)'
            },
            'install_llama3': {
                'command': 'ollama pull llama3',
                'description': 'Download and install LLaMA3 model'
            },
            'verify_installation': {
                'command': 'curl http://localhost:11434/api/tags',
                'description': 'Check if Ollama is running and models are installed'
            }
        },
        'environment_variables': {
            'OLLAMA_BASE_URL': {
                'current': OLLAMA_BASE_URL,
                'description': 'URL of Ollama server'
            },
            'OLLAMA_MODEL': {
                'current': OLLAMA_MODEL,
                'description': 'Model name to use for local LLM'
            }
        },
        'chat_completion_test': {
            'description': 'After setup, test with:',
            'example': {
                'url': f'{OLLAMA_BASE_URL}/api/chat',
                'payload': {
                    'model': OLLAMA_MODEL,
                    'messages': [{'role': 'user', 'content': 'Hello'}],
                    'stream': False
                }
            }
        },
        'benefits': [
            'No API costs - completely free local inference',
            'Works offline once model is downloaded',
            'Full conversation context and memory',
            'MSPSDC-specific AI assistant responses',
            'Privacy - all processing done locally'
        ]
    })