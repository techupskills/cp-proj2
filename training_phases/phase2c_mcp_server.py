#!/usr/bin/env python3
"""
Phase 2c: MCP Server Implementation (90 min)
Day 2 - MCP Part 1: What MCP is, architecture, and server implementation

Learning Objectives:
- What MCP is and why it matters
- MCP architecture, transports, features
- Frameworks for MCP implementation
- MCP clients and servers
- Hands-on: Building an MCP server and client and using them with an agent

This module introduces the Model Context Protocol (MCP) and demonstrates
how to build production-ready servers that can be consumed by AI agents.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

# Import previous capabilities
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1c_vector_database import VectorDatabase
    from phase1d_basic_rag import BasicRAGSystem
    VECTOR_DB_AVAILABLE = True
    RAG_AVAILABLE = True
except ImportError:
    print("⚠️ Vector database or RAG not available. Some features will be limited.")
    VECTOR_DB_AVAILABLE = False
    RAG_AVAILABLE = False

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        Resource, Tool, TextContent, ImageContent, EmbeddedResource, LoggingLevel
    )
    import mcp.types as types
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP not available. Install with: pip install mcp")
    MCP_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

class CustomerServiceMCPServer:
    """
    Production-ready MCP server for customer service operations.
    Demonstrates MCP protocol implementation with real business tools.
    """
    
    def __init__(self, server_name: str = "customer-service-mcp"):
        """
        Initialize MCP server with customer service capabilities.
        
        Args:
            server_name: Name of the MCP server
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP not available. Install with: pip install mcp")
        
        self.server = Server(server_name)
        self.server_name = server_name
        
        # Business data stores
        self.customers = {}
        self.knowledge_base = None
        self.rag_system = None
        self.support_tickets = {}
        self.server_stats = {
            'requests_handled': 0,
            'tools_called': 0,
            'resources_accessed': 0,
            'start_time': datetime.now()
        }
        
        # Initialize data and tools
        self._setup_data_stores()
        self._register_tools()
        self._register_resources()
        
        logger.info(f"MCP Server '{server_name}' initialized")
    
    def _setup_data_stores(self):
        """Initialize data stores for customer service operations."""
        
        # Customer database
        self.customers = {
            "john.doe@email.com": {
                "id": "CUST001",
                "name": "John Doe",
                "email": "john.doe@email.com",
                "tier": "Premium",
                "phone": "+1-555-0123",
                "address": "123 Main St, Anytown, USA",
                "orders": [
                    {
                        "id": "ORD-001",
                        "date": "2024-11-15",
                        "product": "Wireless Headphones Pro",
                        "amount": 299.99,
                        "status": "Delivered"
                    },
                    {
                        "id": "ORD-002", 
                        "date": "2024-12-01",
                        "product": "Bluetooth Speaker",
                        "amount": 89.99,
                        "status": "Shipped"
                    }
                ],
                "support_history": [
                    {
                        "date": "2024-11-20",
                        "issue": "Setup help for headphones",
                        "status": "Resolved"
                    }
                ],
                "preferences": {
                    "communication": "email",
                    "language": "en",
                    "timezone": "EST"
                }
            },
            "sarah.smith@email.com": {
                "id": "CUST002",
                "name": "Sarah Smith",
                "email": "sarah.smith@email.com", 
                "tier": "Standard",
                "phone": "+1-555-0456",
                "address": "456 Oak Ave, Somewhere, USA",
                "orders": [
                    {
                        "id": "ORD-003",
                        "date": "2024-11-20",
                        "product": "USB-C Cable",
                        "amount": 24.99,
                        "status": "Delivered"
                    }
                ],
                "support_history": [],
                "preferences": {
                    "communication": "sms",
                    "language": "en", 
                    "timezone": "PST"
                }
            }
        }
        
        # Initialize vector database if available
        if VECTOR_DB_AVAILABLE:
            try:
                self.knowledge_base = VectorDatabase("./mcp_server_knowledge")
                self._populate_knowledge_base()
            except Exception as e:
                logger.warning(f"Failed to initialize vector database: {e}")
                self.knowledge_base = None
        
        # Initialize RAG system if available
        if RAG_AVAILABLE and self.knowledge_base:
            try:
                self.rag_system = BasicRAGSystem("./mcp_server_rag")
                # Create sample knowledge for RAG
                self._setup_rag_system()
            except Exception as e:
                logger.warning(f"Failed to initialize RAG system: {e}")
                self.rag_system = None
    
    def _populate_knowledge_base(self):
        """Populate vector database with customer service knowledge."""
        if not self.knowledge_base:
            return
        
        # Create knowledge collection
        success = self.knowledge_base.create_collection(
            "customer_service_kb",
            "Customer service knowledge base with policies and procedures"
        )
        
        if success:
            # Add knowledge documents
            knowledge_docs = [
                {
                    "id": "return_policy_001",
                    "text": "Our return policy allows customers to return items within 30 days of purchase for a full refund. Items must be in original condition with all packaging, accessories, and receipt or order confirmation. Refunds are processed within 5-7 business days to the original payment method.",
                    "metadata": {
                        "category": "returns",
                        "document_type": "policy",
                        "last_updated": "2024-01-15",
                        "authority": "customer_service"
                    }
                },
                {
                    "id": "shipping_policy_001", 
                    "text": "Standard shipping takes 3-5 business days within the US and costs $5.99. Express shipping is available in 1-2 business days for $15.99. Orders over $50 qualify for free standard shipping. International shipping takes 7-14 business days and costs $19.99.",
                    "metadata": {
                        "category": "shipping",
                        "document_type": "policy",
                        "last_updated": "2024-01-10",
                        "authority": "logistics"
                    }
                },
                {
                    "id": "warranty_info_001",
                    "text": "All products come with a 1-year manufacturer warranty covering defects in materials and workmanship. Extended warranty options are available for purchase. Warranty claims require proof of purchase and product registration.",
                    "metadata": {
                        "category": "warranty",
                        "document_type": "info",
                        "last_updated": "2024-01-05",
                        "authority": "product_team"
                    }
                },
                {
                    "id": "troubleshooting_001",
                    "text": "If your device won't turn on: 1) Check power cable connections, 2) Try a different power outlet, 3) Hold power button for 10 seconds to reset, 4) If problem persists, contact support with your order number and device model.",
                    "metadata": {
                        "category": "troubleshooting",
                        "document_type": "guide", 
                        "last_updated": "2024-01-12",
                        "authority": "technical_support"
                    }
                }
            ]
            
            self.knowledge_base.add_documents("customer_service_kb", knowledge_docs)
            logger.info(f"Populated knowledge base with {len(knowledge_docs)} documents")
    
    def _setup_rag_system(self):
        """Setup RAG system with sample knowledge."""
        if not self.rag_system:
            return
        
        # Create sample knowledge files for RAG
        sample_dir = "/tmp/mcp_server_knowledge"
        os.makedirs(sample_dir, exist_ok=True)
        
        sample_content = """
        Customer Service Policies and Procedures
        
        Return Policy:
        Items can be returned within 30 days of purchase for full refund.
        Items must be in original condition with receipt.
        Refunds processed in 5-7 business days.
        
        Shipping Information:
        Standard shipping: 3-5 business days ($5.99)
        Express shipping: 1-2 business days ($15.99)
        Free shipping on orders over $50
        
        Technical Support:
        Available 24/7 for premium customers
        Standard customers: Monday-Friday 9AM-5PM
        Contact via phone, chat, or email
        """
        
        with open(f"{sample_dir}/policies.txt", 'w') as f:
            f.write(sample_content)
        
        try:
            success = self.rag_system.setup_knowledge_base(sample_dir)
            if success:
                logger.info("RAG system setup complete")
        except Exception as e:
            logger.warning(f"RAG system setup failed: {e}")
    
    def _register_tools(self):
        """Register MCP tools for customer service operations."""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List all available MCP tools."""
            return [
                types.Tool(
                    name="lookup_customer",
                    description="Look up customer information by email address",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Customer email address"
                            },
                            "include_orders": {
                                "type": "boolean", 
                                "description": "Include order history",
                                "default": False
                            },
                            "include_support_history": {
                                "type": "boolean",
                                "description": "Include support ticket history", 
                                "default": False
                            }
                        },
                        "required": ["email"]
                    }
                ),
                
                types.Tool(
                    name="search_knowledge",
                    description="Search the customer service knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for knowledge base"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 3
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by knowledge category",
                                "enum": ["returns", "shipping", "warranty", "troubleshooting"]
                            }
                        },
                        "required": ["query"]
                    }
                ),
                
                types.Tool(
                    name="create_support_ticket",
                    description="Create a new customer support ticket",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "customer_email": {
                                "type": "string",
                                "description": "Customer email address"
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Type of support issue",
                                "enum": ["technical", "billing", "shipping", "returns", "general"]
                            },
                            "priority": {
                                "type": "string", 
                                "description": "Ticket priority level",
                                "enum": ["low", "medium", "high", "urgent"],
                                "default": "medium"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the issue"
                            },
                            "order_id": {
                                "type": "string",
                                "description": "Related order ID if applicable"
                            }
                        },
                        "required": ["customer_email", "issue_type", "description"]
                    }
                ),
                
                types.Tool(
                    name="generate_response",
                    description="Generate intelligent response using RAG system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "customer_query": {
                                "type": "string",
                                "description": "Customer question or issue"
                            },
                            "customer_context": {
                                "type": "object",
                                "description": "Customer information context"
                            },
                            "response_tone": {
                                "type": "string",
                                "description": "Tone for the response",
                                "enum": ["professional", "friendly", "empathetic", "technical"],
                                "default": "professional"
                            }
                        },
                        "required": ["customer_query"]
                    }
                ),
                
                types.Tool(
                    name="get_server_stats",
                    description="Get MCP server statistics and health information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_performance": {
                                "type": "boolean",
                                "description": "Include performance metrics",
                                "default": True
                            }
                        }
                    }
                ),
                
                types.Tool(
                    name="validate_order",
                    description="Validate order information and status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "Order ID to validate"
                            },
                            "customer_email": {
                                "type": "string",
                                "description": "Customer email for verification"
                            }
                        },
                        "required": ["order_id", "customer_email"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any] | None) -> List[types.TextContent]:
            """Handle MCP tool calls."""
            try:
                self.server_stats['tools_called'] += 1
                
                if arguments is None:
                    arguments = {}
                
                result = None
                
                if name == "lookup_customer":
                    result = await self._handle_lookup_customer(arguments)
                elif name == "search_knowledge":
                    result = await self._handle_search_knowledge(arguments)
                elif name == "create_support_ticket":
                    result = await self._handle_create_support_ticket(arguments)
                elif name == "generate_response":
                    result = await self._handle_generate_response(arguments)
                elif name == "get_server_stats":
                    result = await self._handle_get_server_stats(arguments)
                elif name == "validate_order":
                    result = await self._handle_validate_order(arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Log tool usage
                logger.info(f"MCP Tool called: {name} with args: {list(arguments.keys())}")
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Tool call error for {name}: {e}")
                error_result = {"error": str(e), "tool": name}
                return [types.TextContent(type="text", text=json.dumps(error_result))]
    
    def _register_resources(self):
        """Register MCP resources for data access."""
        
        @self.server.list_resources()
        async def list_resources() -> List[types.Resource]:
            """List available MCP resources."""
            return [
                types.Resource(
                    uri="customer://database",
                    name="Customer Database",
                    description="Access to customer information and history",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="knowledge://base",
                    name="Knowledge Base",
                    description="Customer service knowledge base and policies",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="tickets://system",
                    name="Support Ticket System", 
                    description="Support ticket creation and management",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read MCP resource content."""
            try:
                self.server_stats['resources_accessed'] += 1
                
                if uri == "customer://database":
                    return json.dumps({
                        "total_customers": len(self.customers),
                        "customer_tiers": {
                            "Premium": sum(1 for c in self.customers.values() if c["tier"] == "Premium"),
                            "Standard": sum(1 for c in self.customers.values() if c["tier"] == "Standard")
                        },
                        "total_orders": sum(len(c["orders"]) for c in self.customers.values())
                    }, indent=2)
                
                elif uri == "knowledge://base":
                    if self.knowledge_base:
                        kb_info = self.knowledge_base.get_collection_info("customer_service_kb")
                        return json.dumps(kb_info, indent=2)
                    else:
                        return json.dumps({"error": "Knowledge base not available"})
                
                elif uri == "tickets://system":
                    return json.dumps({
                        "total_tickets": len(self.support_tickets),
                        "open_tickets": sum(1 for t in self.support_tickets.values() if t["status"] == "Open"),
                        "ticket_types": {}
                    }, indent=2)
                
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
                    
            except Exception as e:
                logger.error(f"Resource read error for {uri}: {e}")
                return json.dumps({"error": str(e)})
    
    # Tool handlers
    async def _handle_lookup_customer(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer lookup requests."""
        email = args.get("email", "").lower()
        include_orders = args.get("include_orders", False)
        include_support_history = args.get("include_support_history", False)
        
        if email not in self.customers:
            return {
                "success": False,
                "error": "Customer not found",
                "email": email
            }
        
        customer = self.customers[email].copy()
        
        if not include_orders and "orders" in customer:
            customer["orders"] = f"{len(customer['orders'])} orders (use include_orders=true to see details)"
        
        if not include_support_history and "support_history" in customer:
            customer["support_history"] = f"{len(customer['support_history'])} support interactions"
        
        return {
            "success": True,
            "customer": customer,
            "lookup_time": datetime.now().isoformat()
        }
    
    async def _handle_search_knowledge(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge base search requests."""
        query = args.get("query", "")
        max_results = args.get("max_results", 3)
        category = args.get("category")
        
        if not query:
            return {"error": "Query is required"}
        
        if self.knowledge_base:
            # Use vector database search
            results = self.knowledge_base.search_similar("customer_service_kb", query, max_results)
            
            # Filter by category if specified
            if category:
                results = [r for r in results if r["metadata"].get("category") == category]
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_found": len(results),
                "search_method": "vector_similarity"
            }
        else:
            # Fallback to simple text search
            mock_results = [
                {
                    "id": "policy_001",
                    "content": "Return policy information: 30-day return window with receipt required",
                    "category": "returns",
                    "relevance": 0.85
                }
            ]
            
            return {
                "success": True,
                "query": query,
                "results": mock_results,
                "total_found": len(mock_results),
                "search_method": "mock_fallback"
            }
    
    async def _handle_create_support_ticket(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle support ticket creation."""
        customer_email = args.get("customer_email", "").lower()
        issue_type = args.get("issue_type", "general")
        priority = args.get("priority", "medium")
        description = args.get("description", "")
        order_id = args.get("order_id")
        
        if not customer_email or not description:
            return {"error": "Customer email and description are required"}
        
        # Generate ticket ID
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{len(self.support_tickets) + 1:04d}"
        
        # Create ticket
        ticket = {
            "id": ticket_id,
            "customer_email": customer_email,
            "issue_type": issue_type,
            "priority": priority,
            "description": description,
            "order_id": order_id,
            "status": "Open",
            "created_at": datetime.now().isoformat(),
            "assigned_to": None,
            "resolution": None
        }
        
        self.support_tickets[ticket_id] = ticket
        
        return {
            "success": True,
            "ticket": ticket,
            "message": f"Support ticket {ticket_id} created successfully"
        }
    
    async def _handle_generate_response(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intelligent response generation using RAG."""
        customer_query = args.get("customer_query", "")
        customer_context = args.get("customer_context", {})
        response_tone = args.get("response_tone", "professional")
        
        if not customer_query:
            return {"error": "Customer query is required"}
        
        if self.rag_system:
            try:
                # Generate RAG response
                rag_response = self.rag_system.generate_response(customer_query)
                
                return {
                    "success": True,
                    "response": rag_response.get("response", ""),
                    "confidence": rag_response.get("avg_context_similarity", 0),
                    "context_documents": rag_response.get("context_count", 0),
                    "generation_method": "rag_system",
                    "tone": response_tone
                }
            except Exception as e:
                logger.error(f"RAG generation failed: {e}")
        
        # Fallback response generation
        fallback_response = f"Thank you for your inquiry about '{customer_query}'. Our customer service team will review your request and respond promptly. For immediate assistance, please contact our support line."
        
        return {
            "success": True,
            "response": fallback_response,
            "confidence": 0.5,
            "context_documents": 0,
            "generation_method": "fallback",
            "tone": response_tone
        }
    
    async def _handle_get_server_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle server statistics requests."""
        include_performance = args.get("include_performance", True)
        
        uptime = (datetime.now() - self.server_stats['start_time']).total_seconds()
        
        stats = {
            "server_name": self.server_name,
            "uptime_seconds": uptime,
            "requests_handled": self.server_stats['requests_handled'],
            "tools_called": self.server_stats['tools_called'],
            "resources_accessed": self.server_stats['resources_accessed'],
            "total_customers": len(self.customers),
            "total_tickets": len(self.support_tickets),
            "capabilities": {
                "vector_database": self.knowledge_base is not None,
                "rag_system": self.rag_system is not None,
                "mcp_version": "1.0"
            }
        }
        
        if include_performance:
            stats["performance"] = {
                "avg_requests_per_minute": (self.server_stats['requests_handled'] / max(1, uptime)) * 60,
                "tools_per_request": self.server_stats['tools_called'] / max(1, self.server_stats['requests_handled'])
            }
        
        return stats
    
    async def _handle_validate_order(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order validation requests."""
        order_id = args.get("order_id", "")
        customer_email = args.get("customer_email", "").lower()
        
        if not order_id or not customer_email:
            return {"error": "Order ID and customer email are required"}
        
        # Find customer and order
        customer = self.customers.get(customer_email)
        if not customer:
            return {
                "success": False,
                "error": "Customer not found",
                "order_id": order_id
            }
        
        # Find order
        order = None
        for o in customer.get("orders", []):
            if o["id"] == order_id:
                order = o
                break
        
        if not order:
            return {
                "success": False,
                "error": "Order not found for this customer",
                "order_id": order_id
            }
        
        return {
            "success": True,
            "order": order,
            "customer": {
                "name": customer["name"],
                "email": customer["email"],
                "tier": customer["tier"]
            },
            "validation_time": datetime.now().isoformat()
        }

async def run_mcp_server():
    """Run the MCP server with stdio transport."""
    if not MCP_AVAILABLE:
        print("❌ MCP not available. Install with: pip install mcp")
        return
    
    try:
        # Create server instance
        server_instance = CustomerServiceMCPServer("customer-service-training")
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="customer-service-training",
                    server_version="1.0.0",
                    capabilities=server_instance.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        logger.error(f"MCP server failed: {e}")
        raise

def demo_mcp_server():
    """
    Demonstrate MCP server capabilities and protocol compliance.
    """
    print("=== Phase 2c: MCP Server Implementation Demo ===\n")
    
    if not MCP_AVAILABLE:
        print("❌ MCP not available. Install with: pip install mcp")
        print("To install: pip install mcp")
        return
    
    # Initialize server
    print("🔧 Initializing MCP Server...")
    try:
        server = CustomerServiceMCPServer("demo-server")
        print("✅ MCP Server initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        return
    
    # Show server capabilities
    print(f"\n📋 Server Information:")
    print(f"  • Server Name: {server.server_name}")
    print(f"  • Customer Database: {len(server.customers)} customers")
    print(f"  • Knowledge Base: {'Available' if server.knowledge_base else 'Not available'}")
    print(f"  • RAG System: {'Available' if server.rag_system else 'Not available'}")
    
    # Demonstrate tool registration
    print(f"\n🔧 MCP Tools Demonstration:")
    
    # Note: In a real scenario, these would be called via MCP protocol
    # Here we simulate the calls to demonstrate functionality
    
    async def simulate_tool_calls():
        """Simulate MCP tool calls for demonstration."""
        
        # Tool 1: Customer Lookup
        print("\n1️⃣ Customer Lookup Tool")
        lookup_args = {"email": "john.doe@email.com", "include_orders": True}
        lookup_result = await server._handle_lookup_customer(lookup_args)
        print(f"   Input: {lookup_args}")
        print(f"   Result: {lookup_result['success']} - Found customer: {lookup_result.get('customer', {}).get('name', 'None')}")
        
        # Tool 2: Knowledge Search
        print("\n2️⃣ Knowledge Search Tool")
        search_args = {"query": "return policy", "max_results": 2}
        search_result = await server._handle_search_knowledge(search_args)
        print(f"   Input: {search_args}")
        print(f"   Result: Found {search_result.get('total_found', 0)} relevant documents")
        
        # Tool 3: Support Ticket Creation
        print("\n3️⃣ Support Ticket Creation Tool")
        ticket_args = {
            "customer_email": "sarah.smith@email.com",
            "issue_type": "technical",
            "priority": "high",
            "description": "Device won't turn on after update"
        }
        ticket_result = await server._handle_create_support_ticket(ticket_args)
        print(f"   Input: {ticket_args['issue_type']} issue for {ticket_args['customer_email']}")
        print(f"   Result: {ticket_result.get('message', 'Failed')}")
        
        # Tool 4: Response Generation
        print("\n4️⃣ Response Generation Tool")
        response_args = {
            "customer_query": "How do I return a product?",
            "response_tone": "friendly"
        }
        response_result = await server._handle_generate_response(response_args)
        print(f"   Input: {response_args['customer_query']}")
        print(f"   Result: Generated response ({response_result.get('generation_method', 'unknown')} method)")
        print(f"   Response preview: {response_result.get('response', '')[:100]}...")
        
        # Tool 5: Server Statistics
        print("\n5️⃣ Server Statistics Tool")
        stats_result = await server._handle_get_server_stats({"include_performance": True})
        print(f"   Server Stats:")
        print(f"   • Tools Called: {stats_result.get('tools_called', 0)}")
        print(f"   • Total Customers: {stats_result.get('total_customers', 0)}")
        print(f"   • Total Tickets: {stats_result.get('total_tickets', 0)}")
        print(f"   • Capabilities: Vector DB: {stats_result.get('capabilities', {}).get('vector_database', False)}")
        
        # Tool 6: Order Validation
        print("\n6️⃣ Order Validation Tool")
        validate_args = {
            "order_id": "ORD-001",
            "customer_email": "john.doe@email.com"
        }
        validate_result = await server._handle_validate_order(validate_args)
        print(f"   Input: Validate {validate_args['order_id']} for {validate_args['customer_email']}")
        print(f"   Result: {validate_result.get('success', False)} - Order amount: ${validate_result.get('order', {}).get('amount', 0)}")
    
    # Run simulation
    try:
        asyncio.run(simulate_tool_calls())
    except Exception as e:
        print(f"❌ Tool simulation failed: {e}")
    
    # MCP Protocol Information
    print(f"\n📡 MCP Protocol Information:")
    print(f"   • Protocol: Model Context Protocol (MCP)")
    print(f"   • Transport: stdio (standard input/output)")
    print(f"   • Message Format: JSON-RPC 2.0")
    print(f"   • Capabilities: Tools, Resources, Prompts")
    print(f"   • Security: Sandboxed execution, input validation")
    
    # Resource demonstration
    print(f"\n📚 MCP Resources Available:")
    resources = [
        "customer://database - Customer information access",
        "knowledge://base - Knowledge base access",
        "tickets://system - Support ticket system access"
    ]
    for resource in resources:
        print(f"   • {resource}")
    
    # Architecture explanation
    print(f"\n🏗️ MCP Architecture Benefits:")
    benefits = [
        "Standardized protocol for AI tool integration",
        "Secure sandboxed execution environment", 
        "Stateless design for scalability",
        "Protocol-agnostic transport layer",
        "Built-in error handling and validation",
        "Resource access controls and permissions"
    ]
    for benefit in benefits:
        print(f"   • {benefit}")

def interactive_mcp_demo():
    """Interactive MCP server demonstration."""
    print("\n=== Interactive MCP Server Demo ===")
    print("Type 'quit' to exit, 'tools' to see available tools, 'stats' for server stats")
    
    if not MCP_AVAILABLE:
        print("❌ MCP not available")
        return
    
    try:
        server = CustomerServiceMCPServer("interactive-demo")
        print("✅ Interactive MCP server ready")
        
        while True:
            try:
                user_input = input("\n🔧 Enter tool name and args (e.g., 'lookup_customer john.doe@email.com'): ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'tools':
                    print("\n🔧 Available Tools:")
                    tools = ["lookup_customer", "search_knowledge", "create_support_ticket", 
                            "generate_response", "get_server_stats", "validate_order"]
                    for tool in tools:
                        print(f"   • {tool}")
                    continue
                elif user_input.lower() == 'stats':
                    async def get_stats():
                        return await server._handle_get_server_stats({"include_performance": True})
                    
                    stats = asyncio.run(get_stats())
                    print(f"\n📊 Server Stats:")
                    for key, value in stats.items():
                        if key != "performance":
                            print(f"   • {key}: {value}")
                    continue
                elif not user_input:
                    continue
                
                # Parse command
                parts = user_input.split()
                if len(parts) < 1:
                    print("❌ Please specify a tool name")
                    continue
                
                tool_name = parts[0]
                
                # Simple tool execution examples
                if tool_name == "lookup_customer" and len(parts) > 1:
                    email = parts[1]
                    async def lookup():
                        return await server._handle_lookup_customer({"email": email})
                    
                    result = asyncio.run(lookup())
                    print(f"✅ Result: {result.get('success', False)}")
                    if result.get('success'):
                        customer = result.get('customer', {})
                        print(f"   Customer: {customer.get('name')} ({customer.get('tier')} tier)")
                
                elif tool_name == "search_knowledge" and len(parts) > 1:
                    query = " ".join(parts[1:])
                    async def search():
                        return await server._handle_search_knowledge({"query": query})
                    
                    result = asyncio.run(search())
                    print(f"✅ Found {result.get('total_found', 0)} results for '{query}'")
                
                else:
                    print(f"❌ Tool '{tool_name}' not recognized or missing arguments")
                    print("Example: 'lookup_customer john.doe@email.com'")
                    print("Example: 'search_knowledge return policy'")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to start interactive demo: {e}")

if __name__ == "__main__":
    # Check if running as MCP server
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp-server":
        print("🚀 Starting MCP Server...")
        asyncio.run(run_mcp_server())
    else:
        # Run demonstration
        demo_mcp_server()
        
        # Optional interactive mode
        print("\n" + "="*60)
        choice = input("Would you like to try interactive MCP demo? (y/n): ").strip().lower()
        if choice == 'y':
            interactive_mcp_demo()
        
        print("\n🎓 Phase 2c Complete!")
        print("Next: Phase 2d - MCP Client Integration")
        print("\nTo run as actual MCP server: python phase2c_mcp_server.py --mcp-server")