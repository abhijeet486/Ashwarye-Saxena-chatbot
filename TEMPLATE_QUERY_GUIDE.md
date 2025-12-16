# Template Query Inference Guide

This guide explains how to use the template query inference feature for the LLM endpoint.

## Overview

The template query inference system provides a standardized way to test and interact with the LLM (Language Model) inference endpoint. It includes predefined template queries that can be used immediately, as well as the ability to run custom queries.

## Architecture

### Components

1. **template_query_inference.py**: Core module providing the `TemplateQueryInference` class
   - `TemplateQuery`: Data class for query templates
   - `TemplateQueryInference`: Client for interacting with the LLM endpoint
   - Pre-defined template queries for common use cases

2. **test_template_query.py**: Test script for running template queries
   - Single template query testing
   - All templates testing
   - Custom query testing

3. **LLM Endpoint**: FastAPI service (openai_functionality.py) running on port 5000
   - POST `/query/` endpoint for query processing
   - GET `/` health check endpoint

## Setup and Execution

### Prerequisites

1. Ensure the virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (.env file):
   ```
   ANTHROPIC_API_KEY=<your_key>
   OPENAI_API_KEY=<your_key>
   ```

### Starting the LLM Service

Start the FastAPI service in one terminal:

```bash
python openai_functionality.py
```

The service should be running on `http://localhost:5000`

### Running Template Query Inference

#### Quick Start - Single Template Query

Run a single template query test:

```bash
python test_template_query.py
```

This will execute the service inquiry template query by default.

#### All Templates

Test all predefined template queries:

```bash
python test_template_query.py all
```

#### Custom Query

Run a custom query:

```bash
python test_template_query.py custom "Your custom question here"
```

#### Advanced Usage - Python Script

For programmatic usage:

```python
from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES

# Initialize client
client = TemplateQueryInference()

# Run inference with a template
result = client.run_inference(TEMPLATE_QUERIES[0])

# Or run with a custom query
result = client.run_custom_query(
    query="What are the available services?",
    query_type="informational"
)

# Print response
print(result["response"])
```

## Predefined Template Queries

The following template queries are available:

1. **service_inquiry**: General inquiry about available services
   - Query: "What services are available at MSPSDC?"
   - Type: informational

2. **complaint_process**: Query about the complaint filing process
   - Query: "How do I file a complaint with MSPSDC?"
   - Type: procedural

3. **contact_info**: Query for contact details
   - Query: "What is the contact information for MSPSDC?"
   - Type: factual

4. **eligibility**: Query about service eligibility
   - Query: "What are the eligibility criteria for MSPSDC services?"
   - Type: procedural

5. **documentation**: Query about required documentation
   - Query: "What documents are required to apply for services?"
   - Type: informational

## Query Structure

The `TemplateQuery` data class has the following fields:

```python
@dataclass
class TemplateQuery:
    name: str                    # Template identifier
    query: str                   # The actual query text
    query_type: str = ""         # Type: informational, procedural, factual, etc.
    description: str = ""        # Human-readable description
```

## API Request/Response

### Request Format

POST to `/query/` endpoint:

```json
{
    "query": "What services are available at MSPSDC?",
    "message_history": [],
    "query_type": "informational"
}
```

### Response Format

```json
{
    "response": "The response text from the LLM...",
    "responses": [
        {
            "role": "system",
            "content": "..."
        }
    ],
    "response_time": "12:34:56.789",
    "inference_time": 45.23,
    "template_name": "service_inquiry"
}
```

## Error Handling

The inference client handles several error scenarios:

- **Connection Error**: Unable to reach the LLM endpoint
  - Suggestion: Verify the FastAPI service is running

- **Timeout**: Request exceeds the configured timeout (default: 120s)
  - Suggestion: Increase timeout or check LLM service performance

- **HTTP Errors**: Non-200 status codes
  - Suggestion: Check endpoint logs for details

## Performance Metrics

Each inference response includes:

- `inference_time`: Total time taken for the request (includes network latency)
- `response_time`: Timestamp from the LLM service
- `template_name`: Name of the template used

## Adding New Template Queries

To add new template queries, update the `TEMPLATE_QUERIES` list in `template_query_inference.py`:

```python
TEMPLATE_QUERIES = [
    # ... existing templates ...
    TemplateQuery(
        name="new_template",
        query="Your new query here?",
        query_type="informational",
        description="Description of the new template"
    ),
]
```

## Troubleshooting

### Issue: Connection refused to localhost:5000

**Solution**: 
1. Ensure the FastAPI service is running
2. Check the service logs for errors
3. Verify port 5000 is not blocked by firewall

### Issue: Timeout errors

**Solution**:
1. Check the LLM service performance (Ollama/GPU utilization)
2. Increase the timeout in the client:
   ```python
   client = TemplateQueryInference(timeout=300)  # 5 minutes
   ```

### Issue: Empty or irrelevant responses

**Solution**:
1. Check the RAG retrieval (context quality)
2. Verify the knowledge base is properly loaded
3. Check the LLM model (ensure llama3 is available)

## Advanced Features

### Message History

Pass conversation history to maintain context:

```python
message_history = [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous response"}
]

result = client.run_inference(
    template,
    message_history=message_history
)
```

### Batch Processing

Run multiple queries and collect results:

```python
results = client.run_all_templates(verbose=False)

for result in results:
    if "error" not in result:
        print(f"{result['template_name']}: {result['response']}")
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI
from template_query_inference import TemplateQueryInference

app = FastAPI()
inference_client = TemplateQueryInference()

@app.post("/test-inference/")
async def test_inference(query: str):
    result = inference_client.run_custom_query(query)
    return result
```

### Flask Integration

```python
from flask import Flask, jsonify, request
from template_query_inference import TemplateQueryInference

app = Flask(__name__)
inference_client = TemplateQueryInference()

@app.route("/test-inference/", methods=["POST"])
def test_inference():
    query = request.json.get("query")
    result = inference_client.run_custom_query(query)
    return jsonify(result)
```

## Performance Optimization

1. **Batch Requests**: Send multiple queries together to reduce overhead
2. **Connection Pooling**: Reuse HTTP connections
3. **Caching**: Cache responses for identical queries
4. **Async Operations**: Use async clients for non-blocking requests

## Monitoring and Logging

To enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = TemplateQueryInference()
result = client.run_inference(template, verbose=True)
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Langroid Documentation](https://langroid.github.io/)
- [Ollama Models](https://ollama.ai/)
