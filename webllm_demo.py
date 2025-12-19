#!/usr/bin/env python3
"""
WebLLM Demo Script

Demonstrates WebLLM capabilities including:
- Model listing and selection
- Single and batch inference
- Configuration management
- Performance monitoring
- Error handling

Usage:
    python3 webllm_demo.py
"""

import requests
import json
import time
from typing import List, Dict, Any
from datetime import datetime

# Configuration
API_BASE = 'http://localhost:8000/webllm/api'
VERBOSE = True


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_info(text: str):
    """Print info message"""
    if VERBOSE:
        print(f"ℹ️  {text}")


def print_success(text: str):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text: str):
    """Print error message"""
    print(f"❌ {text}")


def print_data(data: Dict[str, Any], indent: int = 0):
    """Pretty print data"""
    print(json.dumps(data, indent=indent, sort_keys=True))


def check_api_health():
    """Check if API is available"""
    print_section("API Health Check")
    
    try:
        response = requests.get(f'{API_BASE}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy at {API_BASE}")
            print_info(f"Service: {data['service']}")
            print_info(f"Status: {data['status']}")
            print_info(f"Models loaded: {data['models_loaded']}")
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {API_BASE}")
        print_info("Make sure Flask server is running:")
        print_info("  python3 -c \"from app import create_app; app = create_app()[0]; app.run(port=8000)\"")
        return False


def list_models():
    """List available models"""
    print_section("Available Models")
    
    try:
        response = requests.get(f'{API_BASE}/models')
        data = response.json()
        
        print_success(f"Found {data['count']} models")
        print_info(f"Default model: {data['default_model']}\n")
        
        for i, model in enumerate(data['models'], 1):
            status = "⭐ RECOMMENDED" if model.get('recommended') else ""
            print(f"{i}. {model['model_id']}")
            print(f"   Size: {model['size_gb']}GB | VRAM: {model['vram_required_gb']}GB {status}")
        
        return data['models']
    except Exception as e:
        print_error(f"Error listing models: {e}")
        return []


def get_model_info(model_type: str):
    """Get information about a specific model"""
    print_section(f"Model Information: {model_type}")
    
    try:
        response = requests.get(f'{API_BASE}/models/{model_type}/info')
        
        if response.status_code == 200:
            data = response.json()
            print_success("Model information retrieved")
            print_data(data, indent=2)
            return data
        elif response.status_code == 404:
            print_error(f"Model not found: {model_type}")
            return None
        else:
            print_error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error retrieving model info: {e}")
        return None


def single_inference(prompt: str, model_id: str, config: Dict[str, Any] = None):
    """Run single inference"""
    print_section("Single Inference")
    print_info(f"Prompt: {prompt}")
    print_info(f"Model: {model_id}")
    
    if config:
        print_info(f"Config: temperature={config.get('temperature', 0.7)}, "
                  f"max_tokens={config.get('max_tokens', 512)}")
    
    try:
        payload = {
            'prompt': prompt,
            'model_id': model_id
        }
        
        if config:
            payload.update(config)
        
        start_time = time.time()
        response = requests.post(f'{API_BASE}/infer', json=payload)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Inference completed in {elapsed:.2f}s")
            print(f"\nResponse:")
            print(f"  Text: {data['text'][:200]}...")
            print(f"  Tokens: {data['tokens_generated']}")
            print(f"  Time: {data['inference_time_ms']:.1f}ms")
            print(f"  Mode: {data['mode']}")
            return data
        else:
            error_data = response.json()
            print_error(f"Inference failed: {error_data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Error during inference: {e}")
        return None


def batch_inference(prompts: List[str], model_id: str):
    """Run batch inference"""
    print_section("Batch Inference")
    print_info(f"Prompts: {len(prompts)}")
    print_info(f"Model: {model_id}")
    
    for i, prompt in enumerate(prompts, 1):
        print_info(f"  {i}. {prompt[:50]}...")
    
    try:
        payload = {
            'prompts': prompts,
            'model_id': model_id,
            'temperature': 0.7
        }
        
        start_time = time.time()
        response = requests.post(f'{API_BASE}/infer/batch', json=payload)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Batch inference completed in {elapsed:.2f}s")
            print(f"\nResults:")
            print(f"  Total prompts: {data['total_prompts']}")
            print(f"  Successful: {data['successful']}")
            print(f"  Total time: {data['total_time_ms']:.1f}ms")
            print(f"  Total tokens: {data['total_tokens']}")
            print(f"  Avg time per prompt: {data['total_time_ms']/len(prompts):.1f}ms")
            
            for i, result in enumerate(data['results'], 1):
                if 'error' not in result:
                    print(f"\n  Result {i}:")
                    print(f"    Text: {result['text'][:100]}...")
                    print(f"    Tokens: {result['tokens_generated']}")
                    print(f"    Time: {result['inference_time_ms']:.1f}ms")
            
            return data
        else:
            error_data = response.json()
            print_error(f"Batch inference failed: {error_data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Error during batch inference: {e}")
        return None


def configure_model(model_type: str, config: Dict[str, Any]):
    """Configure a model"""
    print_section("Model Configuration")
    print_info(f"Model: {model_type}")
    print_info(f"Config: {json.dumps(config, indent=2)}")
    
    try:
        payload = {'model_type': model_type}
        payload.update(config)
        
        response = requests.post(f'{API_BASE}/config/models', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Model configured successfully")
            print(f"  Status: {data['status']}")
            print(f"  Model: {data['model_type']}")
            return data
        else:
            error_data = response.json()
            print_error(f"Configuration failed: {error_data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Error configuring model: {e}")
        return None


def get_metrics():
    """Get performance metrics"""
    print_section("Performance Metrics")
    
    try:
        response = requests.get(f'{API_BASE}/metrics')
        
        if response.status_code == 200:
            data = response.json()
            metrics = data['metrics']
            
            print_success("Metrics retrieved")
            print(f"\nInference Statistics:")
            print(f"  Total inferences: {metrics['total_inferences']}")
            print(f"  Total tokens: {metrics['total_tokens']}")
            print(f"  Total time: {metrics['total_time_ms']:.1f}ms")
            print(f"  Average inference time: {metrics['average_inference_time']:.1f}ms")
            print(f"\nExecution Mode:")
            print(f"  Client-side: {metrics['client_side_count']}")
            print(f"  Server-side: {metrics['server_side_count']}")
            
            if metrics['total_inferences'] > 0:
                client_pct = (metrics['client_side_count'] / metrics['total_inferences']) * 100
                print(f"  Client-side %: {client_pct:.1f}%")
            
            return data
        else:
            print_error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error retrieving metrics: {e}")
        return None


def get_history(limit: int = 5):
    """Get inference history"""
    print_section(f"Inference History (last {limit})")
    
    try:
        response = requests.get(f'{API_BASE}/history?limit={limit}')
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {data['count']} recent inferences")
            
            for i, record in enumerate(data['history'], 1):
                print(f"\n{i}. [{record['timestamp']}]")
                print(f"   Model: {record['model_id']}")
                print(f"   Mode: {record['mode']}")
                print(f"   Tokens: {record['tokens_generated']}")
                print(f"   Time: {record['inference_time_ms']:.1f}ms")
                print(f"   Text: {record['text'][:80]}...")
            
            return data
        else:
            print_error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error retrieving history: {e}")
        return None


def get_status():
    """Get system status"""
    print_section("System Status")
    
    try:
        response = requests.get(f'{API_BASE}/status')
        
        if response.status_code == 200:
            data = response.json()
            print_success("Status retrieved")
            print(f"\nSystem Information:")
            print(f"  Status: {data['status']}")
            print(f"  Service: {data['service']}")
            print(f"  Timestamp: {data['timestamp']}")
            print(f"\nResources:")
            print(f"  Models configured: {data['models_configured']}")
            print(f"  Models loaded: {data['models_loaded']}")
            print(f"\nPerformance:")
            print(f"  Total inferences: {data['total_inferences']}")
            print(f"  Average inference time: {data['average_inference_time_ms']:.1f}ms")
            
            return data
        else:
            print_error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error retrieving status: {e}")
        return None


def clear_data():
    """Clear all data"""
    print_section("Clear Data")
    
    try:
        response = requests.post(f'{API_BASE}/clear')
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Data cleared at {data['timestamp']}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error clearing data: {e}")
        return False


def run_demo_scenarios():
    """Run comprehensive demo scenarios"""
    print_section("Running Demo Scenarios")
    
    # Scenario 1: Get models
    models = list_models()
    if not models:
        return
    
    default_model = models[0]['model_id']
    
    # Scenario 2: Get model info
    get_model_info(default_model)
    
    # Scenario 3: Configure model
    config = {
        'temperature': 0.7,
        'max_tokens': 256,
        'top_p': 0.9
    }
    configure_model('default', config)
    
    # Scenario 4: Single inference
    prompts = [
        "What is machine learning?",
        "Explain neural networks briefly",
        "How does WebLLM work?"
    ]
    
    for prompt in prompts:
        single_inference(prompt, default_model)
        time.sleep(0.5)
    
    # Scenario 5: Batch inference
    batch_prompts = [
        "What is Python?",
        "What is JavaScript?",
        "What is Go?"
    ]
    batch_inference(batch_prompts, default_model)
    
    # Scenario 6: Get metrics
    get_metrics()
    
    # Scenario 7: Get history
    get_history(limit=10)
    
    # Scenario 8: Get status
    get_status()


def main():
    """Main demo function"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "WebLLM Demo Script" + " " * 40 + "║")
    print("║" + " " * 78 + "║")
    print("║" + " Client-Side Browser-Based LLM Inference" + " " * 38 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Check API health
    if not check_api_health():
        return
    
    # Run demo scenarios
    try:
        run_demo_scenarios()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    # Final status
    print_section("Demo Complete")
    print_success("WebLLM demo completed successfully!")
    print_info("Access the web interface at: http://localhost:8000/webllm/")
    print_info("Check the full documentation: WEBLLM_DOCUMENTATION.md")
    print_info("View the quick start guide: WEBLLM_QUICKSTART.md")


if __name__ == '__main__':
    main()
