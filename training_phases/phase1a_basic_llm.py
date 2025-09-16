#!/usr/bin/env python3
"""
Phase 1a: Basic LLM Integration (90 min)
Day 1 - Understanding AI Models

Learning Objectives:
- How LLMs work: embeddings, transformers, attention
- Finding, running, and qualifying models
- Basic prompt engineering and response handling

This module demonstrates the simplest possible LLM integration without
any complexity from RAG, agents, or protocols.
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("basic-llm")

class BasicLLMClient:
    """
    Simple LLM client that demonstrates core model interaction concepts.
    Uses Ollama as the local model provider.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.request_history = []
        
    def generate_response(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            prompt: The input text prompt
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            
        Returns:
            Dictionary with response data and metadata
        """
        start_time = datetime.now()
        
        try:
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 500  # Limit response length
                }
            }
            
            # Make API call to local Ollama instance
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Calculate timing
            duration = (datetime.now() - start_time).total_seconds()
            
            # Prepare structured response
            structured_response = {
                "prompt": prompt,
                "response": result.get("response", ""),
                "model": self.model,
                "temperature": temperature,
                "duration_seconds": duration,
                "token_count": len(result.get("response", "").split()),
                "timestamp": start_time.isoformat(),
                "success": True
            }
            
            # Log request for analysis
            self.request_history.append(structured_response)
            logger.info(f"LLM Response generated in {duration:.2f}s")
            
            return structured_response
            
        except Exception as e:
            error_response = {
                "prompt": prompt,
                "response": f"Error: {str(e)}",
                "model": self.model,
                "temperature": temperature,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "token_count": 0,
                "timestamp": start_time.isoformat(),
                "success": False,
                "error": str(e)
            }
            
            self.request_history.append(error_response)
            logger.error(f"LLM request failed: {e}")
            
            return error_response
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            current_model = next((m for m in models if m["name"].startswith(self.model)), None)
            
            if current_model:
                return {
                    "name": current_model["name"],
                    "size": current_model.get("size", 0),
                    "modified": current_model.get("modified_at", ""),
                    "available": True
                }
            else:
                return {"available": False, "error": f"Model {self.model} not found"}
                
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_request_history(self) -> list:
        """
        Get history of all LLM requests for analysis.
        """
        return self.request_history
    
    def clear_history(self):
        """
        Clear request history.
        """
        self.request_history = []

def demo_basic_prompting():
    """
    Demonstrate basic prompting techniques and model interaction.
    """
    print("=== Phase 1a: Basic LLM Integration Demo ===\n")
    
    # Initialize LLM client
    llm = BasicLLMClient()
    
    # Check model availability
    model_info = llm.get_model_info()
    print(f"Model Info: {json.dumps(model_info, indent=2)}\n")
    
    if not model_info.get("available", False):
        print("❌ Model not available. Please ensure Ollama is running with llama3.2 model.")
        return
    
    # Example 1: Simple question-answer
    print("🔤 Example 1: Simple Question-Answer")
    response1 = llm.generate_response(
        "What is artificial intelligence in simple terms?",
        temperature=0.3  # Lower temperature for factual responses
    )
    print(f"Q: What is artificial intelligence in simple terms?")
    print(f"A: {response1['response']}")
    print(f"⏱️ Response time: {response1['duration_seconds']:.2f}s\n")
    
    # Example 2: Creative prompt
    print("🎨 Example 2: Creative Writing")
    response2 = llm.generate_response(
        "Write a short haiku about customer service.",
        temperature=0.8  # Higher temperature for creativity
    )
    print(f"Q: Write a short haiku about customer service.")
    print(f"A: {response2['response']}")
    print(f"⏱️ Response time: {response2['duration_seconds']:.2f}s\n")
    
    # Example 3: Structured output
    print("📋 Example 3: Structured Output Request")
    response3 = llm.generate_response(
        """Create a JSON response with customer support categories. 
        Format: {"categories": ["category1", "category2", ...]}""",
        temperature=0.1  # Very low for consistent structure
    )
    print(f"Q: Create a JSON response with customer support categories.")
    print(f"A: {response3['response']}")
    print(f"⏱️ Response time: {response3['duration_seconds']:.2f}s\n")
    
    # Example 4: Prompt engineering demonstration
    print("🔧 Example 4: Prompt Engineering - Context Matters")
    
    # Poor prompt
    poor_response = llm.generate_response(
        "Help customer",
        temperature=0.5
    )
    
    # Better prompt
    good_response = llm.generate_response(
        """You are a professional customer service representative. 
        A customer needs help with a product return. 
        Provide a helpful, empathetic response that includes:
        1. Acknowledgment of their concern
        2. Clear next steps
        3. Contact information if needed""",
        temperature=0.5
    )
    
    print("Poor prompt: 'Help customer'")
    print(f"Response: {poor_response['response'][:100]}...\n")
    
    print("Better prompt with context and structure:")
    print(f"Response: {good_response['response'][:200]}...\n")
    
    # Analysis
    print("📊 Session Analysis:")
    history = llm.get_request_history()
    avg_duration = sum(r['duration_seconds'] for r in history) / len(history)
    total_tokens = sum(r['token_count'] for r in history)
    
    print(f"• Total requests: {len(history)}")
    print(f"• Average response time: {avg_duration:.2f}s")
    print(f"• Total tokens generated: {total_tokens}")
    print(f"• Success rate: {sum(1 for r in history if r['success']) / len(history) * 100:.1f}%")

def interactive_mode():
    """
    Interactive mode for experimenting with the LLM.
    """
    print("\n=== Interactive LLM Mode ===")
    print("Type 'quit' to exit, 'history' to see request history, 'clear' to clear history")
    
    llm = BasicLLMClient()
    
    while True:
        try:
            user_input = input("\n🤖 Enter your prompt: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'history':
                history = llm.get_request_history()
                print(f"\n📝 Request History ({len(history)} requests):")
                for i, req in enumerate(history[-5:], 1):  # Show last 5
                    print(f"{i}. [{req['timestamp'][:19]}] {req['prompt'][:50]}...")
                    print(f"   → {req['response'][:100]}...")
                continue
            elif user_input.lower() == 'clear':
                llm.clear_history()
                print("✅ History cleared")
                continue
            elif not user_input:
                continue
            
            # Generate response
            response = llm.generate_response(user_input)
            
            print(f"\n🤖 Response: {response['response']}")
            print(f"⏱️ Time: {response['duration_seconds']:.2f}s | Tokens: {response['token_count']}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run the demo
    demo_basic_prompting()
    
    # Optional interactive mode
    print("\n" + "="*50)
    choice = input("Would you like to try interactive mode? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_mode()
    
    print("\n🎓 Phase 1a Complete!")
    print("Next: Phase 1b - Document Processing & Embeddings")