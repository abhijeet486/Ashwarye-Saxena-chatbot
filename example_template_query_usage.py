#!/usr/bin/env python3
"""
Example Usage of Template Query Inference

This script demonstrates how to use the template query inference module
in various scenarios and use cases.
"""

from template_query_inference import (
    TemplateQueryInference,
    TemplateQuery,
    TEMPLATE_QUERIES
)


def example_1_single_template():
    """Example 1: Run a single predefined template query"""
    print("\n" + "="*80)
    print("Example 1: Running a Single Template Query")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    # Get the first template (service inquiry)
    template = TEMPLATE_QUERIES[0]

    print(f"Template Name: {template.name}")
    print(f"Query: {template.query}")
    print(f"Type: {template.query_type}\n")

    result = client.run_inference(template, verbose=False)

    if "error" not in result:
        print(f"Response received in {result.get('inference_time', 0):.2f}s\n")
        print(f"Response:\n{result['response']}")
    else:
        print(f"Error: {result['error']}")


def example_2_custom_query():
    """Example 2: Run a custom query"""
    print("\n" + "="*80)
    print("Example 2: Running a Custom Query")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    custom_query = "Tell me about the online application process"

    print(f"Custom Query: {custom_query}\n")

    result = client.run_custom_query(
        query=custom_query,
        query_type="procedural",
        verbose=False
    )

    if "error" not in result:
        print(f"Response received in {result.get('inference_time', 0):.2f}s\n")
        print(f"Response:\n{result['response']}")
    else:
        print(f"Error: {result['error']}")


def example_3_with_context():
    """Example 3: Run query with message history context"""
    print("\n" + "="*80)
    print("Example 3: Running Query with Message History")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    # Create a message history to provide context
    message_history = [
        {
            "role": "user",
            "content": "I want to apply for a service"
        },
        {
            "role": "assistant",
            "content": "I can help you with that. Which service are you interested in?"
        }
    ]

    template = TemplateQuery(
        name="follow_up",
        query="What documents do I need?",
        query_type="informational",
        description="Follow-up question in a conversation"
    )

    print(f"Previous Context:")
    for msg in message_history:
        print(f"  {msg['role'].upper()}: {msg['content']}")

    print(f"\nNew Query: {template.query}\n")

    result = client.run_inference(template, message_history=message_history, verbose=False)

    if "error" not in result:
        print(f"Response received in {result.get('inference_time', 0):.2f}s\n")
        print(f"Response:\n{result['response']}")
    else:
        print(f"Error: {result['error']}")


def example_4_batch_processing():
    """Example 4: Batch process multiple templates"""
    print("\n" + "="*80)
    print("Example 4: Batch Processing Multiple Templates")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    # Select specific templates to process
    templates_to_process = TEMPLATE_QUERIES[:3]  # First 3 templates

    results = []

    for i, template in enumerate(templates_to_process, 1):
        print(f"[{i}/{len(templates_to_process)}] Processing: {template.name}...", end=" ", flush=True)

        result = client.run_inference(template, verbose=False)
        results.append(result)

        if "error" in result:
            print(f"✗ Error")
        else:
            print(f"✓ ({result.get('inference_time', 0):.2f}s)")

    # Summary
    print(f"\nBatch Processing Summary:")
    print(f"Total queries: {len(results)}")
    successful = sum(1 for r in results if "error" not in r)
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")

    total_time = sum(r.get('inference_time', 0) for r in results if "error" not in r)
    print(f"Total time: {total_time:.2f}s")
    if successful > 0:
        print(f"Average time: {total_time/successful:.2f}s")


def example_5_error_handling():
    """Example 5: Handle errors gracefully"""
    print("\n" + "="*80)
    print("Example 5: Error Handling")
    print("="*80 + "\n")

    client = TemplateQueryInference(endpoint="http://localhost:9999")  # Wrong endpoint

    print("Attempting to reach non-existent endpoint...")
    result = client.run_custom_query(
        query="This will fail",
        verbose=False
    )

    if "error" in result:
        print(f"✓ Error caught: {result['error']}")
        print(f"  This is expected - endpoint is not reachable")
    else:
        print("Unexpected success!")


def example_6_create_custom_template():
    """Example 6: Create and use a custom template"""
    print("\n" + "="*80)
    print("Example 6: Creating and Using Custom Templates")
    print("="*80 + "\n")

    # Create custom templates
    custom_templates = [
        TemplateQuery(
            name="custom_service_fee",
            query="What is the fee structure for online services?",
            query_type="factual",
            description="Query about service fees"
        ),
        TemplateQuery(
            name="custom_grievance",
            query="What should I do if I have a complaint?",
            query_type="procedural",
            description="Query about grievance redressal"
        ),
    ]

    client = TemplateQueryInference()

    for template in custom_templates:
        print(f"Template: {template.name}")
        print(f"Query: {template.query}\n")

        result = client.run_inference(template, verbose=False)

        if "error" not in result:
            print(f"Response: {result['response'][:100]}...")
        else:
            print(f"Error: {result['error']}")
        print()


def example_7_response_analysis():
    """Example 7: Analyze inference responses"""
    print("\n" + "="*80)
    print("Example 7: Response Analysis")
    print("="*80 + "\n")

    client = TemplateQueryInference()

    template = TEMPLATE_QUERIES[0]
    result = client.run_inference(template, verbose=False)

    if "error" not in result:
        print("Response Analysis:")
        print(f"-" * 80)
        print(f"Template Name: {result.get('template_name')}")
        print(f"Inference Time: {result.get('inference_time'):.2f}s")
        print(f"Response Time: {result.get('response_time')}")

        response_text = result.get('response', '')
        print(f"Response Length: {len(response_text)} characters")
        print(f"Response Word Count: {len(response_text.split())}")

        # Check for key indicators
        if len(response_text) > 50:
            print(f"✓ Response has substantive content")
        if "mspsdc" in response_text.lower() or "meghalaya" in response_text.lower():
            print(f"✓ Response mentions relevant keywords")

        print(f"\nFirst 200 characters of response:")
        print(f"{response_text[:200]}...")
    else:
        print(f"Error: {result['error']}")


def main():
    """Run all examples"""
    import sys

    print("\n" + "="*80)
    print("Template Query Inference - Usage Examples")
    print("="*80)

    examples = [
        ("Single Template", example_1_single_template),
        ("Custom Query", example_2_custom_query),
        ("With Context", example_3_with_context),
        ("Batch Processing", example_4_batch_processing),
        ("Error Handling", example_5_error_handling),
        ("Custom Template", example_6_create_custom_template),
        ("Response Analysis", example_7_response_analysis),
    ]

    if len(sys.argv) > 1:
        # Run specific example
        example_num = int(sys.argv[1])
        if 1 <= example_num <= len(examples):
            name, func = examples[example_num - 1]
            print(f"\nRunning: {name}")
            func()
        else:
            print(f"Invalid example number. Choose between 1 and {len(examples)}")
    else:
        # Run all examples
        for i, (name, func) in enumerate(examples, 1):
            try:
                func()
            except Exception as e:
                print(f"\n✗ Example {i} failed: {str(e)}")
                print(f"  Make sure the LLM endpoint is running")
                break

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
