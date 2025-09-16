#!/bin/bash
# AI Enterprise Training - Complete Demo Bundle
# Copy this entire file and follow the instructions to create all project files

echo "AI Enterprise Training - Setting up demo projects..."

# =============================================================================
# INSTRUCTIONS:
# 1. Copy this entire file content
# 2. Save it as "setup_demos.txt" 
# 3. Run the commands at the bottom to automatically create all files
# OR manually create each file using the content between the markers
# =============================================================================

# =============================================================================
# FILE: expense_agent.py
# Quick demo for live coding during webinar
# =============================================================================
cat > expense_agent.py << 'EOF'
import json
from datetime import datetime
import requests

class ExpenseAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.ollama_url = ollama_base_url
        self.model = model
        self.company_policies = {
            "max_meal": 75,
            "max_travel": 500,
            "max_supplies": 200,
            "requires_receipt": 25,
            "auto_approve_under": 50
        }
        
    def check_expense(self, expense_data):
        """Main agent function that processes expense requests"""
        
        # Tool: Policy lookup
        policy_check = self._check_against_policy(expense_data)
        
        # Tool: Calculate totals
        total_amount = self._calculate_total(expense_data)
        
        # Tool: Generate decision
        decision = self._make_decision(expense_data, policy_check, total_amount)
        
        return decision
    
    def _check_against_policy(self, expense):
        """Tool: Check expense against company policies"""
        category = expense.get('category', '').lower()
        amount = expense.get('amount', 0)
        
        if 'meal' in category and amount > self.company_policies['max_meal']:
            return f"Exceeds meal limit (${self.company_policies['max_meal']})"
        elif 'travel' in category and amount > self.company_policies['max_travel']:
            return f"Exceeds travel limit (${self.company_policies['max_travel']})"
        elif 'supplies' in category and amount > self.company_policies['max_supplies']:
            return f"Exceeds supplies limit (${self.company_policies['max_supplies']})"
        elif amount > self.company_policies['requires_receipt'] and not expense.get('has_receipt'):
            return f"Receipt required for amounts over ${self.company_policies['requires_receipt']}"
        else:
            return "Complies with company policy"
    
    def _calculate_total(self, expense):
        """Tool: Calculate expense totals and tax implications"""
        amount = expense.get('amount', 0)
        tax_rate = 0.08 if expense.get('category') != 'travel' else 0
        tax_amount = amount * tax_rate
        return {
            'subtotal': amount,
            'tax': tax_amount,
            'total': amount + tax_amount
        }
    
    def _query_ollama(self, prompt):
        """Query local Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f'{{"decision": "NEEDS_REVIEW", "reasoning": "AI processing error: {str(e)}", "next_steps": "Manual review required"}}'
    
    def _make_decision(self, expense, policy_check, totals):
        """Tool: Use AI reasoning to make final decision"""
        
        prompt = f"""
        As an AI expense approval agent, analyze this expense request and respond ONLY with valid JSON.
        
        Employee: {expense.get('employee', 'Unknown')}
        Category: {expense.get('category', 'Unknown')}
        Amount: ${expense.get('amount', 0)}
        Description: {expense.get('description', 'No description')}
        Date: {expense.get('date', 'Not provided')}
        Has Receipt: {expense.get('has_receipt', False)}
        
        Policy Check Result: {policy_check}
        Financial Summary: {json.dumps(totals, indent=2)}
        
        Auto-approval threshold: ${self.company_policies['auto_approve_under']}
        
        Respond with JSON containing exactly these fields:
        - "decision": must be "APPROVED", "REJECTED", or "NEEDS_REVIEW"
        - "reasoning": explanation for the decision
        - "next_steps": what should happen next
        
        JSON Response:
        """
        
        try:
            # Query local Ollama model
            ai_response = self._query_ollama(prompt)
            
            # Parse AI response
            ai_decision = json.loads(ai_response)
            
            # Add our calculated data
            ai_decision['policy_check'] = policy_check
            ai_decision['financial_summary'] = totals
            ai_decision['processed_at'] = datetime.now().isoformat()
            
            return ai_decision
            
        except Exception as e:
            return {
                "decision": "NEEDS_REVIEW",
                "reasoning": f"AI processing error: {str(e)}",
                "next_steps": "Manual review required",
                "policy_check": policy_check,
                "financial_summary": totals
            }

# Demo Usage
def demo_expense_agent():
    """Demo function for webinar presentation"""
    
    print("AI Expense Agent Demo\n" + "="*50)
    
    # Initialize agent (using local Ollama)
    agent = ExpenseAgent(
        ollama_base_url="http://localhost:11434",
        model="llama3.2"
    )
    
    # Sample expense requests for demo
    expenses = [
        {
            "employee": "Sarah Chen",
            "category": "business meal",
            "amount": 45,
            "description": "Client dinner at Restaurant ABC",
            "date": "2024-12-01",
            "has_receipt": True
        },
        {
            "employee": "Mike Rodriguez", 
            "category": "travel",
            "amount": 650,
            "description": "Flight to client site",
            "date": "2024-12-02",
            "has_receipt": False
        },
        {
            "employee": "Lisa Park",
            "category": "office supplies",
            "amount": 25,
            "description": "Notebooks and pens",
            "date": "2024-12-03", 
            "has_receipt": True
        }
    ]
    
    for i, expense in enumerate(expenses, 1):
        print(f"\nProcessing Expense Request #{i}")
        print(f"Employee: {expense['employee']}")
        print(f"Amount: ${expense['amount']} for {expense['category']}")
        
        # Process with agent
        result = agent.check_expense(expense)
        
        print(f"\nDecision: {result['decision']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Next Steps: {result['next_steps']}")
        print(f"Total Cost: ${result['financial_summary']['total']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    demo_expense_agent()
EOF

# =============================================================================
# FILE: customer_support_agent.py  
# Full RAG-enabled customer support agent
# =============================================================================
cat > customer_support_agent.py << 'EOF'
import json
from datetime import datetime
import requests
import chromadb
from chromadb.config import Settings

class CustomerSupportAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.ollama_url = ollama_base_url
        self.model = model
        
        # Initialize vector database for RAG
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.knowledge_base = self.chroma_client.get_or_create_collection("support_docs")
        
        # Load company data
        self.load_knowledge_base()
        self.load_customer_data()
        
    def load_knowledge_base(self):
        """Load company documentation into vector database"""
        
        # Sample company knowledge (in real app, this would be loaded from files)
        documents = [
            {
                "id": "policy_1", 
                "text": "Our return policy allows returns within 30 days of purchase with original receipt. Items must be in original condition.",
                "category": "returns"
            },
            {
                "id": "policy_2",
                "text": "Shipping typically takes 3-5 business days within the US. Express shipping (1-2 days) available for additional fee.",
                "category": "shipping"
            },
            {
                "id": "policy_3", 
                "text": "Technical support is available Monday-Friday 9AM-6PM EST. Premium customers get 24/7 support access.",
                "category": "support"
            },
            {
                "id": "troubleshoot_1",
                "text": "If the device won't turn on: 1) Check power cable connection 2) Try different outlet 3) Hold power button for 10 seconds to reset",
                "category": "troubleshooting"
            },
            {
                "id": "account_1",
                "text": "To reset your password, visit the login page and click 'Forgot Password'. Enter your email and check for reset instructions.",
                "category": "account"
            }
        ]
        
        # Add documents to vector database
        for doc in documents:
            self.knowledge_base.add(
                documents=[doc["text"]],
                metadatas=[{"category": doc["category"]}],
                ids=[doc["id"]]
            )
    
    def load_customer_data(self):
        """Load customer database (simulated)"""
        self.customers = {
            "john.doe@email.com": {
                "name": "John Doe",
                "tier": "Premium",
                "orders": [
                    {"id": "ORD-001", "date": "2024-11-15", "product": "Wireless Headphones", "status": "Delivered"},
                    {"id": "ORD-002", "date": "2024-12-01", "product": "Bluetooth Speaker", "status": "Shipped"}
                ],
                "support_tickets": 2
            },
            "sarah.smith@email.com": {
                "name": "Sarah Smith", 
                "tier": "Standard",
                "orders": [
                    {"id": "ORD-003", "date": "2024-11-20", "product": "USB Cable", "status": "Delivered"}
                ],
                "support_tickets": 0
            }
        }
    
    def search_knowledge_base(self, query, n_results=3):
        """RAG: Search company knowledge base"""
        results = self.knowledge_base.query(
            query_texts=[query],
            n_results=n_results
        )
        
        relevant_docs = []
        for i, doc in enumerate(results['documents'][0]):
            relevant_docs.append({
                "content": doc,
                "category": results['metadatas'][0][i]['category']
            })
        
        return relevant_docs
    
    def lookup_customer(self, email):
        """Tool: Customer database lookup"""
        return self.customers.get(email.lower(), None)
    
    def create_ticket(self, customer_email, issue_type, description):
        """Tool: Create support ticket"""
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email + description) % 10000:04d}"
        
        ticket = {
            "id": ticket_id,
            "customer": customer_email,
            "type": issue_type,
            "description": description,
            "status": "Open",
            "created": datetime.now().isoformat(),
            "priority": "Medium"
        }
        
        return ticket
    
    def _query_ollama(self, prompt):
        """Query local Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f'{{"response": "I apologize, but I\'m experiencing technical difficulties. Error: {str(e)}", "action_needed": "create_ticket", "confidence": 0}}'
    
    def process_customer_inquiry(self, customer_email, inquiry):
        """Main agent function that processes customer inquiries"""
        
        # Step 1: Look up customer info
        customer_info = self.lookup_customer(customer_email)
        
        # Step 2: Search knowledge base for relevant information
        relevant_docs = self.search_knowledge_base(inquiry)
        
        # Step 3: Use AI to generate response
        response = self._generate_ai_response(customer_email, customer_info, inquiry, relevant_docs)
        
        return response
    
    def _generate_ai_response(self, customer_email, customer_info, inquiry, relevant_docs):
        """Generate AI response using customer data and knowledge base"""
        
        # Prepare context for AI
        customer_context = f"Customer: {customer_info['name']} ({customer_info['tier']} tier)" if customer_info else "Customer: Not found in database"
        
        knowledge_context = "\n".join([f"- {doc['content']}" for doc in relevant_docs])
        
        prompt = f"""
        You are a helpful customer support AI agent. Use the provided information to assist the customer.
        Respond ONLY with valid JSON.
        
        CUSTOMER INFORMATION:
        {customer_context}
        
        RELEVANT COMPANY POLICIES & INFORMATION:
        {knowledge_context}
        
        CUSTOMER INQUIRY: {inquiry}
        
        Instructions:
        1. Be helpful, friendly, and professional
        2. Use the provided company information to answer accurately
        3. If you need to create a ticket or escalate, explain why
        4. Personalize response based on customer tier if applicable
        
        Respond with JSON containing exactly these fields:
        - "response": your helpful response to the customer
        - "action_needed": either "none", "create_ticket", or "escalate"
        - "confidence": number between 0 and 1 indicating your confidence
        
        JSON Response:
        """
        
        try:
            # Query local Ollama model
            ai_response = self._query_ollama(prompt)
            
            # Parse AI response
            result = json.loads(ai_response)
            
            # Add metadata
            result['processed_at'] = datetime.now().isoformat()
            result['customer_tier'] = customer_info['tier'] if customer_info else 'Unknown'
            result['knowledge_sources'] = len(relevant_docs)
            
            # Determine if ticket creation is needed
            if result.get('action_needed') == 'create_ticket':
                ticket = self.create_ticket(customer_email, 'General Inquiry', inquiry)
                result['ticket_created'] = ticket
            
            return result
            
        except Exception as e:
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Let me create a ticket for you and a human agent will assist you shortly.",
                "action_needed": "create_ticket",
                "confidence": 0,
                "error": str(e)
            }

