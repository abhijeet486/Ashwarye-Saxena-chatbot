#!/usr/bin/env python3
"""
Visual Demo of Template Query Inference

This script provides a visual demonstration of how the inference system works,
even when the server is not running.
"""

import json
from template_query_inference import TEMPLATE_QUERIES

def print_banner(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def print_section(title):
    print(f"\n{title}")
    print("-" * len(title))

def demo_template_queries():
    """Show all available template queries"""
    print_banner("TEMPLATE QUERY INFERENCE - VISUAL DEMONSTRATION")
    
    print_section("📋 Available Template Queries")
    for i, template in enumerate(TEMPLATE_QUERIES, 1):
        print(f"\n{i}. {template.name.upper()}")
        print(f"   Query: \"{template.query}\"")
        print(f"   Type: {template.query_type}")
        print(f"   Description: {template.description}")

def demo_json_templates():
    """Show JSON template configuration"""
    print_section("\n📄 JSON Template Configuration")
    
    with open('template_queries.json', 'r') as f:
        data = json.load(f)
    
    print(f"\nTotal templates in JSON: {len(data['templates'])}")
    
    categories = {}
    for template in data['templates']:
        cat = template.get('category', 'general')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(template['name'])
    
    print(f"\nCategories: {', '.join(categories.keys())}")
    print("\nTemplates by category:")
    for cat, names in sorted(categories.items()):
        print(f"  • {cat.capitalize()}: {', '.join(names)}")

def demo_api_usage():
    """Show Python API usage examples"""
    print_section("\n🐍 Python API Usage Examples")
    
    code1 = """
# Basic usage
from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES

client = TemplateQueryInference()
result = client.run_inference(TEMPLATE_QUERIES[0])
print(result['response'])
"""
    
    code2 = """
# Custom query
result = client.run_custom_query(
    query="What are the office hours?",
    query_type="factual"
)
"""
    
    code3 = """
# With message history
history = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
]
result = client.run_inference(TEMPLATE_QUERIES[0], message_history=history)
"""
    
    print("\nExample 1: Basic Usage")
    print(code1)
    
    print("\nExample 2: Custom Query")
    print(code2)
    
    print("\nExample 3: With Context")
    print(code3)

def demo_cli_usage():
    """Show CLI usage examples"""
    print_section("\n💻 Command Line Usage Examples")
    
    commands = [
        ("List all templates", "python3 run_template_query_inference.py --list"),
        ("Check server health", "python3 run_template_query_inference.py --health"),
        ("Run specific template", "python3 run_template_query_inference.py --template service_inquiry"),
        ("Custom query", 'python3 run_template_query_inference.py --query "Your question"'),
        ("Run all templates", "python3 run_template_query_inference.py --all"),
        ("JSON output", "python3 run_template_query_inference.py --json"),
    ]
    
    for desc, cmd in commands:
        print(f"\n{desc}:")
        print(f"  $ {cmd}")

def demo_inference_flow():
    """Show the inference flow"""
    print_section("\n🔄 Inference Flow")
    
    flow = """
    User Input (Query)
         ↓
    TemplateQueryInference Client
         ↓
    HTTP POST to /query/
         ↓
    FastAPI Server (openai_functionality.py)
         ↓
    RAG Pipeline (tmp.py)
         ↓
    Document Search (ChromaDB)
         ↓
    LLM Processing (Llama3)
         ↓
    Response with Context
         ↓
    Return to Client
    """
    print(flow)

def demo_expected_response():
    """Show expected response format"""
    print_section("\n📦 Expected Response Format")
    
    example_response = {
        "response": "The Meghalaya State Public Services Delivery Commission (MSPSDC) provides various citizen services including...",
        "responses": [
            {
                "role": "system",
                "content": "RESPONSE BY RAG: [Full response with context]"
            }
        ],
        "response_time": "2024-01-15T14:23:45.123",
        "inference_time": 42.5
    }
    
    print("\nJSON Response Structure:")
    print(json.dumps(example_response, indent=2))

def main():
    """Run the complete demo"""
    demo_template_queries()
    demo_json_templates()
    demo_api_usage()
    demo_cli_usage()
    demo_inference_flow()
    demo_expected_response()
    
    print_banner("DEMO COMPLETE")
    
    print("\n📚 Next Steps:")
    print("  1. Start the LLM server: python3 openai_functionality.py")
    print("  2. Run integration tests: python3 test_template_query_integration.py")
    print("  3. Try interactive mode: python3 test_llm_inference.py")
    print("  4. Run a template: python3 run_template_query_inference.py --template service_inquiry")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
