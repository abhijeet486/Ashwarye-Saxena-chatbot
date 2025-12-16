# Quick Start Guide - Template Query Inference

This guide provides step-by-step instructions to run template query inference on the LLM endpoint.

## 5-Minute Quick Start

### 1. Activate Virtual Environment (if not already active)

```bash
cd /home/engine/project
source venv/bin/activate
```

### 2. Check Endpoint Health

Verify the LLM endpoint is running:

```bash
python run_template_query_inference.py --health
```

Expected output:
```
Checking LLM endpoint health...
✓ LLM endpoint is reachable
```

If the endpoint is not reachable, start the FastAPI service in another terminal:

```bash
python openai_functionality.py
```

Wait for it to output: `INFO:     Application startup complete`

### 3. Run Template Query Inference

#### Option A: Run Single Template (Default)

```bash
python run_template_query_inference.py
```

This will run the "Service Inquiry" template query.

#### Option B: List Available Templates

```bash
python run_template_query_inference.py --list
```

#### Option C: Run Specific Template

```bash
python run_template_query_inference.py --template complaint_process
```

#### Option D: Run All Templates

```bash
python run_template_query_inference.py --all
```

#### Option E: Run Custom Query

```bash
python run_template_query_inference.py --query "What are the online services available?"
```

### 4. View JSON Output

For JSON formatted output:

```bash
python run_template_query_inference.py --json
```

## Expected Output Example

When running a template query, you'll see output like:

```
======================================================================
Template: service_inquiry
Description: General inquiry about available services
Query: What services are available at MSPSDC?
Query Type: informational
======================================================================
Sending request to LLM endpoint...
✓ Response received in 45.23s

Response:
----------------------------------------------------------------------
MSPSDC provides a wide range of services including:
1. Online service applications
2. Status tracking and updates
3. Complaint handling and resolution
4. Document verification
5. Service delivery monitoring

For more information, visit: https://mspsdc.meghalaya.gov.in/
----------------------------------------------------------------------
Response time: 12:34:56.789

✓ Template query inference successful!
```

## Common Commands Reference

| Command | Purpose |
|---------|---------|
| `python run_template_query_inference.py` | Run first template |
| `python run_template_query_inference.py --all` | Run all templates |
| `python run_template_query_inference.py --template <name>` | Run specific template |
| `python run_template_query_inference.py --query "<text>"` | Run custom query |
| `python run_template_query_inference.py --list` | List templates |
| `python run_template_query_inference.py --health` | Check endpoint |
| `python run_template_query_inference.py --json` | JSON output |

## Troubleshooting

### Issue: "Cannot connect to LLM endpoint"

**Solution**: Start the FastAPI service:
```bash
python openai_functionality.py
```

### Issue: "Timeout" error after 120 seconds

**Possible causes**:
- GPU is busy
- Ollama model is not fully loaded
- Network latency

**Solution**: Wait a moment and retry, or check GPU status.

### Issue: Empty or irrelevant responses

**Possible causes**:
- Knowledge base not properly indexed
- Retrieval system not finding relevant documents

**Solution**:
1. Check that the RAG pipeline is properly initialized
2. Verify knowledge base is loaded (check logs in `openai_functionality.py`)

## Testing via Python

For programmatic usage:

```python
from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES

# Create client
client = TemplateQueryInference()

# Test a template
result = client.run_inference(TEMPLATE_QUERIES[0])
print(result["response"])

# Test custom query
result = client.run_custom_query("Your question here?")
print(result["response"])
```

## File Structure

```
/home/engine/project/
├── openai_functionality.py           # FastAPI LLM service
├── template_query_inference.py       # Core inference module
├── test_template_query.py            # Simple test script
├── run_template_query_inference.py   # CLI runner (recommended)
├── template_queries.json             # Template definitions
├── TEMPLATE_QUERY_GUIDE.md           # Detailed guide
└── QUICKSTART.md                     # This file
```

## Performance Metrics

After running a query, you'll get:

- **inference_time**: Total time from request to response (includes network)
- **response_time**: Timestamp from LLM service
- **template_name**: Which template was used

Example:
```
Response time: 12:34:56.789
Total inference time: 45.23s
Template: service_inquiry
```

## Next Steps

1. **Explore Templates**: Run `--list` to see all available templates
2. **Test Custom Queries**: Try your own questions with `--query`
3. **Batch Testing**: Run `--all` to test all templates
4. **Integration**: Use the module in your own code (see TEMPLATE_QUERY_GUIDE.md)

## Support

For issues or questions:
1. Check TEMPLATE_QUERY_GUIDE.md for detailed documentation
2. Review FastAPI service logs for errors
3. Check Ollama service status if using local model
4. Verify RAG pipeline initialization in openai_functionality.py

## Environment Setup

To ensure all dependencies are installed:

```bash
# Install requirements
pip install -r requirements.txt

# Set environment variables (if needed)
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

## Performance Tips

1. **First request is slower**: The LLM model needs to be loaded
2. **Batch requests**: Group multiple queries for efficiency
3. **Monitor GPU**: Check GPU usage during queries
4. **Keep-alive**: The service maintains state between requests

Enjoy using template queries for LLM inference! 🚀
