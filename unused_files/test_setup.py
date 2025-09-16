#!/usr/bin/env python3
"""
Quick test script to verify Ollama and projects are working
Run this before your webinar to ensure everything is ready
"""

import requests
import json
import sys

def test_ollama():
    """Test if Ollama is running and has the model"""
    print("Testing Ollama connection...")
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if any('llama3.2' in name for name in model_names):
                print("SUCCESS: Ollama is running with llama3.2 model")
                return True
            else:
                print(f"WARNING: Ollama is running but llama3.2 not found. Available: {model_names}")
                print("Try: ollama pull llama3.2")
                return False
        else:
            print(f"ERROR: Ollama returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama")
        print("Try: ollama serve")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_expense_agent():
    """Test the expense agent"""
    print("\nTesting Expense Agent...")
    
    try:
        from expense_agent import ExpenseAgent
        agent = ExpenseAgent()
        
        test_expense = {
            "employee": "Test User",
            "category": "business meal",
            "amount": 45,
            "description": "Test expense",
            "date": "2024-12-01",
            "has_receipt": True
        }
        
        result = agent.check_expense(test_expense)
        
        if isinstance(result, dict) and 'decision' in result:
            print("SUCCESS: Expense Agent working correctly")
            return True
        else:
            print("ERROR: Expense Agent returned unexpected format")
            return False
            
    except ImportError:
        print("ERROR: Cannot import expense_agent.py - file missing?")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_customer_support():
    """Test the customer support agent"""
    print("\nTesting Customer Support Agent...")
    
    try:
        from customer_support_agent import CustomerSupportAgent
        agent = CustomerSupportAgent()
        
        result = agent.process_customer_inquiry(
            "john.doe@email.com", 
            "How do I return an item?"
        )
        
        if isinstance(result, dict) and 'response' in result:
            print("SUCCESS: Customer Support Agent working correctly")
            return True
        else:
            print("ERROR: Customer Support Agent returned unexpected format")
            return False
            
    except ImportError:
        print("ERROR: Cannot import customer_support_agent.py - file missing?")
        return False
    except Exception as e:
        print("ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("AI Enterprise Training - Pre-Webinar Test")
    print("="*50)
    
    tests = [
        ("Ollama Setup", test_ollama),
        ("Expense Agent", test_expense_agent),
        ("Customer Support Agent", test_customer_support)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All systems ready for webinar!")
        print("\nDemo commands:")
        print("   python expense_agent.py")
        print("   streamlit run streamlit_app.py")
    else:
        print("WARNING: Some issues detected. Check setup before webinar.")

if __name__ == "__main__":
    main()
