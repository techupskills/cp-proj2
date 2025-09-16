import json
from datetime import datetime
import requests

class ExpenseAgent:
    def __init__(self, ollama_base_url="http://localhost:11434", model="llama3.2"):
        self.ollama_url = ollama_base_url
        self.model = model
        self.company_policies = {
            "max_meal": 75,
            "max_travel": 500,
            "max_supplies": 200,
            "requires_receipt": 25,
            "auto_approve_under": 50
        }
        
    def check_expense(self, expense_data):
        """Main agent function that processes expense requests"""
        
        # Tool: Policy lookup
        policy_check = self._check_against_policy(expense_data)
        
        # Tool: Calculate totals
        total_amount = self._calculate_total(expense_data)
        
        # Tool: Generate decision
        decision = self._make_decision(expense_data, policy_check, total_amount)
        
        return decision
    
    def _check_against_policy(self, expense):
        """Tool: Check expense against company policies"""
        category = expense.get('category', '').lower()
        amount = expense.get('amount', 0)
        
        if 'meal' in category and amount > self.company_policies['max_meal']:
            return f"Exceeds meal limit (${self.company_policies['max_meal']})"
        elif 'travel' in category and amount > self.company_policies['max_travel']:
            return f"Exceeds travel limit (${self.company_policies['max_travel']})"
        elif 'supplies' in category and amount > self.company_policies['max_supplies']:
            return f"Exceeds supplies limit (${self.company_policies['max_supplies']})"
        elif amount > self.company_policies['requires_receipt'] and not expense.get('has_receipt'):
            return f"Receipt required for amounts over ${self.company_policies['requires_receipt']}"
        else:
            return "Complies with company policy"
    
    def _calculate_total(self, expense):
        """Tool: Calculate expense totals and tax implications"""
        amount = expense.get('amount', 0)
        tax_rate = 0.08 if expense.get('category') != 'travel' else 0
        tax_amount = amount * tax_rate
        return {
            'subtotal': amount,
            'tax': tax_amount,
            'total': amount + tax_amount
        }
    
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
                timeout=30
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f'{{"decision": "NEEDS_REVIEW", "reasoning": "AI processing error: {str(e)}", "next_steps": "Manual review required"}}'
    
    def _make_decision(self, expense, policy_check, totals):
        """Tool: Use AI reasoning to make final decision"""
        
        prompt = f"""
        As an AI expense approval agent, analyze this expense request and respond ONLY with valid JSON.
        
        Employee: {expense.get('employee', 'Unknown')}
        Category: {expense.get('category', 'Unknown')}
        Amount: ${expense.get('amount', 0)}
        Description: {expense.get('description', 'No description')}
        Date: {expense.get('date', 'Not provided')}
        Has Receipt: {expense.get('has_receipt', False)}
        
        Policy Check Result: {policy_check}
        Financial Summary: {json.dumps(totals, indent=2)}
        
        Auto-approval threshold: ${self.company_policies['auto_approve_under']}
        
        Respond with JSON containing exactly these fields:
        - "decision": must be "APPROVED", "REJECTED", or "NEEDS_REVIEW"
        - "reasoning": explanation for the decision
        - "next_steps": what should happen next
        
        JSON Response:
        """
        
        try:
            # Query local Ollama model
            ai_response = self._query_ollama(prompt)
            
            # Parse AI response
            ai_decision = json.loads(ai_response)
            
            # Add our calculated data
            ai_decision['policy_check'] = policy_check
            ai_decision['financial_summary'] = totals
            ai_decision['processed_at'] = datetime.now().isoformat()
            
            return ai_decision
            
        except Exception as e:
            return {
                "decision": "NEEDS_REVIEW",
                "reasoning": f"AI processing error: {str(e)}",
                "next_steps": "Manual review required",
                "policy_check": policy_check,
                "financial_summary": totals
            }

# Demo Usage
def demo_expense_agent():
    """Demo function for webinar presentation"""
    
    print("AI Expense Agent Demo\n" + "="*50)
    
    # Initialize agent (using local Ollama)
    agent = ExpenseAgent(
        ollama_base_url="http://localhost:11434",
        model="llama3.2"
    )
    
    # Sample expense requests for demo
    expenses = [
        {
            "employee": "Sarah Chen",
            "category": "business meal",
            "amount": 45,
            "description": "Client dinner at Restaurant ABC",
            "date": "2024-12-01",
            "has_receipt": True
        },
        {
            "employee": "Mike Rodriguez", 
            "category": "travel",
            "amount": 650,
            "description": "Flight to client site",
            "date": "2024-12-02",
            "has_receipt": False
        },
        {
            "employee": "Lisa Park",
            "category": "office supplies",
            "amount": 25,
            "description": "Notebooks and pens",
            "date": "2024-12-03", 
            "has_receipt": True
        }
    ]
    
    for i, expense in enumerate(expenses, 1):
        print(f"\nProcessing Expense Request #{i}")
        print(f"Employee: {expense['employee']}")
        print(f"Amount: ${expense['amount']} for {expense['category']}")
        
        # Process with agent
        result = agent.check_expense(expense)
        
        print(f"\nDecision: {result['decision']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Next Steps: {result['next_steps']}")
        print(f"Total Cost: ${result['financial_summary']['total']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    demo_expense_agent()