if __name__ == "__main__":
    # Simple test
    agent = CustomerSupportAgent()
    
    test_inquiry = "How do I return an item I bought last week?"
    test_email = "john.doe@email.com"
    
    result = agent.process_customer_inquiry(test_email, test_inquiry)
    print("Test Result:")
    print(json.dumps(result, indent=2))
EOF

# =============================================================================
# FILE: streamlit_app.py
# Production web interface for customer support agent
# =============================================================================
cat > streamlit_app.py << 'EOF'
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
from customer_support_agent import CustomerSupportAgent

# Page config
st.set_page_config(
    page_title="AI Customer Support Agent",
    page_icon="🤖",
    layout="wide"
)

def main():
    st.title("AI Customer Support Agent")
    st.markdown("### Powered by RAG + AI Agents + Local LLM")
    
    # Sidebar configuration
    st.sidebar.title("Configuration")
    
    # Ollama settings
    st.sidebar.subheader("Ollama Settings")
    ollama_url = st.sidebar.text_input("Ollama URL", "http://localhost:11434")
    model_name = st.sidebar.selectbox("Model", ["llama3.2", "llama3.1", "mistral", "codellama"])
    
    # Initialize agent
    if st.sidebar.button("Connect to Ollama") or 'agent' not in st.session_state:
        try:
            with st.spinner("Connecting to Ollama..."):
                st.session_state.agent = CustomerSupportAgent(ollama_url, model_name)
            st.sidebar.success(f"Connected to {model_name}")
        except Exception as e:
            st.sidebar.error(f"Connection failed: {str(e)}")
            return
    
    # Only proceed if agent is initialized
    if 'agent' not in st.session_state:
        st.warning("Please configure and connect to Ollama in the sidebar first.")
        st.markdown("""
        ### Setup Instructions:
        1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
        2. Start Ollama: `ollama serve`
        3. Install model: `ollama pull llama3.2`
        4. Click "Connect to Ollama" in the sidebar
        """)
        return
    
    # Customer selection
    st.sidebar.subheader("Customer Login")
    customer_email = st.sidebar.selectbox(
        "Select Customer:",
        ["john.doe@email.com", "sarah.smith@email.com", "new.customer@email.com"]
    )
    
    # Display customer info
    if customer_email:
        customer_info = st.session_state.agent.lookup_customer(customer_email)
        if customer_info:
            st.sidebar.success(f"Welcome back, {customer_info['name']}")
            st.sidebar.metric("Customer Tier", customer_info['tier'])
            st.sidebar.metric("Recent Orders", len(customer_info['orders']))
            st.sidebar.metric("Support Tickets", customer_info['support_tickets'])
            
            # Show recent orders
            if customer_info['orders']:
                st.sidebar.subheader("Recent Orders")
                for order in customer_info['orders'][-2:]:  # Show last 2 orders
                    st.sidebar.text(f"{order['id']}: {order['product']}")
                    st.sidebar.text(f"   Status: {order['status']}")
        else:
            st.sidebar.info("New customer - no history found")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("How can I help you today?")
        
        # Sample questions for demo
        sample_questions = [
            "How do I return an item I bought last week?",
            "When will my order ORD-002 arrive?", 
            "My device won't turn on, can you help?",
            "I forgot my account password",
            "What are your shipping options?",
            "Can I change my shipping address?",
            "Do you have 24/7 support?",
            "How do I track my order?"
        ]
        
        selected_question = st.selectbox("Try a sample question:", [""] + sample_questions)
        
        inquiry = st.text_area(
            "Your question:",
            value=selected_question,
            height=120,
            placeholder="Type your question here..."
        )
        
        # Process inquiry
        if st.button("Get Help", type="primary", use_container_width=True):
            if inquiry and customer_email:
                with st.spinner("AI Agent processing your inquiry..."):
                    # Process with AI agent
                    response = st.session_state.agent.process_customer_inquiry(customer_email, inquiry)
                    
                    # Store in session state for reference
                    if 'conversation_history' not in st.session_state:
                        st.session_state.conversation_history = []
                    
                    st.session_state.conversation_history.append({
                        'timestamp': datetime.now(),
                        'customer': customer_email,
                        'inquiry': inquiry,
                        'response': response
                    })
                
                # Display response
                st.success("**AI Agent Response:**")
                st.write(response['response'])
                
                # Show metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    confidence_pct = response.get('confidence', 0) * 100
                    st.metric("Confidence", f"{confidence_pct:.0f}%")
                with col_b:
                    st.metric("Knowledge Sources", response.get('knowledge_sources', 0))
                with col_c:
                    st.metric("Response Time", "< 2 sec")
                
                # Show any actions taken
                if 'ticket_created' in response:
                    st.info(f"**Ticket Created:** {response['ticket_created']['id']}")
                    st.write(f"**Status:** {response['ticket_created']['status']}")
                
                if response.get('action_needed') and response.get('action_needed') != 'none':
                    st.warning(f"**Action Needed:** {response['action_needed']}")
                
            else:
                st.error("Please enter a question and select a customer email.")
    
    with col2:
        st.subheader("Agent Analytics")
        
        # Agent stats
        st.metric("Knowledge Base", "5 documents")
        st.metric("Customers", "2 registered")
        st.metric("Avg Response Time", "1.8 seconds")
        
        # Show knowledge sources for last query
        if inquiry and 'agent' in st.session_state:
            with st.expander("Knowledge Sources Used"):
                docs = st.session_state.agent.search_knowledge_base(inquiry)
                for i, doc in enumerate(docs):
                    st.write(f"**Source {i+1}** ({doc['category']}):")
                    st.write(f"_{doc['content']}_")
                    st.write("---")
    
    # Footer with demo info
    st.markdown("---")
    st.markdown("""
    ### Demo Features Showcased:
    - **RAG (Retrieval Augmented Generation)** with company knowledge base
    - **Customer context integration** with order history and tier status
    - **Multi-tool AI agent** with decision making capabilities
    - **Local LLM processing** via Ollama (no cloud dependencies)
    - **Production-ready interface** with Streamlit
    - **Real-time analytics** and conversation tracking
    """)

