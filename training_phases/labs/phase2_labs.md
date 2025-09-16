# Phase 2 Labs: AI Agents & MCP Protocol

> **Duration:** Each lab 10-12 minutes | **Total:** ~45 minutes  
> **Focus:** Hands-on agent development and MCP implementation

---

## Lab 2A: Simple Agent Logic (11 minutes)

### **Objective**
Build an intelligent agent that uses tools and maintains conversation memory.

### **Steps**

1. **Initialize Agent Framework** (2 min)
   ```bash
   cd /path/to/capstone/training_phases
   python phase2a_simple_agent.py
   ```

2. **Create Tool-Enabled Agent** (3 min)
   - Select option 1: "Create Simple Agent"
   - Name your agent "CustomerServiceAgent"
   - Watch the tool registration process

3. **Test Agent Reasoning** (4 min)
   - Select option 2: "Interactive Agent Chat"
   - Try these scenarios:
     ```
     "I need to check if customer john.doe@email.com has any recent orders"
     "What tools do you have available?"
     "Can you help me calculate a 15% discount on a $200 order?"
     "Remember that this customer prefers email communication"
     ```

4. **Examine Agent Memory** (2 min)
   - Ask: "What do you remember about our conversation?"
   - Note how the agent recalls previous context
   - Test memory persistence across multiple interactions

**Expected Output:** Agent successfully uses tools and maintains conversation context

**Key Learning:** Agents combine reasoning, tool usage, and memory for complex problem solving

---

## Lab 2B: Multi-Agent Coordination (12 minutes)

### **Objective**
Implement coordinated agents with RAG capabilities and workflow management.

### **Steps**

1. **Setup Multi-Agent System** (3 min)
   ```bash
   python phase2b_multi_agent.py
   ```

2. **Initialize Agent Roles** (2 min)
   - Select option 1: "Initialize Multi-Agent System"
   - Create these specialized agents:
     - CustomerServiceAgent (handles inquiries)
     - KnowledgeAgent (RAG-enhanced for documentation)
     - WorkflowAgent (coordinates tasks)

3. **Test Agent Coordination** (4 min)
   - Select option 2: "Multi-Agent Workflow"
   - Present this scenario:
     ```
     "Customer Sarah wants to return a damaged laptop she bought 2 weeks ago. 
     She's a Premium member and wants to know the fastest way to get a replacement."
     ```
   - Watch agents coordinate: knowledge lookup → policy check → workflow execution

4. **RAG-Enhanced Agent Testing** (3 min)
   - Select option 3: "Test RAG Agent"
   - Ask complex questions requiring document research:
     ```
     "What's the difference between standard and premium support?"
     "How do shipping costs work for international orders?"
     "What are the requirements for warranty claims?"
     ```

**Expected Output:** Agents working together, with RAG agent providing accurate policy information

**Key Learning:** Specialized agents can coordinate to handle complex, multi-step processes

---

## Lab 2C: MCP Server Implementation (10 minutes)

### **Objective**
Build a production-ready MCP server exposing customer service tools and resources.

### **Steps**

1. **Start MCP Server** (2 min)
   ```bash
   python phase2c_mcp_server.py --mcp-server
   ```
   *Keep this terminal open - server will run in background*

2. **Verify Server Status** (1 min)
   ```bash
   # In a new terminal window
   python phase2c_mcp_server.py --test-connection
   ```

3. **Explore Available Tools** (3 min)
   ```bash
   # Test server capabilities
   python phase2c_mcp_server.py --list-tools
   ```
   - Note available tools: customer_lookup, knowledge_search, order_status, etc.
   - Check resource endpoints: policies, shipping info, support contacts

4. **Test MCP Tools** (4 min)
   ```bash
   # Test individual tools
   python phase2c_mcp_server.py --test-tools
   ```
   - Try customer lookup: `john.doe@email.com`
   - Test knowledge search: `"return policy"`
   - Verify order status: `"ORD-12345"`

**Expected Output:** MCP server running on stdio transport with functional tools and resources

**Key Learning:** MCP standardizes AI tool communication across different systems

---

## Lab 2D: MCP Client Integration (12 minutes)

### **Objective**
Create an MCP client that connects to servers and integrates with agent workflows.

### **Steps**

1. **Initialize MCP Client** (2 min)
   ```bash
   # Ensure MCP server from Lab 2C is still running
   python phase2d_mcp_client.py
   ```

