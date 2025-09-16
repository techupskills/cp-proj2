#!/usr/bin/env python3
"""
Phase 2a: Simple Agent Logic (90 min)
Day 2 - AI Agents Part 1: Motivations, use cases, and basic reasoning

Learning Objectives:
- Motivations and use cases for agents
- What agents are and how they work
- Chain of thought, memory, and data management
- Hands-on: creating an AI agent that leverages tools

This module introduces the concept of AI agents - systems that can reason,
make decisions, and use tools to accomplish complex tasks.
"""

import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Import previous phase capabilities
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1a_basic_llm import BasicLLMClient
    LLM_AVAILABLE = True
except ImportError:
    print("⚠️ Phase 1a not available. Some features will be limited.")
    LLM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple-agent")

class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentAction:
    """Represents an action the agent can take"""
    name: str
    description: str
    parameters: Dict[str, Any]
    tool_function: Callable
    required_params: List[str]

@dataclass
class AgentMemory:
    """Agent's working memory for a task"""
    task_id: str
    goal: str
    context: Dict[str, Any]
    steps_taken: List[Dict[str, Any]]
    current_state: AgentState
    reasoning_chain: List[str]
    created_at: datetime
    updated_at: datetime

class SimpleAgent:
    """
    A basic AI agent that can reason about tasks, make decisions,
    and use tools to accomplish goals.
    """
    
    def __init__(self, 
                 agent_name: str = "CustomerServiceAgent",
                 llm_base_url: str = "http://localhost:11434",
                 llm_model: str = "llama3.2"):
        """
        Initialize the agent with its capabilities.
        
        Args:
            agent_name: Name/role of the agent
            llm_base_url: URL for LLM service
            llm_model: LLM model to use
        """
        self.agent_name = agent_name
        self.llm_available = LLM_AVAILABLE
        
        if self.llm_available:
            self.llm_client = BasicLLMClient(llm_base_url, llm_model)
        
        # Agent capabilities
        self.available_actions = {}
        self.memory_store = {}  # task_id -> AgentMemory
        self.execution_log = []
        
        # Agent configuration
        self.max_reasoning_steps = 10
        self.temperature = 0.3  # Lower for more focused reasoning
        
        # Initialize with basic tools
        self._register_basic_tools()
        
        logger.info(f"Agent '{agent_name}' initialized with {len(self.available_actions)} tools")
    
    def _register_basic_tools(self):
        """Register basic tools that the agent can use."""
        
        # Calculator tool
        def calculator(expression: str) -> Dict[str, Any]:
            """Evaluate mathematical expressions safely."""
            try:
                # Simple safe evaluation (limited scope)
                allowed_chars = set('0123456789+-*/.() ')
                if not all(c in allowed_chars for c in expression):
                    return {"error": "Invalid characters in expression"}
                
                result = eval(expression)
                return {"result": result, "expression": expression}
            except Exception as e:
                return {"error": str(e), "expression": expression}
        
        # Customer lookup tool
        def lookup_customer(email: str) -> Dict[str, Any]:
            """Look up customer information by email."""
            # Simulated customer database
            customers = {
                "john.doe@email.com": {
                    "name": "John Doe",
                    "tier": "Premium",
                    "orders": ["ORD-001", "ORD-002"],
                    "support_tickets": 2
                },
                "sarah.smith@email.com": {
                    "name": "Sarah Smith", 
                    "tier": "Standard",
                    "orders": ["ORD-003"],
                    "support_tickets": 0
                }
            }
            
            customer = customers.get(email.lower())
            if customer:
                return {"success": True, "customer": customer}
            else:
                return {"success": False, "error": "Customer not found"}
        
        # Knowledge search tool
        def search_knowledge(query: str) -> Dict[str, Any]:
            """Search knowledge base for relevant information."""
            # Simulated knowledge base
            knowledge_items = [
                {
                    "id": "return_policy",
                    "title": "Return Policy",
                    "content": "Items can be returned within 30 days with receipt. Refunds processed in 5-7 business days.",
                    "keywords": ["return", "refund", "policy", "30 days"]
                },
                {
                    "id": "shipping_info",
                    "title": "Shipping Information", 
                    "content": "Standard shipping 3-5 days ($5.99), Express 1-2 days ($15.99). Free shipping over $50.",
                    "keywords": ["shipping", "delivery", "cost", "express", "free"]
                },
                {
                    "id": "password_reset",
                    "title": "Password Reset",
                    "content": "Use 'Forgot Password' link on login page. Check email for reset instructions within 5-10 minutes.",
                    "keywords": ["password", "reset", "login", "forgot"]
                }
            ]
            
            query_words = query.lower().split()
            matches = []
            
            for item in knowledge_items:
                score = sum(1 for word in query_words 
                           if any(word in keyword for keyword in item["keywords"]))
                if score > 0:
                    matches.append({**item, "relevance_score": score})
            
            matches.sort(key=lambda x: x["relevance_score"], reverse=True)
            return {"results": matches[:3], "query": query}
        
        # Create ticket tool
        def create_ticket(customer_email: str, issue_type: str, description: str) -> Dict[str, Any]:
            """Create a support ticket for a customer."""
            ticket_id = f"TKT-{int(time.time())}"
            ticket = {
                "id": ticket_id,
                "customer": customer_email,
                "type": issue_type,
                "description": description,
                "status": "Open",
                "created": datetime.now().isoformat()
            }
            return {"success": True, "ticket": ticket}
        
        # Register all tools
        self.register_action("calculator", "Perform mathematical calculations", calculator, ["expression"])
        self.register_action("lookup_customer", "Look up customer information", lookup_customer, ["email"])
        self.register_action("search_knowledge", "Search the knowledge base", search_knowledge, ["query"])
        self.register_action("create_ticket", "Create a support ticket", create_ticket, ["customer_email", "issue_type", "description"])
    
    def register_action(self, name: str, description: str, tool_function: Callable, required_params: List[str]):
        """
        Register a new action/tool that the agent can use.
        
        Args:
            name: Action name
            description: What the action does
            tool_function: Function to execute
            required_params: Required parameter names
        """
        action = AgentAction(
            name=name,
            description=description,
            parameters={},
            tool_function=tool_function,
            required_params=required_params
        )
        self.available_actions[name] = action
        logger.info(f"Registered action: {name}")
    
    def create_task_memory(self, task_id: str, goal: str, context: Dict[str, Any] = None) -> AgentMemory:
        """
        Create memory for a new task.
        
        Args:
            task_id: Unique task identifier
            goal: What the agent should accomplish
            context: Additional context information
            
        Returns:
            Created memory object
        """
        memory = AgentMemory(
            task_id=task_id,
            goal=goal,
            context=context or {},
            steps_taken=[],
            current_state=AgentState.IDLE,
            reasoning_chain=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.memory_store[task_id] = memory
        logger.info(f"Created task memory: {task_id}")
        return memory
    
    def update_memory(self, task_id: str, new_info: Dict[str, Any]):
        """Update task memory with new information."""
        if task_id in self.memory_store:
            memory = self.memory_store[task_id]
            memory.context.update(new_info)
            memory.updated_at = datetime.now()
    
    def generate_reasoning(self, task_id: str, current_situation: str) -> Dict[str, Any]:
        """
        Generate reasoning about what action to take next.
        
        Args:
            task_id: Task identifier
            current_situation: Description of current situation
            
        Returns:
            Reasoning result with next action
        """
        if not self.llm_available:
            # Fallback reasoning without LLM
            return self._fallback_reasoning(task_id, current_situation)
        
        memory = self.memory_store.get(task_id)
        if not memory:
            return {"error": "Task memory not found"}
        
        # Prepare context for reasoning
        available_tools = [
            f"- {name}: {action.description} (requires: {', '.join(action.required_params)})"
            for name, action in self.available_actions.items()
        ]
        
        previous_steps = [
            f"Step {i+1}: {step.get('action', 'unknown')} - {step.get('result', 'unknown')}"
            for i, step in enumerate(memory.steps_taken)
        ]
        
        # Create reasoning prompt
        prompt = f"""You are an AI agent tasked with helping customers. Analyze the situation and decide what to do next.

GOAL: {memory.goal}

CURRENT SITUATION: {current_situation}

AVAILABLE TOOLS:
{chr(10).join(available_tools)}

PREVIOUS STEPS TAKEN:
{chr(10).join(previous_steps) if previous_steps else "None"}

CONTEXT INFORMATION:
{json.dumps(memory.context, indent=2)}

Think step by step about what you should do next. Consider:
1. What information do you still need?
2. Which tool would be most helpful?
3. What are the parameters you need for that tool?

Respond with JSON containing:
- "reasoning": your step-by-step thinking
- "next_action": the tool name to use next, or "complete" if done
- "parameters": object with parameter values for the tool
- "confidence": number 0-1 indicating confidence in this decision

JSON Response:"""

        try:
            response = self.llm_client.generate_response(prompt, self.temperature)
            reasoning_result = json.loads(response['response'])
            
            # Add to reasoning chain
            memory.reasoning_chain.append(reasoning_result.get('reasoning', ''))
            
            return reasoning_result
            
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {"error": str(e), "reasoning": "Failed to generate reasoning"}
    
    def _fallback_reasoning(self, task_id: str, current_situation: str) -> Dict[str, Any]:
        """Simple fallback reasoning when LLM is not available."""
        memory = self.memory_store.get(task_id)
        
        # Simple heuristic reasoning
        if "customer" in current_situation.lower() and not memory.steps_taken:
            if "@" in current_situation:
                # Extract email for customer lookup
                words = current_situation.split()
                email = next((word for word in words if "@" in word), "")
                return {
                    "reasoning": "Found email in situation, should lookup customer first",
                    "next_action": "lookup_customer",
                    "parameters": {"email": email},
                    "confidence": 0.8
                }
        
        if "return" in current_situation.lower() or "refund" in current_situation.lower():
            return {
                "reasoning": "Customer asking about returns, should search knowledge base",
                "next_action": "search_knowledge", 
                "parameters": {"query": "return policy"},
                "confidence": 0.7
            }
        
        return {
            "reasoning": "No clear pattern, searching general knowledge",
            "next_action": "search_knowledge",
            "parameters": {"query": current_situation},
            "confidence": 0.5
        }
    
    def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific action with given parameters.
        
        Args:
            action_name: Name of action to execute
            parameters: Parameters for the action
            
        Returns:
            Result of the action execution
        """
        if action_name not in self.available_actions:
            return {"error": f"Unknown action: {action_name}"}
        
        action = self.available_actions[action_name]
        
        # Validate required parameters
        missing_params = [param for param in action.required_params 
                         if param not in parameters]
        if missing_params:
            return {"error": f"Missing required parameters: {missing_params}"}
        
        try:
            start_time = time.time()
            result = action.tool_function(**parameters)
            execution_time = time.time() - start_time
            
            execution_record = {
                "action": action_name,
                "parameters": parameters,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "success": "error" not in result
            }
            
            self.execution_log.append(execution_record)
            logger.info(f"Executed {action_name} in {execution_time:.3f}s")
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            error_record = {
                "action": action_name,
                "parameters": parameters,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
            
            self.execution_log.append(error_record)
            logger.error(f"Action {action_name} failed: {e}")
            
            return {"error": str(e), "success": False}
    
    def solve_task(self, task_id: str, initial_situation: str) -> Dict[str, Any]:
        """
        Solve a complete task using reasoning and action execution.
        
        Args:
            task_id: Task identifier
            initial_situation: Description of the problem to solve
            
        Returns:
            Complete solution with all steps taken
        """
        memory = self.memory_store.get(task_id)
        if not memory:
            return {"error": "Task not found in memory"}
        
        memory.current_state = AgentState.THINKING
        current_situation = initial_situation
        
        for step in range(self.max_reasoning_steps):
            logger.info(f"Step {step + 1}: Reasoning about situation")
            
            # Generate reasoning about next action
            reasoning = self.generate_reasoning(task_id, current_situation)
            
            if "error" in reasoning:
                memory.current_state = AgentState.ERROR
                return {"error": reasoning["error"], "steps": memory.steps_taken}
            
            next_action = reasoning.get("next_action")
            
            # Check if task is complete
            if next_action == "complete" or next_action is None:
                memory.current_state = AgentState.COMPLETED
                break
            
            # Execute the next action
            memory.current_state = AgentState.ACTING
            parameters = reasoning.get("parameters", {})
            
            execution_result = self.execute_action(next_action, parameters)
            
            # Record the step
            step_record = {
                "step_number": step + 1,
                "reasoning": reasoning.get("reasoning", ""),
                "action": next_action,
                "parameters": parameters,
                "result": execution_result,
                "confidence": reasoning.get("confidence", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            memory.steps_taken.append(step_record)
            memory.current_state = AgentState.THINKING
            
            # Update situation based on result
            if execution_result.get("success"):
                result_data = execution_result.get("result", {})
                current_situation = f"Previous action: {next_action}. Result: {json.dumps(result_data)}"
                
                # Store important information in context
                if next_action == "lookup_customer" and result_data.get("success"):
                    memory.context["customer_info"] = result_data["customer"]
                elif next_action == "search_knowledge":
                    memory.context["knowledge_results"] = result_data["results"]
            else:
                current_situation = f"Previous action {next_action} failed: {execution_result.get('error')}"
        
        # Generate final summary
        summary = self._generate_task_summary(memory)
        
        return {
            "task_id": task_id,
            "goal": memory.goal,
            "steps_taken": len(memory.steps_taken),
            "final_state": memory.current_state.value,
            "summary": summary,
            "all_steps": memory.steps_taken,
            "reasoning_chain": memory.reasoning_chain,
            "context": memory.context
        }
    
    def _generate_task_summary(self, memory: AgentMemory) -> str:
        """Generate a human-readable summary of task completion."""
        if memory.current_state == AgentState.COMPLETED:
            return f"Successfully completed task: {memory.goal}. Took {len(memory.steps_taken)} steps."
        elif memory.current_state == AgentState.ERROR:
            return f"Task failed: {memory.goal}. Error occurred during execution."
        else:
            return f"Task incomplete: {memory.goal}. Reached maximum steps ({len(memory.steps_taken)})."
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about agent performance."""
        total_executions = len(self.execution_log)
        successful_executions = sum(1 for log in self.execution_log if log.get("success", False))
        
        if total_executions > 0:
            success_rate = successful_executions / total_executions
            avg_execution_time = sum(log.get("execution_time", 0) for log in self.execution_log) / total_executions
        else:
            success_rate = 0
            avg_execution_time = 0
        
        return {
            "agent_name": self.agent_name,
            "total_tasks": len(self.memory_store),
            "total_tool_executions": total_executions,
            "success_rate": round(success_rate, 3),
            "average_execution_time": round(avg_execution_time, 3),
            "available_tools": list(self.available_actions.keys()),
            "llm_available": self.llm_available
        }

def demo_simple_agent():
    """
    Demonstrate simple agent capabilities with various scenarios.
    """
    print("=== Phase 2a: Simple Agent Logic Demo ===\n")
    
    # Initialize agent
    print("🤖 Initializing Simple Agent...")
    agent = SimpleAgent("CustomerServiceAgent")
    
    print(f"✅ Agent initialized with {len(agent.available_actions)} tools:")
    for tool_name, action in agent.available_actions.items():
        print(f"  • {tool_name}: {action.description}")
    
    # Scenario 1: Customer lookup and simple reasoning
    print("\n" + "="*50)
    print("🎯 Scenario 1: Customer Information Lookup")
    
    task1_id = "task_customer_lookup"
    goal1 = "Help customer john.doe@email.com with their inquiry"
    situation1 = "Customer john.doe@email.com is asking about their account status"
    
    agent.create_task_memory(task1_id, goal1)
    result1 = agent.solve_task(task1_id, situation1)
    
    print(f"Goal: {goal1}")
    print(f"Situation: {situation1}")
    print(f"Result: {result1['summary']}")
    print(f"Steps taken: {result1['steps_taken']}")
    
    if result1['all_steps']:
        print("Detailed steps:")
        for step in result1['all_steps']:
            print(f"  {step['step_number']}. {step['action']} → {step['result'].get('success', False)}")
    
    # Scenario 2: Knowledge search and reasoning
    print("\n" + "="*50)
    print("🎯 Scenario 2: Knowledge-Based Question")
    
    task2_id = "task_return_policy"
    goal2 = "Answer customer question about return policy"
    situation2 = "Customer wants to know how to return a product they bought last week"
    
    agent.create_task_memory(task2_id, goal2)
    result2 = agent.solve_task(task2_id, situation2)
    
    print(f"Goal: {goal2}")
    print(f"Situation: {situation2}")
    print(f"Result: {result2['summary']}")
    print(f"Knowledge found: {len(result2['context'].get('knowledge_results', []))} items")
    
    # Scenario 3: Multi-step problem solving
    print("\n" + "="*50)
    print("🎯 Scenario 3: Complex Customer Issue")
    
    task3_id = "task_complex_issue"
    goal3 = "Handle a customer complaint requiring ticket creation"
    situation3 = "Customer sarah.smith@email.com has a defective product and needs help with return and refund"
    
    agent.create_task_memory(task3_id, goal3)
    result3 = agent.solve_task(task3_id, situation3)
    
    print(f"Goal: {goal3}")
    print(f"Situation: {situation3}")
    print(f"Result: {result3['summary']}")
    print(f"Final context keys: {list(result3['context'].keys())}")
    
    # Show reasoning chain for complex task
    if result3['reasoning_chain']:
        print("\nReasoning chain:")
        for i, reasoning in enumerate(result3['reasoning_chain'][:3], 1):
            print(f"  {i}. {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}")
    
    # Scenario 4: Error handling and fallback
    print("\n" + "="*50)
    print("🎯 Scenario 4: Error Handling")
    
    task4_id = "task_error_handling"
    goal4 = "Handle invalid customer email"
    situation4 = "Customer with email invalid@notfound.com needs assistance"
    
    agent.create_task_memory(task4_id, goal4)
    result4 = agent.solve_task(task4_id, situation4)
    
    print(f"Goal: {goal4}")
    print(f"Situation: {situation4}")
    print(f"Result: {result4['summary']}")
    
    # Agent performance summary
    print("\n" + "="*50)
    print("📊 Agent Performance Summary")
    
    stats = agent.get_agent_stats()
    print(f"  • Agent Name: {stats['agent_name']}")
    print(f"  • Total Tasks: {stats['total_tasks']}")
    print(f"  • Tool Executions: {stats['total_tool_executions']}")
    print(f"  • Success Rate: {stats['success_rate']:.1%}")
    print(f"  • Avg Execution Time: {stats['average_execution_time']:.3f}s")
    print(f"  • LLM Available: {stats['llm_available']}")
    
    # Tool usage analysis
    print("\n🔧 Tool Usage Analysis:")
    tool_usage = {}
    for log in agent.execution_log:
        action = log.get('action', 'unknown')
        tool_usage[action] = tool_usage.get(action, 0) + 1
    
    for tool, count in sorted(tool_usage.items()):
        print(f"  • {tool}: {count} times")

def interactive_agent():
    """Interactive mode for experimenting with the agent."""
    print("\n=== Interactive Agent Mode ===")
    print("Type 'quit' to exit, 'stats' for agent statistics, 'tools' to see available tools")
    
    agent = SimpleAgent("InteractiveAgent")
    
    while True:
        try:
            user_input = input("\n🎯 Describe a customer service scenario: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'stats':
                stats = agent.get_agent_stats()
                print(f"\n📊 Agent Stats:")
                for key, value in stats.items():
                    print(f"  • {key}: {value}")
                continue
            elif user_input.lower() == 'tools':
                print(f"\n🔧 Available Tools:")
                for name, action in agent.available_actions.items():
                    print(f"  • {name}: {action.description}")
                continue
            elif not user_input:
                continue
            
            # Create and solve task
            task_id = f"interactive_{int(time.time())}"
            goal = f"Handle customer scenario: {user_input}"
            
            agent.create_task_memory(task_id, goal)
            
            print("\n🤖 Agent working...")
            result = agent.solve_task(task_id, user_input)
            
            print(f"\n✅ Task Result:")
            print(f"  Status: {result['final_state']}")
            print(f"  Steps: {result['steps_taken']}")
            print(f"  Summary: {result['summary']}")
            
            if result['all_steps']:
                print(f"\n📋 Steps taken:")
                for step in result['all_steps'][-3:]:  # Show last 3 steps
                    action = step['action']
                    success = step['result'].get('success', False)
                    status = "✅" if success else "❌"
                    print(f"    {status} {action}: {step['reasoning'][:80]}...")
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run demonstration
    demo_simple_agent()
    
    # Optional interactive mode
    print("\n" + "="*60)
    choice = input("Would you like to try interactive agent mode? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_agent()
    
    print("\n🎓 Phase 2a Complete!")
    print("Next: Phase 2b - Multi-step Agent Processing")