#!/usr/bin/env python3
"""
WhatsApp Chat UI Demo and Test Script

This script demonstrates the complete chat interface functionality,
shows how it integrates with the existing WhatsApp system, and provides
testing utilities for the live preview.

Usage:
    python3 chat_ui_demo.py

Features:
- Starts Flask app on port 8000
- Starts LLM service on port 5000 (when available)
- Provides demo chat interactions
- Shows integration with existing WhatsApp system
- Creates test scenarios for the live preview
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

def print_banner():
    """Print demo banner"""
    print("=" * 80)
    print("🚀 WhatsApp Chat UI Live Preview Demo")
    print("=" * 80)
    print("This demo showcases the new frontend interface that:")
    print("• Shows messages from user and bot side")
    print("• Provides options to message bot and see responses")
    print("• Uses the same response pipeline as WhatsApp integration")
    print("• Hosts a live preview accessible via web browser")
    print("=" * 80)

def check_services():
    """Check if services are running"""
    print("\n📡 Checking service status...")
    
    # Check Flask app
    try:
        response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
        if response.status_code == 200:
            flask_status = "✅ Running"
            flask_data = response.json()
        else:
            flask_status = "❌ Error"
    except:
        flask_status = "❌ Not Running"
    
    # Check LLM service
    try:
        response = requests.post("http://127.0.0.1:5000/query/", 
                               json={"query": "test", "query_type": "greeting"}, 
                               timeout=5)
        if response.status_code == 200:
            llm_status = "✅ Running"
        else:
            llm_status = "⚠️  Error"
    except:
        llm_status = "❌ Not Running"
    
    print(f"Flask Chat UI (port 8000): {flask_status}")
    print(f"LLM Service (port 5000): {llm_status}")
    
    return flask_status.startswith("✅"), llm_status.startswith("✅")

def demo_chat_interaction():
    """Demonstrate chat interaction"""
    print("\n💬 Demo Chat Interaction")
    print("-" * 40)
    
    demo_messages = [
        "Hello! I'm looking for information about MSPSDC services.",
        "What documents do I need to apply for a caste certificate?",
        "Tell me about welfare schemes available in Meghalaya.",
        "How can I track my application status?",
        "Thank you for the help!"
    ]
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n🤖 Demo {i}: {message}")
        
        try:
            response = requests.post("http://127.0.0.1:8000/api/chat/send", 
                                   json={"message": message}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"👤 User: {message}")
                print(f"🤖 Bot: {data.get('bot_response', 'No response')}")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)  # Small delay between messages

def test_chat_features():
    """Test various chat features"""
    print("\n🧪 Testing Chat Features")
    print("-" * 40)
    
    # Test chat history
    print("\n📜 Testing Chat History...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/chat/history")
        if response.status_code == 200:
            data = response.json()
            chat_count = len(data.get('chat_history', []))
            print(f"✅ Chat history: {chat_count} messages stored")
        else:
            print("❌ Chat history failed")
    except Exception as e:
        print(f"❌ Chat history error: {e}")
    
    # Test clear chat
    print("\n🗑️  Testing Clear Chat...")
    try:
        response = requests.post("http://127.0.0.1:8000/api/chat/clear")
        if response.status_code == 200:
            print("✅ Chat cleared successfully")
        else:
            print("❌ Clear chat failed")
    except Exception as e:
        print(f"❌ Clear chat error: {e}")

def show_integration_details():
    """Show how it integrates with existing WhatsApp system"""
    print("\n🔗 Integration with WhatsApp System")
    print("-" * 40)
    
    print("""
The chat UI uses the SAME response pipeline as WhatsApp:

1. 📱 WhatsApp Integration Flow:
   WhatsApp → Webhook → Flask App → LLM Service → Response

2. 🌐 Chat UI Integration Flow:
   Web Browser → Flask UI → LLM Service → Response

3. 🔄 Shared Components:
   • Same LLM service endpoint (/query/)
   • Same message processing logic
   • Same response formatting
   • Same session management

4. 📊 Benefits:
   • Consistent responses across channels
   • Same AI capabilities
   • Unified backend
   • Easy maintenance and updates
""")

def show_access_info():
    """Show how to access the interface"""
    print("\n🌐 Access Information")
    print("-" * 40)
    print(f"""
🔗 Live Preview URLs:
   • Chat Interface: http://127.0.0.1:8000/
   • Health Check: http://127.0.0.1:8000/api/health
   • API Endpoints: http://127.0.0.1:8000/api/

📱 Mobile Friendly:
   • Responsive design for all devices
   • Touch-friendly interface
   • Optimized for chat experience

🧪 Testing:
   • Open http://127.0.0.1:8000/ in your browser
   • Type messages and see real-time responses
   • Test on mobile devices for responsive design
""")

def show_api_examples():
    """Show API usage examples"""
    print("\n📚 API Usage Examples")
    print("-" * 40)
    
    examples = [
        {
            "name": "Send Message",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/chat/send",
            "data": {"message": "Hello, I need help with services"}
        },
        {
            "name": "Get Chat History",
            "method": "GET", 
            "url": "http://127.0.0.1:8000/api/chat/history",
            "data": None
        },
        {
            "name": "Clear Chat",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/chat/clear", 
            "data": None
        }
    ]
    
    for example in examples:
        print(f"\n🔧 {example['name']}:")
        print(f"   {example['method']} {example['url']}")
        if example['data']:
            print(f"   Data: {json.dumps(example['data'], indent=4)}")

def main():
    """Main demo function"""
    print_banner()
    
    # Check if services are running
    flask_running, llm_running = check_services()
    
    if not flask_running:
        print("\n❌ Flask app is not running!")
        print("   Please start it with: python3 run.py")
        sys.exit(1)
    
    # Run demos
    demo_chat_interaction()
    test_chat_features()
    show_integration_details()
    show_access_info()
    show_api_examples()
    
    print("\n" + "=" * 80)
    print("🎉 Demo Complete!")
    print("=" * 80)
    print("Visit http://127.0.0.1:8000/ to try the live chat interface!")
    print("The interface provides a WhatsApp-like chat experience")
    print("with the same backend processing as your existing system.")
    print("=" * 80)

if __name__ == "__main__":
    main()