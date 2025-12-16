# LLM Template Query Inference

Welcome to the Template Query Inference system! This module provides a comprehensive framework for querying the LLM endpoint with predefined templates or custom questions.

## 🚀 Quick Start (30 seconds)

### 1. Check Endpoint Health
```bash
python run_template_query_inference.py --health
```

### 2. Run First Template Query
```bash
python run_template_query_inference.py
```

### 3. Get Response
The LLM will process your query and return a structured response.

## 📋 What is Template Query Inference?

Template Query Inference is a system for:
- Running predefined query templates against an LLM endpoint
- Executing custom queries through the same interface
- Batching multiple queries for testing
- Integrating LLM capabilities into applications

## 📁 Key Files

| File | Purpose |
|------|---------|
| `template_query_inference.py` | Core inference module |
| `run_template_query_inference.py` | CLI tool (recommended entry point) |
| `template_queries.json` | Template definitions |
| `QUICKSTART.md` | Quick reference guide |
| `TEMPLATE_QUERY_GUIDE.md` | Detailed documentation |
| `example_template_query_usage.py` | Usage examples |

## 🎯 Available Templates

| Template | Query |
|----------|-------|
| service_inquiry | What services are available at MSPSDC? |
| complaint_process | How do I file a complaint with MSPSDC? |
| contact_info | What is the contact information for MSPSDC? |
| eligibility | What are the eligibility criteria for MSPSDC services? |
| documentation | What documents are required to apply for services? |

## 🛠️ Usage Examples

### Single Template
```bash
python run_template_query_inference.py --template service_inquiry
```

### All Templates
```bash
python run_template_query_inference.py --all
```

### Custom Query
```bash
python run_template_query_inference.py --query "What are the online services?"
```

### List Templates
```bash
python run_template_query_inference.py --list
```

### JSON Output
```bash
python run_template_query_inference.py --json
```

## 🐍 Python API

```python
from template_query_inference import TemplateQueryInference, TEMPLATE_QUERIES

# Create client
client = TemplateQueryInference()

# Run template
result = client.run_inference(TEMPLATE_QUERIES[0])
print(result["response"])

# Custom query
result = client.run_custom_query("Your question here?")
print(result["response"])
```

## 🔧 Requirements

- Python 3.8+
- FastAPI service running on port 5000
- LLM endpoint accessible at `http://localhost:5000/query/`
- Dependencies from `requirements.txt`

### Start the LLM Service

In a separate terminal:
```bash
python openai_functionality.py
```

## 📊 Response Structure

Every inference returns:
```json
{
    "response": "Answer from the LLM",
    "response_time": "12:34:56.789",
    "inference_time": 45.23,
    "template_name": "template_id"
}
```

## ✅ Testing

Run integration tests:
```bash
python test_template_query_integration.py
```

Run quick tests:
```bash
python test_template_query.py
```

Run usage examples:
```bash
python example_template_query_usage.py
```

## 📖 Documentation

- **QUICKSTART.md** - Get started in 5 minutes
- **TEMPLATE_QUERY_GUIDE.md** - Comprehensive guide
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **example_template_query_usage.py** - 7 usage examples

## 🎓 Learning Path

1. **New to the system?** → Start with QUICKSTART.md
2. **Need details?** → Read TEMPLATE_QUERY_GUIDE.md
3. **Want examples?** → Check example_template_query_usage.py
4. **Writing code?** → See Python API section above

## 🔧 Common Commands

```bash
# Health check
python run_template_query_inference.py --health

# Run first template
python run_template_query_inference.py

# Run specific template
python run_template_query_inference.py --template complaint_process

# Run all templates
python run_template_query_inference.py --all

# Custom query
python run_template_query_inference.py --query "Your question?"

# List all templates
python run_template_query_inference.py --list

# JSON output
python run_template_query_inference.py --json

# Run tests
python test_template_query_integration.py

# Run examples
python example_template_query_usage.py
```

## 🐛 Troubleshooting

### "Cannot connect to endpoint"
**Solution**: Start the FastAPI service first
```bash
python openai_functionality.py
```

### "Timeout after 120 seconds"
**Solution**: The LLM is processing. Wait and try again, or check GPU status.

### "Empty response"
**Solution**: Check that the knowledge base is properly loaded in the RAG pipeline.

## 🚀 Advanced Features

### Message History
```python
history = [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous response"}
]
result = client.run_inference(template, message_history=history)
```

### Batch Processing
```python
results = client.run_all_templates()
for result in results:
    print(result["template_name"], result["inference_time"])
```

### Custom Templates
```python
from template_query_inference import TemplateQuery
template = TemplateQuery(
    name="custom",
    query="Your question?",
    query_type="informational"
)
result = client.run_inference(template)
```

## 🔄 Integration

### FastAPI Integration
```python
from fastapi import FastAPI
from template_query_inference import TemplateQueryInference

app = FastAPI()
client = TemplateQueryInference()

@app.post("/ask/")
async def ask(question: str):
    result = client.run_custom_query(question)
    return result
```

### Flask Integration
```python
from flask import Flask, jsonify, request
from template_query_inference import TemplateQueryInference

app = Flask(__name__)
client = TemplateQueryInference()

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question")
    result = client.run_custom_query(question)
    return jsonify(result)
```

## 📈 Performance Tips

1. **First request is slower** - Model loading takes 30-60 seconds
2. **Batch requests** - Group queries for better efficiency
3. **GPU monitoring** - Check GPU during inference
4. **Keep-alive** - Service maintains state between requests

## 🤝 Contributing

To add new templates:
1. Edit `template_queries.json`
2. Add to the `templates` array
3. Include: id, name, query, query_type, description

Example:
```json
{
    "id": "my_template",
    "name": "My Template",
    "query": "Sample question?",
    "query_type": "informational",
    "description": "Description of template"
}
```

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review TEMPLATE_QUERY_GUIDE.md
3. Check FastAPI service logs
4. Verify endpoint health: `python run_template_query_inference.py --health`

## 📄 License

Part of the MSPSDC Chatbot project.

## 🎉 Ready to Use!

You now have a complete template query inference system. Start with:

```bash
python run_template_query_inference.py --help
```

Happy querying! 🚀
