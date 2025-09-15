import json
from datetime import datetime
import requests
import chromadb
from chromadb.config import Settings

class CustomerSupportAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.ollama_url = ollama_base_url
        self.model = model
        
        # Initialize vector database for RAG
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.knowledge_base = self.chroma_client.get_or_create_collection("support_docs")
        
        # Load company data
        self.load_knowledge_base()
        self.load_customer_data()
        
    def load_knowledge_base(self):
        """Load company documentation into vector database"""
        
        # Expanded company knowledge with more specific content
        documents = [
            {
                "id": "policy_returns", 
                "text": "Return Policy: Items can be returned within 30 days of purchase with original receipt. Products must be in original condition and packaging. Refunds processed within 5-7 business days. Worn or damaged items not eligible for return.",
                "category": "returns",
                "keywords": ["return", "refund", "exchange", "30 days", "receipt"]
            },
            {
                "id": "policy_shipping",
                "text": "Shipping Information: Standard shipping takes 3-5 business days within US ($5.99). Express shipping available in 1-2 days ($15.99). Free shipping on orders over $50. International shipping to most countries 7-14 days ($19.99).",
                "category": "shipping", 
                "keywords": ["shipping", "delivery", "express", "standard", "international", "free shipping"]
            },
            {
                "id": "policy_support",
                "text": "Support Hours: Technical support available Monday-Friday 9AM-6PM EST. Premium customers get 24/7 support access. Live chat during business hours. Phone support: 1-800-SUPPORT. Email: support@company.com",
                "category": "support",
                "keywords": ["support hours", "phone", "email", "chat", "24/7", "premium"]
            },
            {
                "id": "troubleshoot_power",
                "text": "Device Power Issues: If device won't turn on: 1) Check power cable securely connected 2) Try different outlet 3) Hold power button 10 seconds to reset 4) Check battery level indicator 5) Contact support if still not working.",
                "category": "troubleshooting",
                "keywords": ["power", "won't turn on", "battery", "cable", "reset", "device"]
            },
            {
                "id": "account_password",
                "text": "Password Reset: To reset password visit login page, click 'Forgot Password', enter email address, check email for reset link (may take 5-10 minutes), follow instructions. If no email received, check spam folder or contact support.",
                "category": "account",
                "keywords": ["password", "reset", "login", "forgot", "email", "account"]
            },
            {
                "id": "warranty_coverage",
                "text": "Warranty Information: All products include 1-year manufacturer warranty covering defects and malfunctions. Extended warranty available for purchase. Warranty does not cover physical damage, water damage, or normal wear. Proof of purchase required.",
                "category": "warranty",
                "keywords": ["warranty", "defects", "malfunction", "extended", "coverage", "proof purchase"]
            },
            {
                "id": "payment_methods",
                "text": "Payment Options: We accept Visa, MasterCard, American Express, Discover, PayPal, Apple Pay, Google Pay, and bank transfers. All payments processed securely. Installment plans available for orders over $200.",
                "category": "payment",
                "keywords": ["payment", "credit card", "paypal", "apple pay", "installment", "secure"]
            },
            {
                "id": "order_tracking",
                "text": "Order Tracking: Track orders using order number and email on our website. Tracking info sent via email when order ships. For order status questions, contact customer service with order number. Processing takes 1-2 business days.",
                "category": "orders",
                "keywords": ["tracking", "order status", "processing", "shipped", "order number"]
            },
            {
                "id": "product_compatibility",
                "text": "Product Compatibility: Check product specifications before purchase. Our headphones work with all Bluetooth devices. Cables compatible with USB-C, Lightning, and Micro-USB. Software requirements listed on product pages.",
                "category": "compatibility",
                "keywords": ["compatibility", "bluetooth", "usb-c", "lightning", "specifications"]
            },
            {
                "id": "bulk_orders",
                "text": "Bulk Orders: Discounts available for orders of 10+ items. Contact sales team for custom pricing. Educational discounts for schools and universities. Corporate accounts eligible for net payment terms.",
                "category": "sales",
                "keywords": ["bulk", "discount", "educational", "corporate", "wholesale", "quantity"]
            }
        ]
        
        # Clear existing collection and reload
        try:
            self.chroma_client.delete_collection("support_docs")
        except:
            pass
        self.knowledge_base = self.chroma_client.get_or_create_collection("support_docs")
        
        # Add documents to vector database
        for doc in documents:
            self.knowledge_base.add(
                documents=[doc["text"]],
                metadatas=[{"category": doc["category"], "keywords": ",".join(doc["keywords"])}],
                ids=[doc["id"]]
            )
    
    def load_customer_data(self):
        """Load customer database (simulated)"""
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
    
    def search_knowledge_base(self, query, n_results=5):
        """Improved RAG: Search company knowledge base with relevance filtering"""
        
        # Get more results initially
        results = self.knowledge_base.query(
            query_texts=[query],
            n_results=n_results
        )
        
        relevant_docs = []
        
        # Process results with relevance scoring
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results.get('distances') else 0
                metadata = results['metadatas'][0][i]
                
                # Simple keyword matching for relevance
                doc_keywords = metadata.get('keywords', '').lower().split(',')
                query_words = query.lower().split()
                
                # Count keyword matches
                keyword_matches = sum(1 for word in query_words 
                                    if any(word in keyword.strip() for keyword in doc_keywords))
                
                # Only include if there are keyword matches or very low distance
                if keyword_matches > 0 or distance < 0.5:
                    relevant_docs.append({
                        "content": doc,
                        "category": metadata['category'],
                        "relevance_score": keyword_matches,
                        "distance": distance
                    })
        
        # Sort by relevance (keyword matches first, then by distance)
        relevant_docs.sort(key=lambda x: (-x['relevance_score'], x['distance']))
        
        # Return top 3 relevant docs, or fewer if not enough relevant matches
        return relevant_docs[:3] if len(relevant_docs) >= 3 else relevant_docs
    
    def lookup_customer(self, email):
        """Tool: Customer database lookup"""
        return self.customers.get(email.lower(), None)
    
    def create_ticket(self, customer_email, issue_type, description):
        """Tool: Create support ticket"""
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email + description) % 10000:04d}"
        
        ticket = {
            "id": ticket_id,
            "customer": customer_email,
            "type": issue_type,
            "description": description,
            "status": "Open",
            "created": datetime.now().isoformat(),
            "priority": "Medium"
        }
        
        return ticket
    
    def _query_ollama(self, prompt):
        """Query local Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f'{{"response": "I apologize, but I\'m experiencing technical difficulties. Error: {str(e)}", "action_needed": "create_ticket", "confidence": 0}}'
    
    def process_customer_inquiry(self, customer_email, inquiry):
        """Main agent function that processes customer inquiries"""
        
        # Step 1: Look up customer info
        customer_info = self.lookup_customer(customer_email)
        
        # Step 2: Search knowledge base for relevant information
        relevant_docs = self.search_knowledge_base(inquiry)
        
        # Step 3: Use AI to generate response
        response = self._generate_ai_response(customer_email, customer_info, inquiry, relevant_docs)
        
        return response
    
    def _generate_ai_response(self, customer_email, customer_info, inquiry, relevant_docs):
        """Generate AI response using customer data and knowledge base"""
        
        # Prepare context for AI
        customer_context = f"Customer: {customer_info['name']} ({customer_info['tier']} tier)" if customer_info else "Customer: Not found in database"
        
        # Only include knowledge context if we have relevant docs
        if relevant_docs:
            knowledge_context = "\n".join([
                f"- [{doc['category']}] {doc['content']} (relevance: {doc['relevance_score']})" 
                for doc in relevant_docs
            ])
        else:
            knowledge_context = "No specific company policy documents found for this query."
        
        prompt = f"""
        You are a helpful customer support AI agent. Use the provided information to assist the customer.
        Respond ONLY with valid JSON.
        
        CUSTOMER INFORMATION:
        {customer_context}
        
        RELEVANT COMPANY POLICIES & INFORMATION:
        {knowledge_context}
        
        CUSTOMER INQUIRY: {inquiry}
        
        Instructions:
        1. Be helpful, friendly, and professional
        2. Use the provided company information to answer accurately
        3. If no relevant policies found, provide general helpful response and suggest contacting support
        4. If you need to create a ticket or escalate, explain why
        5. Personalize response based on customer tier if applicable
        
        Respond with JSON containing exactly these fields:
        - "response": your helpful response to the customer
        - "action_needed": either "none", "create_ticket", or "escalate"
        - "confidence": number between 0 and 1 indicating your confidence
        
        JSON Response:
        """
        
        try:
            # Query local Ollama model
            ai_response = self._query_ollama(prompt)
            
            # Parse AI response
            result = json.loads(ai_response)
            
            # Add metadata
            result['processed_at'] = datetime.now().isoformat()
            result['customer_tier'] = customer_info['tier'] if customer_info else 'Unknown'
            result['knowledge_sources'] = len(relevant_docs)
            result['knowledge_categories'] = [doc['category'] for doc in relevant_docs] if relevant_docs else []
            
            # Determine if ticket creation is needed
            if result.get('action_needed') == 'create_ticket':
                ticket = self.create_ticket(customer_email, 'General Inquiry', inquiry)
                result['ticket_created'] = ticket
            
            return result
            
        except Exception as e:
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Let me create a ticket for you and a human agent will assist you shortly.",
                "action_needed": "create_ticket",
                "confidence": 0,
                "error": str(e),
                "knowledge_sources": 0,
                "knowledge_categories": []
            }

# Test function to demonstrate improved RAG
def test_improved_rag():
    """Test the improved RAG functionality"""
    agent = CustomerSupportAgent()
    
    test_queries = [
        "How do I return an item?",
        "What are your shipping options?", 
        "My device won't turn on",
        "I forgot my password",
        "Do you accept PayPal?",
        "Can I track my order?",
        "What's your phone number?",
        "I want to buy 20 items, any discounts?"
    ]
    
    print("Testing Improved RAG System")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        docs = agent.search_knowledge_base(query)
        
        if docs:
            print(f"Found {len(docs)} relevant documents:")
            for i, doc in enumerate(docs, 1):
                print(f"  {i}. [{doc['category']}] Relevance: {doc['relevance_score']}")
        else:
            print("No relevant documents found")
        print("-" * 30)

if __name__ == "__main__":
    # Run the test
    test_improved_rag()
    
    # Also test a full inquiry
    print("\nFull Agent Test:")
    agent = CustomerSupportAgent()
    result = agent.process_customer_inquiry("john.doe@email.com", "How do I return my headphones?")
    print(json.dumps(result, indent=2))