# Unused Files Archive

This directory contains files that were moved out of the main project to simplify the codebase structure. These files are kept for reference but are not actively used by the current application.

## Files Moved Here:

### **Redundant/Obsolete Implementation Files:**
- **`mcp_server_fixed.py`** - Duplicate of `mcp_server.py`, likely an old backup version
- **`customer_support_agent.py`** - Original customer support agent, replaced by `mcp_agent.py`
- **`direct_agent.py`** - Alternative agent implementation not used by main application
- **`expense_agent.py`** - Unrelated expense tracking agent, appears to be demo/test code
- **`mpc_agent_app.py`** - MCP agent app with typo in filename, not referenced anywhere

### **Testing/Demo Files:**
- **`test_setup.py`** - Basic testing utility for agent setup
- **`test_suite.py`** - Test suite for validating agent functionality
- **`sample_data.py`** - Sample data generator for demos
- **`health_check.py`** - Health check utility not integrated into main app

### **Setup/Deployment Scripts:**
- **`deployment_files.sh`** - Old deployment setup script, replaced by other deployment files
- **`setup_demos.sh`** - Demo setup script for creating sample applications
- **`training_doc.txt`** - Original training document, replaced by comprehensive training_phases/README.md

### **Log Files:**
- **`mcp_server.log`** - Runtime log file (will regenerate when server runs)

## Why These Files Were Moved:

1. **Simplify Project Structure** - Remove duplicate and unused files to make the project easier to navigate
2. **Focus on Active Components** - Keep only files that are actively used by the main application
3. **Preserve History** - Keep files as reference rather than deleting them permanently
4. **Reduce Confusion** - Prevent developers from working on outdated versions

## Current Active Files:

The main project now focuses on these core components:
- `streamlit_app.py` - Main Streamlit UI application
- `mcp_agent.py` - Core MCP-enabled customer support agent
- `mcp_server.py` - MCP server implementation
- `knowledge_service.py` - Knowledge base service
- `training_phases/` - Complete training curriculum (8 phases)
- Various deployment configs (Docker, Kubernetes, etc.)

## Restoring Files:

If any of these files are needed again, they can be moved back to the main directory:
```bash
mv unused_files/filename.py ./
```

## Date Archived:
September 16, 2025