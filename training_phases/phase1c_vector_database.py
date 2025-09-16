#!/usr/bin/env python3
"""
Phase 1c: Vector Database Setup (90 min)
Day 1 - Understanding RAG: Vector databases and data pipelines

Learning Objectives:
- Understanding vector databases and embeddings storage
- Setting up ChromaDB for semantic search
- Creating collections and managing vector data
- Basic similarity search and retrieval
- Hands-on: storing and querying document embeddings

This module focuses on the storage and retrieval layer of RAG systems.
"""

import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB not available. Install with: pip install chromadb")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector-database")

class VectorDatabase:
    """
    Vector database manager using ChromaDB for semantic search and retrieval.
    Demonstrates core concepts of embedding storage and similarity search.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize vector database with ChromaDB.
        
        Args:
            persist_directory: Directory to persist database files
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not available. Install with: pip install chromadb")
        
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        self.operation_log = []
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client with persistence."""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Use default embedding function (sentence transformers)
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            logger.info(f"Vector database initialized at: {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    def create_collection(self, name: str, description: str = "") -> bool:
        """
        Create a new collection in the vector database.
        
        Args:
            name: Collection name
            description: Optional description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(name)
                logger.info(f"Deleted existing collection: {name}")
            except:
                pass  # Collection didn't exist
            
            # Create new collection
            collection = self.client.create_collection(
                name=name,
                embedding_function=self.embedding_function,
                metadata={"description": description, "created_at": datetime.now().isoformat()}
            )
            
            self.collections[name] = collection
            
            self._log_operation("create_collection", {"name": name, "description": description})
            logger.info(f"Created collection: {name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {name}: {e}")
            return False
    
    def get_collection(self, name: str):
        """Get existing collection by name."""
        try:
            if name in self.collections:
                return self.collections[name]
            
            collection = self.client.get_collection(name)
            self.collections[name] = collection
            return collection
            
        except Exception as e:
            logger.error(f"Collection {name} not found: {e}")
            return None
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents with 'id', 'text', and optional 'metadata'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection {collection_name} not found")
                return False
            
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                ids.append(doc['id'])
                texts.append(doc['text'])
                metadatas.append(doc.get('metadata', {}))
            
            # Add to collection
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            self._log_operation("add_documents", {
                "collection": collection_name,
                "count": len(documents)
            })
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            return False
    
    def search_similar(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity.
        
        Args:
            collection_name: Name of the collection to search
            query: Search query text
            n_results: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection {collection_name} not found")
                return []
            
            start_time = time.time()
            
            # Perform similarity search
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            search_time = time.time() - start_time
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    result = {
                        'id': results['ids'][0][i] if results.get('ids') else f"result_{i}",
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else 0,
                        'similarity': round(1 - results['distances'][0][i], 4) if results.get('distances') else 1
                    }
                    formatted_results.append(result)
            
            self._log_operation("search_similar", {
                "collection": collection_name,
                "query": query,
                "n_results": n_results,
                "found": len(formatted_results),
                "search_time": round(search_time, 4)
            })
            
            logger.info(f"Search in {collection_name}: {len(formatted_results)} results in {search_time:.3f}s")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed in {collection_name}: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information and statistics
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return {"error": f"Collection {collection_name} not found"}
            
            # Get collection count and metadata
            count = collection.count()
            metadata = collection.metadata
            
            # Get a sample of documents
            sample_results = collection.peek(limit=3)
            
            return {
                "name": collection_name,
                "document_count": count,
                "metadata": metadata,
                "sample_documents": sample_results,
                "embedding_function": str(type(self.embedding_function).__name__)
            }
            
        except Exception as e:
            logger.error(f"Failed to get info for {collection_name}: {e}")
            return {"error": str(e)}
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections in the database."""
        try:
            collections = self.client.list_collections()
            collection_info = []
            
            for col in collections:
                info = self.get_collection_info(col.name)
                collection_info.append(info)
            
            return collection_info
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            
            self._log_operation("delete_collection", {"name": collection_name})
            logger.info(f"Deleted collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False
    
    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log database operations for analysis."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        self.operation_log.append(log_entry)
        
        # Keep only last 100 operations
        if len(self.operation_log) > 100:
            self.operation_log = self.operation_log[-100:]
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log for analysis."""
        return self.operation_log

def create_sample_documents():
    """Create sample documents for demonstration."""
    return [
        {
            "id": "policy_returns_1",
            "text": "Our return policy allows customers to return items within 30 days of purchase. Items must be in original condition with receipt. Refunds are processed within 5-7 business days.",
            "metadata": {"category": "returns", "document_type": "policy", "priority": "high"}
        },
        {
            "id": "policy_shipping_1", 
            "text": "Standard shipping takes 3-5 business days and costs $5.99. Express shipping is available in 1-2 days for $15.99. Free shipping on orders over $50.",
            "metadata": {"category": "shipping", "document_type": "policy", "priority": "medium"}
        },
        {
            "id": "policy_support_1",
            "text": "Customer support is available 24/7 for premium customers. Standard customers can reach us Monday-Friday 9AM-5PM. Contact via phone, chat, or email.",
            "metadata": {"category": "support", "document_type": "policy", "priority": "medium"}
        },
        {
            "id": "troubleshoot_power_1",
            "text": "If your device won't turn on, first check the power cable connection. Try a different outlet. Hold the power button for 10 seconds to reset. If issues persist, contact support.",
            "metadata": {"category": "troubleshooting", "document_type": "guide", "priority": "high"}
        },
        {
            "id": "account_password_1",
            "text": "To reset your password, click 'Forgot Password' on the login page. Enter your email address and check for a reset link. The link expires in 24 hours.",
            "metadata": {"category": "account", "document_type": "guide", "priority": "high"}
        },
        {
            "id": "payment_methods_1",
            "text": "We accept major credit cards, PayPal, and Apple Pay. All payments are processed securely using industry-standard encryption. Payment information is never stored on our servers.",
            "metadata": {"category": "payment", "document_type": "info", "priority": "medium"}
        }
    ]

def demo_vector_database():
    """
    Demonstrate vector database capabilities.
    """
    print("=== Phase 1c: Vector Database Setup Demo ===\n")
    
    if not CHROMADB_AVAILABLE:
        print("❌ ChromaDB not available. Install with: pip install chromadb")
        return
    
    # Initialize vector database
    print("🔄 Initializing vector database...")
    try:
        db = VectorDatabase("./demo_chroma_db")
        print("✅ Vector database initialized")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return
    
    # Create collection
    print("\n📁 Creating collection...")
    success = db.create_collection(
        "customer_support_docs",
        "Customer support policies and troubleshooting guides"
    )
    
    if not success:
        print("❌ Failed to create collection")
        return
    
    print("✅ Collection created")
    
    # Add sample documents
    print("\n📄 Adding sample documents...")
    sample_docs = create_sample_documents()
    success = db.add_documents("customer_support_docs", sample_docs)
    
    if not success:
        print("❌ Failed to add documents")
        return
    
    print(f"✅ Added {len(sample_docs)} documents")
    
    # Show collection info
    print("\n📊 Collection Information:")
    info = db.get_collection_info("customer_support_docs")
    print(f"  • Document count: {info.get('document_count', 0)}")
    print(f"  • Embedding function: {info.get('embedding_function', 'Unknown')}")
    
    # Demonstrate similarity search
    print("\n🔍 Similarity Search Demonstrations:")
    
    search_queries = [
        "How do I return a product?",
        "My device won't start",
        "What payment methods do you accept?",
        "I forgot my password",
        "How long does shipping take?"
    ]
    
    for query in search_queries:
        print(f"\n🔤 Query: '{query}'")
        results = db.search_similar("customer_support_docs", query, n_results=3)
        
        if results:
            print("  Top matches:")
            for i, result in enumerate(results, 1):
                print(f"    {i}. [{result['similarity']:.3f}] {result['text'][:80]}...")
                print(f"       Category: {result['metadata'].get('category', 'unknown')}")
        else:
            print("  No results found")
    
    # Advanced search analysis
    print("\n📈 Search Quality Analysis:")
    
    test_cases = [
        ("return policy", "returns"),
        ("shipping time", "shipping"),
        ("password reset", "account"),
        ("device problems", "troubleshooting"),
        ("payment options", "payment")
    ]
    
    accuracy_scores = []
    
    for query, expected_category in test_cases:
        results = db.search_similar("customer_support_docs", query, n_results=1)
        if results:
            actual_category = results[0]['metadata'].get('category', 'unknown')
            accuracy = 1.0 if actual_category == expected_category else 0.0
            accuracy_scores.append(accuracy)
            status = "✅" if accuracy == 1.0 else "❌"
            print(f"  {status} '{query}' → Expected: {expected_category}, Got: {actual_category}")
        else:
            accuracy_scores.append(0.0)
            print(f"  ❌ '{query}' → No results")
    
    overall_accuracy = sum(accuracy_scores) / len(accuracy_scores) * 100
    print(f"\n📊 Overall Search Accuracy: {overall_accuracy:.1f}%")
    
    # Show operation log
    print("\n📋 Database Operations Log:")
    operations = db.get_operation_log()
    for op in operations[-5:]:  # Show last 5 operations
        print(f"  • {op['timestamp'][:19]} - {op['operation']}: {op['details']}")
    
    # Collection management demo
    print("\n🗂️ Collection Management:")
    collections = db.list_collections()
    for col in collections:
        if 'error' not in col:
            print(f"  • {col['name']}: {col['document_count']} documents")

def interactive_search():
    """Interactive search interface for experimentation."""
    print("\n=== Interactive Vector Search ===")
    print("Type 'quit' to exit, 'info' for collection info")
    
    if not CHROMADB_AVAILABLE:
        print("❌ ChromaDB not available")
        return
    
    try:
        db = VectorDatabase("./demo_chroma_db")
        collection_name = "customer_support_docs"
        
        # Check if collection exists
        info = db.get_collection_info(collection_name)
        if 'error' in info:
            print(f"❌ Collection not found. Run the main demo first.")
            return
        
        print(f"✅ Connected to collection with {info['document_count']} documents")
        
        while True:
            try:
                query = input("\n🔍 Enter search query: ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'info':
                    info = db.get_collection_info(collection_name)
                    print(f"Collection: {collection_name}")
                    print(f"Documents: {info['document_count']}")
                    continue
                elif not query:
                    continue
                
                # Perform search
                results = db.search_similar(collection_name, query, n_results=5)
                
                if results:
                    print(f"\n📋 Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. [Similarity: {result['similarity']:.3f}]")
                        print(f"   Category: {result['metadata'].get('category', 'unknown')}")
                        print(f"   Text: {result['text']}")
                else:
                    print("❌ No results found")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")

if __name__ == "__main__":
    # Run main demo
    demo_vector_database()
    
    # Optional interactive mode
    print("\n" + "="*50)
    choice = input("Would you like to try interactive search? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_search()
    
    print("\n🎓 Phase 1c Complete!")
    print("Next: Phase 1d - Basic RAG Implementation")