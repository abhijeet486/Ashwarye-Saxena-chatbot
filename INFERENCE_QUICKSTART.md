# Quick Start: Testing LLM Template Query Inference

## Quick Commands

### 1. Run All Tests (No Server Required)
```bash
# Integration tests
python3 test_template_query_integration.py

# Infrastructure tests in demo mode
python3 test_llm_inference.py 3
```

### 2. Check Available Templates
```bash
python3 run_template_query_inference.py --list
```

### 3. Check Server Status
```bash
python3 run_template_query_inference.py --health
```

## Testing With Live Server

### Start the Server
```bash
python3 openai_functionality.py
```

### Run Single Query
```bash
python3 run_template_query_inference.py --template service_inquiry
```

### Run All Templates
```bash
python3 run_template_query_inference.py --all
```

### Interactive Testing
```bash
python3 test_llm_inference.py
# Select option 2 for interactive mode
```

### Custom Query
```bash
python3 run_template_query_inference.py --query "What are the office hours?"
```

## Python API Quick Example

```python
from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES

# Initialize
client = TemplateQueryInference()

# Run inference
result = client.run_inference(TEMPLATE_QUERIES[0])
print(result['response'])
```

## Expected Performance

- **First request**: 30-60 seconds (model loading)
- **Subsequent requests**: 20-45 seconds
- **Response format**: JSON with response, context, and timing

## Output Files

- `response_data.csv` - Log of all queries and responses
- `llm_server.log` - Server logs (if running in background)

## Troubleshooting

### Server Won't Start
Check dependencies:
```bash
pip install torch langroid sentence-transformers
```

### Connection Refused
Ensure server is running:
```bash
python3 run_template_query_inference.py --health
```

### Slow Responses
First request loads the model (normal). Subsequent requests should be faster.

## All Test Files

1. `test_template_query_integration.py` - Unit tests (no server needed)
2. `test_llm_inference.py` - End-to-end tests (works with or without server)
3. `run_template_query_inference.py` - CLI tool for inference
4. `example_template_query_usage.py` - Python API examples

## Quick Verification

Run this one command to verify everything works:
```bash
python3 test_template_query_integration.py && \
python3 test_llm_inference.py 3 && \
echo "✓ All tests passed!"
```