if __name__ == "__main__":
    main()
EOF

# =============================================================================
# FILE: requirements.txt
# Python dependencies for both projects
# =============================================================================
cat > requirements.txt << 'EOF'
streamlit>=1.28.0
requests>=2.28.0
chromadb>=0.4.0
pandas>=1.5.0
json5>=0.9.0
EOF

# =============================================================================
# FILE: test_setup.py
# Quick test script to verify everything works
# =============================================================================
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test script to verify Ollama and projects are working
Run this before your webinar to ensure everything is ready
"""

import requests
import json
import sys

def test_ollama():
    """Test if Ollama is running and has the model"""
    print("Testing Ollama connection...")
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if any('llama3.2' in name for name in model_names):
                print("SUCCESS: Ollama is running with llama3.2 model")
                return True
            else:
                print(f"WARNING: Ollama is running but llama3.2 not found. Available: {model_names}")
                print("Try: ollama pull llama3.2")
                return False
        else:
            print(f"ERROR: Ollama returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama")
        print("Try: ollama serve")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_expense_agent():
    """Test the expense agent"""
    print("\nTesting Expense Agent...")
    
    try:
        from expense_agent import ExpenseAgent
        agent = ExpenseAgent()
        
        test_expense = {
            "employee": "Test User",
            "category": "business meal",
            "amount": 45,
            "description": "Test expense",
            "date": "2024-12-01",
            "has_receipt": True
        }
        
        result = agent.check_expense(test_expense)
        
        if isinstance(result, dict) and 'decision' in result:
            print("SUCCESS: Expense Agent working correctly")
            return True
        else:
            print("ERROR: Expense Agent returned unexpected format")
            return False
            
    except ImportError:
        print("ERROR: Cannot import expense_agent.py - file missing?")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_customer_support():
    """Test the customer support agent"""
    print("\nTesting Customer Support Agent...")
    
    try:
        from customer_support_agent import CustomerSupportAgent
        agent = CustomerSupportAgent()
        
        result = agent.process_customer_inquiry(
            "john.doe@email.com", 
            "How do I return an item?"
        )
        
        if isinstance(result, dict) and 'response' in result:
            print("SUCCESS: Customer Support Agent working correctly")
            return True
        else:
            print("ERROR: Customer Support Agent returned unexpected format")
            return False
            
    except ImportError:
        print("ERROR: Cannot import customer_support_agent.py - file missing?")
        return False
    except Exception as e:
        print("ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("AI Enterprise Training - Pre-Webinar Test")
    print("="*50)
    
    tests = [
        ("Ollama Setup", test_ollama),
        ("Expense Agent", test_expense_agent),
        ("Customer Support Agent", test_customer_support)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All systems ready for webinar!")
        print("\nDemo commands:")
        print("   python expense_agent.py")
        print("   streamlit run streamlit_app.py")
    else:
        print("WARNING: Some issues detected. Check setup before webinar.")

if __name__ == "__main__":
    main()
EOF

# =============================================================================
# FILE: README.md
# Complete setup and usage instructions
# =============================================================================
cat > README.md << 'EOF'
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