#!/usr/bin/env python3
"""
Enhanced Mode Demo for WhatsApp Chat UI

This script demonstrates the Enhanced Mode functionality that integrates with 
the real LLM service while providing graceful fallback to demo responses.

Features:
- Enhanced Mode with real AI responses
- Demo Mode with predefined responses  
- Runtime mode switching
- LLM service availability detection
- Fallback mechanisms
"""

import requests
import json
import time
import sys

def print_banner():
    """Print enhanced mode demo banner"""
    print("=" * 80)
    print("🚀 WhatsApp Chat UI - Enhanced Mode Demo")
    print("=" * 80)
    print("This demo showcases the Enhanced Mode that:")
    print("• Integrates with real LLM service for AI responses")
    print("• Provides graceful fallback to demo responses")
    print("• Supports runtime mode switching")
    print("• Shows service availability status")
    print("• Uses same backend pipeline as WhatsApp integration")
    print("=" * 80)

def check_services():
    """Check both Flask and LLM service status"""
    print("\n📡 Checking Service Status")
    print("-" * 40)
    
    # Check Flask app
    try:
        response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
        if response.status_code == 200:
            flask_data = response.json()
            flask_status = "✅ Running"
            print(f"Flask Chat UI (port 8000): {flask_status}")
            print(f"   Current Mode: {flask_data.get('mode', 'unknown')}")
            print(f"   Enhanced Mode: {flask_data.get('enhanced_mode', False)}")
            print(f"   LLM Service: {'✅ Available' if flask_data.get('llm_service', {}).get('available') else '❌ Not Available'}")
        else:
            flask_status = "❌ Error"
            print(f"Flask Chat UI (port 8000): {flask_status}")
    except Exception as e:
        flask_status = "❌ Not Running"
        print(f"Flask Chat UI (port 8000): {flask_status}")
        print(f"   Error: {e}")
    
    # Check LLM service specifically
    print("\n🔍 LLM Service Details")
    print("-" * 40)
    try:
        response = requests.get("http://127.0.0.1:8000/api/llm/status", timeout=2)
        if response.status_code == 200:
            llm_data = response.json()
            print(f"LLM Service Available: {'✅' if llm_data.get('llm_service_available') else '❌'}")
            print(f"LLM Service Test: {'✅' if llm_data.get('llm_service_test') else '❌'}")
            print(f"Enhanced Mode Enabled: {'✅' if llm_data.get('enhanced_mode_enabled') else '❌'}")
            print(f"Service URL: {llm_data.get('service_url', 'N/A')}")
            print(f"Recommendation: {llm_data.get('recommendation', 'N/A')}")
        else:
            print("❌ Could not get LLM status")
    except Exception as e:
        print(f"❌ LLM service error: {e}")

def test_demo_mode():
    """Test demo mode functionality"""
    print("\n🎭 Testing Demo Mode")
    print("-" * 40)
    
    # Switch to demo mode first
    try:
        response = requests.post("http://127.0.0.1:8000/api/mode/demo")
        if response.status_code == 200:
            print("✅ Switched to Demo Mode")
        else:
            print("❌ Failed to switch to Demo Mode")
            return
    except Exception as e:
        print(f"❌ Error switching to Demo Mode: {e}")
        return
    
    demo_messages = [
        "Hello! I need help with MSPSDC services.",
        "What documents do I need for a caste certificate?", 
        "Tell me about welfare schemes in Meghalaya.",
        "How can I track my application status?"
    ]
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n🎬 Demo Test {i}: {message}")
        
        try:
            response = requests.post("http://127.0.0.1:8000/api/chat/send", 
                                   json={"message": message}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"👤 User: {message}")
                print(f"🤖 Bot (Demo): {data.get('bot_response', 'No response')}")
                print(f"💬 Mode: Demo Response")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)

def test_enhanced_mode():
    """Test enhanced mode functionality"""
    print("\n🚀 Testing Enhanced Mode")
    print("-" * 40)
    
    # Check if LLM service is available
    try:
        status_response = requests.get("http://127.0.0.1:8000/api/llm/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            if not status_data.get('llm_service_available'):
                print("⚠️  LLM service not available - Enhanced Mode will fallback to demo responses")
            else:
                print("✅ LLM service available - Enhanced Mode will use AI responses")
    except:
        print("⚠️  Could not check LLM service status")
    
    # Switch to enhanced mode
    try:
        response = requests.post("http://127.0.0.1:8000/api/mode/enhanced")
        if response.status_code == 200:
            print("✅ Switched to Enhanced Mode")
        else:
            print("❌ Failed to switch to Enhanced Mode")
            print("💡 This is expected if LLM service is not available")
            return
    except Exception as e:
        print(f"❌ Error switching to Enhanced Mode: {e}")
        return
    
    enhanced_messages = [
        "Hello! I need detailed information about MSPSDC services.",
        "Can you help me understand the application process for documents?",
        "What are the eligibility criteria for welfare schemes?"
    ]
    
    for i, message in enumerate(enhanced_messages, 1):
        print(f"\n🧠 Enhanced Test {i}: {message}")
        
        try:
            response = requests.post("http://127.0.0.1:8000/api/chat/send", 
                                   json={"message": message}, 
                                   timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"👤 User: {message}")
                print(f"🤖 Bot (Enhanced): {data.get('bot_response', 'No response')}")
                print(f"💬 Mode: Enhanced Response (AI or Fallback)")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)

