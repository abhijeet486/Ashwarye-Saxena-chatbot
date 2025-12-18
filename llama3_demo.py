#!/usr/bin/env python3
"""
Self-hosted LLaMA3 Demo for WhatsApp Chat UI

This script demonstrates the new LLaMA3 self-hosted support that enables
actual LLM responses when external APIs are not available.

Features:
- Self-hosted LLaMA3 via Ollama
- Automatic fallback hierarchy: Main LLM → Local LLaMA3 → Demo responses
- Real AI responses without API costs
- Works offline once model is downloaded
- MSPSDC-specific AI assistant capabilities
"""

import requests
import json
import time
import sys

def print_banner():
    """Print LLaMA3 self-hosted demo banner"""
    print("=" * 80)
    print("🦙 WhatsApp Chat UI - LLaMA3 Self-Hosted Demo")
    print("=" * 80)
    print("This demo showcases LLaMA3 self-hosted support that:")
    print("• Provides real AI responses without external APIs")
    print("• Uses local LLaMA3 via Ollama for inference")
    print("• Works offline once model is downloaded")
    print("• Offers zero API costs and complete privacy")
    print("• Maintains conversation context and memory")
    print("• Serves as fallback when main LLM service unavailable")
    print("=" * 80)

def check_services():
    """Check all service statuses including local LLM"""
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
            print(f"   Active Service: {flask_data.get('active_service', 'unknown')}")
            print(f"   Enhanced Mode: {flask_data.get('enhanced_mode', False)}")
        else:
            flask_status = "❌ Error"
            print(f"Flask Chat UI (port 8000): {flask_status}")
    except Exception as e:
        flask_status = "❌ Not Running"
        print(f"Flask Chat UI (port 8000): {flask_status}")
        print(f"   Error: {e}")
    
    # Check detailed LLM status
    print("\n🔍 Detailed LLM Service Status")
    print("-" * 40)
    try:
        response = requests.get("http://127.0.0.1:8000/api/llm/status", timeout=5)
        if response.status_code == 200:
            llm_data = response.json()
            
            print(f"Main LLM Service:")
            print(f"   Available: {'✅' if llm_data.get('main_llm_available') else '❌'}")
            print(f"   Test Response: {'✅' if llm_data.get('main_llm_test') else '❌'}")
            print(f"   URL: {llm_data.get('main_service_url', 'N/A')}")
            
            print(f"\nLocal LLM (LLaMA3):")
            print(f"   Available: {'✅' if llm_data.get('local_llm_available') else '❌'}")
            print(f"   Test Response: {'✅' if llm_data.get('local_llm_test') else '❌'}")
            print(f"   URL: {llm_data.get('local_service_url', 'N/A')}")
            print(f"   Model: {llm_data.get('local_model', 'N/A')}")
            
            print(f"\nActive Service: {llm_data.get('active_service', 'unknown')}")
            print(f"Recommendation: {llm_data.get('recommendation', 'N/A')}")
        else:
            print("❌ Could not get LLM status")
    except Exception as e:
        print(f"❌ LLM service error: {e}")

