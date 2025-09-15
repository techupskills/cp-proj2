#!/usr/bin/env python3
"""
MCP Server for Customer Support AI Agent
Provides tools for customer lookup, knowledge search, ticket creation via MCP protocol
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        Resource, Tool, TextContent, ImageContent, EmbeddedResource, LoggingLevel
    )
    import mcp.types as types
    from mcp.server.stdio import stdio_server
except ImportError:
    print("MCP not installed. Install with: pip install mcp")
    sys.exit(1)

import chromadb
from chromadb.config import Settings
import pypdf
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("customer-support-mcp")

class CustomerSupportMCPServer:
    def __init__(self):
        self.server = Server("customer-support-ai")
        self.knowledge_base = None
        self.customers = {}
        self.request_log = []
        self.setup_data()
        self.setup_tools()
        
    def load_pdf_documents(self):
        """Load knowledge base documents from PDF files"""
        pdf_directory = "/Users/developer/capstone/knowledge_base_pdfs"
        documents = []
        
        # Category and keywords mapping based on filename patterns
        file_mappings = {
            "policy_returns": {"category": "returns", "keywords": ["return", "refund", "exchange", "30 days", "receipt"]},
            "policy_shipping": {"category": "shipping", "keywords": ["shipping", "delivery", "express", "standard", "international", "free shipping"]},
            "policy_support": {"category": "support", "keywords": ["support hours", "phone", "chat", "24/7", "premium", "contact"]},
            "troubleshoot_power": {"category": "troubleshooting", "keywords": ["power", "won't turn on", "battery", "cable", "reset", "device", "charge"]},
            "account_password": {"category": "account", "keywords": ["password", "reset", "login", "forgot", "email", "account"]},
            "payment_methods": {"category": "payment", "keywords": ["payment", "credit card", "paypal", "apple pay", "visa", "secure"]}
        }
        
        if not os.path.exists(pdf_directory):
            logger.error(f"PDF directory not found: {pdf_directory}")
            return []
        
        for filename in os.listdir(pdf_directory):
            if filename.endswith('.pdf'):
                file_id = filename.replace('.pdf', '')
                file_path = os.path.join(pdf_directory, filename)
                
                try:
                    # Extract text from PDF
                    with open(file_path, 'rb') as file:
                        pdf_reader = pypdf.PdfReader(file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + " "
                    
                    # Clean up extracted text
                    text = re.sub(r'\s+', ' ', text.strip())
                    
                    # Get metadata from mapping
                    metadata = file_mappings.get(file_id, {"category": "general", "keywords": []})
                    
                    documents.append({
                        "id": file_id,
                        "text": text,
                        "category": metadata["category"],
                        "keywords": metadata["keywords"],
                        "source": f"PDF: {filename}"
                    })
                    
                    logger.info(f"Loaded PDF: {filename} ({len(text)} characters)")
                    
                except Exception as e:
                    logger.error(f"Failed to load PDF {filename}: {e}")
        
        return documents

    def setup_data(self):
        """Initialize knowledge base and customer data"""
        logger.info("Initializing knowledge base and customer data...")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        try:
            self.chroma_client.delete_collection("support_docs")
        except:
            pass
        self.knowledge_base = self.chroma_client.create_collection("support_docs")
        
        # Load knowledge documents from PDF files
        documents = self.load_pdf_documents()
        
        if not documents:
            logger.warning("No PDF documents found, falling back to hardcoded data")
            # Fallback to hardcoded documents if PDFs not available
            documents = [
                {
                    "id": "policy_returns",
                    "text": "Return Policy: Items can be returned within 30 days of purchase with original receipt. Products must be in original condition and packaging. Refunds processed within 5-7 business days.",
                    "category": "returns",
                    "keywords": ["return", "refund", "exchange", "30 days", "receipt"],
                    "source": "Hardcoded fallback"
                },
                {
                    "id": "policy_shipping",
                    "text": "Shipping Information: Standard shipping takes 3-5 business days within US ($5.99). Express shipping available in 1-2 days ($15.99). Free shipping on orders over $50. International shipping 7-14 days ($19.99).",
                    "category": "shipping",
                    "keywords": ["shipping", "delivery", "express", "standard", "international", "free shipping"],
                    "source": "Hardcoded fallback"
                }
            ]
        
        # Add to knowledge base
        for doc in documents:
            self.knowledge_base.add(
                documents=[doc["text"]],
                metadatas=[{"category": doc["category"], "keywords": ",".join(doc["keywords"]), "source": doc.get("source", "Unknown")}],
                ids=[doc["id"]]
            )
        
        # Customer database
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
        
        logger.info(f"Loaded {len(documents)} PDF knowledge documents and {len(self.customers)} customers")
        logger.info("MCP Server v3.0 - PDF Knowledge Base with Fixed Tool Registration")

    async def handle_search_knowledge_base(self, arguments: Dict[str, Any]):
        """Handle search_knowledge_base tool"""
        try:
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 3)
            
            results = self.knowledge_base.query(
                query_texts=[query],
                n_results=max_results
            )
            
            relevant_docs = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    metadata = results['metadatas'][0][i]
                    
                    # Calculate relevance score with improved keyword matching
                    doc_keywords = metadata.get('keywords', '').lower().split(',')
                    doc_content = doc.lower()
                    query_words = query.lower().split()
                    
                    # Check both keywords and content for matches
                    keyword_matches = sum(1 for word in query_words 
                                        if any(word in keyword.strip() for keyword in doc_keywords))
                    content_matches = sum(1 for word in query_words if word in doc_content)
                    total_matches = keyword_matches + content_matches
                    
                    if total_matches > 0 or distance < 1.5:
                        doc_id = results['ids'][0][i] if results.get('ids') else f"doc_{i}"
                        relevant_docs.append({
                            "id": doc_id,
                            "content": doc,
                            "category": metadata['category'],
                            "keywords": metadata.get('keywords', '').split(','),
                            "source": metadata.get('source', 'Unknown'),
                            "relevance_score": total_matches,
                            "distance": distance,
                            "similarity": round(1 - distance, 3),
                            "matched_keywords": [word for word in query_words 
                                               if any(word in keyword.strip() for keyword in doc_keywords)],
                            "search_query": query,
                            "retrieval_method": "semantic_search"
                        })
            
            # Sort by relevance
            relevant_docs.sort(key=lambda x: (-x['relevance_score'], x['distance']))
            result = relevant_docs[:max_results]
            
            self.log_request("search_knowledge_base", {"query": query, "max_results": max_results}, result)
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            self.log_request("search_knowledge_base", {"query": query}, f"Error: {e}")
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def handle_lookup_customer(self, arguments: Dict[str, Any]):
        """Handle lookup_customer tool"""
        try:
            email = arguments.get("email", "")
            customer = self.customers.get(email.lower())
            self.log_request("lookup_customer", {"email": email}, customer)
            return [types.TextContent(type="text", text=json.dumps(customer))]
        except Exception as e:
            logger.error(f"Customer lookup error: {e}")
            self.log_request("lookup_customer", {"email": email}, f"Error: {e}")
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def handle_create_support_ticket(self, arguments: Dict[str, Any]):
        """Handle create_support_ticket tool"""
        try:
            customer_email = arguments.get("customer_email", "")
            issue_type = arguments.get("issue_type", "general")
            description = arguments.get("description", "")
            priority = arguments.get("priority", "medium")
            
            ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email + description) % 10000:04d}"
            
            ticket = {
                "id": ticket_id,
                "customer": customer_email,
                "type": issue_type,
                "description": description,
                "priority": priority,
                "status": "Open",
                "created": datetime.now().isoformat(),
                "assigned_agent": None
            }
            
            self.log_request("create_support_ticket", 
                           {"customer_email": customer_email, "issue_type": issue_type, "priority": priority}, 
                           ticket)
            
            logger.info(f"Created support ticket {ticket_id} for {customer_email}")
            return [types.TextContent(type="text", text=json.dumps(ticket))]
            
        except Exception as e:
            logger.error(f"Ticket creation error: {e}")
            self.log_request("create_support_ticket", 
                           {"customer_email": customer_email, "issue_type": issue_type}, 
                           f"Error: {e}")
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def handle_get_server_stats(self, arguments: Dict[str, Any]):
        """Handle get_server_stats tool"""
        try:
            stats = {
                "total_requests": len(self.request_log),
                "knowledge_documents": len(self.knowledge_base.get()['documents']) if self.knowledge_base else 0,
                "customers_in_db": len(self.customers),
                "server_uptime": "Active - PDF Knowledge Base",
                "recent_requests": self.request_log[-10:],
                "tools_available": [
                    "search_knowledge_base",
                    "lookup_customer", 
                    "create_support_ticket",
                    "get_server_stats"
                ]
            }
            
            self.log_request("get_server_stats", {}, stats)
            return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
    
    def log_request(self, tool_name: str, args: Dict[str, Any], result: Any):
        """Log MCP tool requests for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": args,
            "result_type": type(result).__name__,
            "result_preview": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
        }
        self.request_log.append(log_entry)
        
        # Keep only last 50 requests
        if len(self.request_log) > 50:
            self.request_log = self.request_log[-50:]
        
        logger.info(f"MCP Tool Call: {tool_name} with args {args}")
    
    def setup_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="search_knowledge_base",
                    description="Search the company knowledge base for relevant information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"},
                            "max_results": {"type": "integer", "description": "Maximum number of results to return", "default": 3}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="lookup_customer", 
                    description="Look up customer information by email address",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Customer email address"}
                        },
                        "required": ["email"]
                    }
                ),
                types.Tool(
                    name="create_support_ticket",
                    description="Create a new support ticket",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "customer_email": {"type": "string", "description": "Customer's email address"},
                            "issue_type": {"type": "string", "description": "Type of issue"},
                            "description": {"type": "string", "description": "Description of the issue"},
                            "priority": {"type": "string", "description": "Priority level", "default": "medium"}
                        },
                        "required": ["customer_email", "issue_type", "description"]
                    }
                ),
                types.Tool(
                    name="get_server_stats",
                    description="Get MCP server statistics and recent activity",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any] | None) -> List[types.TextContent]:
            """
            Handle all MCP tool calls
            """
            try:
                if arguments is None:
                    arguments = {}
                
                if name == "search_knowledge_base":
                    return await self.handle_search_knowledge_base(arguments)
                elif name == "lookup_customer":
                    return await self.handle_lookup_customer(arguments)
                elif name == "create_support_ticket":
                    return await self.handle_create_support_ticket(arguments)
                elif name == "get_server_stats":
                    return await self.handle_get_server_stats(arguments)
                else:
                    return [types.TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
            except Exception as e:
                logger.error(f"Tool call error for {name}: {e}")
                return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point"""
    # Create server instance
    server_instance = CustomerSupportMCPServer()
    
    # Run with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="customer-support-ai",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())