# WebLLM Swagger/OpenAPI API Documentation

## Overview

Complete OpenAPI 3.0 specification and Swagger UI documentation for the WebLLM browser-based inference API.

## Access Swagger UI

**Swagger Documentation**: `http://localhost:8000/docs`
**ReDoc Documentation**: `http://localhost:8000/redoc`
**OpenAPI Specification**: `http://localhost:8000/swagger.json`

## API Base URL

```
http://localhost:8000/webllm/api
```

## Authentication

Currently **no authentication** is required. In production, implement appropriate authentication mechanisms.

---

## API Endpoints Reference

### 1. Health Check

**GET** `/health`

Check if WebLLM service is operational.

#### Request

```bash
curl -X GET http://localhost:8000/webllm/api/health
```

#### Response (200 OK)

```json
{
  "status": "healthy",
  "service": "webllm",
  "timestamp": "2024-01-15T10:30:00.000000",
  "models_loaded": 0
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Service health status (`healthy`, `degraded`, `unhealthy`) |
| `service` | string | Service identifier |
| `timestamp` | string | ISO format timestamp |
| `models_loaded` | integer | Number of loaded models |

---

### 2. List Models

**GET** `/models`

Get available models for WebLLM inference.

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `recommended` | boolean | No | If true, return only recommended models | `true` |

#### Request

```bash
# Get all models
curl -X GET http://localhost:8000/webllm/api/models

# Get recommended models only
curl -X GET http://localhost:8000/webllm/api/models?recommended=true
```

#### Response (200 OK)

```json
{
  "models": [
    {
      "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
      "size_gb": 14,
      "vram_required_gb": 6,
      "recommended": true
    },
    {
      "model_id": "microsoft/phi-2",
      "size_gb": 5.5,
      "vram_required_gb": 4,
      "recommended": true
    }
  ],
  "default_model": "mistralai/Mistral-7B-Instruct-v0.2",
  "count": 7
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `models` | array | List of available models |
| `models[].model_id` | string | Model identifier |
| `models[].size_gb` | number | Model size in GB |
| `models[].vram_required_gb` | integer | VRAM required in GB |
| `models[].recommended` | boolean | Whether recommended for browser |
| `default_model` | string | Default model identifier |
| `count` | integer | Number of models |

---

### 3. Get Model Info

**GET** `/models/info`

Get detailed information about a specific model.

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `model` | string | Yes | Model identifier | `mistralai/Mistral-7B-Instruct-v0.2` |

#### Request

```bash
curl -X GET "http://localhost:8000/webllm/api/models/info?model=mistralai/Mistral-7B-Instruct-v0.2"
```

#### Response (200 OK)

```json
{
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "size_gb": 14,
  "vram_required_gb": 6,
  "recommended": true
}
```

#### Error Response (404 Not Found)

```json
{
  "error": "Model not found",
  "code": "NOT_FOUND"
}
```

---

### 4. Single Inference

**POST** `/infer`

Run inference on a single prompt.

#### Request Body

```json
{
  "prompt": "What is machine learning?",
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "temperature": 0.7,
  "max_tokens": 512,
  "top_p": 0.9,
  "top_k": 50,
  "mode": "client_side"
}
```

#### Request Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| `prompt` | string | Yes | 1-2000 chars | Input prompt for the model |
| `model_id` | string | No | - | Model to use (default: mistral) |
| `temperature` | number | No | 0.0-2.0 | Sampling temperature |
| `max_tokens` | integer | No | 1-2048 | Max response length |
| `top_p` | number | No | 0.0-1.0 | Nucleus sampling |
| `top_k` | integer | No | ≥1 | Top-k sampling |
| `mode` | string | No | See below | Inference mode |

#### Mode Options

| Mode | Description |
|------|-------------|
| `client_side` | Browser-based inference (default) |
| `server_side` | Server-side inference |
| `hybrid` | Combined approach |

#### Request Example

```bash
curl -X POST http://localhost:8000/webllm/api/infer \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

#### Response (200 OK)

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Quantum computing is a type of computation that harnesses the power of quantum mechanics. Unlike classical computers...",
  "tokens_generated": 45,
  "inference_time_ms": 234.5,
  "mode": "client_side",
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique request identifier (UUID) |
| `text` | string | Generated response from the model |
| `tokens_generated` | integer | Approximate token count |
| `inference_time_ms` | number | Time taken in milliseconds |
| `mode` | string | Execution mode used |
| `model_id` | string | Model used for inference |
| `timestamp` | string | ISO format timestamp |

#### Error Response (400 Bad Request)

```json
{
  "error": "Prompt cannot be empty",
  "code": "VALIDATION_ERROR"
}
```

---

### 5. Batch Inference

**POST** `/infer/batch`

Run inference on multiple prompts in a single request.

#### Request Body

```json
{
  "prompts": [
    "What is AI?",
    "What is ML?",
    "What is DL?"
  ],
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "temperature": 0.7,
  "max_tokens": 512
}
```

#### Request Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| `prompts` | array | Yes | Max 100 items | Array of prompts |
| `model_id` | string | No | - | Model to use |
| `temperature` | number | No | 0.0-2.0 | Sampling temperature |
| `max_tokens` | integer | No | 1-2048 | Max tokens per response |

#### Request Example

```bash
curl -X POST http://localhost:8000/webllm/api/infer/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["What is AI?", "What is ML?"],
    "model_id": "mistralai/Mistral-7B-Instruct-v0.2"
  }'
