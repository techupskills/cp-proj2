#!/usr/bin/env python3
"""
Direct Customer Support Agent
Uses direct knowledge service instead of MCP for better reliability
"""

import json
import logging
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional

from knowledge_service import get_knowledge_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("direct-agent")

class DirectCustomerSupportAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.ollama_url = ollama_base_url
        self.model = model
        self.knowledge_service = get_knowledge_service()
        self.call_log = []
        
    def log_call(self, operation: str, args: Dict[str, Any], result: Any, duration: float):
        """Log operations for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": operation,
            "arguments": args,
            "result": result,
            "duration_ms": round(duration * 1000, 2),
            "success": "error" not in str(result).lower()
        }
        self.call_log.append(log_entry)
        
        # Keep only last 20 calls
        if len(self.call_log) > 20:
            self.call_log = self.call_log[-20:]
    
    def search_knowledge_base(self, query: str, max_results: int = 3):
        """Search knowledge base"""
        start_time = datetime.now()
        try:
            result = self.knowledge_service.search_knowledge_base(query, max_results)
            duration = (datetime.now() - start_time).total_seconds()
            self.log_call("search_knowledge_base", {"query": query, "max_results": max_results}, result, duration)
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_result = {"error": str(e)}
            self.log_call("search_knowledge_base", {"query": query}, error_result, duration)
            return []
    
    def lookup_customer(self, email: str):
        """Look up customer"""
        start_time = datetime.now()
        try:
            result = self.knowledge_service.lookup_customer(email)
            duration = (datetime.now() - start_time).total_seconds()
            self.log_call("lookup_customer", {"email": email}, result, duration)
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_result = {"error": str(e)}
            self.log_call("lookup_customer", {"email": email}, error_result, duration)
            return None
    
    def create_ticket(self, customer_email: str, issue_type: str, description: str):
        """Create support ticket"""
        start_time = datetime.now()
        try:
            result = self.knowledge_service.create_support_ticket(customer_email, issue_type, description)
            duration = (datetime.now() - start_time).total_seconds()
            self.log_call("create_support_ticket", {"customer_email": customer_email, "issue_type": issue_type}, result, duration)
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_result = {"error": str(e)}
            self.log_call("create_support_ticket", {"customer_email": customer_email}, error_result, duration)
            return error_result
    
    def get_stats(self):
        """Get agent statistics"""
        knowledge_docs = len(self.knowledge_service.knowledge_base.get()['documents']) if self.knowledge_service.knowledge_base else 0
        
        stats = {
            "total_requests": len(self.call_log),
            "knowledge_documents": knowledge_docs,
            "customers_in_db": len(self.knowledge_service.customers),
            "server_uptime": "Active - Direct Service",
            "recent_requests": self.call_log[-10:],
            "tools_available": [
                "search_knowledge_base",
                "lookup_customer", 
                "create_support_ticket",
                "get_stats"
            ]
        }
        return stats
    
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
    
    def process_customer_inquiry(self, customer_email: str, inquiry: str, conversation_history: List[Dict] = None):
        """Process customer inquiry using direct knowledge service"""
        try:
            # Step 1: Look up customer
            customer_info = self.lookup_customer(customer_email)
            
            # Step 2: Search knowledge base
            relevant_docs = self.search_knowledge_base(inquiry)
            
            # Step 3: Prepare context for LLM
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
                recent_messages = conversation_history[-6:]
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
                result = {
                    "response": ai_response,
                    "action_needed": "none",
                    "confidence": 0.5
                }
            
            # Step 6: Create ticket if needed
            if result.get('action_needed') == 'create_ticket':
                ticket = self.create_ticket(customer_email, 'General Inquiry', inquiry)
                result['ticket_created'] = ticket
            
            # Add metadata
            result['processed_at'] = datetime.now().isoformat()
            result['customer_tier'] = customer_info.get('tier', 'Unknown') if isinstance(customer_info, dict) else 'Unknown'
            result['knowledge_sources'] = len(relevant_docs) if isinstance(relevant_docs, list) else 0
            result['knowledge_categories'] = [
                doc.get('category', 'unknown') for doc in relevant_docs 
                if isinstance(doc, dict)
            ] if isinstance(relevant_docs, list) else []
            result['processing_time_ms'] = 500  # Approximate
            
            # Include detailed document information
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
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Let me create a ticket for you.",
                "action_needed": "create_ticket",
                "confidence": 0,
                "error": str(e)
            }
    
    def get_call_log(self):
        """Get recent call log"""
        return self.call_log