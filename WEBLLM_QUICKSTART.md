# WebLLM Quick Start Guide

Get up and running with WebLLM in 5 minutes!

## Installation (2 min)

```bash
# Navigate to project
cd /home/engine/project

# Start the server
python3 -c "from app import create_app; app = create_app()[0]; app.run(debug=True, port=8000)"
```

## Access (30 sec)

Open browser:
```
http://localhost:8000/webllm/
```

## First Chat (2 min)

1. **Select Model**: Choose from dropdown (default is Mistral)
2. **Type Message**: "What is artificial intelligence?"
3. **Send**: Click Send or press Enter
4. **View Response**: See AI response with timing info

## Key Features

| Feature | How to Use |
|---------|-----------|
| **Models** | Click dropdown in sidebar |
| **Temperature** | Adjust slider (0.3-1.5) |
| **Max Tokens** | Set response length |
| **Mode** | Choose Client/Server/Hybrid |
| **Metrics** | Click "Metrics" in header |
| **History** | Auto-saved in browser |
| **Clear** | Click "Clear Chat" button |

## API Quick Reference

### Python
```python
import requests

# Single inference
r = requests.post('http://localhost:8000/webllm/api/infer', json={
    'prompt': 'What is AI?',
    'model_id': 'mistralai/Mistral-7B-Instruct-v0.2'
})
print(r.json()['text'])
```

### JavaScript
```javascript
const response = await fetch('/webllm/api/infer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        prompt: 'What is AI?',
        model_id: 'mistralai/Mistral-7B-Instruct-v0.2'
    })
});
const result = await response.json();
console.log(result.text);
```

### cURL
```bash
curl -X POST http://localhost:8000/webllm/api/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is AI?","model_id":"mistralai/Mistral-7B-Instruct-v0.2"}'
```

## Common Tasks

### Get Available Models
```bash
curl http://localhost:8000/webllm/api/models
```

### Run Batch Inference
```bash
curl -X POST http://localhost:8000/webllm/api/infer/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["What is AI?", "What is ML?"],
    "model_id": "mistralai/Mistral-7B-Instruct-v0.2"
  }'
```

### Get Performance Metrics
```bash
curl http://localhost:8000/webllm/api/metrics
```

### Clear Chat History
```bash
curl -X POST http://localhost:8000/webllm/api/clear
```

## Running Tests

```bash
# Unit tests
python3 test_webllm_unit.py

# Integration tests
python3 test_webllm_integration.py

# Full test suite
python3 run_tests.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 8000 in use** | `lsof -i :8000` then kill process |
| **Module not found** | Install: `pip install flask requests` |
| **Slow response** | Try smaller model or reduce max_tokens |
| **WebGPU not available** | Use server-side mode, upgrade browser |

## Next Steps

- Read [Full Documentation](./WEBLLM_DOCUMENTATION.md)
- Check [Test Examples](./test_webllm_unit.py)
- View [Integration Examples](./test_webllm_integration.py)
- Deploy to [Production](./WEBLLM_DOCUMENTATION.md#deployment)

## API Endpoints

```
GET  /webllm/                          # Chat interface
GET  /webllm/api/health                # Health check
GET  /webllm/api/models                # List models
GET  /webllm/api/models/{id}/info      # Model info
POST /webllm/api/infer                 # Single inference
POST /webllm/api/infer/batch           # Batch inference
POST /webllm/api/config/models         # Configure model
GET  /webllm/api/metrics               # Get metrics
GET  /webllm/api/history               # Get history
GET  /webllm/api/status                # Get status
POST /webllm/api/clear                 # Clear data
```

## Configuration Options

```json
{
  "temperature": 0.7,      // 0=deterministic, 2=creative
  "max_tokens": 512,       // Max response length
  "top_p": 0.9,            // Nucleus sampling
  "top_k": 50,             // Top-k sampling
  "mode": "client_side"    // client_side, server_side, hybrid
}
```

## Model Guide

| Model | Size | Speed | Quality | Recommended |
|-------|------|-------|---------|-------------|
| Phi-2 | 2.7B | ⚡⚡⚡ | ⭐⭐⭐ | ✅ |
| StableLM | 3B | ⚡⚡⚡ | ⭐⭐⭐ | ✅ |
| Mistral | 7B | ⚡⚡ | ⭐⭐⭐⭐ | ✅ |
| Llama-2 | 7B | ⚡⚡ | ⭐⭐⭐⭐ | ✅ |
| Llama-3 | 8B | ⚡⚡ | ⭐⭐⭐⭐ | ✅ |

## Performance Tips

1. **Smaller models** = Faster responses
2. **Lower temperature** = More consistent
3. **Batch processing** = More efficient
4. **Close browser tabs** = More VRAM available
5. **GPU browser** = 10x faster (if available)

## Need Help?

1. Check browser console: `F12` → `Console`
2. Check server logs: Look for errors
3. Test health endpoint: `curl http://localhost:8000/webllm/api/health`
4. Review documentation for your issue

---

**Ready to use WebLLM! 🚀**

Visit: http://localhost:8000/webllm/