```

#### Response (200 OK)

```json
{
  "results": [
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "AI is artificial intelligence...",
      "tokens_generated": 35,
      "inference_time_ms": 200.0
    },
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440001",
      "text": "Machine learning is...",
      "tokens_generated": 42,
      "inference_time_ms": 215.0
    }
  ],
  "total_prompts": 2,
  "successful": 2,
  "total_time_ms": 445.0,
  "total_tokens": 77
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Array of inference results |
| `total_prompts` | integer | Total prompts submitted |
| `successful` | integer | Number of successful inferences |
| `total_time_ms` | number | Total time for all inferences |
| `total_tokens` | integer | Total tokens generated |

---

### 6. Configure Model

**POST** `/config/models`

Configure inference parameters for a model.

#### Request Body

```json
{
  "model_type": "mistral",
  "temperature": 0.5,
  "max_tokens": 256,
  "top_p": 0.8,
  "top_k": 40
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_type` | string | Yes | Model type/identifier |
| `temperature` | number | No | Default temperature |
| `max_tokens` | integer | No | Default max tokens |
| `top_p` | number | No | Default top_p value |
| `top_k` | integer | No | Default top_k value |

#### Request Example

```bash
curl -X POST http://localhost:8000/webllm/api/config/models \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "mistral",
    "temperature": 0.5,
    "max_tokens": 256
  }'
```

#### Response (200 OK)

```json
{
  "status": "configured",
  "model_type": "mistral",
  "config": {
    "model_id": "mistral",
    "model_type": "mistralai/Mistral-7B-Instruct-v0.2",
    "temperature": 0.5,
    "max_tokens": 256,
    "top_p": 0.8,
    "top_k": 40,
    "repeat_penalty": 1.0
  }
}
```

---

### 7. Get Performance Metrics

**GET** `/metrics`

Get performance metrics and statistics.

#### Request

```bash
curl -X GET http://localhost:8000/webllm/api/metrics
```

#### Response (200 OK)

```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "metrics": {
    "total_inferences": 42,
    "total_tokens": 1840,
    "total_time_ms": 8450.5,
    "average_inference_time": 201.2,
    "client_side_count": 35,
    "server_side_count": 7
  },
  "inference_history_count": 42
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | Metrics timestamp |
| `metrics.total_inferences` | integer | Total inferences performed |
| `metrics.total_tokens` | integer | Total tokens generated |
| `metrics.total_time_ms` | number | Total inference time |
| `metrics.average_inference_time` | number | Average time per inference |
| `metrics.client_side_count` | integer | Client-side inferences |
| `metrics.server_side_count` | integer | Server-side inferences |
| `inference_history_count` | integer | Records in history |

---

### 8. Get Inference History

**GET** `/history`

Get recent inference history.

#### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-----------|-------------|
| `limit` | integer | 10 | 1-100 | Number of records to return |

#### Request

```bash
# Get last 10 inferences
curl -X GET http://localhost:8000/webllm/api/history

# Get last 25 inferences
curl -X GET http://localhost:8000/webllm/api/history?limit=25
```

#### Response (200 OK)

```json
{
  "count": 10,
  "history": [
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Response text...",
      "tokens_generated": 45,
      "inference_time_ms": 234.5,
      "mode": "client_side",
      "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
      "success": true,
      "timestamp": "2024-01-15T10:30:00.000000"
    }
  ]
}
```

---

### 9. Get System Status

**GET** `/status`

Get overall system status and diagnostics.

#### Request

```bash
curl -X GET http://localhost:8000/webllm/api/status
```

#### Response (200 OK)

```json
{
  "status": "operational",
  "timestamp": "2024-01-15T10:30:00.000000",
  "service": "webllm",
  "models_configured": 2,
  "models_loaded": 1,
  "total_inferences": 42,
  "average_inference_time_ms": 201.2
}
```

---

### 10. Clear Data

**POST** `/clear`

Clear all inference history and reset metrics.

#### Request

```bash
curl -X POST http://localhost:8000/webllm/api/clear
```

#### Response (200 OK)

```json
{
  "status": "cleared",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Successful request |
| `400` | Bad request (validation error) |
| `404` | Resource not found |
| `500` | Server error |
| `503` | Service unavailable |

### Error Response Format

```json
{
  "error": "Error message describing the problem",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### Common Errors

#### Missing Required Field

```json
{
  "error": "Missing required field: prompt",
  "code": "VALIDATION_ERROR"
}
```

#### Invalid Parameter

```json
{
  "error": "Temperature must be between 0 and 2",
  "code": "VALIDATION_ERROR"
}
```

#### Model Not Found

```json
{
  "error": "Model not found: invalid_model",
  "code": "NOT_FOUND"
}
```

#### Too Many Prompts

```json
{
  "error": "Maximum 100 prompts per batch",
  "code": "VALIDATION_ERROR"
}
```

---

## Request/Response Examples

### Example 1: Simple Query

```bash
curl -X POST http://localhost:8000/webllm/api/infer \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?"
  }'
