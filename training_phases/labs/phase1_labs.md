# Phase 1 Labs: Models & RAG Foundation

> **Duration:** Each lab 10-12 minutes | **Total:** ~45 minutes  
> **Focus:** Hands-on implementation of core AI functionality

---

## Lab 1A: Basic LLM Integration (12 minutes)

### **Objective**
Set up and test LLM communication with Ollama, focusing on practical prompt engineering.

### **Steps**

1. **Verify Ollama Setup** (2 min)
   ```bash
   # Check if Ollama is running
   ollama list
   
   # If llama3.2 not available, pull it
   ollama pull llama3.2
   ```

2. **Create Basic LLM Client** (3 min)
   ```bash
   # Navigate to training phases
   cd /path/to/capstone/training_phases
   
   # Test the basic LLM client
   python phase1a_basic_llm.py
   ```

3. **Interactive Testing** (4 min)
   - When prompted, choose "Interactive Mode"
   - Test these prompts:
     ```
     "Explain what a customer service agent should do when a customer wants to return an item"
     "How would you handle an angry customer complaint?"
     "What information do you need to process a refund?"
     ```

4. **Observe Response Quality** (2 min)
   - Note response time
   - Evaluate response relevance
   - Check for consistent formatting

5. **Test Performance Metrics** (1 min)
   - Exit interactive mode
   - Review the performance analysis output
   - Note tokens per second and response quality scores

**Expected Output:** Working LLM connection with performance metrics showing ~20-50 tokens/second

**Troubleshooting:** If Ollama connection fails, ensure it's running on port 11434

---

## Lab 1B: Document Processing Pipeline (10 minutes)

### **Objective**
Process PDF documents and extract structured text for AI consumption.

### **Steps**

1. **Verify Knowledge Base** (1 min)
   ```bash
   # Check that PDF files exist
   ls ../knowledge_base_pdfs/
   ```

2. **Run Document Processor** (2 min)
   ```bash
   python phase1b_document_processing.py
   ```

3. **Process Sample Documents** (3 min)
   - Select option 1: "Process Documents"
   - Choose "All Documents" when prompted
   - Watch the processing progress and statistics

4. **Examine Processed Output** (2 min)
   - Review the text chunks displayed
   - Note chunk sizes (should be ~500-1000 characters)
   - Check for proper text cleaning (no weird characters)

5. **Test Embedding Concepts** (2 min)
   - Select option 2: "Embedding Demonstration"
   - Try different text examples:
     ```
     "return policy"
     "shipping information"
     "customer support"
     ```
   - Observe similarity scores between related concepts

**Expected Output:** Successfully processed 6 PDF documents with ~50-100 text chunks total

**Key Learning:** Documents are chunked for optimal AI processing, with metadata preserved

---

## Lab 1C: Vector Database Setup (11 minutes)

### **Objective**
Create a searchable vector database using ChromaDB for semantic document retrieval.

### **Steps**

1. **Initialize Vector Database** (2 min)
   ```bash
   python phase1c_vector_database.py
   ```

2. **Create Document Collection** (3 min)
   - Select option 1: "Initialize Database"
   - Choose "Create New Collection"
   - Name it "customer_service_docs"
   - Watch the embedding process

3. **Add Documents to Collection** (3 min)
   - Select option 2: "Add Documents"
   - Use the processed documents from Lab 1B
   - Confirm all documents are indexed

4. **Test Semantic Search** (3 min)
   - Select option 3: "Search Collection"
   - Try these queries:
     ```
     "How do I return an item?"
     "What are the shipping options?"
     "How to contact support?"
     "Payment methods accepted"
     ```
   - Examine relevance scores (should be > 0.7 for good matches)

**Expected Output:** ChromaDB collection with 50+ document chunks, returning relevant results for queries

**Key Learning:** Vector databases enable semantic search beyond keyword matching

---

## Lab 1D: Complete RAG Implementation (12 minutes)

### **Objective**
Build a complete RAG system that retrieves relevant documents and generates informed responses.

### **Steps**

1. **Initialize RAG System** (2 min)
   ```bash
   python phase1d_basic_rag.py
   ```

2. **Load Vector Database** (2 min)
   - Select option 1: "Initialize RAG System"
   - Use the collection created in Lab 1C
   - Verify connection to both ChromaDB and Ollama

3. **Test RAG Pipeline** (4 min)
   - Select option 2: "RAG Query Processing"
   - Ask customer service questions:
     ```
     "What is your return policy for electronics?"
     "How long does shipping take?"
     "Can I track my order?"
     "What payment methods do you accept?"
     ```

4. **Analyze RAG Quality** (2 min)
   - For each response, note:
     - Number of source documents retrieved
     - Relevance of retrieved content
     - Quality of generated answer
     - Response time

5. **Compare with Non-RAG** (2 min)
   - Select option 3: "Compare RAG vs Non-RAG"
   - Ask the same questions without document context
   - Notice the difference in specificity and accuracy

**Expected Output:** RAG system providing accurate, context-aware answers citing specific company policies

**Key Learning:** RAG combines retrieval and generation for factual, grounded responses

---

## Phase 1 Summary & Validation

### **Checkpoint Questions**
After completing all labs, verify understanding:

1. **Can you explain the difference between embeddings and traditional keyword search?**
2. **What happens when you ask the RAG system about something not in your documents?**
3. **How does chunk size affect retrieval quality?**
4. **What are the performance trade-offs between accuracy and speed?**

### **Success Criteria**
- ✅ LLM responds consistently in under 3 seconds
- ✅ Documents are processed into semantic chunks
- ✅ Vector database returns relevant results (>0.7 similarity)
- ✅ RAG system provides factual answers with citations

### **Next Steps**
Ready for Phase 2: AI Agents & MCP Protocol integration

---

## Code Snippets for Quick Reference

### Test LLM Connection
```python
from phase1a_basic_llm import BasicLLMClient

client = BasicLLMClient()
response = client.generate_response("Hello, how are you?")
print(response)
```

### Quick Document Processing
```python
from phase1b_document_processing import DocumentProcessor

processor = DocumentProcessor()
chunks = processor.process_file("../knowledge_base_pdfs/policy_returns.pdf")
print(f"Processed {len(chunks)} chunks")
```

### Vector Search Example
```python
from phase1c_vector_database import VectorDatabase

db = VectorDatabase()
db.load_collection("customer_service_docs")
results = db.search("return policy", limit=3)
for result in results:
    print(f"Score: {result['similarity']:.3f} - {result['content'][:100]}...")
```

### RAG Query
```python
from phase1d_basic_rag import BasicRAGSystem

rag = BasicRAGSystem()
rag.initialize()
answer = rag.query("What is the return policy?")
print(answer)
```