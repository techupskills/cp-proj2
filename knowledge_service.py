#!/usr/bin/env python3
"""
Direct Knowledge Service - bypasses MCP for now
This provides the same functionality without MCP complexity
"""

import os
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
import pypdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowledge-service")

class DirectKnowledgeService:
    def __init__(self):
        self.knowledge_base = None
        self.customers = {}
        self.setup_data()
        
    def load_pdf_documents(self):
        """Load knowledge base documents from PDF files"""
        pdf_directory = "/Users/developer/capstone/knowledge_base_pdfs"
        documents = []
        
        # Category and keywords mapping
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
                    with open(file_path, 'rb') as file:
                        pdf_reader = pypdf.PdfReader(file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + " "
                    
                    text = re.sub(r'\s+', ' ', text.strip())
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
        logger.info("Initializing direct knowledge service...")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        try:
            self.chroma_client.delete_collection("support_docs")
        except:
            pass
        self.knowledge_base = self.chroma_client.create_collection("support_docs")
        
        # Load documents from PDFs
        documents = self.load_pdf_documents()
        
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
        
        logger.info(f"Loaded {len(documents)} knowledge documents and {len(self.customers)} customers")
    
    def search_knowledge_base(self, query: str, max_results: int = 3):
        """Search the knowledge base"""
        try:
            results = self.knowledge_base.query(
                query_texts=[query],
                n_results=max_results
            )
            
            relevant_docs = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    metadata = results['metadatas'][0][i]
                    
                    # Improved keyword matching
                    doc_keywords = metadata.get('keywords', '').lower().split(',')
                    doc_content = doc.lower()
                    query_words = query.lower().split()
                    
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
            return relevant_docs[:max_results]
            
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            return []
    
    def lookup_customer(self, email: str):
        """Look up customer by email"""
        try:
            return self.customers.get(email.lower())
        except Exception as e:
            logger.error(f"Customer lookup error: {e}")
            return None
    
    def create_support_ticket(self, customer_email: str, issue_type: str, description: str, priority: str = "medium"):
        """Create a support ticket"""
        try:
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
            
            logger.info(f"Created support ticket {ticket_id} for {customer_email}")
            return ticket
            
        except Exception as e:
            logger.error(f"Ticket creation error: {e}")
            return {"error": str(e)}

# Global instance
_knowledge_service = None

def get_knowledge_service():
    """Get or create the global knowledge service instance"""
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = DirectKnowledgeService()
    return _knowledge_service