def check_ollama_directly():
    """Check Ollama service directly"""
    print("\n🦙 Direct Ollama Check")
    print("-" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_names = [model.get('name', '') for model in models.get('models', [])]
            
            print(f"Ollama Server: ✅ Running")
            print(f"Available Models: {len(model_names)}")
            for model in model_names:
                print(f"   • {model}")
            
            # Check specifically for LLaMA3
            llama_models = [m for m in model_names if 'llama3' in m.lower()]
            if llama_models:
                print(f"\n🦙 LLaMA3 Models Found: {len(llama_models)}")
                for model in llama_models:
                    print(f"   ✅ {model}")
            else:
                print(f"\n⚠️  No LLaMA3 models found")
                print("   Install with: ollama pull llama3")
        else:
            print(f"Ollama Server: ❌ Error (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("Ollama Server: ❌ Not running")
        print("   Start with: ollama serve")
    except Exception as e:
        print(f"Ollama Server: ❌ Error: {e}")

def test_ollama_setup_info():
    """Test the Ollama setup info endpoint"""
    print("\n📋 Ollama Setup Information")
    print("-" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/ollama/setup")
        if response.status_code == 200:
            setup_data = response.json()
            
            print("Setup Instructions:")
            for step, info in setup_data.get('setup_instructions', {}).items():
                print(f"\n📌 {step.replace('_', ' ').title()}:")
                print(f"   Command: {info.get('command', 'N/A')}")
                print(f"   Description: {info.get('description', 'N/A')}")
            
            print(f"\n💡 Benefits of Local LLaMA3:")
            for benefit in setup_data.get('benefits', []):
                print(f"   ✅ {benefit}")
                
        else:
            print("❌ Could not get setup information")
    except Exception as e:
        print(f"❌ Setup info error: {e}")

def test_demo_vs_local_ai():
    """Test responses in different modes"""
    print("\n🎭 Testing Demo vs Local AI Responses")
    print("-" * 40)
    
    test_messages = [
        "Hello! I need information about MSPSDC services.",
        "What documents are required for a caste certificate?",
        "Can you explain the welfare schemes available in Meghalaya?"
    ]
    
    # Test current mode
    try:
        health_response = requests.get("http://127.0.0.1:8000/api/health")
        current_mode = health_response.json().get('active_service', 'unknown')
        print(f"Current Active Service: {current_mode}")
    except:
        print("Could not determine current mode")
        current_mode = "unknown"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        
        try:
            response = requests.post("http://127.0.0.1:8000/api/chat/send", 
                                   json={"message": message}, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"👤 User: {message}")
                print(f"🤖 Response ({current_mode}):")
                print(f"   {data.get('bot_response', 'No response')}")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)

def demonstrate_fallback_hierarchy():
    """Demonstrate the intelligent fallback system"""
    print("\n🔄 Fallback Hierarchy Demonstration")
    print("-" * 40)
    print("""
The system uses intelligent fallback in this order:

1️⃣  Primary: Main LLM Service (Port 5000)
    • External API services (OpenAI, Anthropic, etc.)
    • Used when USE_ENHANCED_MODE=true
    • Highest quality responses

2️⃣  Secondary: Local LLaMA3 (Ollama Port 11434)
    • Self-hosted LLaMA3 model
    • Works offline, no API costs
    • Full conversation context
    • MSPSDC-specific responses

3️⃣  Tertiary: Demo Responses
    • Predefined responses for testing
    • Always available fallback
    • Categorized by query type

Benefits:
• Never fails - always provides a response
• Cost-effective - uses local model when possible
• Privacy-focused - local processing
• Reliable - multiple fallback options
""")

def show_ollama_setup_guide():
    """Show complete Ollama setup guide"""
    print("\n🦙 Complete Ollama + LLaMA3 Setup Guide")
    print("-" * 50)
    
    print("""
📥 INSTALLATION STEPS:

1. Install Ollama:
   curl -fsSL https://ollama.ai/install.sh | sh

2. Start Ollama Server:
   ollama serve
   # Runs on http://localhost:11434

3. Download LLaMA3 Model:
   ollama pull llama3
   # Downloads ~4.7GB model file

4. Verify Installation:
   curl http://localhost:11434/api/tags

5. Test LLaMA3:
   curl -X POST http://localhost:11434/api/chat \\
     -H "Content-Type: application/json" \\
     -d '{
       "model": "llama3",
       "messages": [{"role": "user", "content": "Hello"}],
       "stream": false
     }'

🔧 CONFIGURATION:
   • Set OLLAMA_BASE_URL=http://127.0.0.1:11434
   • Set OLLAMA_MODEL=llama3
   • Restart Flask app after configuration

✅ VERIFICATION:
   • Chat interface will show "Local AI" mode
   • Responses will be generated by LLaMA3
   • No external API calls required

🎯 ADVANTAGES:
   • Completely free - no API costs
   • Works offline once model is downloaded
   • Full privacy - all processing local
   • Fast responses for small queries
   • Consistent with your MSPSDC use case
""")

def show_api_examples():
    """Show API examples for LLaMA3 integration"""
    print("\n📚 LLaMA3 Integration API Examples")
    print("-" * 40)
    
    examples = [
        {
            "name": "Check Ollama Setup Info",
            "method": "GET",
            "url": "http://127.0.0.1:8000/api/ollama/setup",
            "description": "Get complete Ollama installation and setup instructions"
        },
        {
            "name": "Service Status with Local LLM",
            "method": "GET",
            "url": "http://127.0.0.1:8000/api/health",
            "description": "Check which service is active (main LLM, local LLM, or demo)"
        },
        {
            "name": "LLM Service Details",
            "method": "GET",
            "url": "http://127.0.0.1:8000/api/llm/status",
            "description": "Detailed status of both main and local LLM services"
        },
        {
            "name": "Test Local LLM Direct",
            "method": "POST",
            "url": "http://127.0.0.1:11434/api/chat",
            "description": "Direct test of Ollama API",
            "data": {
                "model": "llama3",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
        },
        {
            "name": "Chat with Current Service",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/chat/send",
            "description": "Send message using whichever service is available",
            "data": {"message": "Your query here"}
        }
    ]
    
    for example in examples:
        print(f"\n🔧 {example['name']}:")
        print(f"   {example['method']} {example['url']}")
        print(f"   📝 {example['description']}")
        if 'data' in example:
            print(f"   📄 Data: {json.dumps(example['data'], indent=4)}")

def main():
    """Main LLaMA3 self-hosted demo function"""
    print_banner()
    
    # Check current services
    check_services()
    
    # Check Ollama directly
    check_ollama_directly()
    
    # Get setup info
    test_ollama_setup_info()
    
    # Test responses
    test_demo_vs_local_ai()
    
    # Demonstrate fallback system
    demonstrate_fallback_hierarchy()
    
    # Show setup guide
    show_ollama_setup_guide()
    
    # Show API examples
    show_api_examples()
    
    print("\n" + "=" * 80)
    print("🦙 LLaMA3 Self-Hosted Demo Complete!")
    print("=" * 80)
    print("✅ LLaMA3 Self-Hosted Benefits:")
    print("   • Real AI responses without external APIs")
    print("   • Zero ongoing costs - completely free")
    print("   • Works offline once model is downloaded")
    print("   • Complete privacy - all processing local")
    print("   • Fallback support for reliable service")
    print("   • MSPSDC-specific AI assistant responses")
    print("")
    print("🚀 Get Started:")
    print("   1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    print("   2. Start service: ollama serve")
    print("   3. Download model: ollama pull llama3")
    print("   4. Chat interface: http://127.0.0.1:8000/")
    print("=" * 80)

if __name__ == "__main__":
    main()