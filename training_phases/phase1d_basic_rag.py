#!/usr/bin/env python3
"""
Phase 1d: Basic RAG Implementation (90 min)
Day 1 - Applying RAG: Combining retrieval and generation

Learning Objectives:
- Implementing the complete RAG pipeline
- Prompt engineering with retrieved context
- Evaluating RAG system performance
- Hands-on: building agentic RAG with curated datasets

This module combines document processing, vector search, and LLM generation
into a complete Retrieval-Augmented Generation system.
"""

import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import our previous phase modules
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1a_basic_llm import BasicLLMClient
    from phase1b_document_processing import DocumentProcessor
    from phase1c_vector_database import VectorDatabase
    LLM_AVAILABLE = True
    DOC_PROCESSING_AVAILABLE = True
    VECTOR_DB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Make sure previous phase modules are available")
    LLM_AVAILABLE = False
    DOC_PROCESSING_AVAILABLE = False
    VECTOR_DB_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("basic-rag")

class BasicRAGSystem:
    """
    Complete RAG (Retrieval-Augmented Generation) system that combines
    document retrieval with LLM generation for enhanced responses.
    """
    
    def __init__(self, 
                 vector_db_path: str = "./rag_chroma_db",
                 llm_base_url: str = "http://localhost:11434",
                 llm_model: str = "llama3.2"):
        """
        Initialize RAG system with vector database and LLM.
        
        Args:
            vector_db_path: Path for vector database storage
            llm_base_url: URL for LLM service (Ollama)
            llm_model: LLM model name
        """
        # Check dependencies
        if not all([LLM_AVAILABLE, DOC_PROCESSING_AVAILABLE, VECTOR_DB_AVAILABLE]):
            raise ImportError("Required phase modules not available")
        
        # Initialize components
        self.llm_client = BasicLLMClient(llm_base_url, llm_model)
        self.doc_processor = DocumentProcessor()
        self.vector_db = VectorDatabase(vector_db_path)
        
        # RAG configuration
        self.collection_name = "rag_documents"
        self.max_retrieved_docs = 3
        self.chunk_size = 400
        
        # Performance tracking
        self.rag_sessions = []
        self.performance_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'avg_retrieval_time': 0,
            'avg_generation_time': 0,
            'avg_relevance_score': 0
        }
    
    def setup_knowledge_base(self, documents_path: str) -> bool:
        """
        Set up the knowledge base by processing documents and storing in vector DB.
        
        Args:
            documents_path: Path to directory containing documents
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Setting up RAG knowledge base...")
            
            # Create collection
            success = self.vector_db.create_collection(
                self.collection_name,
                "RAG system knowledge base for customer support"
            )
            
            if not success:
                logger.error("Failed to create vector collection")
                return False
            
            # Process documents
            if os.path.isdir(documents_path):
                processed_docs = self.doc_processor.process_directory(documents_path, self.chunk_size)
            elif os.path.isfile(documents_path):
                doc = self.doc_processor.process_document(documents_path, self.chunk_size)
                processed_docs = [doc] if doc.get("success", False) else []
            else:
                logger.error(f"Documents path not found: {documents_path}")
                return False
            
            if not processed_docs:
                logger.error("No documents were processed successfully")
                return False
            
            # Prepare documents for vector storage
            vector_docs = []
            for doc in processed_docs:
                for chunk in doc['chunks']:
                    vector_doc = {
                        'id': f"{doc['id']}_{chunk['id']}",
                        'text': chunk['text'],
                        'metadata': {
                            'source_file': doc['file_name'],
                            'source_type': doc['source_type'],
                            'chunk_index': chunk['chunk_index'],
                            'word_count': chunk['word_count'],
                            'doc_id': doc['id'],
                            'processed_at': doc['metadata']['processed_at']
                        }
                    }
                    vector_docs.append(vector_doc)
            
            # Add to vector database
            success = self.vector_db.add_documents(self.collection_name, vector_docs)
            
            if success:
                logger.info(f"Knowledge base setup complete: {len(vector_docs)} chunks from {len(processed_docs)} documents")
                return True
            else:
                logger.error("Failed to add documents to vector database")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup knowledge base: {e}")
            return False
    
    def retrieve_relevant_context(self, query: str, max_docs: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query using vector similarity search.
        
        Args:
            query: User query
            max_docs: Maximum number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        max_docs = max_docs or self.max_retrieved_docs
        
        try:
            start_time = time.time()
            
            # Perform vector search
            results = self.vector_db.search_similar(
                self.collection_name,
                query,
                n_results=max_docs
            )
            
            retrieval_time = time.time() - start_time
            
            # Enhance results with relevance analysis
            enhanced_results = []
            for result in results:
                # Simple keyword overlap analysis
                query_words = set(query.lower().split())
                doc_words = set(result['text'].lower().split())
                keyword_overlap = len(query_words & doc_words) / len(query_words | doc_words)
                
                enhanced_result = {
                    **result,
                    'keyword_overlap': round(keyword_overlap, 3),
                    'retrieval_time': retrieval_time,
                    'query': query
                }
                enhanced_results.append(enhanced_result)
            
            logger.info(f"Retrieved {len(enhanced_results)} documents in {retrieval_time:.3f}s")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def generate_rag_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate a prompt that combines the user query with retrieved context.
        
        Args:
            query: User query
            context_docs: Retrieved context documents
            
        Returns:
            Formatted prompt for the LLM
        """
        # Format context documents
        context_text = ""
        if context_docs:
            context_text = "RELEVANT INFORMATION:\n"
            for i, doc in enumerate(context_docs, 1):
                source = doc['metadata'].get('source_file', 'Unknown')
                context_text += f"\n{i}. [Source: {source}]\n{doc['text']}\n"
        else:
            context_text = "RELEVANT INFORMATION:\nNo specific relevant information found in the knowledge base.\n"
        
        # Create comprehensive prompt
        prompt = f"""You are a helpful customer service assistant. Use the provided information to answer the customer's question accurately and helpfully.

{context_text}

CUSTOMER QUESTION: {query}

INSTRUCTIONS:
1. Answer based primarily on the provided relevant information
2. If the information doesn't fully answer the question, say so clearly
3. Be helpful, professional, and concise
4. If you need to suggest contacting support, explain why
5. Format your response in a friendly, conversational tone

RESPONSE:"""

        return prompt
    
    def generate_response(self, query: str, max_retrieved_docs: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a complete RAG response: retrieve context + generate answer.
        
        Args:
            query: User query
            max_retrieved_docs: Maximum documents to retrieve
            
        Returns:
            Complete RAG response with metadata
        """
        session_start = time.time()
        session_id = f"rag_{int(time.time())}"
        
        try:
            # Step 1: Retrieve relevant context
            retrieval_start = time.time()
            context_docs = self.retrieve_relevant_context(query, max_retrieved_docs)
            retrieval_time = time.time() - retrieval_start
            
            # Step 2: Generate prompt with context
            prompt = self.generate_rag_prompt(query, context_docs)
            
            # Step 3: Generate LLM response
            generation_start = time.time()
            llm_response = self.llm_client.generate_response(prompt, temperature=0.3)
            generation_time = time.time() - generation_start
            
            # Step 4: Analyze response quality
            total_time = time.time() - session_start
            avg_similarity = sum(doc['similarity'] for doc in context_docs) / len(context_docs) if context_docs else 0
            
            # Create comprehensive response
            rag_response = {
                'session_id': session_id,
                'query': query,
                'response': llm_response['response'],
                'context_documents': context_docs,
                'context_count': len(context_docs),
                'avg_context_similarity': round(avg_similarity, 3),
                'retrieval_time': round(retrieval_time, 3),
                'generation_time': round(generation_time, 3),
                'total_time': round(total_time, 3),
                'llm_metadata': {
                    'model': llm_response['model'],
                    'temperature': llm_response['temperature'],
                    'token_count': llm_response['token_count']
                },
                'prompt_used': prompt,
                'timestamp': datetime.now().isoformat(),
                'success': llm_response['success']
            }
            
            # Track session
            self.rag_sessions.append(rag_response)
            self._update_performance_metrics(rag_response)
            
            logger.info(f"RAG response generated: {total_time:.3f}s total")
            
            return rag_response
            
        except Exception as e:
            error_response = {
                'session_id': session_id,
                'query': query,
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'context_documents': [],
                'context_count': 0,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            
            self.rag_sessions.append(error_response)
            logger.error(f"RAG generation failed: {e}")
            
            return error_response
    
    def _update_performance_metrics(self, response: Dict[str, Any]):
        """Update performance tracking metrics."""
        self.performance_metrics['total_queries'] += 1
        
        if response.get('success', False):
            self.performance_metrics['successful_queries'] += 1
            
            # Update running averages
            total = self.performance_metrics['total_queries']
            
            self.performance_metrics['avg_retrieval_time'] = (
                (self.performance_metrics['avg_retrieval_time'] * (total - 1) + 
                 response.get('retrieval_time', 0)) / total
            )
            
            self.performance_metrics['avg_generation_time'] = (
                (self.performance_metrics['avg_generation_time'] * (total - 1) + 
                 response.get('generation_time', 0)) / total
            )
            
            self.performance_metrics['avg_relevance_score'] = (
                (self.performance_metrics['avg_relevance_score'] * (total - 1) + 
                 response.get('avg_context_similarity', 0)) / total
            )
    
    def evaluate_rag_quality(self, test_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate RAG system quality using test queries.
        
        Args:
            test_queries: List of test queries with expected categories/keywords
            
        Returns:
            Evaluation results and metrics
        """
        evaluation_results = []
        
        for test in test_queries:
            query = test['query']
            expected_category = test.get('expected_category', '')
            expected_keywords = test.get('expected_keywords', [])
            
            # Generate RAG response
            response = self.generate_response(query)
            
            # Evaluate response quality
            context_relevance = response.get('avg_context_similarity', 0)
            context_count = response.get('context_count', 0)
            
            # Check if expected keywords appear in response
            response_text = response.get('response', '').lower()
            keyword_matches = sum(1 for keyword in expected_keywords 
                                if keyword.lower() in response_text)
            keyword_score = keyword_matches / len(expected_keywords) if expected_keywords else 0
            
            # Check if context contains expected category
            category_found = any(
                expected_category.lower() in doc['metadata'].get('source_file', '').lower()
                for doc in response.get('context_documents', [])
            )
            
            eval_result = {
                'query': query,
                'expected_category': expected_category,
                'expected_keywords': expected_keywords,
                'context_relevance': context_relevance,
                'context_count': context_count,
                'keyword_score': round(keyword_score, 3),
                'category_found': category_found,
                'response_length': len(response.get('response', '')),
                'retrieval_time': response.get('retrieval_time', 0),
                'generation_time': response.get('generation_time', 0),
                'success': response.get('success', False)
            }
            
            evaluation_results.append(eval_result)
        
        # Calculate overall metrics
        successful_tests = [r for r in evaluation_results if r['success']]
        
        if successful_tests:
            overall_metrics = {
                'total_tests': len(test_queries),
                'successful_tests': len(successful_tests),
                'success_rate': len(successful_tests) / len(test_queries),
                'avg_context_relevance': sum(r['context_relevance'] for r in successful_tests) / len(successful_tests),
                'avg_keyword_score': sum(r['keyword_score'] for r in successful_tests) / len(successful_tests),
                'category_accuracy': sum(1 for r in successful_tests if r['category_found']) / len(successful_tests),
                'avg_retrieval_time': sum(r['retrieval_time'] for r in successful_tests) / len(successful_tests),
                'avg_generation_time': sum(r['generation_time'] for r in successful_tests) / len(successful_tests)
            }
        else:
            overall_metrics = {'error': 'No successful tests'}
        
        return {
            'test_results': evaluation_results,
            'overall_metrics': overall_metrics,
            'evaluation_timestamp': datetime.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.performance_metrics,
            'sessions_count': len(self.rag_sessions),
            'knowledge_base_info': self.vector_db.get_collection_info(self.collection_name)
        }
    
    def get_recent_sessions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent RAG sessions for analysis."""
        return self.rag_sessions[-count:]

def create_sample_knowledge_base():
    """Create sample documents for RAG demonstration."""
    sample_docs = [
        {
            "filename": "return_policy.txt",
            "content": """Return Policy Guidelines
            
            Customers can return items within 30 days of purchase for a full refund.
            Items must be in original condition with all packaging and accessories.
            Original receipt or order confirmation required for all returns.
            
            Return Process:
            1. Contact customer service to initiate return
            2. Receive return authorization number
            3. Package item securely with return label
            4. Drop off at any authorized location
            
            Refund Processing:
            - Refunds processed within 5-7 business days
            - Original payment method will be credited
            - Shipping costs are non-refundable except for defective items
            
            Exceptions:
            - Software downloads cannot be returned
            - Custom or personalized items are final sale
            - Items damaged by customer misuse not eligible"""
        },
        {
            "filename": "shipping_info.txt", 
            "content": """Shipping Information and Policies
            
            Shipping Options:
            - Standard Shipping: 3-5 business days ($5.99)
            - Express Shipping: 1-2 business days ($15.99)
            - Overnight Shipping: Next business day ($25.99)
            - International Shipping: 7-14 business days ($19.99)
            
            Free Shipping:
            Orders over $50 qualify for free standard shipping within the US.
            
            Processing Time:
            Orders placed before 2 PM EST ship same day.
            Orders placed after 2 PM EST ship next business day.
            
            Tracking:
            All shipments include tracking numbers sent via email.
            Track packages at our website or carrier website.
            
            International Shipping:
            Available to most countries worldwide.
            Customs fees and duties are customer responsibility.
            Delivery times may vary due to customs processing."""
        },
        {
            "filename": "account_help.txt",
            "content": """Account Management and Password Help
            
            Creating an Account:
            Visit our website and click 'Sign Up' to create a new account.
            Provide email address and create a secure password.
            Verify email address through confirmation link.
            
            Password Requirements:
            - Minimum 8 characters
            - Include uppercase and lowercase letters
            - Include at least one number
            - Include at least one special character
            
            Password Reset:
            1. Go to login page and click 'Forgot Password'
            2. Enter your email address
            3. Check email for reset link (may take 5-10 minutes)
            4. Click link and enter new password
            5. Reset link expires in 24 hours
            
            Account Security:
            - Never share your password
            - Log out when using shared computers
            - Update password regularly
            - Contact us immediately if account is compromised
            
            Profile Updates:
            Update address, phone, and preferences in Account Settings."""
        }
    ]
    
    # Create sample files
    sample_dir = "/Users/developer/capstone/training_phases/sample_knowledge"
    os.makedirs(sample_dir, exist_ok=True)
    
    for doc in sample_docs:
        file_path = os.path.join(sample_dir, doc["filename"])
        with open(file_path, 'w') as f:
            f.write(doc["content"])
    
    return sample_dir

def demo_basic_rag():
    """
    Demonstrate complete RAG system functionality.
    """
    print("=== Phase 1d: Basic RAG Implementation Demo ===\n")
    
    # Check dependencies
    if not all([LLM_AVAILABLE, DOC_PROCESSING_AVAILABLE, VECTOR_DB_AVAILABLE]):
        print("❌ Required dependencies not available. Ensure previous phases are set up.")
        return
    
    # Create sample knowledge base
    print("📁 Creating sample knowledge base...")
    knowledge_dir = create_sample_knowledge_base()
    print(f"✅ Sample documents created in: {knowledge_dir}")
    
    # Initialize RAG system
    print("\n🤖 Initializing RAG system...")
    try:
        rag = BasicRAGSystem()
        print("✅ RAG system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return
    
    # Setup knowledge base
    print("\n📚 Setting up knowledge base...")
    success = rag.setup_knowledge_base(knowledge_dir)
    if not success:
        print("❌ Failed to setup knowledge base")
        return
    
    print("✅ Knowledge base setup complete")
    
    # Show knowledge base info
    kb_info = rag.get_performance_metrics()
    print(f"  • Documents loaded: {kb_info['knowledge_base_info'].get('document_count', 0)}")
    
    # Demonstrate RAG queries
    print("\n🔍 RAG Query Demonstrations:")
    
    test_queries = [
        "How do I return a product I bought?",
        "What are the shipping options and costs?",
        "I forgot my password, how do I reset it?", 
        "Do you offer free shipping?",
        "What is your refund policy?",
        "How long does international shipping take?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: '{query}'")
        response = rag.generate_response(query)
        
        if response['success']:
            print(f"🤖 Response: {response['response'][:200]}{'...' if len(response['response']) > 200 else ''}")
            print(f"📊 Metrics: {response['context_count']} docs, {response['avg_context_similarity']:.3f} avg similarity, {response['total_time']:.2f}s")
            
            if response['context_documents']:
                print("📚 Context sources:")
                for doc in response['context_documents'][:2]:
                    source = doc['metadata']['source_file']
                    similarity = doc['similarity']
                    print(f"    • {source} (similarity: {similarity:.3f})")
        else:
            print(f"❌ Error: {response.get('error', 'Unknown error')}")
    
    # RAG evaluation
    print("\n📈 RAG System Evaluation:")
    
    evaluation_queries = [
        {
            "query": "return policy details",
            "expected_category": "return",
            "expected_keywords": ["30 days", "refund", "receipt"]
        },
        {
            "query": "shipping costs and timeframes", 
            "expected_category": "shipping",
            "expected_keywords": ["business days", "cost", "express"]
        },
        {
            "query": "password reset instructions",
            "expected_category": "account",
            "expected_keywords": ["email", "reset", "link"]
        }
    ]
    
    evaluation = rag.evaluate_rag_quality(evaluation_queries)
    
    if 'overall_metrics' in evaluation:
        metrics = evaluation['overall_metrics']
        print(f"  • Success Rate: {metrics.get('success_rate', 0):.1%}")
        print(f"  • Avg Context Relevance: {metrics.get('avg_context_relevance', 0):.3f}")
        print(f"  • Keyword Match Score: {metrics.get('avg_keyword_score', 0):.3f}")
        print(f"  • Category Accuracy: {metrics.get('category_accuracy', 0):.1%}")
        print(f"  • Avg Retrieval Time: {metrics.get('avg_retrieval_time', 0):.3f}s")
        print(f"  • Avg Generation Time: {metrics.get('avg_generation_time', 0):.3f}s")
    
    # Performance summary
    print("\n📊 Overall Performance Summary:")
    perf = rag.get_performance_metrics()
    print(f"  • Total Queries: {perf['total_queries']}")
    print(f"  • Successful Queries: {perf['successful_queries']}")
    print(f"  • Success Rate: {perf['successful_queries']/max(1, perf['total_queries']):.1%}")
    print(f"  • Avg Retrieval Time: {perf['avg_retrieval_time']:.3f}s")
    print(f"  • Avg Generation Time: {perf['avg_generation_time']:.3f}s")

def interactive_rag():
    """Interactive RAG system for experimentation."""
    print("\n=== Interactive RAG System ===")
    print("Type 'quit' to exit, 'stats' for performance metrics")
    
    try:
        # Use existing knowledge base if available
        rag = BasicRAGSystem()
        
        # Quick setup check
        kb_info = rag.vector_db.get_collection_info(rag.collection_name)
        if 'error' in kb_info:
            print("❌ Knowledge base not found. Run the main demo first.")
            return
        
        print(f"✅ Connected to knowledge base with {kb_info['document_count']} documents")
        
        while True:
            try:
                query = input("\n🔍 Enter your question: ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'stats':
                    stats = rag.get_performance_metrics()
                    print(f"\n📊 Performance Stats:")
                    print(f"  • Total queries: {stats['total_queries']}")
                    print(f"  • Success rate: {stats['successful_queries']/max(1, stats['total_queries']):.1%}")
                    print(f"  • Avg response time: {stats['avg_retrieval_time'] + stats['avg_generation_time']:.3f}s")
                    continue
                elif not query:
                    continue
                
                # Generate RAG response
                response = rag.generate_response(query)
                
                if response['success']:
                    print(f"\n🤖 Response:")
                    print(response['response'])
                    print(f"\n📚 Used {response['context_count']} context documents (avg similarity: {response['avg_context_similarity']:.3f})")
                    print(f"⏱️ Response time: {response['total_time']:.2f}s")
                else:
                    print(f"❌ Error: {response.get('error', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")

if __name__ == "__main__":
    # Run main demonstration
    demo_basic_rag()
    
    # Optional interactive mode
    print("\n" + "="*60)
    choice = input("Would you like to try interactive RAG mode? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_rag()
    
    print("\n🎓 Phase 1d Complete!")
    print("🎉 Day 1 Complete: Models & RAG Foundation")
    print("Next: Day 2 - AI Agents & Model Context Protocol (MCP)")