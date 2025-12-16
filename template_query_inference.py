#!/usr/bin/env python3
"""
Template Query Inference Script

This script demonstrates running inference on the LLM endpoint with template queries.
It provides predefined template queries that can be used to test the RAG pipeline.
"""

import requests
import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Configuration
LLM_ENDPOINT = "http://localhost:5000/query/"
DEFAULT_TIMEOUT = 120  # 2 minutes timeout for LLM responses


@dataclass
class TemplateQuery:
    """Data class for template queries"""
    name: str
    query: str
    query_type: str = ""
    description: str = ""


# Predefined template queries for testing
TEMPLATE_QUERIES = [
    TemplateQuery(
        name="service_inquiry",
        query="What services are available at MSPSDC?",
        query_type="informational",
        description="General inquiry about available services"
    ),
    TemplateQuery(
        name="complaint_process",
        query="How do I file a complaint with MSPSDC?",
        query_type="procedural",
        description="Query about the complaint filing process"
    ),
    TemplateQuery(
        name="contact_info",
        query="What is the contact information for MSPSDC?",
        query_type="factual",
        description="Query for contact details"
    ),
    TemplateQuery(
        name="eligibility",
        query="What are the eligibility criteria for MSPSDC services?",
        query_type="procedural",
        description="Query about service eligibility"
    ),
    TemplateQuery(
        name="documentation",
        query="What documents are required to apply for services?",
        query_type="informational",
        description="Query about required documentation"
    ),
]


class TemplateQueryInference:
    """Class to handle template query inference"""

    def __init__(self, endpoint: str = LLM_ENDPOINT, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the template query inference client

        Args:
            endpoint: The LLM endpoint URL
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.timeout = timeout

    def prepare_query_payload(
        self,
        template: TemplateQuery,
        message_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Prepare the query payload for the LLM endpoint

        Args:
            template: TemplateQuery object
            message_history: Optional message history

        Returns:
            Dictionary with query payload
        """
        if message_history is None:
            message_history = []

        return {
            "query": template.query,
            "message_history": message_history,
            "query_type": template.query_type
        }

    def run_inference(
        self,
        template: TemplateQuery,
        message_history: List[Dict[str, str]] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run inference with a template query

        Args:
            template: TemplateQuery object
            message_history: Optional message history
            verbose: Whether to print detailed output

        Returns:
            Response from the LLM endpoint
        """
        payload = self.prepare_query_payload(template, message_history)

        if verbose:
            print(f"\n{'='*70}")
            print(f"Template: {template.name}")
            print(f"Description: {template.description}")
            print(f"Query: {template.query}")
            print(f"Query Type: {template.query_type}")
            print(f"{'='*70}")
            print("Sending request to LLM endpoint...")

        try:
            start_time = time.time()
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout
            )
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                if verbose:
                    print(f"✓ Response received in {elapsed_time:.2f}s")
                    print(f"\nResponse:")
                    print(f"-" * 70)
                    print(result.get("response", "No response content"))
                    print(f"-" * 70)
                    if "response_time" in result:
                        print(f"Response time: {result['response_time']}")

                result["inference_time"] = elapsed_time
                result["template_name"] = template.name
                return result

            else:
                error_msg = f"Error: HTTP {response.status_code}"
                if verbose:
                    print(f"✗ {error_msg}")
                    print(f"Response: {response.text}")
                return {"error": error_msg, "status_code": response.status_code}

        except requests.exceptions.Timeout:
            error_msg = f"Timeout: Request exceeded {self.timeout}s"
            if verbose:
                print(f"✗ {error_msg}")
            return {"error": error_msg}
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection Error: Unable to reach endpoint at {self.endpoint}"
            if verbose:
                print(f"✗ {error_msg}")
                print(f"Make sure the FastAPI service is running on port 5000")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            if verbose:
                print(f"✗ {error_msg}")
            return {"error": error_msg}

    def run_all_templates(self, verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Run inference for all predefined template queries

        Args:
            verbose: Whether to print detailed output

        Returns:
            List of responses from all template queries
        """
        results = []
        for template in TEMPLATE_QUERIES:
            result = self.run_inference(template, verbose=verbose)
            results.append(result)
            # Add a small delay between requests
            time.sleep(1)

        return results

    def run_custom_query(
        self,
        query: str,
        query_type: str = "",
        message_history: List[Dict[str, str]] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run inference with a custom query

        Args:
            query: The query string
            query_type: Type of query
            message_history: Optional message history
            verbose: Whether to print detailed output

        Returns:
            Response from the LLM endpoint
        """
        custom_template = TemplateQuery(
            name="custom",
            query=query,
            query_type=query_type,
            description="Custom query"
        )
        return self.run_inference(custom_template, message_history, verbose)


def main():
    """Main function to demonstrate template query inference"""
    print("\n" + "="*70)
    print("LLM Template Query Inference")
    print("="*70)

    # Initialize the inference client
    inference_client = TemplateQueryInference()

    # Check if endpoint is reachable
    print(f"\nAttempting to connect to LLM endpoint: {LLM_ENDPOINT}")
    try:
        response = requests.get(
            LLM_ENDPOINT.replace("/query/", "/"),
            timeout=5
        )
        if response.status_code == 200:
            print("✓ Connected to LLM endpoint successfully")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Endpoint returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to LLM endpoint")
        print("Please make sure:")
        print("  1. The FastAPI service is running: python openai_functionality.py")
        print("  2. The service is accessible at http://localhost:5000")
        return

    # Run a single template query as example
    print("\n" + "="*70)
    print("Running Example: Service Inquiry")
    print("="*70)

    result = inference_client.run_inference(TEMPLATE_QUERIES[0])

    if "error" not in result:
        print("\n✓ Inference completed successfully!")
        print(f"Total inference time: {result.get('inference_time', 'N/A'):.2f}s")
    else:
        print(f"\n✗ Inference failed: {result['error']}")

    # Optional: Run all templates (commented out for quick testing)
    # print("\n" + "="*70)
    # print("Running All Template Queries")
    # print("="*70)
    # all_results = inference_client.run_all_templates()
    # print(f"\nCompleted {len(all_results)} template queries")

    # Optional: Run a custom query
    print("\n" + "="*70)
    print("Running Custom Query Example")
    print("="*70)
    custom_result = inference_client.run_custom_query(
        query="Tell me about the online services available",
        query_type="informational"
    )


if __name__ == "__main__":
    main()
