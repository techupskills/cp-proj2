import streamlit as st
import requests
import json
from datetime import datetime

def check_ollama():
    """Check Ollama service health"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                "status": "healthy",
                "models": [m['name'] for m in models],
                "model_count": len(models)
            }
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_agent():
    """Check AI agent functionality"""
    try:
        from customer_support_agent import CustomerSupportAgent
        agent = CustomerSupportAgent()
        
        # Quick test
        result = agent.process_customer_inquiry(
            "test@example.com",
            "Health check test"
        )
        
        if isinstance(result, dict) and 'response' in result:
            return {"status": "healthy", "agent": "functional"}
        else:
            return {"status": "unhealthy", "agent": "non-functional"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def main():
    st.title("System Health Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ollama Service")
        ollama_health = check_ollama()
        
        if ollama_health['status'] == 'healthy':
            st.success("Ollama is running")
            st.write(f"Models: {ollama_health.get('model_count', 0)}")
        else:
            st.error("Ollama is not running")
            st.write(f"Error: {ollama_health.get('error', 'Unknown')}")
    
    with col2:
        st.subheader("AI Agent")
        agent_health = check_agent()
        
        if agent_health['status'] == 'healthy':
            st.success("AI Agent is functional")
        else:
            st.error("AI Agent has issues")
            st.write(f"Error: {agent_health.get('error', 'Unknown')}")
    
    # Overall status
    st.subheader("Overall Status")
    overall_healthy = (
        ollama_health['status'] == 'healthy' and 
        agent_health['status'] == 'healthy'
    )
    
    if overall_healthy:
        st.success("All systems operational")
    else:
        st.error("System issues detected")
    
    # System info
    st.subheader("System Information")
    st.json({
        "timestamp": datetime.now().isoformat(),
        "ollama": ollama_health,
        "agent": agent_health,
        "overall_status": "healthy" if overall_healthy else "unhealthy"
    })

if __name__ == "__main__":
    main()
