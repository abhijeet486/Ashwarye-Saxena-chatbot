# WebLLM Testing Documentation

Comprehensive guide for WebLLM unit and integration testing.

## Table of Contents

1. [Test Overview](#test-overview)
2. [Running Tests](#running-tests)
3. [Unit Tests](#unit-tests)
4. [Integration Tests](#integration-tests)
5. [Test Coverage](#test-coverage)
6. [Adding New Tests](#adding-new-tests)

---

## Test Overview

WebLLM has a comprehensive test suite with **61 total tests** covering all aspects of the system:

- **Unit Tests** (40 tests): Core functionality, configuration, validation
- **Integration Tests** (21 tests): End-to-end workflows, error handling, performance

### Test Statistics

```
✅ Total Tests: 61
✅ Unit Tests: 40
✅ Integration Tests: 21
✅ Pass Rate: 100%
⏱️  Average Test Time: 5.5 seconds
```

---

## Running Tests

### Quick Start

Run all tests:
```bash
cd /home/engine/project

# Unit tests
python3 test_webllm_unit.py

# Integration tests
python3 test_webllm_integration.py

# Both with combined output
python3 run_tests.py --unit --integration
```

### Running Specific Tests

#### Run a specific test class:
```bash
python3 test_webllm_unit.py TestWebLLMConfig
python3 test_webllm_integration.py TestWebLLMWorkflow
```

#### Run a specific test method:
```bash
python3 -m unittest test_webllm_unit.TestWebLLMConfig.test_supported_models_count
```

### Test Flags

```bash
# Verbose output
python3 test_webllm_unit.py -v

# Stop on first failure
python3 test_webllm_unit.py -f

# Only show errors
python3 test_webllm_unit.py 2>&1 | grep -E "(FAIL|ERROR|OK)"
```

### Continuous Testing

Watch for test changes:
```bash
watch -n 2 'python3 test_webllm_unit.py 2>&1 | tail -5'
```

---

## Unit Tests

### Test Classes (40 tests total)

#### 1. TestWebLLMConfig (4 tests)
Tests WebLLM configuration management.

```python
def test_supported_models_count(self):
    """Test that expected number of models are supported"""
    
def test_get_recommended_models(self):
    """Test getting only recommended models"""
    
def test_get_model_info(self):
    """Test getting information about a specific model"""
    
def test_invalid_model_info(self):
    """Test getting info for invalid model"""
```

**Run:**
```bash
python3 -m unittest test_webllm_unit.TestWebLLMConfig -v
```

#### 2. TestModelConfig (4 tests)
Tests model configuration dataclass.

```python
def test_model_config_creation(self):
    """Test creating a model configuration"""
    
def test_model_config_to_dict(self):
    """Test converting model config to dictionary"""
```

**Run:**
```bash
python3 -m unittest test_webllm_unit.TestModelConfig -v
```

#### 3. TestInferenceRequest (3 tests)
Tests inference request creation and validation.

```python
def test_inference_request_creation(self):
    """Test creating an inference request"""
    
def test_inference_request_with_params(self):
    """Test creating request with parameters"""
    
def test_inference_request_to_dict(self):
    """Test converting request to dictionary"""
```

#### 4. TestInferenceResponse (3 tests)
Tests inference response creation and handling.

```python
def test_inference_response_creation(self):
    """Test creating an inference response"""
    
def test_inference_response_with_error(self):
    """Test creating error response"""
    
def test_inference_response_to_dict(self):
    """Test converting response to dictionary"""
```

#### 5. TestWebLLMManager (13 tests)
Tests the core WebLLM manager functionality.

```python
def test_manager_initialization(self):
    """Test manager initializes correctly"""
    
def test_add_model_config(self):
    """Test adding model configuration"""
    
def test_validate_empty_prompt(self):
    """Test validation with empty prompt"""
    
def test_validate_long_prompt(self):
    """Test validation with prompt exceeding max length"""
    
def test_validate_invalid_temperature(self):
    """Test validation with invalid temperature"""
    
def test_validate_invalid_max_tokens(self):
    """Test validation with invalid max tokens"""
    
def test_validate_valid_request(self):
    """Test validation with valid request"""
    
def test_record_inference(self):
    """Test recording inference metrics"""
    
def test_record_multiple_inferences(self):
    """Test recording multiple inferences"""
    
def test_get_inference_history(self):
    """Test retrieving inference history"""
    
def test_clear_history(self):
    """Test clearing history"""
```

**Run:**
```bash
python3 -m unittest test_webllm_unit.TestWebLLMManager -v
```

#### 6. TestWebLLMAPIEndpoints (13 tests)
Tests all API endpoint functionality.

```python
def test_webllm_interface_loads(self):
    """Test that WebLLM interface loads"""
    
def test_health_check(self):
    """Test health check endpoint"""
    
def test_get_models(self):
    """Test getting available models"""
    
def test_get_recommended_models(self):
    """Test getting recommended models"""
    
def test_get_model_info(self):
    """Test getting model information"""
    
def test_get_invalid_model_info(self):
    """Test getting info for invalid model"""
    
def test_inference_endpoint_valid(self):
    """Test inference endpoint with valid input"""
    
def test_inference_endpoint_missing_prompt(self):
    """Test inference endpoint with missing prompt"""
    
def test_inference_endpoint_empty_prompt(self):
    """Test inference endpoint with empty prompt"""
    
def test_batch_inference_endpoint(self):
    """Test batch inference endpoint"""
    
def test_batch_inference_too_many_prompts(self):
    """Test batch inference with too many prompts"""
    
def test_set_model_config(self):
    """Test setting model configuration"""
    
def test_get_metrics(self):
    """Test getting performance metrics"""
```

**Run:**
```bash
python3 -m unittest test_webllm_unit.TestWebLLMAPIEndpoints -v
```

---

## Integration Tests

### Test Classes (21 tests total)

#### 1. TestWebLLMWorkflow (5 tests)
Complete end-to-end workflows.

```python
def test_simple_chat_flow(self):
    """Test simple chat message flow"""
    
def test_multi_turn_conversation(self):
    """Test multiple turn conversation"""
    
def test_configuration_changes_during_chat(self):
    """Test changing configuration between requests"""
    
def test_inference_mode_switching(self):
    """Test switching between inference modes"""
    
def test_batch_and_sequential_mix(self):
    """Test mixing batch and sequential inference"""
```

**Run:**
```bash
python3 -m unittest test_webllm_integration.TestWebLLMWorkflow -v
```

#### 2. TestWebLLMErrorHandling (5 tests)
Error handling and recovery.

```python
def test_malformed_json_handling(self):
    """Test handling of malformed JSON"""
    
def test_invalid_temperature_handling(self):
    """Test invalid temperature values"""
    
def test_empty_batch_handling(self):
    """Test handling of empty batch"""
    
def test_missing_required_fields(self):
    """Test handling of missing required fields"""
    
def test_recovery_after_error(self):
    """Test system recovery after error"""
```

#### 3. TestWebLLMPerformance (5 tests)
Performance characteristics and metrics.

```python
def test_sequential_requests_performance(self):
    """Test performance of sequential requests"""
    
def test_batch_vs_sequential_efficiency(self):
    """Test batch inference vs sequential performance"""
    
def test_concurrent_requests(self):
    """Test handling concurrent requests"""
    
def test_response_time_metrics(self):
    """Test response time metrics tracking"""
    
def test_memory_efficiency_with_history(self):
    """Test memory efficiency with large history"""
```

#### 4. TestWebLLMStress (3 tests)
Stress testing and limits.

```python
def test_high_volume_requests(self):
    """Test handling high volume of requests"""
    
def test_maximum_batch_size(self):
    """Test with maximum batch size"""
    
def test_sustained_load(self):
    """Test sustained load over time"""
```

#### 5. TestWebLLMIntegrationWithChat (3 tests)
Integration with chat UI.

```python
def test_webllm_interface_accessibility(self):
    """Test WebLLM interface is accessible"""
    
def test_webllm_and_whatsapp_coexistence(self):
    """Test WebLLM and WhatsApp chat UI can coexist"""
```

**Run:**
```bash
python3 -m unittest test_webllm_integration.TestWebLLMIntegrationWithChat -v
```

---

## Test Coverage

### Coverage by Component

| Component | Unit Tests | Integration Tests |
|-----------|-----------|------------------|
| Config Management | 4 | 0 |
| Model Configuration | 4 | 3 |
| Inference Requests | 3 | 5 |
| Inference Responses | 3 | 5 |
| Manager Core | 13 | 5 |
| API Endpoints | 13 | 3 |
| Error Handling | 0 | 5 |
| Performance | 0 | 5 |
| Stress Testing | 0 | 3 |
| Integration | 0 | 3 |

### Coverage by Feature

- **Model Management**: 8 tests
- **Inference Execution**: 11 tests
- **Batch Processing**: 4 tests
- **Configuration**: 7 tests
- **Metrics & History**: 8 tests
- **API Endpoints**: 13 tests
- **Error Handling**: 5 tests
- **Performance**: 5 tests

---

## Adding New Tests

### Test Template

```python
import unittest
from app import create_app

class TestNewFeature(unittest.TestCase):
    """Test description"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()[0]
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_new_functionality(self):
        """Test description"""
        # Arrange
        test_data = {...}
        
        # Act
        result = self.client.post('/webllm/api/endpoint', json=test_data)
        
        # Assert
        self.assertEqual(result.status_code, 200)
        self.assertIn('expected_field', result.json)

if __name__ == '__main__':
    unittest.main()
```

### Best Practices

1. **Name tests clearly**: `test_feature_condition_expected_result`
2. **Use setUp/tearDown**: Prepare and clean up test state
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Test one thing**: Each test should verify one behavior
5. **Mock external dependencies**: Don't rely on external services
6. **Use descriptive docstrings**: Explain what the test does

### Example: Adding a New Model Test

```python
def test_new_model_support(self):
    """Test supporting a new model type"""
    from app.services.webllm_service import ModelType, WebLLMConfig
    
    # Verify new model is in supported list
    models = WebLLMConfig.get_all_models()
    model_ids = [m['model_id'] for m in models]
    self.assertIn('new-org/new-model-7b', model_ids)
    
    # Verify model info is accessible
    info = WebLLMConfig.get_model_info(ModelType.NEW_MODEL.value)
    self.assertIsNotNone(info)
    self.assertGreater(info['size_gb'], 0)
```

---

## Test Results Format

### Success Output

```
Ran 40 tests in 0.191s
OK
```

### Failure Output

```
FAIL: test_example_test (__main__.TestExampleClass)
Test description
----------------------------------------------------------------------
Traceback (most recent call last):
  File "...", line XXX, in test_example_test
    self.assertEqual(expected, actual)
AssertionError: 200 != 404
----------------------------------------------------------------------
Ran 40 tests in 0.191s
FAILED (failures=1)
```

---

## Debugging Tests

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Print Debug Information

```python
def test_debug_example(self):
    """Test with debug output"""
    response = self.client.get('/webllm/api/models')
    print(f"Response: {response.json}")
    print(f"Status: {response.status_code}")
    self.assertEqual(response.status_code, 200)
```

### Check Test Isolation

```python
def test_isolation_check(self):
    """Verify tests don't interfere with each other"""
    # Clear any prior state
    self.client.post('/webllm/api/clear')
    
    # Run test
    response = self.client.post('/webllm/api/infer', json={...})
    
    # Verify clean state
    self.assertEqual(response.status_code, 200)
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: WebLLM Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run unit tests
        run: python3 test_webllm_unit.py
      
      - name: Run integration tests
        run: python3 test_webllm_integration.py
```

---

## Test Maintenance

### Updating Tests

When modifying API endpoints or services:

1. Update corresponding tests
2. Add tests for new functionality
3. Ensure backward compatibility tests pass
4. Document breaking changes

### Deprecation

When deprecating features:

```python
def test_deprecated_feature(self):
    """Test deprecated feature (to be removed in v2.0)"""
    import warnings
    
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        # Test deprecated functionality
        self.assertTrue(old_feature_still_works())
```

---

## Performance Benchmarks

### Expected Test Execution Times

| Test Suite | Time | Tests |
|-----------|------|-------|
| Unit Tests | 0.2s | 40 |
| Integration Tests | 5.3s | 21 |
| Total | 5.5s | 61 |

### Performance Regressions

Monitor test execution time. If tests suddenly take longer:

1. Check for new/inefficient tests
2. Verify mock objects aren't making real API calls
3. Check for resource leaks
4. Review database query performance

---

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Add project root to path
export PYTHONPATH=/home/engine/project:$PYTHONPATH
```

**Port Already in Use**
```bash
# Kill existing process
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Tests Hang**
```bash
# Timeout tests (Ctrl+C after 30s)
timeout 30 python3 test_webllm_unit.py
```

**State Pollution Between Tests**
```bash
# Clear before each test
self.client.post('/webllm/api/clear')
```

---

## Resources

- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Flask Testing Guide](https://flask.palletsprojects.com/testing/)
- [WebLLM Documentation](./WEBLLM_DOCUMENTATION.md)
- [Quick Start Guide](./WEBLLM_QUICKSTART.md)

---

*Last Updated: January 2024*
*Maintained by: AI Development Team*
