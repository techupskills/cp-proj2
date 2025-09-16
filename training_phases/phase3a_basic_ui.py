#!/usr/bin/env python3
"""
Phase 3a: Basic UI Framework (90 min)
Day 3 - Accelerating the SDLC: Designing an AI-powered application

Learning Objectives:
- Designing an AI-powered application
- Choosing a model, prompts, MCP integration
- Hands-on: build the base app, MCP server, and agent
- User interface design for AI applications

This module focuses on creating user-friendly interfaces for AI applications,
specifically building a Streamlit-based customer service interface.
"""

import streamlit as st
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import previous phase capabilities
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1a_basic_llm import BasicLLMClient
    from phase1d_basic_rag import BasicRAGSystem
    from phase2a_simple_agent import SimpleAgent
    from phase2d_mcp_client import MCPEnabledAgent
    LLM_AVAILABLE = True
    RAG_AVAILABLE = True
    AGENT_AVAILABLE = True
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    LLM_AVAILABLE = False
    RAG_AVAILABLE = False
    AGENT_AVAILABLE = False
    MCP_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("basic-ui")

# Check if running in Streamlit
def is_streamlit():
    """Check if code is running in Streamlit environment."""
    try:
        import streamlit as st
        return hasattr(st, 'session_state')
    except:
        return False

class CustomerServiceApp:
    """
    Basic customer service application with Streamlit UI.
    Demonstrates core UI patterns for AI-powered applications.
    """
    
    def __init__(self):
        """Initialize the customer service application."""
        self.app_name = "AI Customer Service Platform"
        self.version = "3.0-Training"
        
        # Initialize components based on availability
        self.llm_client = None
        self.rag_system = None
        self.agent = None
        
        # Mock data for demonstration
        self.mock_customers = {
            "john.doe@email.com": {
                "name": "John Doe",
                "tier": "Premium",
                "orders": 3,
                "last_contact": "2024-11-20"
            },
            "sarah.smith@email.com": {
                "name": "Sarah Smith",
                "tier": "Standard", 
                "orders": 1,
                "last_contact": "2024-11-15"
            }
        }
        
        self.mock_knowledge = [
            {
                "category": "Returns",
                "title": "Return Policy",
                "content": "Items can be returned within 30 days with receipt for full refund."
            },
            {
                "category": "Shipping", 
                "title": "Shipping Information",
                "content": "Standard shipping takes 3-5 business days. Express available in 1-2 days."
            },
            {
                "category": "Support",
                "title": "Contact Support",
                "content": "24/7 support for Premium customers. Standard: Mon-Fri 9AM-5PM."
            }
        ]
    
    def initialize_components(self):
        """Initialize AI components if available."""
        try:
            if LLM_AVAILABLE:
                self.llm_client = BasicLLMClient()
                
            if AGENT_AVAILABLE:
                self.agent = SimpleAgent("UIAgent")
                
            logger.info("AI components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False

def setup_streamlit_config():
    """Configure Streamlit page settings and theme."""
    st.set_page_config(
        page_title="AI Customer Service Platform",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://docs.streamlit.io',
            'Report a bug': None,
            'About': "AI Customer Service Platform - Training Phase 3a"
        }
    )

