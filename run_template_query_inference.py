#!/usr/bin/env python3
"""
Template Query Inference Runner

This is a standalone script to run template query inference against the LLM endpoint.
It can be invoked from command line with various options.

Usage:
    python run_template_query_inference.py                    # Run with first template
    python run_template_query_inference.py --all              # Run all templates
    python run_template_query_inference.py --template <name>  # Run specific template
    python run_template_query_inference.py --query "<text>"   # Run custom query
    python run_template_query_inference.py --json             # Output as JSON
    python run_template_query_inference.py --list             # List available templates
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES, TemplateQuery


def load_templates_from_json(json_file="template_queries.json"):
    """Load template queries from JSON file"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            templates = []
            for template_data in data.get("templates", []):
                template = TemplateQuery(
                    name=template_data["id"],
                    query=template_data["query"],
                    query_type=template_data.get("query_type", ""),
                    description=template_data.get("description", "")
                )
                templates.append(template)
            return templates
    except FileNotFoundError:
        print(f"Warning: {json_file} not found. Using built-in templates.")
        return TEMPLATE_QUERIES
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in {json_file}. Using built-in templates.")
        return TEMPLATE_QUERIES


def list_templates(templates=None):
    """Display available templates"""
    if templates is None:
        templates = TEMPLATE_QUERIES

    print("\n" + "="*80)
    print("Available Template Queries")
    print("="*80 + "\n")

    for i, template in enumerate(templates, 1):
        print(f"{i}. {template.name}")
        print(f"   Query: {template.query}")
        print(f"   Type: {template.query_type}")
        print(f"   Description: {template.description}")
        print()


def run_single_template(template_name, templates=None, output_json=False):
    """Run a single template by name"""
    if templates is None:
        templates = TEMPLATE_QUERIES

    template = None
    for t in templates:
        if t.name == template_name:
            template = t
            break

    if template is None:
        print(f"Error: Template '{template_name}' not found")
        list_templates(templates)
        return False

    client = TemplateQueryInference()
    result = client.run_inference(template, verbose=not output_json)

    if output_json:
        print(json.dumps(result, indent=2))

    return "error" not in result


def run_all_templates(templates=None, output_json=False):
    """Run all template queries"""
    if templates is None:
        templates = TEMPLATE_QUERIES

    client = TemplateQueryInference()
    results = []

    print("\n" + "="*80)
    print("Running All Template Queries")
    print("="*80 + "\n")

    for i, template in enumerate(templates, 1):
        if not output_json:
            print(f"[{i}/{len(templates)}] {template.name}...", end=" ", flush=True)

        result = client.run_inference(template, verbose=False)
        results.append(result)

        if not output_json:
            if "error" in result:
                print(f"✗ Error: {result['error']}")
            else:
                print(f"✓ ({result.get('inference_time', 0):.2f}s)")

    if output_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n✓ Completed {len(results)} template queries")

    return all("error" not in r for r in results)


def run_custom_query(query_text, query_type="", output_json=False):
    """Run a custom query"""
    client = TemplateQueryInference()
    result = client.run_custom_query(
        query=query_text,
        query_type=query_type,
        verbose=not output_json
    )

    if output_json:
        print(json.dumps(result, indent=2))

    return "error" not in result


def check_endpoint_health():
    """Check if the LLM endpoint is accessible"""
    import requests

    print("\nChecking LLM endpoint health...")
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✓ LLM endpoint is reachable")
            return True
        else:
            print(f"✗ LLM endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to LLM endpoint at http://localhost:5000")
        print("\nPlease ensure the FastAPI service is running:")
        print("  python openai_functionality.py")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request to LLM endpoint timed out")
        return False
    except Exception as e:
        print(f"✗ Error checking endpoint: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run template query inference against LLM endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run first template query
  python run_template_query_inference.py

  # Run all templates
  python run_template_query_inference.py --all

  # Run specific template
  python run_template_query_inference.py --template service_inquiry

  # Run custom query
  python run_template_query_inference.py --query "What are the services?"

  # List available templates
  python run_template_query_inference.py --list

  # Check endpoint health
  python run_template_query_inference.py --health

  # Output as JSON
  python run_template_query_inference.py --json
        """
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all template queries"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="Run specific template by name"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Run custom query"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available templates"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check LLM endpoint health"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--query-type",
        type=str,
        default="",
        help="Query type for custom queries (informational, procedural, factual, etc.)"
    )

    args = parser.parse_args()

    # Load templates
    templates = load_templates_from_json()

    # Handle different modes
    if args.health:
        success = check_endpoint_health()
        sys.exit(0 if success else 1)

    if args.list:
        list_templates(templates)
        sys.exit(0)

    if args.template:
        success = run_single_template(args.template, templates, args.json)
        sys.exit(0 if success else 1)

    if args.query:
        success = run_custom_query(args.query, args.query_type, args.json)
        sys.exit(0 if success else 1)

    if args.all:
        success = run_all_templates(templates, args.json)
        sys.exit(0 if success else 1)

    # Default: run first template
    if templates:
        success = run_single_template(templates[0].name, templates, args.json)
        sys.exit(0 if success else 1)
    else:
        print("Error: No templates available")
        sys.exit(1)


if __name__ == "__main__":
    main()
