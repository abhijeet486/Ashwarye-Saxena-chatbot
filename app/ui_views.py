import json
import logging
from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import random
import requests
import os

ui_blueprint = Blueprint("ui", __name__, template_folder="templates")

# Configuration
LLM_SERVICE_URL = os.getenv('LLM_SERVICE_URL', 'http://127.0.0.1:5000/query/')
USE_ENHANCED_MODE = os.getenv('USE_ENHANCED_MODE', 'false').lower() == 'true'

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
        
        # Get response (LLM if enhanced mode enabled, otherwise demo)
        if USE_ENHANCED_MODE:
            # Try LLM service first, fallback to demo if fails
            bot_response = get_llm_response(message, chat_history[:-1])
        else:
            # Use demo response
            bot_response = get_fallback_response(message)
        
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
    """Check if LLM service is available"""
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        return True
    except:
        return False

@ui_blueprint.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    llm_available = check_llm_service()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'WhatsApp Chat UI',
        'mode': 'enhanced' if USE_ENHANCED_MODE else 'demo',
        'llm_service': {
            'available': llm_available,
            'url': LLM_SERVICE_URL
        },
        'enhanced_mode': USE_ENHANCED_MODE
    })

@ui_blueprint.route('/api/llm/status', methods=['GET'])
def llm_status():
    """Check LLM service status"""
    llm_available = check_llm_service()
    
    if llm_available:
        try:
            test_response = requests.post(
                LLM_SERVICE_URL,
                json={"query": "hello", "query_type": "greeting"},
                timeout=10
            )
            test_ok = test_response.status_code == 200
        except:
            test_ok = False
    else:
        test_ok = False
    
    return jsonify({
        'llm_service_available': llm_available,
        'llm_service_test': test_ok,
        'enhanced_mode_enabled': USE_ENHANCED_MODE,
        'service_url': LLM_SERVICE_URL,
        'recommendation': 'Enhanced mode ready' if llm_available and test_ok else 'Using demo responses'
    })

@ui_blueprint.route('/api/mode/demo', methods=['POST'])
def switch_to_demo():
    """Switch to demo mode"""
    os.environ['USE_ENHANCED_MODE'] = 'false'
    return jsonify({'success': True, 'mode': 'demo', 'message': 'Switched to demo mode'})

@ui_blueprint.route('/api/mode/enhanced', methods=['POST'])
def switch_to_enhanced():
    """Switch to enhanced mode (if LLM service is available)"""
    llm_available = check_llm_service()
    if not llm_available:
        return jsonify({'error': 'LLM service not available. Cannot switch to enhanced mode.'}), 503
    
    os.environ['USE_ENHANCED_MODE'] = 'true'
    return jsonify({'success': True, 'mode': 'enhanced', 'message': 'Switched to enhanced mode'})