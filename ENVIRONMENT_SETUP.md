# Environment Variables Configuration Guide

## Current Status: ✅ **LIVE AND WORKING**

The WhatsApp Chat UI interface is **currently running in demo mode** at `http://127.0.0.1:8000/` and does NOT require any environment variables for basic functionality.

## 🎯 **Functionality Levels**

### **Level 1: Demo Mode** (Currently Active)
- ✅ Full chat interface with WhatsApp-like design
- ✅ User and bot message bubbles
- ✅ Session management and chat history
- ✅ Real-time messaging experience
- ✅ Mobile responsive design
- ✅ All UI features working
- ❌ Pre-defined responses (not AI-powered)

**No environment variables needed for this level.**

---

### **Level 2: Basic LLM Integration** (Recommended Next Step)
To enable real AI responses using your existing LLM service:

**Required Environment Variables:**
```bash
# File: .env (or set in your environment)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Benefits:**
- Real AI-powered responses
- Integration with your existing LLM pipeline
- Same responses as WhatsApp integration

---

### **Level 3: Complete WhatsApp Integration** (Full Production)
For full WhatsApp webhook functionality alongside chat UI:

**Required Environment Variables:**
```bash
# WhatsApp Configuration
ACCESS_TOKEN=your_facebook_whatsapp_api_access_token
YOUR_PHONE_NUMBER=your_whatsapp_business_phone_number
APP_ID=your_facebook_app_id
APP_SECRET=your_facebook_app_secret
RECIPIENT_WAID=recipient_whatsapp_id
VERSION=v17.0
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_webhook_verify_token

# LLM Configuration  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
OPENAI_API_KEY=sk-your-openai-api-key

# Background Task Processing
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Optional: Database & Security
DATABASE_URL=sqlite:///mspsdc.db
SECRET_KEY=your-secure-secret-key-for-production
FLASK_ENV=production
```

## 🚀 **Quick Setup Instructions**

### **Option 1: Test Demo Mode (Immediate)**
```bash
# No setup needed - interface is already live!
# Visit: http://127.0.0.1:8000/
```

### **Option 2: Enable Real AI Responses**
```bash
# 1. Add API keys to environment
export ANTHROPIC_API_KEY="sk-ant-your-key"
export OPENAI_API_KEY="sk-your-key"

# 2. Restart Flask app
python3 run.py
```

### **Option 3: Full Production Setup**
```bash
# 1. Copy the complete .env template
# 2. Fill in all your actual API keys and tokens
# 3. Ensure Redis is running for Celery
redis-server
# 4. Start services
python3 run.py
python3 openai_functionality.py  # If needed
```

## 🔍 **Current Interface Testing**

The chat interface is **already accessible** and working:

**URLs to Test:**
- 🌐 **Chat Interface**: http://127.0.0.1:8000/
- 🩺 **Health Check**: http://127.0.0.1:8000/api/health
- 📡 **API Endpoints**: 
  - `POST /api/chat/send` - Send messages
  - `GET /api/chat/history` - View chat history
  - `POST /api/chat/clear` - Clear chat

**Sample Test Commands:**
```bash
# Test health endpoint
curl http://127.0.0.1:8000/api/health

# Test chat functionality
curl -X POST http://127.0.0.1:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with MSPSDC services"}'
```

## 🎨 **Interface Features Working Now**

✅ **WhatsApp-like Design**: Green theme with message bubbles
✅ **User/Bot Distinction**: Different colors for user vs bot messages  
✅ **Real-time Chat**: Instant send/receive experience
✅ **Session Persistence**: Chat history maintained during session
✅ **Mobile Responsive**: Works on desktop, tablet, mobile
✅ **Typing Indicators**: Visual feedback during message processing
✅ **Clear Chat**: Reset conversation functionality
✅ **Timestamps**: Shows when each message was sent

## 🔄 **Switching to Production Mode**

To switch from demo responses to real LLM responses:

1. **Add API keys** to your environment
2. **Modify** `app/ui_views.py`:
   - Replace demo response logic with actual LLM calls
   - Use the same `/query/` endpoint as WhatsApp integration
3. **Restart** the Flask application

## 📞 **Troubleshooting**

**Interface not loading?**
- Check if Flask is running: `ps aux | grep run.py`
- View logs: `tail -f flask_app.log`
- Test health endpoint: `curl http://127.0.0.1:8000/api/health`

**Want real AI responses?**
- Add your API keys to the environment
- Ensure LLM service is running on port 5000
- Update `ui_views.py` to use real LLM endpoint

**Need WhatsApp integration?**
- Configure all WhatsApp variables in `.env`
- Set up Redis for Celery background tasks
- Configure webhook endpoints

## ✅ **Summary**

**Current Status**: Chat interface is **LIVE and FUNCTIONAL** in demo mode at `http://127.0.0.1:8000/`

**No environment variables required** for testing the interface and user experience.

**For production use**: Add the appropriate API keys based on your desired functionality level.

The implementation provides a complete, working chat interface that can be enhanced with real AI responses and WhatsApp integration as needed.