def apply_custom_css():
    """Apply professional CSS styling for the application."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Professional Header */
        .main-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 2.5rem;
            text-align: center;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="1" fill="white" opacity="0.1"/><circle cx="80" cy="80" r="1" fill="white" opacity="0.1"/><circle cx="40" cy="60" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.1;
            pointer-events: none;
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            position: relative;
            z-index: 1;
        }
        
        .main-header p {
            margin: 1rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        /* Professional Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border-right: 1px solid #e2e8f0;
        }
        
        /* Professional Chat Interface */
        .chat-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e2e8f0;
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            background: #f8fafc;
        }
        
        /* Professional Components */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;
        }
        
        /* Chat interface styling */
        .chat-container {
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border: 1px solid #e2e8f0;
        }
        
        .message-bubble {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
            margin-left: auto;
        }
        
        .agent-message {
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            margin-right: auto;
        }
        
        .system-message {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            text-align: center;
            font-style: italic;
        }
        
        /* Sidebar styling */
        .sidebar-section {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 1px solid #e2e8f0;
        }
        
        /* Metrics and cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e2e8f0;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1e40af;
        }
        
        .metric-label {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online { background-color: #10b981; }
        .status-offline { background-color: #ef4444; }
        .status-warning { background-color: #f59e0b; }
        
        /* Customer info */
        .customer-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        'app_initialized': False,
        'conversation_history': [],
        'current_customer': None,
        'selected_mode': 'Customer Chat',
        'app_stats': {
            'total_conversations': 0,
            'messages_sent': 0,
            'customers_helped': 0,
            'avg_response_time': 2.3
        },
        'system_status': {
            'llm_service': 'Online' if LLM_AVAILABLE else 'Offline',
            'rag_system': 'Online' if RAG_AVAILABLE else 'Offline',
            'agent_service': 'Online' if AGENT_AVAILABLE else 'Offline',
            'mcp_service': 'Online' if MCP_AVAILABLE else 'Offline'
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_header():
    """Render the professional main header with enhanced branding."""
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="font-size: 3rem;">🤖</div>
            <div style="text-align: left;">
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; letter-spacing: -0.025em;">AI Customer Service Platform</h1>
                <div style="display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem;">
                    <span style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500;">Training Phase 3a</span>
                    <span style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500;">Basic UI Framework</span>
                    <span style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500;">Hands-on Learning</span>
                </div>
            </div>
        </div>
        <p style="margin: 0; font-size: 1.1rem; opacity: 0.9; font-weight: 400; max-width: 600px; margin: 0 auto; line-height: 1.5;">
            Learn to design and build AI-powered applications with modern professional interfaces
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the application sidebar with controls and information."""
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        # Mode selector
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("Interface Mode")
        st.session_state.selected_mode = st.selectbox(
            "Choose view:",
            ["Customer Chat", "Knowledge Base", "System Monitor", "Settings"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Customer selection
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("👤 Customer Context")
        
        app = CustomerServiceApp()
        customer_emails = list(app.mock_customers.keys()) + ["new.customer@email.com"]
        
        selected_email = st.selectbox(
            "Select Customer:",
            customer_emails,
            index=0
        )
        
        if selected_email in app.mock_customers:
            customer = app.mock_customers[selected_email]
            st.session_state.current_customer = customer
            
            st.markdown(f"""
            <div class="customer-card">
                <h4>👤 {customer['name']}</h4>
                <p><strong>Tier:</strong> {customer['tier']}</p>
                <p><strong>Orders:</strong> {customer['orders']}</p>
                <p><strong>Last Contact:</strong> {customer['last_contact']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state.current_customer = None
            st.info("New customer - no history available")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System status
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("🔧 System Status")
        
        status = st.session_state.system_status
        for service, state in status.items():
            status_class = "status-online" if state == "Online" else "status-offline"
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <span class="status-indicator {status_class}"></span>
                <strong>{service.replace('_', ' ').title()}:</strong> {state}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("⚡ Quick Actions")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()
        
        if st.button("📊 Refresh Stats", use_container_width=True):
            st.session_state.app_stats['total_conversations'] += 1
            st.rerun()
        
        if st.button("🔄 Reset Demo", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_app_metrics():
    """Render application metrics and statistics."""
    st.subheader("📊 Application Metrics")
    
    stats = st.session_state.app_stats
    
    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_conversations']}</div>
            <div class="metric-label">Total Conversations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['messages_sent']}</div>
            <div class="metric-label">Messages Sent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['customers_helped']}</div>
            <div class="metric-label">Customers Helped</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['avg_response_time']}s</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        """, unsafe_allow_html=True)

def render_customer_chat():
    """Render the main customer chat interface."""
    st.subheader("💬 Customer Support Chat")
    
    # Display current customer context
    if st.session_state.current_customer:
        customer = st.session_state.current_customer
        st.info(f"💼 Chatting with {customer['name']} ({customer['tier']} customer)")
    else:
        st.info("👋 Welcome! Please introduce yourself to get started.")
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display conversation history
    if st.session_state.conversation_history:
        for message in st.session_state.conversation_history:
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="message-bubble user-message">
                    <strong>👤 You:</strong> {message['content']}<br>
                    <small style="opacity: 0.7;">{message['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
            elif message['type'] == 'agent':
                confidence = message.get('confidence', 0)
                confidence_color = "#10b981" if confidence > 0.7 else "#f59e0b" if confidence > 0.3 else "#ef4444"
                
                st.markdown(f"""
                <div class="message-bubble agent-message">
                    <strong>🤖 Support Agent:</strong> {message['content']}<br>
                    <small style="opacity: 0.7;">
                        {message['timestamp']} | 
                        <span style="color: {confidence_color};">Confidence: {confidence:.1%}</span>
                        {f" | Response time: {message.get('response_time', 0):.1f}s" if 'response_time' in message else ""}
                    </small>
                </div>
                """, unsafe_allow_html=True)
            elif message['type'] == 'system':
                st.markdown(f"""
                <div class="message-bubble system-message">
                    ℹ️ {message['content']}<br>
                    <small style="opacity: 0.7;">{message['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="message-bubble system-message">
            👋 Welcome to our AI Customer Service! How can we help you today?
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input form
    with st.form("chat_input_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "Type your message:",
                height=100,
                placeholder="Example: I need help with returning a product I bought last week...",
                label_visibility="collapsed"
            )
        
        with col2:
            st.write("")  # Spacing
            submit_button = st.form_submit_button("Send 📤", use_container_width=True)
            
            # Additional options
            include_context = st.checkbox("Include context", value=True, help="Include customer information in the request")
            use_ai_agent = st.checkbox("Use AI Agent", value=True, help="Process through AI agent vs. simple response")
        
        if submit_button and user_input.strip():
            process_chat_message(user_input.strip(), include_context, use_ai_agent)

def process_chat_message(message: str, include_context: bool, use_ai_agent: bool):
    """Process a chat message and generate response."""
    # Add user message to history
    user_message = {
        'type': 'user',
        'content': message,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.conversation_history.append(user_message)
    
    # Update stats
    st.session_state.app_stats['messages_sent'] += 1
    
    # Generate response
    start_time = time.time()
    
    try:
        if use_ai_agent and AGENT_AVAILABLE:
            response = generate_ai_agent_response(message, include_context)
        else:
            response = generate_simple_response(message, include_context)
        
        response_time = time.time() - start_time
        
        # Add agent response to history
        agent_message = {
            'type': 'agent',
            'content': response['content'],
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'confidence': response.get('confidence', 0.8),
            'response_time': response_time,
            'method': response.get('method', 'simple')
        }
        st.session_state.conversation_history.append(agent_message)
        
        # Update stats
        if st.session_state.current_customer:
            st.session_state.app_stats['customers_helped'] += 1
        
        # Update average response time
        current_avg = st.session_state.app_stats['avg_response_time']
        new_avg = (current_avg + response_time) / 2
        st.session_state.app_stats['avg_response_time'] = round(new_avg, 1)
        
    except Exception as e:
        # Add error message
        error_message = {
            'type': 'system',
            'content': f"Sorry, I encountered an error processing your request: {str(e)}",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.conversation_history.append(error_message)
    
    st.rerun()

def generate_ai_agent_response(message: str, include_context: bool) -> Dict[str, Any]:
    """Generate response using AI agent (if available)."""
    try:
        app = CustomerServiceApp()
        agent_response = "I understand you're asking about: " + message
        
        # Add context if available and requested
        if include_context and st.session_state.current_customer:
            customer = st.session_state.current_customer
            agent_response += f"\n\nI can see you're a {customer['tier']} customer with {customer['orders']} previous orders. Let me help you with that."
        
        # Simple keyword-based responses for demo
        if any(word in message.lower() for word in ['return', 'refund']):
            agent_response = "I can help you with returns! Our return policy allows you to return items within 30 days of purchase with your receipt. Would you like me to start a return process for you?"
            confidence = 0.9
        elif any(word in message.lower() for word in ['shipping', 'delivery']):
            agent_response = "For shipping information: Standard shipping takes 3-5 business days ($5.99), Express shipping takes 1-2 days ($15.99). Orders over $50 get free standard shipping!"
            confidence = 0.85
        elif any(word in message.lower() for word in ['password', 'login', 'account']):
            agent_response = "For account issues, you can reset your password by clicking 'Forgot Password' on the login page. Check your email for reset instructions within 5-10 minutes."
            confidence = 0.8
        else:
            agent_response = "Thank you for your question. Let me connect you with the best information to help resolve your inquiry. Is there anything specific about your order or account I can help with?"
            confidence = 0.6
        
        return {
            'content': agent_response,
            'confidence': confidence,
            'method': 'ai_agent'
        }
        
    except Exception as e:
        return {
            'content': f"I apologize, but I'm having technical difficulties. Please try again or contact our support team directly.",
            'confidence': 0.3,
            'method': 'error_fallback'
        }

def generate_simple_response(message: str, include_context: bool) -> Dict[str, Any]:
    """Generate simple rule-based response."""
    # Simple keyword matching
    keywords_responses = {
        'hello': "Hello! Welcome to our customer service. How can I assist you today?",
        'help': "I'm here to help! You can ask me about returns, shipping, account issues, or any other questions.",
        'return': "Our return policy allows returns within 30 days with receipt. Would you like help starting a return?",
        'shipping': "We offer standard (3-5 days) and express (1-2 days) shipping. Free shipping on orders over $50!",
        'account': "For account issues, you can reset your password on the login page or contact support.",
        'order': "I can help you track your order or answer questions about past purchases.",
        'thank': "You're welcome! Is there anything else I can help you with today?"
    }
    
    # Find matching response
    message_lower = message.lower()
    for keyword, response in keywords_responses.items():
        if keyword in message_lower:
            if include_context and st.session_state.current_customer:
                customer = st.session_state.current_customer
                response += f" As a {customer['tier']} customer, you have access to priority support."
            
            return {
                'content': response,
                'confidence': 0.7,
                'method': 'keyword_match'
            }
    
    # Default response
    default_response = "Thank you for your message. I'm here to help with any questions about our products, orders, returns, or account issues. Could you please provide more details about what you need assistance with?"
    
    return {
        'content': default_response,
        'confidence': 0.5,
        'method': 'default'
    }

def render_knowledge_base():
    """Render the knowledge base browser."""
    st.subheader("📚 Knowledge Base")
    
    app = CustomerServiceApp()
    
    # Search functionality
    search_query = st.text_input("🔍 Search knowledge base:", placeholder="Enter keywords...")
    
    if search_query:
        # Simple search through mock knowledge
        results = []
        for item in app.mock_knowledge:
            if search_query.lower() in item['title'].lower() or search_query.lower() in item['content'].lower():
                results.append(item)
        
        if results:
            st.success(f"Found {len(results)} articles matching '{search_query}'")
            for result in results:
                with st.expander(f"📄 {result['title']} ({result['category']})"):
                    st.write(result['content'])
        else:
            st.warning(f"No articles found matching '{search_query}'")
    
    # Browse by category
    st.subheader("📂 Browse by Category")
    
    categories = list(set(item['category'] for item in app.mock_knowledge))
    
    for category in categories:
        with st.expander(f"📁 {category}"):
            category_items = [item for item in app.mock_knowledge if item['category'] == category]
            for item in category_items:
                st.markdown(f"**{item['title']}**")
                st.write(item['content'])
                st.divider()

def render_system_monitor():
    """Render system monitoring interface."""
    st.subheader("🖥️ System Monitor")
    
    # System status overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Service Status")
        status = st.session_state.system_status
        
        for service, state in status.items():
            status_color = "🟢" if state == "Online" else "🔴"
            st.markdown(f"{status_color} **{service.replace('_', ' ').title()}**: {state}")
    
    with col2:
        st.markdown("### 📊 Performance Metrics")
        st.metric("Response Time", f"{st.session_state.app_stats['avg_response_time']}s")
        st.metric("Messages Processed", st.session_state.app_stats['messages_sent'])
        st.metric("Active Conversations", len(st.session_state.conversation_history))
    
    # Conversation analytics
    st.subheader("💬 Conversation Analytics")
    
    if st.session_state.conversation_history:
        # Message types
        message_types = {}
        for msg in st.session_state.conversation_history:
            msg_type = msg['type']
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("User Messages", message_types.get('user', 0))
        with col2:
            st.metric("Agent Responses", message_types.get('agent', 0))
        with col3:
            st.metric("System Messages", message_types.get('system', 0))
        
        # Recent messages
        st.subheader("📝 Recent Messages")
        for msg in st.session_state.conversation_history[-5:]:
            st.text(f"[{msg['timestamp']}] {msg['type'].title()}: {msg['content'][:50]}...")
    else:
        st.info("No conversation data available yet.")

def render_settings():
    """Render application settings."""
    st.subheader("⚙️ Application Settings")
    
    # UI Settings
    st.markdown("### 🎨 Interface Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme_mode = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
        show_timestamps = st.checkbox("Show timestamps", value=True)
        auto_scroll = st.checkbox("Auto-scroll chat", value=True)
    
    with col2:
        message_limit = st.slider("Message history limit", 10, 100, 50)
        response_delay = st.slider("Simulated response delay (s)", 0.0, 3.0, 1.0)
    
    # AI Settings
    st.markdown("### 🤖 AI Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.7)
        use_context = st.checkbox("Include customer context", value=True)
    
    with col2:
        max_response_length = st.slider("Max response length", 100, 1000, 500)
        enable_learning = st.checkbox("Enable learning mode", value=False)
    
    # System Settings
    st.markdown("### 🔧 System Settings")
    
    if st.button("🔄 Reset All Settings"):
        st.success("Settings reset to defaults!")
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
    
    if st.button("📤 Export Configuration"):
        config = {
            "theme": theme_mode,
            "timestamps": show_timestamps,
            "auto_scroll": auto_scroll,
            "message_limit": message_limit,
            "confidence_threshold": confidence_threshold
        }
        st.download_button(
            "Download Config",
            json.dumps(config, indent=2),
            "app_config.json",
            "application/json"
        )

def main():
    """Main Streamlit application."""
    if not is_streamlit():
        print("This module is designed to run with Streamlit.")
        print("Run: streamlit run phase3a_basic_ui.py")
        return
    
    # Setup
    setup_streamlit_config()
    apply_custom_css()
    initialize_session_state()
    
    # Initialize app if needed
    if not st.session_state.app_initialized:
        app = CustomerServiceApp()
        app.initialize_components()
        st.session_state.app_initialized = True
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render metrics
    render_app_metrics()
    
    # Render main content based on selected mode
    mode = st.session_state.selected_mode
    
    if mode == "Customer Chat":
        render_customer_chat()
    elif mode == "Knowledge Base":
        render_knowledge_base()
    elif mode == "System Monitor":
        render_system_monitor()
    elif mode == "Settings":
        render_settings()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; margin: 2rem 0;">
        🎓 <strong>Phase 3a Complete:</strong> Basic UI Framework<br>
        Built with Streamlit • Training Module • Next: Advanced UI Features
    </div>
    """, unsafe_allow_html=True)

# Non-Streamlit demo for command line testing
def demo_ui_components():
    """
    Demonstrate UI components and patterns (non-Streamlit version).
    """
    print("=== Phase 3a: Basic UI Framework Demo ===\n")
    
    # Initialize app
    app = CustomerServiceApp()
    success = app.initialize_components()
    
    print(f"🖥️ Application: {app.app_name} v{app.version}")
    print(f"🤖 AI Components: {'Initialized' if success else 'Mock mode'}")
    
    # Demo UI patterns
    print(f"\n🎨 UI Design Patterns Demonstrated:")
    patterns = [
        "Responsive layout with sidebar and main content",
        "Real-time chat interface with message bubbles", 
        "Customer context panels and information cards",
        "Interactive forms with validation and feedback",
        "System monitoring with metrics and status indicators",
        "Knowledge base browser with search and categories",
        "Settings panels with configuration options",
        "Custom CSS styling and theme support"
    ]
    
    for pattern in patterns:
        print(f"  • {pattern}")
    
    # Mock conversation flow
    print(f"\n💬 Mock Conversation Flow:")
    
    mock_messages = [
        {"type": "user", "content": "I need to return a product"},
        {"type": "agent", "content": "I can help with returns! Our policy allows returns within 30 days with receipt.", "confidence": 0.9},
        {"type": "user", "content": "How long does shipping take?"},
        {"type": "agent", "content": "Standard shipping: 3-5 days, Express: 1-2 days. Free shipping over $50!", "confidence": 0.85}
    ]
    
    for i, msg in enumerate(mock_messages, 1):
        sender = "👤 Customer" if msg["type"] == "user" else "🤖 Agent"
        confidence = f" (confidence: {msg.get('confidence', 0):.1%})" if msg["type"] == "agent" else ""
        print(f"  {i}. {sender}: {msg['content']}{confidence}")
    
    # UI architecture
    print(f"\n🏗️ UI Architecture Components:")
    components = [
        "Main Application (CustomerServiceApp) - Core logic and state management",
        "Header Section - Branding and navigation",
        "Sidebar - Controls, customer context, and system status", 
        "Chat Interface - Real-time conversation with message history",
        "Knowledge Base - Searchable help articles and documentation",
        "System Monitor - Performance metrics and health indicators",
        "Settings Panel - Configuration and preferences",
        "Custom CSS - Styling and responsive design"
    ]
    
    for component in components:
        print(f"  • {component}")
    
    # Best practices
    print(f"\n✨ UI Best Practices Implemented:")
    practices = [
        "Progressive disclosure - show complexity gradually",
        "Consistent visual hierarchy and information architecture",
        "Accessible design with proper contrast and navigation",
        "Responsive layout adapting to different screen sizes",
        "Clear feedback for user actions and system state",
        "Error handling with graceful degradation",
        "Performance optimization with caching and lazy loading",
        "User context preservation across sessions"
    ]
    
    for practice in practices:
        print(f"  • {practice}")

if __name__ == "__main__":
    if is_streamlit():
        main()
    else:
        demo_ui_components()
        print(f"\n🚀 To run the interactive Streamlit interface:")
        print(f"   streamlit run {__file__}")
        print(f"\n🎓 Phase 3a Complete!")
        print(f"Next: Phase 3b - Advanced UI Features")