#!/usr/bin/env python3
"""
Quick test script to run template query inference
"""

import sys
from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES


def test_single_template():
    """Test a single template query"""
    print("\n" + "="*80)
    print("Testing Single Template Query Inference")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    # Test the first template query (service inquiry)
    template = TEMPLATE_QUERIES[0]
    print(f"Testing template: {template.name}")
    print(f"Query: {template.query}\n")

    result = client.run_inference(template, verbose=True)

    if "error" in result:
        print(f"\nError occurred: {result['error']}")
        return False
    else:
        print(f"\nTemplate query inference successful!")
        return True


def test_all_templates():
    """Test all template queries"""
    print("\n" + "="*80)
    print("Testing All Template Queries")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    for i, template in enumerate(TEMPLATE_QUERIES, 1):
        print(f"\n[{i}/{len(TEMPLATE_QUERIES)}] Testing: {template.name}")
        result = client.run_inference(template, verbose=False)

        if "error" in result:
            print(f"  ✗ Error: {result['error']}")
        else:
            print(f"  ✓ Success (inference time: {result.get('inference_time', 'N/A'):.2f}s)")

    print(f"\n✓ All templates tested!")


def test_custom_query(query_text=None):
    """Test with a custom query"""
    if query_text is None:
        query_text = "What are the services provided by MSPSDC?"

    print("\n" + "="*80)
    print("Testing Custom Query")
    print("="*80 + "\n")

    client = TemplateQueryInference()
    result = client.run_custom_query(
        query=query_text,
        query_type="informational",
        verbose=True
    )

    if "error" in result:
        print(f"\nError: {result['error']}")
        return False
    else:
        print(f"\n✓ Custom query inference successful!")
        return True


if __name__ == "__main__":
    print("LLM Template Query Inference Test")
    print("="*80)
    print("Available options:")
    print("  1. Single template query test")
    print("  2. All template queries test")
    print("  3. Custom query test")
    print("="*80 + "\n")

    # Run single template by default
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            test_all_templates()
        elif sys.argv[1] == "custom":
            custom_query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
            test_custom_query(custom_query)
        else:
            test_single_template()
    else:
        # Default: run single template
        test_single_template()

    print("\n" + "="*80)
    print("Test completed!")
    print("="*80 + "\n")
