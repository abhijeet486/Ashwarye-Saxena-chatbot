# WhatsApp Chat UI - Local AI Mode Test Suite

## Overview

This comprehensive test suite provides complete coverage for the WhatsApp Chat UI with Local AI mode functionality, including unit tests, integration tests, performance tests, and stress tests.

## 🏗️ Test Architecture

### Test Structure
```
test_whatsapp_ui_local_ai_unit.py          # Unit tests
test_whatsapp_ui_local_ai_integration.py   # Integration tests  
test_config.py                             # Test configuration & fixtures
mock_services.py                          # Mock implementations
run_tests.py                              # Test runner
```

## 🧪 Unit Tests

### Test Coverage Areas

#### **1. Local LLM Detection (`TestLocalLLMDetection`)**
- ✅ Ollama availability with LLaMA3 model
- ✅ Ollama available but no LLaMA3 model
- ✅ Ollama connection errors
- ✅ Ollama timeout handling
- ✅ Availability caching mechanism

#### **2. Local LLM Response (`TestLocalLLMResponse`)**
- ✅ Successful LLaMA3 response generation
- ✅ LLaMA3 timeout handling
- ✅ LLaMA3 connection error handling
- ✅ LLaMA3 API error handling
- ✅ MSPSDC context in prompts

#### **3. Service Status (`TestServiceStatus`)**
- ✅ All services available (main + local)
- ✅ Only local LLM available
- ✅ No services available
- ✅ Service status reporting

#### **4. Enhanced Response (`TestEnhancedResponse`)**
- ✅ Main LLM success
- ✅ Fallback to local LLM
- ✅ Fallback to demo responses
- ✅ Demo mode responses
- ✅ Query categorization

#### **5. API Endpoints (`TestAPIEndpoints`)**
- ✅ Health check endpoint
- ✅ LLM status endpoint
- ✅ Ollama setup endpoint
- ✅ Chat send endpoint
- ✅ Chat history endpoint
- ✅ Chat clear endpoint
- ✅ Error handling

#### **6. Mode Switching (`TestModeSwitching`)**
- ✅ Switch to demo mode
- ✅ Switch to enhanced mode (no services)
- ✅ Enhanced mode switching logic

#### **7. Environment Configuration (`TestEnvironmentConfiguration`)**
- ✅ Default configuration
- ✅ Custom environment variables
- ✅ Configuration validation

## 🔗 Integration Tests

### Test Coverage Areas

#### **1. Chat Workflow Integration (`TestChatWorkflowIntegration`)**
- ✅ Basic chat workflow
- ✅ Conversation history persistence
- ✅ Chat clear functionality
- ✅ Error handling invalid messages

#### **2. Service Integration (`TestServiceIntegration`)**
- ✅ Service status monitoring
- ✅ Intelligent fallback integration
- ✅ UI interface accessibility

#### **3. Performance and Reliability (`TestPerformanceAndReliability`)**
- ✅ Concurrent requests handling
- ✅ Response time performance
- ✅ Memory usage with large history

#### **4. Real-World Scenarios (`TestRealWorldScenarios`)**
- ✅ MSPSDC service inquiry workflow
- ✅ Error recovery workflow
- ✅ Session isolation

#### **5. Environment Integration (`TestEnvironmentIntegration`)**
- ✅ Enhanced mode environment integration
- ✅ Ollama configuration integration
- ✅ Main LLM service configuration integration

#### **6. Fallback Mechanism Integration (`TestFallbackMechanismIntegration`)**
- ✅ Complete fallback chain
- ✅ Partial service recovery

## 🚀 Running Tests

### Basic Usage
```bash
# Run all tests
python3 run_tests.py

# Run only unit tests
python3 run_tests.py --unit

# Run only integration tests  
python3 run_tests.py --integration

# Run performance tests
python3 run_tests.py --performance

# Run stress tests
python3 run_tests.py --stress

# Run specific test
python3 run_tests.py --specific TestLocalLLMDetection

# Verbose output
python3 run_tests.py --verbose

# Generate coverage report
python3 run_tests.py --coverage
```

### Test Configuration

#### Environment Variables
```bash
# Test environment
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:
export USE_ENHANCED_MODE=false

# Mock service URLs
export LLM_SERVICE_URL=http://127.0.0.1:5000/query/
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3
```

#### Test Directories
```
test_temp/                 # Temporary test files
test_report.json          # Test execution report
```

## 🛠️ Test Fixtures and Configuration

### Mock Services

#### **MockOllamaServer**
- Simulates Ollama server responses
- Configurable model availability
- Request logging and monitoring
- Error simulation capabilities

#### **MockMainLLMService**
- Simulates main LLM service responses
- Configurable availability
- Processing time simulation
- Advanced response generation

### Test Scenarios

#### **Service Availability Scenarios**
1. **All services available** - Main LLM + Local LLM
2. **Only local LLM available** - Ollama only
3. **Only main LLM available** - External API only
4. **No services available** - Demo mode fallback
5. **Connection errors** - Service failure handling
6. **Timeout scenarios** - Performance testing

#### **Real-World Test Messages**
```python
TEST_MESSAGES = {
    'greeting': ["Hello", "Hi there", "Hey"],
    'services': ["What services do you offer?", "Tell me about MSPSDC services"],
    'documents': ["I need a birth certificate", "How do I apply for caste certificate?"],
    'schemes': ["What welfare schemes are available?", "Tell me about government schemes"],
    'complex_queries': [/* Detailed multi-sentence queries */]
}
```

## 📊 Performance Testing

### Performance Thresholds
```python
PERFORMANCE_THRESHOLDS = {
    'response_time_max': 5.0,     # seconds
    'concurrent_requests': 10,     # parallel requests
    'memory_messages': 100,        # conversation length
    'stress_test_messages': 50     # stress test volume
}
```