2. **Connect to MCP Server** (3 min)
   - Select option 1: "Initialize MCP Client"
   - Configure connection to local server (stdio transport)
   - Verify successful handshake and tool discovery

3. **Test Agent-MCP Integration** (4 min)
   - Select option 2: "Create MCP-Enabled Agent"
   - Name: "AdvancedCustomerAgent"
   - Test with scenarios:
     ```
     "Look up customer sarah.smith@email.com and check their order history"
     "Find information about our shipping policies for international customers"
     "What's the status of order ORD-67890?"
     ```

4. **Multi-Server Connection** (3 min)
   - Select option 3: "Multi-Server Setup"
   - Configure connections to multiple MCP servers
   - Test cross-server tool usage and resource access

**Expected Output:** Agent seamlessly using MCP tools from external servers for enhanced capabilities

**Key Learning:** MCP enables agents to access distributed tools and services transparently

---

## Phase 2 Integration Challenge (10 minutes)

### **Objective**
Combine all Phase 2 concepts in a real customer service scenario.

### **Scenario**
A Premium customer contacts support about a complex issue:
- They received a damaged product
- Want to exchange for a different model
- Need expedited shipping
- Have specific accessibility requirements

### **Steps**

1. **Deploy Full System** (3 min)
   - Ensure MCP server is running
   - Start multi-agent coordinator
   - Initialize MCP-enabled agents

2. **Process Customer Request** (5 min)
   - Present the full scenario to your agent system
   - Watch the coordination:
     - Customer lookup (MCP tool)
     - Policy research (RAG agent)
     - Exchange workflow (coordination agent)
     - Shipping options (MCP resource)

3. **Validate Solution** (2 min)
   - Verify all customer requirements addressed
   - Check that proper policies were cited
   - Confirm workflow steps are appropriate

**Expected Output:** Complete end-to-end customer service resolution using all Phase 2 technologies

---

## Phase 2 Summary & Validation

### **Architecture Diagram**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Simple Agent  │    │  Multi-Agent    │    │   MCP Client    │
│                 │    │  Coordinator    │    │                 │
│ • Memory        │────│ • RAG Agent     │────│ • Tool Access   │
│ • Tools         │    │ • Workflow      │    │ • Multi-Server  │
│ • Reasoning     │    │ • Coordination  │    │ • Standards     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MCP Server    │
                    │                 │
                    │ • Tools Export  │
                    │ • Resources     │
                    │ • Protocol      │
                    └─────────────────┘
```

### **Checkpoint Questions**
1. **What's the difference between a simple agent and a multi-agent system?**
2. **How does MCP enable agent interoperability?**
3. **When would you use agent coordination vs. single agent workflows?**
4. **What are the security considerations for MCP deployments?**

### **Success Criteria**
- ✅ Agent maintains conversation memory and uses tools effectively
- ✅ Multi-agent system coordinates complex workflows
- ✅ MCP server exposes functional tools and resources
- ✅ MCP client integrates seamlessly with agent workflows

### **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| Agent doesn't use tools | Check tool registration and descriptions |
| MCP connection fails | Verify server is running and transport config |
| Agents don't coordinate | Review message routing and workflow logic |
| Memory not persisting | Check session state management |

---

## Code Snippets for Quick Reference

### Create Simple Agent
```python
from phase2a_simple_agent import SimpleAgent

agent = SimpleAgent("CustomerAgent")
agent.add_tool("customer_lookup", lambda email: f"Customer data for {email}")
response = agent.process_request("Look up john@email.com")
```

### Multi-Agent Workflow
```python
from phase2b_multi_agent import MultiAgentCoordinator

coordinator = MultiAgentCoordinator()
coordinator.add_agent("customer", CustomerServiceAgent())
coordinator.add_agent("knowledge", RAGEnhancedAgent())

result = coordinator.process_workflow("customer_return_request", context)
```

### MCP Server Setup
```python
from phase2c_mcp_server import CustomerServiceMCPServer

server = CustomerServiceMCPServer()
server.add_tool("customer_lookup", customer_lookup_handler)
server.start()  # Runs on stdio transport
```

### MCP Client Usage
```python
from phase2d_mcp_client import MCPEnabledAgent

agent = MCPEnabledAgent()
agent.connect_to_server("stdio://./mcp_server.py")
result = agent.use_tool("customer_lookup", {"email": "test@email.com"})
```