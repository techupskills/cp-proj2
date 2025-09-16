#!/usr/bin/env python3
"""
Phase 2d: MCP Client Integration (90 min)
Day 2 - MCP Part 2: Connecting to MCP servers and leveraging public servers

Learning Objectives:
- Connecting to MCP servers
- Common patterns and pitfalls
- Security and predictions for MCP adoption
- Hands-on: How to leverage and use public MCP servers in your AI processes

This module demonstrates how to build MCP clients that can connect to servers
and integrate MCP functionality into AI agent workflows.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack

# Import previous capabilities
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase2a_simple_agent import SimpleAgent, AgentState
    from phase2c_mcp_server import CustomerServiceMCPServer
    AGENT_AVAILABLE = True
    MCP_SERVER_AVAILABLE = True
except ImportError:
    print("⚠️ Previous phases not available. Some features will be limited.")
    AGENT_AVAILABLE = False
    MCP_SERVER_AVAILABLE = False

# MCP client imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP not available. Install with: pip install mcp")
    MCP_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")

class MCPClient:
    """
    MCP client that can connect to MCP servers and integrate with AI agents.
    Demonstrates production-ready client patterns and best practices.
    """
    
    def __init__(self, client_name: str = "training-mcp-client"):
        """
        Initialize MCP client.
        
        Args:
            client_name: Name of this MCP client
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP not available. Install with: pip install mcp")
        
        self.client_name = client_name
        self.sessions = {}  # server_name -> ClientSession
        self.exit_stack = None
        self.connection_log = []
        self.tool_call_log = []
        
        logger.info(f"MCP Client '{client_name}' initialized")
    
    async def connect_to_server(self, 
                               server_name: str, 
                               command: str, 
                               args: List[str] = None,
                               env: Dict[str, str] = None) -> bool:
        """
        Connect to an MCP server using stdio transport.
        
        Args:
            server_name: Unique name for this server connection
            command: Command to start the MCP server
            args: Command line arguments for the server
            env: Environment variables for the server
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.exit_stack:
                self.exit_stack = AsyncExitStack()
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=command,
                args=args or [],
                env=env
            )
            
            # Connect to server
            logger.info(f"Connecting to MCP server: {server_name}")
            
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport
            
            # Create client session
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize connection
            await session.initialize()
            
            self.sessions[server_name] = session
            
            # Log connection
            connection_info = {
                "server_name": server_name,
                "command": command,
                "args": args,
                "connected_at": datetime.now().isoformat(),
                "status": "connected"
            }
            self.connection_log.append(connection_info)
            
            logger.info(f"Successfully connected to MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            
            # Log failed connection
            connection_info = {
                "server_name": server_name,
                "command": command,
                "error": str(e),
                "connected_at": datetime.now().isoformat(),
                "status": "failed"
            }
            self.connection_log.append(connection_info)
            
            return False
    
    async def disconnect_from_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server.
        
        Args:
            server_name: Name of server to disconnect from
            
        Returns:
            True if disconnection successful
        """
        try:
            if server_name in self.sessions:
                # Session cleanup is handled by AsyncExitStack
                del self.sessions[server_name]
                
                # Update connection log
                for conn in self.connection_log:
                    if conn["server_name"] == server_name and conn["status"] == "connected":
                        conn["status"] = "disconnected"
                        conn["disconnected_at"] = datetime.now().isoformat()
                
                logger.info(f"Disconnected from MCP server: {server_name}")
                return True
            else:
                logger.warning(f"Server {server_name} not connected")
                return False
                
        except Exception as e:
            logger.error(f"Error disconnecting from {server_name}: {e}")
            return False
    
    async def list_server_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List available tools from an MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of available tools with their schemas
        """
        if server_name not in self.sessions:
            logger.error(f"Not connected to server: {server_name}")
            return []
        
        try:
            session = self.sessions[server_name]
            tools = await session.list_tools()
            
            # Convert to dict format for easier handling
            tool_list = []
            for tool in tools.tools:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                    "server": server_name
                }
                tool_list.append(tool_info)
            
            logger.info(f"Retrieved {len(tool_list)} tools from {server_name}")
            return tool_list
            
        except Exception as e:
            logger.error(f"Failed to list tools from {server_name}: {e}")
            return []
    
    async def call_server_tool(self, 
                              server_name: str, 
                              tool_name: str, 
                              arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        if server_name not in self.sessions:
            return {"error": f"Not connected to server: {server_name}"}
        
        try:
            session = self.sessions[server_name]
            start_time = time.time()
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            
            execution_time = time.time() - start_time
            
            # Extract content from MCP response
            if hasattr(result, 'content') and result.content:
                content = result.content[0].text if result.content else "No content"
                try:
                    parsed_result = json.loads(content)
                except json.JSONDecodeError:
                    parsed_result = {"response": content}
            else:
                parsed_result = {"response": str(result)}
            
            # Log tool call
            call_log = {
                "server_name": server_name,
                "tool_name": tool_name,
                "arguments": arguments,
                "result": parsed_result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            self.tool_call_log.append(call_log)
            
            logger.info(f"Called {tool_name} on {server_name} in {execution_time:.3f}s")
            
            return {
                "success": True,
                "result": parsed_result,
                "execution_time": execution_time,
                "server": server_name
            }
            
        except Exception as e:
            # Log failed call
            call_log = {
                "server_name": server_name,
                "tool_name": tool_name,
                "arguments": arguments,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
            self.tool_call_log.append(call_log)
            
            logger.error(f"Tool call failed: {tool_name} on {server_name} - {e}")
            
            return {
                "success": False,
                "error": str(e),
                "server": server_name
            }
    
    async def list_server_resources(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List available resources from an MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of available resources
        """
        if server_name not in self.sessions:
            logger.error(f"Not connected to server: {server_name}")
            return []
        
        try:
            session = self.sessions[server_name]
            resources = await session.list_resources()
            
            # Convert to dict format
            resource_list = []
            for resource in resources.resources:
                resource_info = {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mime_type": resource.mimeType,
                    "server": server_name
                }
                resource_list.append(resource_info)
            
            logger.info(f"Retrieved {len(resource_list)} resources from {server_name}")
            return resource_list
            
        except Exception as e:
            logger.error(f"Failed to list resources from {server_name}: {e}")
            return []
    
    async def read_server_resource(self, server_name: str, uri: str) -> Dict[str, Any]:
        """
        Read a resource from an MCP server.
        
        Args:
            server_name: Name of the server
            uri: URI of the resource to read
            
        Returns:
            Resource content
        """
        if server_name not in self.sessions:
            return {"error": f"Not connected to server: {server_name}"}
        
        try:
            session = self.sessions[server_name]
            resource_content = await session.read_resource(uri)
            
            return {
                "success": True,
                "uri": uri,
                "content": resource_content.contents,
                "server": server_name
            }
            
        except Exception as e:
            logger.error(f"Failed to read resource {uri} from {server_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "uri": uri,
                "server": server_name
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all server connections."""
        active_connections = [name for name in self.sessions.keys()]
        
        return {
            "client_name": self.client_name,
            "active_connections": active_connections,
            "total_connections_attempted": len(self.connection_log),
            "successful_connections": len([c for c in self.connection_log if c["status"] == "connected"]),
            "tool_calls_made": len(self.tool_call_log),
            "successful_tool_calls": len([c for c in self.tool_call_log if c["success"]])
        }
    
    async def cleanup(self):
        """Clean up all connections and resources."""
        try:
            if self.exit_stack:
                await self.exit_stack.aclose()
            logger.info("MCP client cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

class MCPEnabledAgent(SimpleAgent):
    """
    AI Agent enhanced with MCP client capabilities.
    Can connect to and use multiple MCP servers as tools.
    """
    
    def __init__(self, 
                 agent_name: str = "MCPAgent",
                 **kwargs):
        """
        Initialize MCP-enabled agent.
        
        Args:
            agent_name: Name of the agent
        """
        super().__init__(agent_name, **kwargs)
        self.mcp_client = None
        self.available_mcp_tools = {}  # server_name -> {tool_name -> tool_info}
        
        # Register MCP management tools
        self._register_mcp_tools()
        
        logger.info(f"MCP-enabled agent '{agent_name}' initialized")
    
    async def initialize_mcp_client(self):
        """Initialize the MCP client."""
        if not MCP_AVAILABLE:
            logger.error("MCP not available")
            return False
        
        try:
            self.mcp_client = MCPClient(f"{self.agent_name}_client")
            logger.info("MCP client initialized for agent")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
    async def connect_to_mcp_server(self, server_name: str, server_command: str, server_args: List[str] = None):
        """Connect to an MCP server and register its tools."""
        if not self.mcp_client:
            await self.initialize_mcp_client()
        
        if not self.mcp_client:
            return {"error": "MCP client not available"}
        
        # Connect to server
        success = await self.mcp_client.connect_to_server(server_name, server_command, server_args)
        
        if success:
            # List available tools
            tools = await self.mcp_client.list_server_tools(server_name)
            self.available_mcp_tools[server_name] = {tool["name"]: tool for tool in tools}
            
            # Register MCP tools as agent actions
            for tool in tools:
                self._register_mcp_tool_as_action(server_name, tool)
            
            return {
                "success": True,
                "server": server_name,
                "tools_available": len(tools)
            }
        else:
            return {"error": f"Failed to connect to server: {server_name}"}
    
    def _register_mcp_tools(self):
        """Register MCP management tools."""
        
        def connect_mcp_server(server_name: str, server_command: str) -> Dict[str, Any]:
            """Connect to an MCP server."""
            async def async_connect():
                return await self.connect_to_mcp_server(server_name, server_command)
            
            # Run async function in current event loop or create new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, we need to handle this differently
                    return {"error": "Cannot connect in sync context from async environment"}
                else:
                    return loop.run_until_complete(async_connect())
            except RuntimeError:
                # No event loop exists, create one
                return asyncio.run(async_connect())
        
        def list_mcp_servers() -> Dict[str, Any]:
            """List connected MCP servers."""
            if not self.mcp_client:
                return {"servers": [], "error": "MCP client not initialized"}
            
            status = self.mcp_client.get_connection_status()
            return {
                "servers": status["active_connections"],
                "total_tools": sum(len(tools) for tools in self.available_mcp_tools.values())
            }
        
        # Register tools
        self.register_action("connect_mcp_server", "Connect to an MCP server", connect_mcp_server, ["server_name", "server_command"])
        self.register_action("list_mcp_servers", "List connected MCP servers", list_mcp_servers, [])
    
    def _register_mcp_tool_as_action(self, server_name: str, tool_info: Dict[str, Any]):
        """Register an MCP tool as an agent action."""
        tool_name = tool_info["name"]
        action_name = f"mcp_{server_name}_{tool_name}"
        
        def mcp_tool_wrapper(**kwargs) -> Dict[str, Any]:
            """Wrapper function for MCP tool calls."""
            async def async_call():
                if not self.mcp_client:
                    return {"error": "MCP client not available"}
                
                return await self.mcp_client.call_server_tool(server_name, tool_name, kwargs)
            
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    return {"error": "Cannot call MCP tool in sync context from async environment"}
                else:
                    return loop.run_until_complete(async_call())
            except RuntimeError:
                return asyncio.run(async_call())
        
        # Extract required parameters from schema
        schema = tool_info.get("input_schema", {})
        required_params = schema.get("required", [])
        
        description = f"[MCP:{server_name}] {tool_info['description']}"
        
        self.register_action(action_name, description, mcp_tool_wrapper, required_params)
        
        logger.info(f"Registered MCP tool as action: {action_name}")
    
    async def cleanup(self):
        """Clean up MCP client connections."""
        if self.mcp_client:
            await self.mcp_client.cleanup()

def start_local_mcp_server() -> subprocess.Popen:
    """Start a local MCP server for testing."""
    try:
        # Get the path to our MCP server
        server_script = os.path.join(os.path.dirname(__file__), "phase2c_mcp_server.py")
        
        # Start server process
        process = subprocess.Popen(
            [sys.executable, server_script, "--mcp-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give server time to start
        time.sleep(2)
        
        logger.info("Local MCP server started")
        return process
        
    except Exception as e:
        logger.error(f"Failed to start local MCP server: {e}")
        return None

async def demo_mcp_client():
    """
    Demonstrate MCP client capabilities and integration patterns.
    """
    print("=== Phase 2d: MCP Client Integration Demo ===\n")
    
    if not MCP_AVAILABLE:
        print("❌ MCP not available. Install with: pip install mcp")
        return
    
    # Initialize MCP client
    print("🔧 Initializing MCP Client...")
    client = MCPClient("demo-client")
    
    print("✅ MCP Client initialized")
    
    # Connect to local MCP server
    print("\n🌐 Connecting to Local MCP Server...")
    
    # For demo purposes, we'll simulate server connection
    # In real usage, you'd connect to actual running servers
    
    try:
        # Start local server (if available)
        server_process = None
        if MCP_SERVER_AVAILABLE:
            print("🚀 Starting local MCP server...")
            server_process = start_local_mcp_server()
            
            if server_process and server_process.poll() is None:
                print("✅ Local MCP server started")
                
                # Connect to the server
                server_script = os.path.join(os.path.dirname(__file__), "phase2c_mcp_server.py")
                success = await client.connect_to_server(
                    "local-customer-service",
                    sys.executable,
                    [server_script, "--mcp-server"]
                )
                
                if success:
                    print("✅ Connected to local MCP server")
                    
                    # List available tools
                    print("\n🔧 Available Tools:")
                    tools = await client.list_server_tools("local-customer-service")
                    for tool in tools[:5]:  # Show first 5 tools
                        print(f"  • {tool['name']}: {tool['description']}")
                    
                    if len(tools) > 5:
                        print(f"  ... and {len(tools) - 5} more tools")
                    
                    # Demonstrate tool calls
                    print("\n🎯 Tool Call Demonstrations:")
                    
                    # Tool call 1: Customer lookup
                    print("\n1️⃣ Customer Lookup")
                    lookup_result = await client.call_server_tool(
                        "local-customer-service",
                        "lookup_customer",
                        {"email": "john.doe@email.com", "include_orders": True}
                    )
                    
                    if lookup_result["success"]:
                        customer = lookup_result["result"].get("customer", {})
                        print(f"   ✅ Found customer: {customer.get('name', 'Unknown')} ({customer.get('tier', 'Unknown')} tier)")
                        print(f"   📦 Orders: {len(customer.get('orders', []))}")
                    else:
                        print(f"   ❌ Lookup failed: {lookup_result.get('error')}")
                    
                    # Tool call 2: Knowledge search
                    print("\n2️⃣ Knowledge Search")
                    search_result = await client.call_server_tool(
                        "local-customer-service",
                        "search_knowledge",
                        {"query": "return policy", "max_results": 2}
                    )
                    
                    if search_result["success"]:
                        results = search_result["result"].get("results", [])
                        print(f"   ✅ Found {len(results)} knowledge articles")
                        for result in results[:2]:
                            print(f"   📄 {result.get('id', 'unknown')}: relevance {result.get('similarity', 0):.3f}")
                    else:
                        print(f"   ❌ Search failed: {search_result.get('error')}")
                    
                    # Tool call 3: Support ticket creation
                    print("\n3️⃣ Support Ticket Creation")
                    ticket_result = await client.call_server_tool(
                        "local-customer-service",
                        "create_support_ticket",
                        {
                            "customer_email": "sarah.smith@email.com",
                            "issue_type": "technical",
                            "description": "Device not working after update",
                            "priority": "high"
                        }
                    )
                    
                    if ticket_result["success"]:
                        ticket = ticket_result["result"].get("ticket", {})
                        print(f"   ✅ Created ticket: {ticket.get('id', 'unknown')}")
                        print(f"   🎫 Status: {ticket.get('status', 'unknown')}")
                    else:
                        print(f"   ❌ Ticket creation failed: {ticket_result.get('error')}")
                    
                    # List resources
                    print("\n📚 Available Resources:")
                    resources = await client.list_server_resources("local-customer-service")
                    for resource in resources:
                        print(f"  • {resource['uri']}: {resource['name']}")
                    
                    # Read a resource
                    if resources:
                        print(f"\n📖 Reading Resource Example:")
                        resource_uri = resources[0]['uri']
                        resource_content = await client.read_server_resource("local-customer-service", resource_uri)
                        if resource_content["success"]:
                            print(f"   ✅ Read resource: {resource_uri}")
                            print(f"   📄 Content preview: {str(resource_content['content'])[:100]}...")
                        else:
                            print(f"   ❌ Failed to read resource: {resource_content.get('error')}")
                
                else:
                    print("❌ Failed to connect to local MCP server")
            else:
                print("❌ Failed to start local MCP server")
        else:
            print("⚠️ MCP server not available, using mock demonstrations")
            
            # Mock tool demonstrations
            print("\n🔧 Mock Tool Demonstrations:")
            mock_tools = [
                {"name": "lookup_customer", "description": "Look up customer information"},
                {"name": "search_knowledge", "description": "Search knowledge base"},
                {"name": "create_support_ticket", "description": "Create support ticket"}
            ]
            
            for tool in mock_tools:
                print(f"  • {tool['name']}: {tool['description']}")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Full error:")
    
    finally:
        # Cleanup
        try:
            await client.cleanup()
            if 'server_process' in locals() and server_process:
                server_process.terminate()
                server_process.wait(timeout=5)
        except:
            pass
    
    # MCP Integration Patterns
    print("\n🏗️ MCP Integration Patterns:")
    patterns = [
        "Server Discovery: Automatic discovery and connection to MCP servers",
        "Tool Aggregation: Combining tools from multiple servers into unified interface",
        "Error Handling: Graceful handling of server failures and reconnection",
        "Security: Authentication, authorization, and sandboxed execution",
        "Performance: Connection pooling, caching, and async operations",
        "Monitoring: Logging, metrics, and health checks for MCP connections"
    ]
    
    for pattern in patterns:
        print(f"  • {pattern}")
    
    # Client connection status
    print(f"\n📊 Client Statistics:")
    status = client.get_connection_status()
    for key, value in status.items():
        print(f"  • {key}: {value}")

async def demo_mcp_enabled_agent():
    """
    Demonstrate MCP-enabled AI agent.
    """
    print("\n" + "="*60)
    print("🤖 MCP-Enabled Agent Demonstration")
    
    if not AGENT_AVAILABLE or not MCP_AVAILABLE:
        print("❌ Required components not available")
        return
    
    # Initialize MCP-enabled agent
    print("\n🔧 Initializing MCP-Enabled Agent...")
    agent = MCPEnabledAgent("MCPDemoAgent")
    
    await agent.initialize_mcp_client()
    print("✅ MCP-enabled agent ready")
    
    # Show agent capabilities
    print(f"\n🎯 Agent Capabilities:")
    print(f"  • Basic agent tools: {len(agent.available_actions)} tools")
    print(f"  • MCP client integration: Available")
    print(f"  • Multi-server support: Available")
    
    # Agent workflow demonstration
    print(f"\n🔄 Agent Workflow with MCP Integration:")
    
    # Create a task that would use MCP tools
    task_id = "mcp_demo_task"
    goal = "Help customer with return policy question using MCP server"
    situation = "Customer asks: 'What is your return policy for electronics?'"
    
    agent.create_task_memory(task_id, goal)
    
    print(f"Goal: {goal}")
    print(f"Situation: {situation}")
    
    # In a real scenario, the agent would:
    # 1. Connect to MCP server
    # 2. Use MCP tools to search knowledge base
    # 3. Generate response based on retrieved information
    
    print("\n📋 Simulated Agent Steps:")
    steps = [
        "1. Analyze customer query for intent and topic",
        "2. Connect to customer service MCP server",
        "3. Use search_knowledge tool to find return policy",
        "4. Use generate_response tool to create customer reply",
        "5. Validate response quality and accuracy"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    # Show MCP integration benefits
    print(f"\n🌟 MCP Integration Benefits:")
    benefits = [
        "Standardized tool access across different systems",
        "Secure and sandboxed execution environment",
        "Protocol-agnostic communication",
        "Scalable architecture for enterprise deployment",
        "Centralized tool discovery and management",
        "Built-in error handling and recovery"
    ]
    
    for benefit in benefits:
        print(f"  • {benefit}")
    
    # Cleanup
    await agent.cleanup()

async def interactive_mcp_client():
    """Interactive MCP client for experimentation."""
    print("\n=== Interactive MCP Client ===")
    print("Commands: 'connect <server_name> <command>', 'list', 'call <server> <tool> <args>', 'quit'")
    
    if not MCP_AVAILABLE:
        print("❌ MCP not available")
        return
    
    client = MCPClient("interactive-client")
    
    try:
        while True:
            try:
                user_input = input("\n🔧 MCP> ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'list':
                    status = client.get_connection_status()
                    print(f"Active connections: {status['active_connections']}")
                    print(f"Total tool calls: {status['tool_calls_made']}")
                    continue
                elif user_input.startswith('connect '):
                    parts = user_input.split()
                    if len(parts) >= 3:
                        server_name = parts[1]
                        command = parts[2]
                        args = parts[3:] if len(parts) > 3 else []
                        
                        success = await client.connect_to_server(server_name, command, args)
                        if success:
                            print(f"✅ Connected to {server_name}")
                            tools = await client.list_server_tools(server_name)
                            print(f"Available tools: {[t['name'] for t in tools]}")
                        else:
                            print(f"❌ Failed to connect to {server_name}")
                    else:
                        print("Usage: connect <server_name> <command> [args...]")
                    continue
                elif user_input.startswith('call '):
                    parts = user_input.split(' ', 3)
                    if len(parts) >= 3:
                        server_name = parts[1]
                        tool_name = parts[2]
                        
                        # Parse arguments (simple JSON format expected)
                        try:
                            args = json.loads(parts[3]) if len(parts) > 3 else {}
                        except:
                            args = {}
                        
                        result = await client.call_server_tool(server_name, tool_name, args)
                        print(f"Result: {result}")
                    else:
                        print("Usage: call <server> <tool> <json_args>")
                    continue
                elif not user_input:
                    continue
                else:
                    print("Unknown command. Use 'connect', 'list', 'call', or 'quit'")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    finally:
        await client.cleanup()

if __name__ == "__main__":
    async def main():
        # Run MCP client demonstration
        await demo_mcp_client()
        
        # Run MCP-enabled agent demonstration
        await demo_mcp_enabled_agent()
        
        # Optional interactive mode
        print("\n" + "="*60)
        choice = input("Would you like to try interactive MCP client? (y/n): ").strip().lower()
        if choice == 'y':
            await interactive_mcp_client()
        
        print("\n🎓 Phase 2d Complete!")
        print("🎉 Day 2 Complete: AI Agents & Model Context Protocol")
        print("Next: Day 3 - AI for Productivity & Capstone Project")
    
    # Run the demo
    asyncio.run(main())