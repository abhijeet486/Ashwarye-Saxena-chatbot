import json
import logging
from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import random

ui_blueprint = Blueprint("ui", __name__, template_folder="templates")

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

@ui_blueprint.route('/api/chat/send', methods=['POST'])
def send_message():
    """Handle chat message sending with demo responses"""
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
        
        # Generate demo response
        category = categorize_query(message)
        responses = DEMO_RESPONSES.get(category, DEMO_RESPONSES['default'])
        bot_response = random.choice(responses)
        
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

@ui_blueprint.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'WhatsApp Chat UI Demo',
        'mode': 'demo'
    })