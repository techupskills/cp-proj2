# AI Enterprise Training - Complete Demo Package

This package contains everything you need for the AI Enterprise Training webinar demos.

## What's Included

### Quick Agent Demo (10-minute live coding):
- `expense_agent.py` - AI agent that approves/rejects expenses
- Perfect for showing live AI decision making

### Capstone Project (impressive full demo):
- `customer_support_agent.py` - RAG-enabled AI agent
- `streamlit_app.py` - Production web interface
- Full customer database and knowledge base integration

### Setup & Testing:
- `requirements.txt` - All Python dependencies
- `test_setup.py` - Pre-webinar verification script
- This README with complete instructions

## Quick Setup (5 minutes)

### 1. Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai
```

### 2. Start Ollama and Install Model
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Install model
ollama pull llama3.2
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test Everything
```bash
python test_setup.py
```

If all tests pass, you're ready for the demo!

## Webinar Demo Flow

### 1. Opening Hook (Show Capstone First)
```bash
streamlit run streamlit_app.py
```
- Open browser to http://localhost:8501
- Show the impressive full interface
- Demo a few customer support queries
- **Key message**: "This is what you'll build in 3 days"

### 2. Quick Build Demo (Live Coding)
```bash
python expense_agent.py
```
- Shows immediate output in terminal
- **Key message**: "I built this in 10 minutes"
- Highlight: local processing, business logic, AI reasoning

### 3. Back to Capstone (Deep Dive)
- Show RAG in action (knowledge sources)
- Demonstrate customer context integration
- Highlight production-ready features
- **Key message**: "Enterprise-ready AI that you control"

## Troubleshooting

### Ollama Issues:
- **"Connection refused"**: Run `ollama serve`
- **"Model not found"**: Run `ollama pull llama3.2`
- **Slow responses**: Try `ollama pull llama3.2:1b` (smaller model)

### Python Issues:
- **Import errors**: Run `pip install -r requirements.txt`
- **ChromaDB errors**: Try `pip install --upgrade chromadb`

### Streamlit Issues:
- **Port busy**: Try `streamlit run streamlit_app.py --server.port 8502`
- **Module not found**: Ensure all files are in same directory

## Key Talking Points for Webinar

### Technical Highlights:
- **"This runs entirely on local hardware"** - no data leaves your organization
- **"Notice the business logic"** - it's not just a chatbot, it understands policies
- **"RAG with company data"** - AI + your specific business knowledge
- **"Structured output"** - ready for integration with existing systems

### Business Value:
- **"Built in 10 minutes"** - imagine what you can build in 3 days
- **"Production ready"** - this interface could go live today
- **"Enterprise security"** - complete control over data and processing
- **"No cloud costs"** - no per-token charges or API limits

## Demo Architecture

### Expense Agent (Quick Demo):
```
User Input -> Business Rules -> AI Reasoning -> Structured Decision
```

### Customer Support Agent (Capstone):
```
Customer Query -> RAG Search -> Customer Lookup -> AI Response -> Actions
```

## Next Steps After Demo
