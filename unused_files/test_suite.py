#!/usr/bin/env python3
"""
Comprehensive test suite for Customer Support AI Agent
Run this to verify all components are working correctly
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Import our modules
try:
    from customer_support_agent import CustomerSupportAgent
    from sample_data import get_sample_questions, get_demo_scenarios
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    print("Make sure all required files are in the same directory")
    sys.exit(1)

class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.agent = None
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        if success:
            print(f"SUCCESS: {test_name}")
            self.passed += 1
        else:
            print(f"ERROR: {test_name}: {message}")
            self.failed += 1
    
    def test_ollama_connection(self):
        """Test Ollama service connection"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            success = response.status_code == 200
            
            if success:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                message = f"Available models: {model_names}"
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Ollama Connection", success, message)
            return success
            
        except requests.exceptions.ConnectionError:
            self.log_test("Ollama Connection", False, "Connection refused - is Ollama running?")
            return False
        except Exception as e:
            self.log_test("Ollama Connection", False, str(e))
            return False
    
    def test_model_response(self):
        """Test basic model functionality"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": "Say exactly: 'Model test successful'",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').lower()
                success = 'successful' in response_text
                message = f"Response: '{result.get('response', 'No response')[:50]}...'"
            else:
                success = False
                message = f"HTTP {response.status_code}"
            
            self.log_test("Model Response", success, message)
            return success
            
        except Exception as e:
            self.log_test("Model Response", False, str(e))
            return False
    
    def test_json_formatting(self):
        """Test model's ability to produce valid JSON"""
        try:
            prompt = '''Respond with valid JSON containing:
- "test": "json_formatting"
- "status": "success"
- "timestamp": current time

JSON Response:'''
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                
                try:
                    parsed = json.loads(ai_response)
                    success = parsed.get('test') == 'json_formatting'
                    message = f"Parsed: {parsed}"
                except json.JSONDecodeError:
                    success = False
                    message = f"Invalid JSON: {ai_response[:100]}"
            else:
                success = False
                message = f"HTTP {response.status_code}"
            
            self.log_test("JSON Formatting", success, message)
            return success
            
        except Exception as e:
            self.log_test("JSON Formatting", False, str(e))
            return False
    
    def test_agent_initialization(self):
        """Test CustomerSupportAgent initialization"""
        try:
            self.agent = CustomerSupportAgent()
            success = self.agent is not None
            message = "Agent initialized successfully"
            
            self.log_test("Agent Initialization", success, message)
            return success
            
        except Exception as e:
            self.log_test("Agent Initialization", False, str(e))
            return False
    
    def test_knowledge_base(self):
        """Test RAG knowledge base functionality"""
        if not self.agent:
            self.log_test("Knowledge Base", False, "Agent not initialized")
            return False
        
        try:
            # Test knowledge base search
            results = self.agent.search_knowledge_base("return policy")
            success = len(results) > 0 and any('return' in doc['content'].lower() for doc in results)
            message = f"Found {len(results)} relevant documents"
            
            self.log_test("Knowledge Base Search", success, message)
            return success
            
        except Exception as e:
            self.log_test("Knowledge Base Search", False, str(e))
            return False
    
    def test_customer_lookup(self):
        """Test customer database functionality"""
        if not self.agent:
            self.log_test("Customer Lookup", False, "Agent not initialized")
            return False
        
        try:
            # Test customer lookup
            customer = self.agent.lookup_customer("john.doe@email.com")
            success = customer is not None and customer.get('name') == 'John Doe'
            message = f"Found customer: {customer.get('name') if customer else 'None'}"
            
            self.log_test("Customer Lookup", success, message)
            return success
            
        except Exception as e:
            self.log_test("Customer Lookup", False, str(e))
            return False
    
    def test_ticket_creation(self):
        """Test support ticket creation"""
        if not self.agent:
            self.log_test("Ticket Creation", False, "Agent not initialized")
            return False
        
        try:
            # Test ticket creation
            ticket = self.agent.create_ticket(
                "test@email.com", 
                "Test Issue", 
                "This is a test ticket"
            )
            success = ticket is not None and 'id' in ticket
            message = f"Created ticket: {ticket.get('id') if ticket else 'None'}"
            
            self.log_test("Ticket Creation", success, message)
            return success
            
        except Exception as e:
            self.log_test("Ticket Creation", False, str(e))
            return False
    
    def test_end_to_end_inquiry(self):
        """Test complete customer inquiry processing"""
        if not self.agent:
            self.log_test("End-to-End Processing", False, "Agent not initialized")
            return False
        
        try:
            # Test complete inquiry processing
            inquiry = "How do I return an item?"
            customer_email = "john.doe@email.com"
            
            result = self.agent.process_customer_inquiry(customer_email, inquiry)
            
            success = (
                isinstance(result, dict) and
                'response' in result and
                'confidence' in result and
                len(result['response']) > 10
            )
            
            message = f"Response length: {len(result.get('response', ''))}"
            
            self.log_test("End-to-End Processing", success, message)
            return success
            
        except Exception as e:
            self.log_test("End-to-End Processing", False, str(e))
            return False
    
    def test_sample_scenarios(self):
        """Test all demo scenarios"""
        if not self.agent:
            self.log_test("Demo Scenarios", False, "Agent not initialized")
            return False
        
        try:
            scenarios = get_demo_scenarios()
            successful_scenarios = 0
            
            for scenario in scenarios:
                try:
                    result = self.agent.process_customer_inquiry(
                        scenario['customer'], 
                        scenario['question']
                    )
                    
                    if isinstance(result, dict) and 'response' in result:
                        successful_scenarios += 1
                        
                except Exception:
                    pass
            
            success = successful_scenarios == len(scenarios)
            message = f"{successful_scenarios}/{len(scenarios)} scenarios passed"
            
            self.log_test("Demo Scenarios", success, message)
            return success
            
        except Exception as e:
            self.log_test("Demo Scenarios", False, str(e))
            return False
    
    def test_performance(self):
        """Test response time performance"""
        if not self.agent:
            self.log_test("Performance Test", False, "Agent not initialized")
            return False
        
        try:
            start_time = time.time()
            
            result = self.agent.process_customer_inquiry(
                "john.doe@email.com",
                "What are your business hours?"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response_time < 10  # Should respond within 10 seconds
            message = f"Response time: {response_time:.2f} seconds"
            
            self.log_test("Performance Test", success, message)
            return success
            
        except Exception as e:
            self.log_test("Performance Test", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("Customer Support AI Agent - Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Define test sequence
        tests = [
            ("Ollama Connection", self.test_ollama_connection),
            ("Model Response", self.test_model_response),
            ("JSON Formatting", self.test_json_formatting),
            ("Agent Initialization", self.test_agent_initialization),
            ("Knowledge Base", self.test_knowledge_base),
            ("Customer Lookup", self.test_customer_lookup),
            ("Ticket Creation", self.test_ticket_creation),
            ("End-to-End Processing", self.test_end_to_end_inquiry),
            ("Demo Scenarios", self.test_sample_scenarios),
            ("Performance", self.test_performance),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            test_func()
            print()
        
        # Summary
        total_tests = len(tests)
        print("=" * 60)
        print(f"Test Results: {self.passed}/{total_tests} tests passed")
        
        if self.passed == total_tests:
            print("SUCCESS: All tests passed! System is ready for demo.")
            print("\\nYou can now run:")
            print("   streamlit run streamlit_app.py")
            
        elif self.passed > total_tests // 2:
            print("WARNING: Most tests passed, but some issues detected.")
            print("\\nCheck the failed tests above and:")
            print("   - Ensure Ollama is running: ollama serve")
            print("   - Verify model is installed: ollama pull llama3.2")
            print("   - Check all dependencies: pip install -r requirements.txt")
            
        else:
            print("ERROR: Multiple test failures detected.")
            print("\\nSetup help:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Start service: ollama serve")
            print("   3. Install model: ollama pull llama3.2")
            print("   4. Install dependencies: pip install -r requirements.txt")
            print("   5. Run tests again: python test_suite.py")
        
        return self.passed == total_tests

def main():
    """Main test function"""
    suite = TestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
