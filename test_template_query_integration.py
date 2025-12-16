#!/usr/bin/env python3
"""
Integration tests for template query inference

Run this to verify the template query module is working correctly
"""

import sys
import json
from template_query_inference import (
    TemplateQueryInference,
    TemplateQuery,
    TEMPLATE_QUERIES
)


def test_template_query_class():
    """Test TemplateQuery data class"""
    print("Testing TemplateQuery class...", end=" ")
    
    template = TemplateQuery(
        name="test",
        query="Test query?",
        query_type="test",
        description="Test template"
    )
    
    assert template.name == "test"
    assert template.query == "Test query?"
    assert template.query_type == "test"
    assert template.description == "Test template"
    
    print("✓")


def test_predefined_templates():
    """Test predefined templates"""
    print("Testing predefined templates...", end=" ")
    
    assert len(TEMPLATE_QUERIES) > 0, "No templates found"
    
    for template in TEMPLATE_QUERIES:
        assert hasattr(template, 'name'), "Template missing 'name'"
        assert hasattr(template, 'query'), "Template missing 'query'"
        assert len(template.query) > 0, "Template query is empty"
    
    print(f"✓ ({len(TEMPLATE_QUERIES)} templates)")


def test_inference_client_initialization():
    """Test TemplateQueryInference client initialization"""
    print("Testing TemplateQueryInference initialization...", end=" ")
    
    client = TemplateQueryInference()
    assert client.endpoint == "http://localhost:5000/query/"
    assert client.timeout == 120
    
    client2 = TemplateQueryInference(endpoint="http://test:8000/", timeout=60)
    assert client2.endpoint == "http://test:8000/"
    assert client2.timeout == 60
    
    print("✓")


def test_payload_preparation():
    """Test query payload preparation"""
    print("Testing payload preparation...", end=" ")
    
    client = TemplateQueryInference()
    template = TEMPLATE_QUERIES[0]
    
    payload = client.prepare_query_payload(template)
    assert "query" in payload
    assert "message_history" in payload
    assert "query_type" in payload
    assert payload["query"] == template.query
    assert payload["message_history"] == []
    
    # Test with message history
    history = [{"role": "user", "content": "test"}]
    payload2 = client.prepare_query_payload(template, history)
    assert payload2["message_history"] == history
    
    print("✓")


def test_json_templates():
    """Test JSON template definitions"""
    print("Testing JSON template definitions...", end=" ")
    
    with open("template_queries.json", 'r') as f:
        data = json.load(f)
    
    assert "templates" in data, "No templates in JSON"
    assert len(data["templates"]) > 0, "Empty templates in JSON"
    
    for template in data["templates"]:
        assert "id" in template, "Missing 'id' in template"
        assert "query" in template, "Missing 'query' in template"
        assert "name" in template, "Missing 'name' in template"
    
    print(f"✓ ({len(data['templates'])} templates in JSON)")


def test_template_query_fields():
    """Test that templates have required fields"""
    print("Testing template field validation...", end=" ")
    
    for template in TEMPLATE_QUERIES:
        # Check required fields
        assert isinstance(template.name, str), f"Template name not string: {template.name}"
        assert isinstance(template.query, str), f"Template query not string: {template.query}"
        assert len(template.name) > 0, "Template name is empty"
        assert len(template.query) > 0, "Template query is empty"
        
        # Optional fields can be empty
        assert isinstance(template.query_type, str), "Query type not string"
        assert isinstance(template.description, str), "Description not string"
    
    print("✓")


def test_error_handling():
    """Test error handling in payload preparation"""
    print("Testing error handling...", end=" ")
    
    client = TemplateQueryInference()
    
    # Test with None message_history (should default to empty list)
    template = TEMPLATE_QUERIES[0]
    payload = client.prepare_query_payload(template, None)
    assert isinstance(payload["message_history"], list)
    
    print("✓")


def test_template_uniqueness():
    """Test that templates have unique names"""
    print("Testing template uniqueness...", end=" ")
    
    names = [t.name for t in TEMPLATE_QUERIES]
    assert len(names) == len(set(names)), "Duplicate template names found"
    
    print("✓")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("Template Query Integration Tests")
    print("="*80 + "\n")
    
    tests = [
        test_template_query_class,
        test_predefined_templates,
        test_inference_client_initialization,
        test_payload_preparation,
        test_json_templates,
        test_template_query_fields,
        test_error_handling,
        test_template_uniqueness,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*80 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
