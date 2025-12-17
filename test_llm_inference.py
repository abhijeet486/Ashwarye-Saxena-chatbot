#!/usr/bin/env python3
"""
Test LLM Inference Integration

This script tests the template query inference system with the LLM endpoint.
It can work with both a live server or in demo mode without a server.
"""

import sys
import json
import time
import requests
from template_query_inference import (
    TemplateQueryInference,
    TemplateQuery,
    TEMPLATE_QUERIES,
    LLM_ENDPOINT
)


def check_server_health():
    """Check if the LLM server is running"""
    try:
        response = requests.get(
            LLM_ENDPOINT.replace("/query/", "/"),
            timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        return False, f"Server returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, str(e)


def demo_mode_test():
    """Run tests in demo mode (without actual server)"""
    print("\n" + "="*80)
    print("DEMO MODE - Testing Template Query Infrastructure")
    print("="*80 + "\n")
    
    print("1. Testing TemplateQueryInference initialization...")
    client = TemplateQueryInference()
    print(f"   ✓ Client initialized with endpoint: {client.endpoint}")
    print(f"   ✓ Timeout set to: {client.timeout}s")
    
    print("\n2. Testing template queries loading...")
    print(f"   ✓ Loaded {len(TEMPLATE_QUERIES)} predefined templates:")
    for i, template in enumerate(TEMPLATE_QUERIES, 1):
        print(f"      {i}. {template.name}: {template.query[:50]}...")
    
    print("\n3. Testing payload preparation...")
    template = TEMPLATE_QUERIES[0]
    payload = client.prepare_query_payload(template)
    print(f"   ✓ Payload structure:")
    print(f"      - query: {payload['query'][:50]}...")
    print(f"      - message_history: {payload['message_history']}")
    print(f"      - query_type: {payload['query_type']}")
    
    print("\n4. Testing JSON template configuration...")
    with open('template_queries.json', 'r') as f:
        json_data = json.load(f)
    print(f"   ✓ Loaded {len(json_data['templates'])} templates from JSON")
    print(f"   ✓ Categories: {set(t.get('category', 'general') for t in json_data['templates'])}")
    
    print("\n" + "="*80)
    print("DEMO MODE COMPLETE - All infrastructure tests passed!")
    print("="*80 + "\n")
    
    print("NOTE: To test with actual LLM inference, start the server:")
    print("      python3 openai_functionality.py")
    print("Then run this script again.")


def live_server_test():
    """Run tests with actual LLM server"""
    print("\n" + "="*80)
    print("LIVE SERVER MODE - Testing Actual LLM Inference")
    print("="*80 + "\n")
    
    client = TemplateQueryInference()
    
    print("1. Testing server health endpoint...")
    is_healthy, result = check_server_health()
    if is_healthy:
        print(f"   ✓ Server is healthy: {result}")
    else:
        print(f"   ✗ Server health check failed: {result}")
        return False
    
    print("\n2. Running single template inference...")
    template = TEMPLATE_QUERIES[0]
    print(f"   Template: {template.name}")
    print(f"   Query: {template.query}")
    
    start_time = time.time()
    result = client.run_inference(template, verbose=False)
    elapsed = time.time() - start_time
    
    if "error" not in result:
        print(f"   ✓ Inference successful ({elapsed:.2f}s)")
        print(f"   ✓ Response length: {len(result.get('response', ''))} characters")
        print(f"\n   Response preview:")
        print(f"   {'-'*76}")
        response_preview = result.get('response', '')[:200]
        print(f"   {response_preview}...")
        print(f"   {'-'*76}")
        return True
    else:
        print(f"   ✗ Inference failed: {result['error']}")
        return False


def interactive_test():
    """Run interactive test where user can try queries"""
    print("\n" + "="*80)
    print("INTERACTIVE MODE - Test Your Own Queries")
    print("="*80 + "\n")
    
    is_healthy, _ = check_server_health()
    if not is_healthy:
        print("⚠ Server is not running. Starting demo mode instead.\n")
        demo_mode_test()
        return
    
    client = TemplateQueryInference()
    
    print("Available templates:")
    for i, template in enumerate(TEMPLATE_QUERIES, 1):
        print(f"  {i}. {template.name}: {template.query}")
    
    print("\nCommands:")
    print("  - Enter template number (1-5) to run that template")
    print("  - Enter 'custom: your question' to ask a custom question")
    print("  - Enter 'quit' to exit")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Exiting interactive mode.")
                break
            
            if user_input.startswith('custom:'):
                query_text = user_input[7:].strip()
                result = client.run_custom_query(query_text, verbose=True)
            elif user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(TEMPLATE_QUERIES):
                    result = client.run_inference(TEMPLATE_QUERIES[idx], verbose=True)
                else:
                    print(f"Invalid template number. Choose 1-{len(TEMPLATE_QUERIES)}")
                    continue
            else:
                print("Invalid input. Use template number or 'custom: question'")
                continue
                
        except KeyboardInterrupt:
            print("\nExiting interactive mode.")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("LLM Template Query Inference - Integration Test")
    print("="*80)
    
    # Check if server is running
    print("\nChecking LLM server status...")
    is_healthy, message = check_server_health()
    
    if is_healthy:
        print(f"✓ Server is running: {message}\n")
        
        # Ask user what mode they want
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
        else:
            print("Select test mode:")
            print("  1. Live server test (single query)")
            print("  2. Interactive mode (try multiple queries)")
            print("  3. Demo mode (no server needed)")
            
            try:
                choice = input("\nEnter choice (1-3): ").strip()
                mode = {'1': 'live', '2': 'interactive', '3': 'demo'}.get(choice, 'demo')
            except KeyboardInterrupt:
                print("\nCancelled.")
                return
        
        if mode == 'live':
            live_server_test()
        elif mode == 'interactive':
            interactive_test()
        else:
            demo_mode_test()
    else:
        print(f"✗ Server is not running: {message}")
        print("\nRunning in DEMO MODE (no server required)...")
        demo_mode_test()
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
