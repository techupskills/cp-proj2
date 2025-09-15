#!/usr/bin/env python3
"""
MCP-Enabled Customer Support Agent
Uses MCP protocol to communicate with tools server
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP not installed. Install with: pip install mcp")
    sys.exit(1)

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-agent")

class MCPCustomerSupportAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.ollama_url = ollama_base_url
        self.model = model
        self.session = None
        self.exit_stack = None
        self.mcp_calls_log = []
        
    async def start_mcp_server(self):
        """Start the MCP server process using the correct API pattern"""
        try:
            # Initialize AsyncExitStack for proper resource management
            self.exit_stack = AsyncExitStack()
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=sys.executable,
                args=["mcp_server.py"],
                env=None
            )
            
            # Use AsyncExitStack to manage the stdio_client context
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport
            
            # Create and initialize the client session  
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize the connection
            await self.session.initialize()
            
            logger.info("MCP server started and client connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            logger.exception("Full traceback:")
            return False
    
    def log_mcp_call(self, tool_name: str, args: Dict[str, Any], result: Any, duration: float):
        """Log MCP tool calls for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": args,
            "result": result,
            "duration_ms": round(duration * 1000, 2),
            "success": "error" not in str(result).lower()
        }
        self.mcp_calls_log.append(log_entry)
        
        # Keep only last 20 calls
        if len(self.mcp_calls_log) > 20:
            self.mcp_calls_log = self.mcp_calls_log[-20:]
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool and log the interaction"""
        if not self.session:
            raise Exception("MCP session not initialized")
        
        start_time = datetime.now()
        try:
            result = await self.session.call_tool(tool_name, arguments)
            duration = (datetime.now() - start_time).total_seconds()
            
            # Extract content from MCP response
            if hasattr(result, 'content') and result.content:
                content = result.content[0].text if result.content else "No content"
                try:
                    parsed_result = json.loads(content)
                except json.JSONDecodeError:
                    parsed_result = content
            else:
                # For direct data returns (like search_knowledge_base)
                parsed_result = result
            
            self.log_mcp_call(tool_name, arguments, parsed_result, duration)
            return parsed_result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_result = {"error": str(e)}
            self.log_mcp_call(tool_name, arguments, error_result, duration)
            logger.error(f"MCP tool call failed: {tool_name} - {e}")
            return error_result
    
    async def search_knowledge_base(self, query: str, max_results: int = 3):
        """Search knowledge base via MCP"""
        return await self.call_mcp_tool("search_knowledge_base", {
            "query": query,
            "max_results": max_results
        })
    
    async def lookup_customer(self, email: str):
        """Look up customer via MCP"""
        return await self.call_mcp_tool("lookup_customer", {
            "email": email
        })
    
    async def create_ticket(self, customer_email: str, issue_type: str, description: str):
        """Create support ticket via MCP"""
        return await self.call_mcp_tool("create_support_ticket", {
            "customer_email": customer_email,
            "issue_type": issue_type,
            "description": description,
            "priority": "medium"
        })
    
    async def get_server_stats(self):
        """Get MCP server statistics"""
        return await self.call_mcp_tool("get_server_stats", {})
    
    def _query_ollama(self, prompt):
        """Query local Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return f'{{"response": "I apologize, but I\'m experiencing technical difficulties with the AI model. Error: {str(e)}", "action_needed": "create_ticket", "confidence": 0}}'
    
    async def process_customer_inquiry(self, customer_email: str, inquiry: str, conversation_history: List[Dict] = None):
        """Process customer inquiry using MCP tools"""
        try:
            # Step 1: Look up customer via MCP
            customer_info = await self.lookup_customer(customer_email)
            
            # Step 2: Search knowledge base via MCP
            relevant_docs = await self.search_knowledge_base(inquiry)
            
            # Step 3: Prepare context for LLM - handle string responses gracefully
            if isinstance(customer_info, dict) and 'name' in customer_info:
                customer_context = f"Customer: {customer_info['name']} ({customer_info.get('tier', 'Unknown')} tier)"
            elif customer_info:
                customer_context = f"Customer: {str(customer_info)}"
            else:
                customer_context = "Customer: Not found in database"
            
            if isinstance(relevant_docs, list) and len(relevant_docs) > 0:
                knowledge_context = "\n".join([
                    f"- [{doc.get('category', 'unknown')}] {doc.get('content', str(doc))}" 
                    for doc in relevant_docs
                    if isinstance(doc, dict)
                ])
            elif relevant_docs:
                knowledge_context = f"Knowledge search returned: {str(relevant_docs)}"
            else:
                knowledge_context = "No specific company policy documents found for this query."
            
            # Step 4: Prepare conversation context
            conversation_context = ""
            if conversation_history:
                # Build conversation context from recent messages
                recent_messages = conversation_history[-6:]  # Last 6 messages for context
                for msg in recent_messages:
                    if msg['sender'] == 'customer':
                        conversation_context += f"Customer: {msg['content']}\n"
                    else:
                        conversation_context += f"Agent: {msg['content']}\n"
                conversation_context = f"\nCONVERSATION HISTORY:\n{conversation_context}"
            
            # Step 5: Query LLM
            prompt = f"""
            You are a helpful customer support AI agent. Use the provided information to assist the customer.
            Respond ONLY with valid JSON.
            
            CUSTOMER INFORMATION:
            {customer_context}
            
            RELEVANT COMPANY POLICIES & INFORMATION:
            {knowledge_context}
            {conversation_context}
            
            CUSTOMER INQUIRY: {inquiry}
            
            Instructions:
            1. Be helpful, friendly, and professional
            2. Use the provided company information to answer accurately
            3. MAINTAIN CONVERSATION CONTEXT - remember what the customer previously asked about
            4. If you need to create a ticket or escalate, explain why
            5. Personalize response based on customer tier if applicable
            
            Respond with JSON containing exactly these fields:
            - "response": your helpful response to the customer
            - "action_needed": either "none", "create_ticket", or "escalate"
            - "confidence": number between 0 and 1 indicating your confidence
            
            JSON Response:
            """
            
            ai_response = self._query_ollama(prompt)
            try:
                result = json.loads(ai_response)
            except json.JSONDecodeError:
                # If AI didn't return valid JSON, create a fallback response
                result = {
                    "response": ai_response,
                    "action_needed": "none",
                    "confidence": 0.5
                }
            
            # Store the actual prompt that was sent to LLM for debugging/analysis
            result['llm_prompt'] = prompt
            
            # Step 5: Create ticket if needed via MCP
            if result.get('action_needed') == 'create_ticket':
                ticket = await self.create_ticket(customer_email, 'General Inquiry', inquiry)
                result['ticket_created'] = ticket
            
            # Add metadata including detailed document information
            result['processed_at'] = datetime.now().isoformat()
            result['customer_tier'] = customer_info.get('tier', 'Unknown') if isinstance(customer_info, dict) else 'Unknown'
            result['knowledge_sources'] = len(relevant_docs) if isinstance(relevant_docs, list) else 0
            result['knowledge_categories'] = [
                doc.get('category', 'unknown') for doc in relevant_docs 
                if isinstance(doc, dict)
            ] if isinstance(relevant_docs, list) else []
            result['mcp_calls_made'] = len(self.mcp_calls_log)
            
            # Include detailed document information for UI display
            result['retrieved_documents'] = relevant_docs if isinstance(relevant_docs, list) else []
            result['search_query'] = inquiry
            result['document_retrieval_summary'] = {
                'total_retrieved': len(relevant_docs) if isinstance(relevant_docs, list) else 0,
                'categories_found': list(set([doc.get('category', 'unknown') for doc in relevant_docs if isinstance(doc, dict)])) if isinstance(relevant_docs, list) else [],
                'avg_similarity': round(sum([doc.get('similarity', 0) for doc in relevant_docs if isinstance(doc, dict)]) / len(relevant_docs), 3) if isinstance(relevant_docs, list) and len(relevant_docs) > 0 else 0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            logger.exception("Full traceback:")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Let me create a ticket for you.",
                "action_needed": "create_ticket",
                "confidence": 0,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Clean up MCP resources"""
        try:
            if self.exit_stack:
                await self.exit_stack.aclose()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Synchronous wrapper for Streamlit compatibility
class CustomerSupportAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.agent = MCPCustomerSupportAgent(ollama_base_url, model)
        self.loop = None
        self._initialize_async()
    
    def _initialize_async(self):
        """Initialize the async MCP agent"""
        try:
            # Try to get existing event loop, create new one if needed
            try:
                self.loop = asyncio.get_event_loop()
                if self.loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                # No event loop exists or it's closed, create a new one
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            # Start MCP server
            success = self.loop.run_until_complete(self.agent.start_mcp_server())
            if not success:
                raise Exception("Failed to start MCP server")
                
        except Exception as e:
            logger.error(f"Failed to initialize MCP agent: {e}")
            raise
    
    def search_knowledge_base(self, query: str, max_results: int = 3):
        """Synchronous wrapper for knowledge base search"""
        if not self.loop:
            return []
        try:
            return self.loop.run_until_complete(
                self.agent.search_knowledge_base(query, max_results)
            )
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            return []
    
    def lookup_customer(self, email: str):
        """Synchronous wrapper for customer lookup"""
        if not self.loop:
            return None
        try:
            return self.loop.run_until_complete(
                self.agent.lookup_customer(email)
            )
        except Exception as e:
            logger.error(f"Customer lookup error: {e}")
            return None
    
    def process_customer_inquiry(self, customer_email: str, inquiry: str, conversation_history: List[Dict] = None):
        """Synchronous wrapper for inquiry processing"""
        if not self.loop:
            return {"response": "MCP system not initialized", "confidence": 0}
        try:
            return self.loop.run_until_complete(
                self.agent.process_customer_inquiry(customer_email, inquiry, conversation_history)
            )
        except Exception as e:
            logger.error(f"Inquiry processing error: {e}")
            return {"response": f"Error: {str(e)}", "confidence": 0}
    
    def get_mcp_stats(self):
        """Get MCP server and client statistics"""
        if not self.loop:
            return {"error": "MCP not initialized"}
        try:
            server_stats = self.loop.run_until_complete(self.agent.get_server_stats())
            return {
                "server_stats": server_stats,
                "client_calls": self.agent.mcp_calls_log,
                "total_client_calls": len(self.agent.mcp_calls_log)
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"error": str(e)}
    
    def get_mcp_call_log(self):
        """Get recent MCP call log"""
        return self.agent.mcp_calls_log if self.agent else []
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.loop and self.agent:
            try:
                self.loop.run_until_complete(self.agent.cleanup())
                self.loop.close()
            except:
                pass