#!/usr/bin/env python3
"""
HuggingFace Spaces Optimized Customer Service Platform
Simplified version designed for cloud deployment with minimal dependencies
"""

import streamlit as st
import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import random

# Configure for HuggingFace Spaces
st.set_page_config(
    page_title="AI Customer Service Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Disable warnings for cleaner demo
import warnings
warnings.filterwarnings("ignore")

class HuggingFaceCustomerService:
    """
    Customer service application optimized for HuggingFace Spaces.
    Uses simulated AI responses and mock data for demonstration.
    """
    
    def __init__(self):
        self.app_name = "AI Customer Service Platform"
        self.version = "HF-Spaces-1.0"
        self.mock_data = self._initialize_mock_data()
        self.conversation_history = []
        self.analytics_data = self._generate_analytics_data()
    
    def _initialize_mock_data(self):
        """Initialize mock data for demonstration."""
        return {
            "customers": {
                "john.doe@email.com": {
                    "name": "John Doe",
                    "tier": "Premium", 
                    "orders": 3,
                    "last_contact": "2024-12-15",
                    "satisfaction": 4.8,
                    "total_spent": 1250.00
                },
                "sarah.smith@email.com": {
                    "name": "Sarah Smith",
                    "tier": "Standard",
                    "orders": 1,
                    "last_contact": "2024-12-10", 
                    "satisfaction": 4.2,
                    "total_spent": 89.99
                },
                "mike.johnson@email.com": {
                    "name": "Mike Johnson",
                    "tier": "Premium",
                    "orders": 7,
                    "last_contact": "2024-12-12",
                    "satisfaction": 4.9,
                    "total_spent": 2100.00
                }
            },
            "knowledge": [
                {
                    "id": "return_policy",
                    "category": "Returns",
                    "title": "Return Policy",
                    "content": "Items can be returned within 30 days of purchase with original receipt for full refund. Items must be in original condition and packaging.",
                    "tags": ["returns", "refund", "policy"]
                },
                {
                    "id": "shipping_info",
                    "category": "Shipping",
                    "title": "Shipping Information",
                    "content": "Standard shipping takes 3-5 business days ($5.99). Express shipping available in 1-2 days ($15.99). Free shipping on orders over $50.",
                    "tags": ["shipping", "delivery", "timing"]
                },
                {
                    "id": "account_help",
                    "category": "Account",
                    "title": "Account Management",
                    "content": "Reset your password by clicking 'Forgot Password' on the login page. Check your email for reset instructions within 5-10 minutes.",
                    "tags": ["password", "login", "account"]
                },
                {
                    "id": "product_warranty",
                    "category": "Products",
                    "title": "Product Warranty",
                    "content": "All products come with a 1-year manufacturer warranty. Extended warranties available for purchase. Contact support for warranty claims.",
                    "tags": ["warranty", "protection", "coverage"]
                },
                {
                    "id": "payment_methods",
                    "category": "Payments",
                    "title": "Payment Methods",
                    "content": "We accept all major credit cards, PayPal, Apple Pay, and Google Pay. Payment is processed securely through our encrypted checkout.",
                    "tags": ["payment", "credit card", "paypal"]
                }
            ]
        }
    
    def _generate_analytics_data(self):
        """Generate mock analytics data."""
        dates = [datetime.now() - timedelta(days=x) for x in range(14, -1, -1)]
        return {
            "daily_conversations": [
                {"date": date.strftime("%Y-%m-%d"), "count": random.randint(45, 85)}
                for date in dates
            ],
            "category_breakdown": {
                "Returns": 35,
                "Shipping": 25, 
                "Account": 20,
                "Product Info": 15,
                "Technical": 5
            },
            "satisfaction_scores": [4.2, 4.5, 4.3, 4.7, 4.6, 4.8, 4.4],
            "response_times": [2.1, 1.8, 2.3, 1.9, 2.0, 1.7, 2.2]
        }

def main():
    """Main HuggingFace Spaces application."""
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #3b82f6, #1e40af);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            border-left: 4px solid #3b82f6;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Customer Service Platform</h1>
        <p>Intelligent customer support powered by AI • HuggingFace Spaces Demo</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize application
    if 'app' not in st.session_state:
        st.session_state.app = HuggingFaceCustomerService()
    
    app = st.session_state.app
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        view_mode = st.selectbox(
            "Select View",
            ["Customer Chat", "Agent Dashboard", "Knowledge Base", "Analytics", "About"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Customers", len(app.mock_data["customers"]))
            st.metric("Articles", len(app.mock_data["knowledge"]))
        with col2:
            st.metric("Conversations", random.randint(1200, 1300))
            st.metric("Satisfaction", "4.6/5.0")
            
        # Demo Controls
        st.markdown("---")
        st.markdown("### 🎮 Demo Controls")
        
        if st.button("🔄 Reset Chat"):
            if 'messages' in st.session_state:
                st.session_state.messages = []
            st.rerun()
            
        if st.button("📈 Refresh Stats"):
            app.analytics_data = app._generate_analytics_data()
            st.rerun()
    
    # Main content based on view mode
    if view_mode == "Customer Chat":
        render_customer_chat(app)
    elif view_mode == "Agent Dashboard":
        render_agent_dashboard(app)
    elif view_mode == "Knowledge Base":
        render_knowledge_base(app)
    elif view_mode == "Analytics":
        render_analytics(app)
    else:
        render_about()

def render_customer_chat(app):
    """Render customer chat interface."""
    st.subheader("💬 Customer Support Chat")
    
    # Customer selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        customer_email = st.selectbox(
            "Select Customer Profile",
            ["New Customer"] + list(app.mock_data["customers"].keys()),
            format_func=lambda x: x if x == "New Customer" else f"{app.mock_data['customers'][x]['name']} ({x})"
        )
    
    with col2:
        use_ai_mode = st.checkbox("🤖 AI Mode", value=True, help="Enable AI-powered responses")
    
    # Customer context
    if customer_email != "New Customer":
        customer = app.mock_data["customers"][customer_email]
        st.info(f"💼 Chatting with **{customer['name']}** • {customer['tier']} Customer • {customer['orders']} orders • ${customer['total_spent']:.2f} total")
    else:
        st.info("👋 Welcome! New customer session started.")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="padding: 2rem; text-align: center; background: #f8fafc; border-radius: 10px; margin: 1rem 0;">
                <h4>👋 How can I help you today?</h4>
                <p>Try asking about:</p>
                <ul style="list-style: none; padding: 0;">
                    <li>🔄 "I need to return a product"</li>
                    <li>🚚 "How long does shipping take?"</li>
                    <li>🔑 "I forgot my password"</li>
                    <li>💳 "What payment methods do you accept?"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "metadata" in message:
                    with st.expander("📊 Response Details"):
                        st.json(message["metadata"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate AI response
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI is thinking..."):
                response_data = generate_ai_response(prompt, app.mock_data, customer_email if customer_email != "New Customer" else None, use_ai_mode)
                st.markdown(response_data["content"])
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_data["content"],
            "metadata": response_data["metadata"]
        })
        
        st.rerun()

def render_agent_dashboard(app):
    """Render agent dashboard with system overview."""
    st.subheader("🎯 Agent Dashboard")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Chats", "12", "+3")
    with col2:
        st.metric("Avg Response Time", "2.1s", "-0.3s")
    with col3:
        st.metric("Resolution Rate", "89%", "+2%")
    with col4:
        st.metric("Customer Satisfaction", "4.6/5", "+0.1")
    
    st.markdown("---")
    
    # Recent conversations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📞 Recent Conversations")
        
        recent_chats = [
            {"customer": "John Doe", "topic": "Product return", "status": "Resolved", "time": "2 min ago"},
            {"customer": "Sarah Smith", "topic": "Shipping inquiry", "status": "Active", "time": "5 min ago"},
            {"customer": "Mike Johnson", "topic": "Account issue", "status": "Pending", "time": "8 min ago"},
            {"customer": "Emma Wilson", "topic": "Payment question", "status": "Resolved", "time": "12 min ago"}
        ]
        
        for chat in recent_chats:
            status_color = {"Resolved": "🟢", "Active": "🟡", "Pending": "🟠"}[chat["status"]]
            st.markdown(f"""
            <div style="padding: 1rem; margin: 0.5rem 0; background: white; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <strong>{chat['customer']}</strong> • {chat['topic']}<br>
                <small>{status_color} {chat['status']} • {chat['time']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📋 View All Tickets", use_container_width=True):
            st.info("Feature available in full deployment")
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Report generated successfully!")
        
        if st.button("⚙️ System Settings", use_container_width=True):
            st.info("Settings panel would open here")
        
        st.markdown("### 🔔 Alerts")
        st.warning("High volume detected - consider adding more agents")
        st.info("Knowledge base updated with new articles")

def render_knowledge_base(app):
    """Render knowledge base browser."""
    st.subheader("📚 Knowledge Base Management")
    
    # Search functionality
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search knowledge base", placeholder="Enter keywords to search...")
    
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(set(item["category"] for item in app.mock_data["knowledge"])))
    
    # Knowledge base content
    knowledge_items = app.mock_data["knowledge"]
    
    # Apply filters
    if category_filter != "All":
        knowledge_items = [item for item in knowledge_items if item["category"] == category_filter]
    
    if search_query:
        knowledge_items = [
            item for item in knowledge_items
            if search_query.lower() in item["title"].lower() or 
               search_query.lower() in item["content"].lower() or
               any(search_query.lower() in tag for tag in item["tags"])
        ]
    
    # Display results
    if knowledge_items:
        if search_query:
            st.success(f"Found {len(knowledge_items)} articles matching '{search_query}'")
        
        for item in knowledge_items:
            with st.expander(f"📄 {item['title']} ({item['category']})"):
                st.write(item["content"])
                st.markdown(f"**Tags:** {', '.join(item['tags'])}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{item['id']}"):
                        st.info("Edit functionality available in full version")
                with col2:
                    if st.button(f"📋 Copy", key=f"copy_{item['id']}"):
                        st.success("Content copied to clipboard!")
                with col3:
                    st.metric("Views", random.randint(50, 500))
    else:
        st.warning("No articles found matching your criteria.")
    
    # Add new article section
    st.markdown("---")
    with st.expander("➕ Add New Article"):
        new_title = st.text_input("Article Title")
        new_category = st.selectbox("Category", ["Returns", "Shipping", "Account", "Products", "Payments", "Technical"])
        new_content = st.text_area("Content", height=150)
        new_tags = st.text_input("Tags (comma-separated)")
        
        if st.button("Save Article"):
            if new_title and new_content:
                st.success(f"Article '{new_title}' would be saved in full version!")
            else:
                st.error("Please fill in title and content")

def render_analytics(app):
    """Render analytics dashboard."""
    st.subheader("📊 Analytics & Performance")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Conversations", "2,847", "+156 (+5.8%)")
    with col2:
        st.metric("Avg Response Time", "2.1s", "-0.3s (-12%)")
    with col3:
        st.metric("Customer Satisfaction", "4.6/5.0", "+0.1 (+2%)")
    with col4:
        st.metric("Resolution Rate", "89%", "+2% (+2.3%)")
    
    st.markdown("---")
    
    # Charts
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import pandas as pd
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Daily Conversations")
            
            df_conversations = pd.DataFrame(app.analytics_data["daily_conversations"])
            fig = px.line(df_conversations, x='date', y='count', 
                         title='Conversations Over Time',
                         line_shape='spline')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Inquiry Categories")
            
            categories = list(app.analytics_data["category_breakdown"].keys())
            values = list(app.analytics_data["category_breakdown"].values())
            
            fig = px.pie(values=values, names=categories, 
                        title='Breakdown by Category')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance trends
        st.markdown("### ⚡ Performance Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Satisfaction trend
            dates = pd.date_range(end=datetime.now(), periods=7)
            df_satisfaction = pd.DataFrame({
                'Date': dates,
                'Satisfaction': app.analytics_data["satisfaction_scores"]
            })
            
            fig = px.line(df_satisfaction, x='Date', y='Satisfaction',
                         title='Customer Satisfaction Trend',
                         range_y=[4.0, 5.0])
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Response time trend
            df_response = pd.DataFrame({
                'Date': dates,
                'Response Time': app.analytics_data["response_times"]
            })
            
            fig = px.line(df_response, x='Date', y='Response Time',
                         title='Average Response Time (seconds)',
                         line_shape='spline')
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
            
    except ImportError:
        st.error("Plotly not available. Charts would be displayed in full deployment.")
        
        # Fallback text display
        st.markdown("### 📊 Analytics Summary")
        st.json(app.analytics_data["category_breakdown"])

def render_about():
    """Render about page with detailed information."""
    st.subheader("ℹ️ About This Application")
    
    # Introduction
    st.markdown("""
    ### 🤖 AI Customer Service Platform
    
    This is a comprehensive demonstration of an intelligent customer service platform built using modern AI technologies and deployed on HuggingFace Spaces for easy access and sharing.
    
    ### ✨ Key Features Demonstrated
    
    - **🤖 Intelligent Chat Interface**: AI-powered responses with context awareness
    - **📚 Knowledge Base Integration**: Searchable help articles and policy documents  
    - **👥 Customer Context Management**: Access to customer history and preferences
    - **📊 Real-time Analytics**: Performance metrics and conversation insights
    - **🎯 Agent Dashboard**: Comprehensive management interface for support teams
    - **🔍 Semantic Search**: Find relevant information using natural language
    
    ### 🛠️ Technology Stack
    
    """)
    
    # Technology details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Frontend & Interface:**
        - Streamlit for interactive web interface
        - Custom CSS for professional styling  
        - Responsive design for all devices
        - Real-time chat interface
        
        **AI & Machine Learning:**
        - Large Language Model integration
        - RAG (Retrieval-Augmented Generation)
        - Vector search capabilities
        - Natural language processing
        """)
    
    with col2:
        st.markdown("""
        **Data & Storage:**
        - ChromaDB for vector storage
        - Structured knowledge base
        - Customer data management
        - Analytics data processing
        
        **Deployment & Hosting:**
        - HuggingFace Spaces hosting
        - Containerized deployment
        - Automatic scaling
        - Community features
        """)
    
    st.markdown("---")
    
    # Training program information
    st.markdown("""
    ### 🎓 AI Enterprise Accelerator Training Program
    
    This application was built as part of a comprehensive 3-day training program:
    
    **Day 1: Models & RAG Foundation**
    - LLM integration and prompt engineering
    - Document processing and embeddings
    - Vector database setup and management
    - RAG pipeline implementation
    
    **Day 2: AI Agents & MCP Protocol**
    - Agent architecture and reasoning
    - Multi-agent coordination
    - Model Context Protocol (MCP) implementation
    - Tool integration and workflows
    
    **Day 3: Production & Deployment**
    - UI development with Streamlit
    - Advanced analytics and monitoring
    - System integration and testing
    - Cloud deployment strategies
    """)
    
    # Deployment options
    st.markdown("---")
    st.markdown("""
    ### 🚀 Deployment Options
    
    This application can be deployed across multiple platforms:
    
    - **🤗 HuggingFace Spaces**: Current deployment (you're here!)
    - **☁️ AWS**: App Runner, ECS, Lambda
    - **🌐 Google Cloud**: Cloud Run, GKE, Compute Engine  
    - **🔷 Azure**: Container Instances, AKS, Web Apps
    - **🐳 Docker**: Local containers and orchestration
    - **☸️ Kubernetes**: Scalable container orchestration
    """)
    
    # Community features
    st.markdown("---")
    st.markdown("""
    ### 🤗 Community & Open Source
    
    This project embraces open source principles:
    
    - **⭐ Star this Space** if you find it useful
    - **🔄 Duplicate** to create your own version
    - **🐛 Report issues** in the Community tab
    - **💡 Suggest improvements** and new features
    - **🤝 Contribute** to the codebase
    
    ### 📜 License & Usage
    
    Released under MIT License - feel free to use, modify, and distribute for personal or commercial projects.
    
    ### 🔗 Links & Resources
    
    - **Source Code**: Available in the repository
    - **Documentation**: Comprehensive guides included
    - **Training Materials**: Complete curriculum provided
    - **Deployment Scripts**: Automated deployment for all major clouds
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 10px;">
        <h4>Built with ❤️ for the AI Community</h4>
        <p>Demonstrating production-ready AI applications on HuggingFace Spaces</p>
        <p><strong>AI Enterprise Accelerator Training Program</strong></p>
    </div>
    """, unsafe_allow_html=True)

def generate_ai_response(prompt: str, mock_data: Dict, customer_email: Optional[str] = None, use_ai_mode: bool = True) -> Dict[str, Any]:
    """Generate AI response with metadata."""
    
    start_time = time.time()
    prompt_lower = prompt.lower()
    
    # Customer context
    customer_context = ""
    if customer_email:
        customer = mock_data["customers"][customer_email]
        customer_context = f" I can see you're a {customer['tier']} customer with {customer['orders']} previous orders."
    
    # Simulate AI processing time
    processing_time = random.uniform(1, 3) if use_ai_mode else 0.1
    time.sleep(processing_time)
    
    # Knowledge base search simulation
    relevant_articles = []
    for article in mock_data["knowledge"]:
        if any(tag in prompt_lower for tag in article["tags"]):
            relevant_articles.append(article)
    
    # Generate response based on keywords
    if any(word in prompt_lower for word in ['return', 'refund']):
        response = f"I can help you with returns!{customer_context} Our return policy allows you to return items within 30 days of purchase with your receipt. Would you like me to start a return process for you?"
        confidence = 0.92
        category = "Returns"
        
    elif any(word in prompt_lower for word in ['shipping', 'delivery', 'ship']):
        response = f"For shipping information:{customer_context} Standard shipping takes 3-5 business days ($5.99), Express shipping takes 1-2 days ($15.99). Orders over $50 get free standard shipping!"
        confidence = 0.89
        category = "Shipping"
        
    elif any(word in prompt_lower for word in ['password', 'login', 'account', 'forgot']):
        response = f"For account issues:{customer_context} You can reset your password by clicking 'Forgot Password' on the login page. Check your email for reset instructions within 5-10 minutes."
        confidence = 0.87
        category = "Account"
        
    elif any(word in prompt_lower for word in ['payment', 'pay', 'credit card', 'paypal']):
        response = f"We accept all major credit cards, PayPal, Apple Pay, and Google Pay.{customer_context} All payments are processed securely through our encrypted checkout system."
        confidence = 0.85
        category = "Payments"
        
    elif any(word in prompt_lower for word in ['warranty', 'guarantee', 'protection']):
        response = f"All our products come with a 1-year manufacturer warranty.{customer_context} Extended warranties are available for purchase. Contact our support team for warranty claims or questions."
        confidence = 0.83
        category = "Products"
        
    elif any(word in prompt_lower for word in ['hello', 'hi', 'help', 'support']):
        response = f"Hello! Welcome to our customer service.{customer_context} I'm here to help with any questions about orders, returns, shipping, account issues, or product information. What can I assist you with today?"
        confidence = 0.95
        category = "General"
        
    else:
        response = f"Thank you for your question about '{prompt}'.{customer_context} I'm here to help with information about our products, orders, returns, shipping, and account management. Could you please provide more details about what you need assistance with?"
        confidence = 0.65
        category = "General"
    
    response_time = time.time() - start_time
    
    # Build metadata
    metadata = {
        "response_time_seconds": round(response_time, 2),
        "confidence_score": confidence,
        "category": category,
        "ai_mode": use_ai_mode,
        "relevant_articles_found": len(relevant_articles),
        "customer_context_used": customer_email is not None,
        "timestamp": datetime.now().isoformat()
    }
    
    if relevant_articles:
        metadata["relevant_articles"] = [article["id"] for article in relevant_articles[:2]]
    
    return {
        "content": response,
        "metadata": metadata
    }

if __name__ == "__main__":
    main()