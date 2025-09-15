#!/usr/bin/env python3
"""
MCP-Enabled Enterprise AI Support Platform
Shows real MCP client-server communication for training
"""

import sys
import os
import warnings
import time

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

import logging
logging.getLogger().setLevel(logging.ERROR)

# Version marker to force reload
APP_VERSION = "v2.1-with-rag-dashboard"

try:
    import streamlit as st
    import requests
    import pandas as pd
    from datetime import datetime
    import json
    from mcp_agent import CustomerSupportAgent
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install requirements: pip install streamlit requests chromadb pandas mcp")
    sys.exit(1)

# If running with python directly, start streamlit
if __name__ == "__main__" and "streamlit" not in sys.modules:
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
    sys.exit(0)

# Page config
st.set_page_config(
    page_title="MCP Enterprise AI Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display version
st.sidebar.write(f"App Version: {APP_VERSION}")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .mcp-server-panel {
        background: #0f172a;
        color: #e2e8f0;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1e293b;
    }
    
    .mcp-call {
        background: #f8fafc;
        color: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .mcp-success { 
        border-left-color: #10b981; 
        background: #f0fdf4;
    }
    .mcp-error { 
        border-left-color: #ef4444; 
        background: #fef2f2;
    }
    
    .customer-interface {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin-top: 1rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .chat-message {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .agent-message {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
    }
    
    .customer-message {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
    }
    
    .rag-document {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #0ea5e9;
    }
    
    .pipeline-step {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
        border: 1px solid #e2e8f0;
    }
    
    .rag-analysis {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
    }
    
    .status-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    
    .status-healthy { background-color: #10b981; }
    .status-warning { background-color: #f59e0b; }
    .status-error { background-color: #ef4444; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'interface_mode': "Customer View",
        'conversation_history': [],
        'current_conversation': [],
        'agent_metrics': {
            'total_queries': 0,
            'resolved_queries': 0,
            'tickets_created': 0
        },
        'mcp_logs': [],
        'customer_email': 'john.doe@email.com',
        'agent_initialized': False,
        'agent': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_resource
def initialize_agent():
    """Initialize the MCP agent (cached to prevent reinitialization)"""
    try:
        agent = CustomerSupportAgent()
        return agent
    except Exception as e:
        st.error(f"Failed to initialize MCP agent: {e}")
        return None

def render_header():
    """Render main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🔗 MCP Enterprise AI Support Platform</h1>
        <p>Real-time Model Context Protocol demonstration with RAG and local AI processing</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with controls and metrics"""
    st.sidebar.title("🎛️ Control Panel")
    
    # Interface mode selector
    st.session_state.interface_mode = st.sidebar.selectbox(
        "View Mode",
        ["Customer View", "Agent Dashboard", "MCP Protocol Monitor"],
        index=0
    )
    
    # Customer selector
    st.sidebar.subheader("👤 Customer Context")
    st.session_state.customer_email = st.sidebar.selectbox(
        "Select Customer",
        ["john.doe@email.com", "sarah.smith@email.com", "new.customer@email.com"],
        index=0
    )
    
    # Agent metrics
    st.sidebar.subheader("📊 Agent Metrics")
    metrics = st.session_state.agent_metrics
    st.sidebar.metric("Total Queries", metrics['total_queries'])
    st.sidebar.metric("Resolved Queries", metrics['resolved_queries'])
    st.sidebar.metric("Tickets Created", metrics['tickets_created'])
    
    # MCP Server Status
    st.sidebar.subheader("🔗 MCP Server Status")
    if st.session_state.agent:
        st.sidebar.success("🟢 Connected")
        if st.sidebar.button("Refresh Stats"):
            get_mcp_stats()
    else:
        st.sidebar.error("🔴 Disconnected")
        if st.sidebar.button("Reconnect"):
            st.session_state.agent = initialize_agent()
            st.rerun()
    
    # Clear conversation
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.current_conversation = []
        st.rerun()

def get_mcp_stats():
    """Get MCP server statistics"""
    if st.session_state.agent:
        try:
            stats = st.session_state.agent.get_mcp_stats()
            
            # Update the session state with fresh logs
            fresh_logs = st.session_state.agent.get_mcp_call_log()
            st.session_state.mcp_logs = fresh_logs
            
            return stats
        except Exception as e:
            st.error(f"Failed to get MCP stats: {e}")
            return None
    return None

def render_customer_view():
    """Render customer support interface"""
    st.markdown('<div class="customer-interface">', unsafe_allow_html=True)
    
    st.subheader("💬 Customer Support Chat")
    
    # Display conversation history
    for message in st.session_state.current_conversation:
        if message['sender'] == 'customer':
            st.markdown(f"""
            <div class="chat-message customer-message">
                <strong>👤 You:</strong> {message['content']}
                <small style="color: #666;">{message['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            confidence_display = f" | Confidence: {message.get('confidence', 'N/A')}" if 'confidence' in message else ""
            sources_display = f" | Sources: {message.get('knowledge_sources', 0)}" if 'knowledge_sources' in message else ""
            
            st.markdown(f"""
            <div class="chat-message agent-message">
                <strong>🤖 Support Agent:</strong> {message['content']}
                <small style="color: #666;">{message['timestamp']}{confidence_display}{sources_display}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Input form
    with st.form("customer_query_form"):
        query = st.text_area("How can we help you today?", height=100, placeholder="Example: I need to return my headphones, how do I do that?")
        submit = st.form_submit_button("Send Message", use_container_width=True)
        
        if submit and query:
            process_customer_query(query)
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_customer_query(query):
    """Process customer query through MCP agent"""
    if not st.session_state.agent:
        st.error("Agent not initialized. Please refresh the page.")
        return
    
    # Add customer message to conversation
    customer_msg = {
        'sender': 'customer',
        'content': query,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.current_conversation.append(customer_msg)
    
    # Show processing indicator
    with st.spinner("🤖 AI Agent processing your request..."):
        try:
            # Process through MCP agent
            result = st.session_state.agent.process_customer_inquiry(
                st.session_state.customer_email, 
                query
            )
            
            # Add agent response to conversation with enhanced metadata
            agent_msg = {
                'sender': 'agent',
                'content': result.get('response', 'I apologize, but I encountered an error processing your request.'),
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'confidence': result.get('confidence', 0),
                'knowledge_sources': result.get('knowledge_sources', 0),
                'knowledge_categories': result.get('knowledge_categories', []),
                'action_needed': result.get('action_needed', 'none'),
                'customer_tier': result.get('customer_tier', 'Unknown'),
                'mcp_calls_made': result.get('mcp_calls_made', 0),
                'processing_time_ms': result.get('processing_time_ms', 0),
                'rag_documents_used': result.get('knowledge_categories', [])  # Store for dashboard
            }
            st.session_state.current_conversation.append(agent_msg)
            
            # Update metrics
            st.session_state.agent_metrics['total_queries'] += 1
            if result.get('confidence', 0) > 0.7:
                st.session_state.agent_metrics['resolved_queries'] += 1
            if result.get('action_needed') == 'create_ticket':
                st.session_state.agent_metrics['tickets_created'] += 1
            
            # Show ticket creation if needed
            if 'ticket_created' in result:
                ticket_info = result['ticket_created']
                if isinstance(ticket_info, dict) and 'id' in ticket_info:
                    st.success(f"🎫 Support ticket created: {ticket_info['id']}")
                else:
                    st.success("🎫 Support ticket created successfully")
            
        except Exception as e:
            st.error(f"Error processing query: {e}")
            # Add error message to conversation
            error_msg = {
                'sender': 'agent',
                'content': 'I apologize, but I encountered a technical error. Please try again.',
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'confidence': 0,
                'knowledge_sources': 0,
                'error': str(e)
            }
            st.session_state.current_conversation.append(error_msg)
    
    st.rerun()

def render_agent_dashboard():
    """Render agent dashboard with detailed metrics and RAG information"""
    st.subheader("🤖 Agent Dashboard with RAG Analysis")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Queries</h3>
            <h2>{st.session_state.agent_metrics['total_queries']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        resolved = st.session_state.agent_metrics['resolved_queries']
        total = st.session_state.agent_metrics['total_queries']
        rate = (resolved / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Resolution Rate</h3>
            <h2>{rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Tickets Created</h3>
            <h2>{st.session_state.agent_metrics['tickets_created']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # RAG Pipeline Analysis
    st.markdown('<div class="rag-analysis">', unsafe_allow_html=True)
    st.subheader("🔍 RAG Pipeline Analysis")
    
    if st.session_state.current_conversation:
        # Get the most recent conversation entries
        agent_messages = [msg for msg in st.session_state.current_conversation if msg['sender'] == 'agent']
        
        for i, msg in enumerate(agent_messages[-3:]):  # Show last 3 agent responses
            st.markdown(f"""
            <div class="pipeline-step">
                <h4>🤖 Agent Response #{len(agent_messages) - 2 + i}</h4>
                <p><strong>Response:</strong> {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}</p>
                <p><strong>Confidence:</strong> {msg.get('confidence', 'N/A')} | <strong>Knowledge Sources Used:</strong> {msg.get('knowledge_sources', 0)}</p>
                <p><strong>Customer Tier:</strong> {msg.get('customer_tier', 'Unknown')} | <strong>Processing Time:</strong> {msg.get('processing_time_ms', 'N/A')}ms</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show RAG documents if available
            categories = msg.get('knowledge_categories', [])
            if categories:
                st.markdown("**📚 RAG Documents Retrieved:**")
                for j, category in enumerate(categories):
                    st.markdown(f"""
                    <div class="rag-document">
                        <strong>Document {j+1}:</strong> {category.title()} Policy<br>
                        <small>Retrieved from knowledge base and used for context in response generation</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("**📚 No specific knowledge documents retrieved for this query**")
    else:
        st.info("No conversations yet. Start chatting in Customer View to see RAG pipeline analysis!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent MCP Tool Calls (RAG Operations)
    st.subheader("⚙️ Recent RAG & Tool Operations")
    
    # Get fresh MCP logs
    if st.session_state.agent:
        fresh_logs = st.session_state.agent.get_mcp_call_log()
        
        if fresh_logs:
            # Show last 5 operations
            for log in fresh_logs[-5:]:
                operation_icon = {
                    'search_knowledge_base': '📚',
                    'lookup_customer': '👤', 
                    'create_support_ticket': '🎫',
                    'get_server_stats': '📊'
                }.get(log['tool'], '🔧')
                
                success_indicator = "✅" if log.get('success', False) else "❌"
                
                st.markdown(f"""
                <div class="pipeline-step">
                    <h4>{operation_icon} {log['tool'].replace('_', ' ').title()} {success_indicator}</h4>
                    <p><strong>Time:</strong> {log['timestamp'][:19]} | <strong>Duration:</strong> {log['duration_ms']}ms</p>
                    <p><strong>Arguments:</strong> {json.dumps(log['arguments'], indent=2)}</p>
                    <details>
                        <summary>View Result</summary>
                        <pre style="background: #f8fafc; padding: 0.5rem; border-radius: 4px; font-size: 0.8rem;">
{json.dumps(log['result'], indent=2) if isinstance(log['result'], dict) else str(log['result'])[:500]}
                        </pre>
                    </details>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No MCP operations logged yet.")
    
    # Prompt Engineering Analysis
    st.subheader("💭 Prompt Engineering Insights")
    
    if st.session_state.current_conversation:
        # Analyze the conversation for prompt effectiveness
        agent_messages = [msg for msg in st.session_state.current_conversation if msg['sender'] == 'agent']
        
        if agent_messages:
            avg_confidence = sum(msg.get('confidence', 0) for msg in agent_messages) / len(agent_messages)
            total_sources = sum(msg.get('knowledge_sources', 0) for msg in agent_messages)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Confidence", f"{avg_confidence:.2f}")
                st.metric("Total RAG Retrievals", total_sources)
            
            with col2:
                st.metric("Avg Sources per Query", f"{total_sources/len(agent_messages):.1f}")
                ticket_rate = sum(1 for msg in agent_messages if msg.get('action_needed') == 'create_ticket') / len(agent_messages) * 100
                st.metric("Escalation Rate", f"{ticket_rate:.1f}%")
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation History"):
        st.session_state.current_conversation = []
        st.rerun()

def render_mcp_monitor():
    """Render MCP protocol monitoring interface"""
    st.subheader("🔗 MCP Protocol Monitor")
    
    # Get fresh stats
    stats = get_mcp_stats()
    
    # Debug: Show what we actually got
    if st.checkbox("Show Debug Info"):
        st.write("Raw stats:", stats)
    
    # Check if we have valid stats
    valid_stats = (
        stats and 
        isinstance(stats, dict) and 
        'server_stats' in stats and 
        isinstance(stats['server_stats'], dict)
    )
    
    if valid_stats:
        server_stats = stats['server_stats']
        
        # Server metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total MCP Requests", server_stats.get('total_requests', 0))
        with col2:
            st.metric("Knowledge Documents", server_stats.get('knowledge_documents', 0))
        with col3:
            st.metric("Customers in DB", server_stats.get('customers_in_db', 0))
        
        # Available tools
        st.subheader("🛠️ Available MCP Tools")
        tools = server_stats.get('tools_available', [])
        for tool in tools:
            st.markdown(f"✅ `{tool}`")
    else:
        # Show error or fallback info
        st.warning("Unable to connect to MCP server")
        
        if stats:
            if isinstance(stats, str):
                st.error(f"MCP returned error: {stats}")
            elif isinstance(stats, dict) and 'error' in stats:
                st.error(f"MCP Error: {stats['error']}")
            elif isinstance(stats, dict) and 'server_stats' in stats:
                if isinstance(stats['server_stats'], str):
                    st.error(f"Server error: {stats['server_stats']}")
        
        # Show basic fallback info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("MCP Status", "Disconnected")
        with col2:
            st.metric("Agent Status", "Active" if st.session_state.agent else "Inactive")
        with col3:
            st.metric("Interface Mode", st.session_state.interface_mode)
    
    # Recent MCP calls
    st.subheader("📡 Recent MCP Calls")
    mcp_logs = st.session_state.mcp_logs
    
    if mcp_logs:
        for log in mcp_logs[-10:]:  # Show last 10 calls
            status_class = "mcp-success" if log.get('success', False) else "mcp-error"
            st.markdown(f"""
            <div class="mcp-call {status_class}">
                <strong>🔧 {log['tool']}</strong> ({log['timestamp'][:19]})<br>
                <small>Duration: {log['duration_ms']}ms</small><br>
                <small>Args: {json.dumps(log['arguments'], indent=2)}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No MCP calls logged yet. Try asking a question in Customer View!")
    
    # Auto-refresh toggle
    if st.checkbox("Auto-refresh (5s)"):
        time.sleep(5)
        st.rerun()

def main():
    """Main application logic"""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Initialize agent if not done
    if not st.session_state.agent:
        with st.spinner("🚀 Initializing MCP Agent..."):
            st.session_state.agent = initialize_agent()
            if st.session_state.agent:
                st.success("✅ MCP Agent initialized successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to initialize MCP Agent. Please check your setup.")
                st.stop()
    
    # Render appropriate interface based on mode
    if st.session_state.interface_mode == "Customer View":
        render_customer_view()
    elif st.session_state.interface_mode == "Agent Dashboard":
        render_agent_dashboard()
    elif st.session_state.interface_mode == "MCP Protocol Monitor":
        render_mcp_monitor()

if __name__ == "__main__":
    main()