### Stress Testing Scenarios
1. **Concurrent Requests** - Multiple users simultaneously
2. **Large Message Volumes** - High conversation volumes
3. **Memory Usage** - Long conversation history
4. **Error Recovery** - System resilience testing

## 📈 Test Reporting

### Report Structure
```json
{
  "timestamp": "2025-12-18T12:00:00",
  "environment": {
    "FLASK_ENV": "testing",
    "USE_ENHANCED_MODE": "false"
  },
  "results": {
    "unit": {
      "tests_run": 45,
      "failures": 0,
      "errors": 0,
      "success_rate": 1.0,
      "time": 12.5
    },
    "integration": {
      "tests_run": 30,
      "failures": 1,
      "errors": 0,
      "success_rate": 0.967,
      "time": 25.3
    }
  }
}
```

### Metrics Tracked
- **Test Execution Time**
- **Success/Failure Rates**
- **Response Times**
- **Memory Usage**
- **Concurrent Request Handling**

## 🎯 Key Test Scenarios

### Scenario 1: Local AI Mode Activation
```bash
# Test when Ollama becomes available
1. Start with no services (demo mode)
2. Mock Ollama availability
3. Verify automatic mode switching to "Local AI"
4. Test LLaMA3 response generation
5. Verify conversation context preservation
```

### Scenario 2: Intelligent Fallback Chain
```bash
# Test complete fallback hierarchy
1. Start with enhanced mode enabled
2. Main LLM available → Use main LLM
3. Main LLM fails → Fallback to local LLM
4. Local LLM fails → Fallback to demo
5. Verify response quality at each level
```

### Scenario 3: Service Recovery
```bash
# Test service recovery scenarios
1. Start with all services down
2. Simulate service becomes available
3. Verify automatic service detection
4. Test seamless mode switching
5. Verify performance improvement
```

### Scenario 4: Error Handling
```bash
# Test comprehensive error handling
1. Network connectivity issues
2. API timeouts
3. Invalid responses
4. Malformed requests
5. Recovery mechanisms
```

## 🔧 Mock Implementation Details

### MockOllamaServer Features
```python
class MockOllamaServer:
    def simulate_availability_check(self):
        # Simulates /api/tags endpoint
        
    def simulate_chat_completion(self, model, messages):
        # Simulates /api/chat endpoint with context awareness
        
    def generate_contextual_response(self, user_message, system_context):
        # MSPSDC-specific response generation
```

### MockMainLLMService Features
```python
class MockMainLLMService:
    def simulate_query(self, query_data):
        # Simulates main LLM service with advanced responses
        
    def generate_advanced_response(self, query, query_type):
        # More sophisticated response generation
```

## 🏃‍♂️ Quick Test Examples

### Test Local LLM Detection
```python
# Unit test example
def test_ollama_available_with_llama3(self):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [{"name": "llama3:latest"}]
        }
        result = check_local_llm_availability()
        self.assertTrue(result)
```

### Test Fallback Mechanism
```python
# Integration test example
def test_complete_fallback_chain(self):
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # All services unavailable
        mock_get.side_effect = requests.exceptions.ConnectionError()
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        response = self.client.post('/api/chat/send',
            json={'message': 'Test message'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(data['bot_response'], DEMO_RESPONSES['default'])
```

### Test Service Integration
```python
# Real-world scenario test
def test_mspsdc_service_inquiry_workflow(self):
    workflow_messages = [
        "Hello, I need help with government services",
        "What documents do I need for a caste certificate?",
        "How long does the application process take?",
        "Can I apply online or do I need to visit in person?"
    ]
    
    for message in workflow_messages:
        response = self.client.post('/api/chat/send',
            json={'message': message})
        self.assertEqual(response.status_code, 200)
```

## 📝 Test Documentation

### Test Naming Convention
- **Unit Tests**: `Test{ComponentName}` (e.g., `TestLocalLLMDetection`)
- **Integration Tests**: `Test{WorkflowName}Integration` (e.g., `TestChatWorkflowIntegration`)
- **Individual Tests**: `test_{specific_functionality}` (e.g., `test_ollama_available_with_llama3`)

### Test Documentation Standards
- ✅ Descriptive test names
- ✅ Clear test purpose documentation
- ✅ Expected behavior specifications
- ✅ Mock setup explanations
- ✅ Assertion rationale

## 🎉 Test Success Criteria

### Pass/Fail Criteria
- **Unit Tests**: 100% pass rate required
- **Integration Tests**: 95%+ pass rate required
- **Performance Tests**: Response times < 5 seconds
- **Stress Tests**: 80%+ success rate under load

### Coverage Requirements
- **Line Coverage**: > 90%
- **Branch Coverage**: > 85%
- **Function Coverage**: 100%

## 📞 Test Support

### Debugging Tests
```bash
# Run specific failing test with verbose output
python3 -m unittest test_whatsapp_ui_local_ai_unit.TestLocalLLMDetection.test_ollama_available_with_llama3 -v

# Run tests with debugger
python3 -m pdb run_tests.py --unit --specific TestLocalLLMDetection

# Check test dependencies
python3 -c "import test_whatsapp_ui_local_ai_unit; print('✅ All imports successful')"
```

### Common Test Issues
1. **Import Errors**: Ensure running from project root
2. **Mock Configuration**: Check mock service setup
3. **Environment Variables**: Verify test environment
4. **Database Issues**: Use in-memory SQLite for tests

This comprehensive test suite ensures the WhatsApp Chat UI with Local AI mode is thoroughly tested, reliable, and production-ready.