```

### Example 2: Advanced Configuration

```bash
curl -X POST http://localhost:8000/webllm/api/infer \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a poem about nature",
    "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
    "temperature": 1.5,
    "max_tokens": 300,
    "top_p": 0.95,
    "mode": "client_side"
  }'
```

### Example 3: Batch Processing

```bash
curl -X POST http://localhost:8000/webllm/api/infer/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "What is Python?",
      "What is JavaScript?",
      "What is Go?",
      "What is Rust?"
    ],
    "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
    "temperature": 0.7,
    "max_tokens": 256
  }'
```

---

## Python Client Examples

### Using Requests Library

```python
import requests
import json

API_BASE = 'http://localhost:8000/webllm/api'

# Single inference
response = requests.post(f'{API_BASE}/infer', json={
    'prompt': 'What is machine learning?',
    'temperature': 0.7
})
result = response.json()
print(f"Response: {result['text']}")
print(f"Time: {result['inference_time_ms']}ms")

# Batch inference
batch_response = requests.post(f'{API_BASE}/infer/batch', json={
    'prompts': ['Q1', 'Q2', 'Q3'],
    'temperature': 0.7
})
batch_result = batch_response.json()
print(f"Processed: {batch_result['successful']}/{batch_result['total_prompts']}")

# Get metrics
metrics = requests.get(f'{API_BASE}/metrics').json()
print(f"Total inferences: {metrics['metrics']['total_inferences']}")
```

---

## JavaScript Client Examples

### Using Fetch API

```javascript
const API_BASE = 'http://localhost:8000/webllm/api';

// Single inference
async function runInference(prompt) {
  const response = await fetch(`${API_BASE}/infer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: prompt,
      temperature: 0.7
    })
  });
  
  const result = await response.json();
  console.log(`Response: ${result.text}`);
  console.log(`Time: ${result.inference_time_ms}ms`);
}

// Batch inference
async function runBatchInference(prompts) {
  const response = await fetch(`${API_BASE}/infer/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompts: prompts,
      temperature: 0.7
    })
  });
  
  const result = await response.json();
  console.log(`Success rate: ${result.successful}/${result.total_prompts}`);
}
```

---

## Performance Considerations

### Response Times

- **Fast**: 100-200ms (smaller models, GPU)
- **Normal**: 200-500ms (typical scenario)
- **Slow**: 500ms+ (CPU-only, large models)

### Batch Efficiency

- Batch 10 requests: ~1.5-2x faster than sequential
- Batch 100 requests: ~3-5x faster than sequential

### Memory Usage

- Browser: 100-300MB (UI + utilities)
- Model: 3-15GB (varies by model)

---

## Rate Limiting

Currently no rate limiting is implemented. For production:

1. Implement per-IP rate limiting
2. Add authentication tokens
3. Set request quotas
4. Monitor abuse patterns

---

## Monitoring & Logging

### Available Metrics

```bash
curl http://localhost:8000/webllm/api/metrics | jq
```

### Check Health

```bash
curl http://localhost:8000/webllm/api/health | jq
```

### View Status

```bash
curl http://localhost:8000/webllm/api/status | jq
```

---

## FAQ

### Q: What models are supported?
**A:** Llama-2, Llama-3, Mistral, Phi-2, StableLM, Vicuna, and RedPajama.

### Q: What's the max prompt length?
**A:** 2000 characters.

### Q: How many prompts in a batch?
**A:** Maximum 100 prompts per batch request.

### Q: Can I cancel a request?
**A:** Not currently. Implement client-side timeout if needed.

### Q: Is there a cost?
**A:** No, local inference is free. Only infrastructure costs apply.

---

## Support & Documentation

- **GitHub**: [Link to repo]
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Email**: support@example.com

---

*Last Updated: January 2024*
*API Version: 1.0*
*OpenAPI Specification: 3.0*