def demonstrate_features():
    """Demonstrate Enhanced Mode features"""
    print("\n⭐ Enhanced Mode Features Demo")
    print("-" * 40)
    
    print("""
🔧 Key Features:
• Real-time mode switching between Demo and Enhanced
• Automatic fallback to demo responses if LLM service unavailable
• Same backend pipeline as existing WhatsApp integration
• Service availability monitoring
• Visual mode indicators in the chat interface
• System messages for mode changes

🛡️ Resilience:
• Graceful degradation when LLM service unavailable
• Timeout handling for slow responses
• Connection error recovery
• User-friendly fallback messages

🔄 Integration:
• Uses same /query/ endpoint as WhatsApp webhook
• Identical message processing pipeline
• Consistent response formatting
• Shared session management
""")

def show_access_info():
    """Show how to access Enhanced Mode interface"""
    print("\n🌐 Access Enhanced Mode Interface")
    print("-" * 40)
    print(f"""
🔗 URLs:
   • Chat Interface: http://127.0.0.1:8000/
   • Health Check: http://127.0.0.1:8000/api/health
   • LLM Status: http://127.0.0.1:8000/api/llm/status
   • Switch Modes: Use buttons in chat interface header

🎮 How to Use:
   1. Open http://127.0.0.1:8000/ in browser
   2. Look for mode badge in header (Demo/Enhanced)
   3. Click "Enhanced" button to enable AI responses
   4. Chat normally - responses will be AI-powered
   5. Click "Demo" button to switch back to demo mode

⚡ Quick Test:
   • Send any message and observe response style
   • Mode badge shows current operational mode
   • System messages appear when switching modes
""")

def show_api_examples():
    """Show API examples for Enhanced Mode"""
    print("\n📚 Enhanced Mode API Examples")
    print("-" * 40)
    
    examples = [
        {
            "name": "Get System Status",
            "method": "GET",
            "url": "http://127.0.0.1:8000/api/health",
            "description": "Shows current mode, LLM service status"
        },
        {
            "name": "Get LLM Service Status", 
            "method": "GET",
            "url": "http://127.0.0.1:8000/api/llm/status",
            "description": "Detailed LLM service availability and testing"
        },
        {
            "name": "Switch to Enhanced Mode",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/mode/enhanced",
            "description": "Enables AI responses (requires LLM service)"
        },
        {
            "name": "Switch to Demo Mode",
            "method": "POST", 
            "url": "http://127.0.0.1:8000/api/mode/demo",
            "description": "Uses predefined demo responses"
        },
        {
            "name": "Send Enhanced Message",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/chat/send",
            "data": {"message": "Your query here"},
            "description": "Sends message using current mode"
        }
    ]
    
    for example in examples:
        print(f"\n🔧 {example['name']}:")
        print(f"   {example['method']} {example['url']}")
        print(f"   📝 {example['description']}")
        if 'data' in example:
            print(f"   📄 Data: {json.dumps(example['data'], indent=4)}")

def main():
    """Main Enhanced Mode demo function"""
    print_banner()
    
    # Check current service status
    check_services()
    
    # Test Demo Mode
    test_demo_mode()
    
    # Test Enhanced Mode  
    test_enhanced_mode()
    
    # Demonstrate features
    demonstrate_features()
    
    # Show access information
    show_access_info()
    
    # Show API examples
    show_api_examples()
    
    print("\n" + "=" * 80)
    print("🎉 Enhanced Mode Demo Complete!")
    print("=" * 80)
    print("✅ Enhanced Mode provides:")
    print("   • Real AI responses when LLM service is available")
    print("   • Graceful fallback to demo responses when needed")
    print("   • Same backend pipeline as WhatsApp integration")
    print("   • Runtime mode switching for flexibility")
    print("   • Service availability monitoring")
    print("")
    print("🌐 Try Enhanced Mode now at: http://127.0.0.1:8000/")
    print("=" * 80)

if __name__ == "__main__":
    main()