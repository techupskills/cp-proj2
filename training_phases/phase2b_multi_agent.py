#!/usr/bin/env python3
"""
Phase 2b: Multi-step Agent Processing (90 min)
Day 2 - AI Agents Part 2: Multi-agent design patterns and using RAG with agents

Learning Objectives:
- Multi-agent design patterns
- Using RAG with agents
- Hands-on: Creating an AI agent to process structured business data with canonical queries
- Future of AI agents in enterprise workflows

This module explores advanced agent architectures, including multi-agent coordination
and integration with RAG systems for enhanced reasoning capabilities.
"""

import logging
import json
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Import previous phase capabilities
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1a_basic_llm import BasicLLMClient
    from phase1d_basic_rag import BasicRAGSystem
    from phase2a_simple_agent import SimpleAgent, AgentState, AgentMemory
    RAG_AVAILABLE = True
    AGENT_AVAILABLE = True
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    RAG_AVAILABLE = False
    AGENT_AVAILABLE = False
    LLM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("multi-agent")

class AgentRole(Enum):
    """Specialized agent roles in multi-agent system"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    RESPONDER = "responder"
    VALIDATOR = "validator"

@dataclass
class AgentMessage:
    """Message passed between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    message_type: str = "info"
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1=low, 5=high

@dataclass
class WorkflowStep:
    """Represents a step in a multi-agent workflow"""
    step_id: str
    agent_role: AgentRole
    description: str
    inputs_required: List[str]
    outputs_produced: List[str]
    depends_on: List[str] = field(default_factory=list)
    completed: bool = False
    result: Dict[str, Any] = field(default_factory=dict)

class RAGEnhancedAgent(SimpleAgent):
    """
    Agent enhanced with RAG capabilities for knowledge-based reasoning.
    Extends the basic agent with sophisticated information retrieval.
    """
    
    def __init__(self, 
                 agent_name: str,
                 role: AgentRole,
                 rag_system: Optional[BasicRAGSystem] = None,
                 **kwargs):
        """
        Initialize RAG-enhanced agent.
        
        Args:
            agent_name: Name of the agent
            role: Agent's specialized role
            rag_system: RAG system for knowledge retrieval
        """
        super().__init__(agent_name, **kwargs)
        self.role = role
        self.rag_system = rag_system
        self.message_inbox = []
        self.message_outbox = []
        
        # Enhanced capabilities
        self._register_rag_tools()
        self._register_communication_tools()
        
        logger.info(f"RAG-enhanced agent '{agent_name}' initialized with role: {role.value}")
    
    def _register_rag_tools(self):
        """Register RAG-specific tools."""
        
        def enhanced_knowledge_search(query: str, max_results: int = 3) -> Dict[str, Any]:
            """Search knowledge base using RAG system."""
            if not self.rag_system:
                return {"error": "RAG system not available"}
            
            try:
                # Use RAG system for enhanced search
                context_docs = self.rag_system.retrieve_relevant_context(query, max_results)
                
                return {
                    "success": True,
                    "query": query,
                    "documents": context_docs,
                    "document_count": len(context_docs),
                    "avg_similarity": sum(doc.get('similarity', 0) for doc in context_docs) / len(context_docs) if context_docs else 0
                }
            except Exception as e:
                return {"error": str(e)}
        
        def generate_rag_response(query: str, context_hint: str = "") -> Dict[str, Any]:
            """Generate response using RAG system."""
            if not self.rag_system:
                return {"error": "RAG system not available"}
            
            try:
                full_query = f"{context_hint} {query}".strip()
                rag_response = self.rag_system.generate_response(full_query)
                
                return {
                    "success": rag_response.get('success', False),
                    "response": rag_response.get('response', ''),
                    "context_count": rag_response.get('context_count', 0),
                    "confidence": rag_response.get('avg_context_similarity', 0)
                }
            except Exception as e:
                return {"error": str(e)}
        
        # Register enhanced tools
        self.register_action("enhanced_knowledge_search", "Search knowledge base with RAG", enhanced_knowledge_search, ["query"])
        self.register_action("generate_rag_response", "Generate response using RAG", generate_rag_response, ["query"])
    
    def _register_communication_tools(self):
        """Register inter-agent communication tools."""
        
        def send_message(to_agent: str, message_type: str, content: Dict[str, Any], priority: int = 1) -> Dict[str, Any]:
            """Send message to another agent."""
            message = AgentMessage(
                from_agent=self.agent_name,
                to_agent=to_agent,
                message_type=message_type,
                content=content,
                priority=priority
            )
            
            self.message_outbox.append(message)
            
            return {
                "success": True,
                "message_id": message.id,
                "to_agent": to_agent,
                "message_type": message_type
            }
        
        def receive_messages(message_type: str = None) -> Dict[str, Any]:
            """Receive and process incoming messages."""
            if message_type:
                messages = [msg for msg in self.message_inbox if msg.message_type == message_type]
            else:
                messages = self.message_inbox.copy()
            
            # Sort by priority and timestamp
            messages.sort(key=lambda x: (-x.priority, x.timestamp))
            
            return {
                "success": True,
                "message_count": len(messages),
                "messages": [
                    {
                        "id": msg.id,
                        "from": msg.from_agent,
                        "type": msg.message_type,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "priority": msg.priority
                    }
                    for msg in messages
                ]
            }
        
        self.register_action("send_message", "Send message to another agent", send_message, ["to_agent", "message_type", "content"])
        self.register_action("receive_messages", "Receive incoming messages", receive_messages, [])
    
    def deliver_message(self, message: AgentMessage):
        """Deliver a message to this agent's inbox."""
        self.message_inbox.append(message)
        logger.info(f"Message delivered to {self.agent_name} from {message.from_agent}")
    
    def get_outgoing_messages(self) -> List[AgentMessage]:
        """Get and clear outgoing messages."""
        messages = self.message_outbox.copy()
        self.message_outbox.clear()
        return messages

class MultiAgentCoordinator:
    """
    Coordinates multiple agents working together on complex tasks.
    Implements various multi-agent design patterns.
    """
    
    def __init__(self, rag_system: Optional[BasicRAGSystem] = None):
        """
        Initialize multi-agent coordinator.
        
        Args:
            rag_system: Shared RAG system for all agents
        """
        self.rag_system = rag_system
        self.agents = {}
        self.workflows = {}
        self.message_history = []
        self.coordination_log = []
        
        # Create specialized agents
        self._create_agent_team()
        
        logger.info(f"Multi-agent coordinator initialized with {len(self.agents)} agents")
    
    def _create_agent_team(self):
        """Create a team of specialized agents."""
        
        # Coordinator agent - orchestrates workflow
        coordinator = RAGEnhancedAgent(
            "CoordinatorAgent",
            AgentRole.COORDINATOR,
            self.rag_system
        )
        
        # Research agent - gathers information
        researcher = RAGEnhancedAgent(
            "ResearchAgent", 
            AgentRole.RESEARCHER,
            self.rag_system
        )
        
        # Analyst agent - analyzes data and patterns
        analyst = RAGEnhancedAgent(
            "AnalystAgent",
            AgentRole.ANALYST,
            self.rag_system
        )
        
        # Response agent - generates customer responses
        responder = RAGEnhancedAgent(
            "ResponderAgent",
            AgentRole.RESPONDER,
            self.rag_system
        )
        
        # Validator agent - validates quality of responses
        validator = RAGEnhancedAgent(
            "ValidatorAgent",
            AgentRole.VALIDATOR,
            self.rag_system
        )
        
        self.agents = {
            agent.agent_name: agent for agent in [coordinator, researcher, analyst, responder, validator]
        }
    
    def create_workflow(self, workflow_id: str, steps: List[WorkflowStep]) -> bool:
        """
        Create a new multi-agent workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            steps: List of workflow steps
            
        Returns:
            True if workflow created successfully
        """
        try:
            # Validate workflow dependencies
            step_ids = {step.step_id for step in steps}
            for step in steps:
                for dep in step.depends_on:
                    if dep not in step_ids:
                        raise ValueError(f"Step {step.step_id} depends on non-existent step {dep}")
            
            self.workflows[workflow_id] = {
                "steps": steps,
                "status": "created",
                "created_at": datetime.now(),
                "results": {}
            }
            
            logger.info(f"Created workflow {workflow_id} with {len(steps)} steps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create workflow {workflow_id}: {e}")
            return False
    
    def execute_workflow(self, workflow_id: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow.
        
        Args:
            workflow_id: Workflow to execute
            initial_data: Initial data for the workflow
            
        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow = self.workflows[workflow_id]
        workflow["status"] = "running"
        workflow["started_at"] = datetime.now()
        
        execution_context = initial_data.copy()
        completed_steps = set()
        
        try:
            # Execute steps in dependency order
            while len(completed_steps) < len(workflow["steps"]):
                progress_made = False
                
                for step in workflow["steps"]:
                    if step.step_id in completed_steps:
                        continue
                    
                    # Check if dependencies are satisfied
                    if all(dep in completed_steps for dep in step.depends_on):
                        logger.info(f"Executing step: {step.step_id}")
                        
                        # Execute step with appropriate agent
                        result = self._execute_workflow_step(step, execution_context)
                        
                        if result.get("success", False):
                            step.completed = True
                            step.result = result
                            completed_steps.add(step.step_id)
                            
                            # Update execution context with results
                            for output in step.outputs_produced:
                                if output in result:
                                    execution_context[output] = result[output]
                            
                            progress_made = True
                            
                            self.coordination_log.append({
                                "workflow_id": workflow_id,
                                "step_id": step.step_id,
                                "agent": step.agent_role.value,
                                "status": "completed",
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            logger.error(f"Step {step.step_id} failed: {result.get('error')}")
                            workflow["status"] = "failed"
                            return {
                                "workflow_id": workflow_id,
                                "status": "failed",
                                "error": f"Step {step.step_id} failed",
                                "completed_steps": len(completed_steps),
                                "total_steps": len(workflow["steps"])
                            }
                
                if not progress_made:
                    # Circular dependency or other issue
                    workflow["status"] = "stuck"
                    return {
                        "workflow_id": workflow_id,
                        "status": "stuck",
                        "error": "No progress possible, check dependencies",
                        "completed_steps": len(completed_steps),
                        "total_steps": len(workflow["steps"])
                    }
            
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now()
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "execution_context": execution_context,
                "completed_steps": len(completed_steps),
                "total_steps": len(workflow["steps"]),
                "duration": (workflow["completed_at"] - workflow["started_at"]).total_seconds()
            }
            
        except Exception as e:
            workflow["status"] = "error"
            logger.error(f"Workflow {workflow_id} failed: {e}")
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            }
    
    def _execute_workflow_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step with the appropriate agent."""
        
        # Find agent for this role
        agent = None
        for agent_instance in self.agents.values():
            if agent_instance.role == step.agent_role:
                agent = agent_instance
                break
        
        if not agent:
            return {"error": f"No agent found for role {step.agent_role.value}"}
        
        # Prepare task for agent
        task_id = f"workflow_{step.step_id}_{int(time.time())}"
        goal = step.description
        
        # Create situation description with available context
        situation_parts = [f"Workflow step: {step.description}"]
        
        for input_key in step.inputs_required:
            if input_key in context:
                situation_parts.append(f"{input_key}: {json.dumps(context[input_key])}")
        
        situation = " | ".join(situation_parts)
        
        # Execute with agent
        agent.create_task_memory(task_id, goal, {"workflow_step": step.step_id, "context": context})
        result = agent.solve_task(task_id, situation)
        
        if result["final_state"] == "completed":
            return {"success": True, **result["context"]}
        else:
            return {"success": False, "error": result.get("summary", "Step failed")}
    
    def route_messages(self):
        """Route messages between agents."""
        for agent in self.agents.values():
            outgoing = agent.get_outgoing_messages()
            
            for message in outgoing:
                if message.to_agent in self.agents:
                    self.agents[message.to_agent].deliver_message(message)
                    self.message_history.append(message)
                    
                    logger.info(f"Routed message: {message.from_agent} → {message.to_agent}")
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination statistics."""
        return {
            "total_agents": len(self.agents),
            "agent_roles": [agent.role.value for agent in self.agents.values()],
            "workflows_created": len(self.workflows),
            "messages_routed": len(self.message_history),
            "coordination_events": len(self.coordination_log)
        }

def create_customer_service_workflow() -> List[WorkflowStep]:
    """Create a comprehensive customer service workflow."""
    
    steps = [
        WorkflowStep(
            step_id="research_customer",
            agent_role=AgentRole.RESEARCHER,
            description="Research customer information and history",
            inputs_required=["customer_email"],
            outputs_produced=["customer_info", "customer_history"]
        ),
        
        WorkflowStep(
            step_id="research_knowledge",
            agent_role=AgentRole.RESEARCHER, 
            description="Research relevant knowledge base information",
            inputs_required=["customer_query"],
            outputs_produced=["knowledge_results", "relevant_policies"]
        ),
        
        WorkflowStep(
            step_id="analyze_situation",
            agent_role=AgentRole.ANALYST,
            description="Analyze customer situation and determine best approach",
            inputs_required=["customer_info", "customer_query", "knowledge_results"],
            outputs_produced=["situation_analysis", "recommended_actions"],
            depends_on=["research_customer", "research_knowledge"]
        ),
        
        WorkflowStep(
            step_id="generate_response",
            agent_role=AgentRole.RESPONDER,
            description="Generate customer response based on analysis",
            inputs_required=["situation_analysis", "relevant_policies", "customer_info"],
            outputs_produced=["draft_response", "response_metadata"],
            depends_on=["analyze_situation"]
        ),
        
        WorkflowStep(
            step_id="validate_response",
            agent_role=AgentRole.VALIDATOR,
            description="Validate response quality and accuracy",
            inputs_required=["draft_response", "customer_query", "relevant_policies"],
            outputs_produced=["validation_result", "final_response", "quality_score"],
            depends_on=["generate_response"]
        )
    ]
    
    return steps

def demo_multi_agent_system():
    """
    Demonstrate multi-agent system capabilities.
    """
    print("=== Phase 2b: Multi-step Agent Processing Demo ===\n")
    
    # Check dependencies
    if not all([RAG_AVAILABLE, AGENT_AVAILABLE]):
        print("❌ Required dependencies not available")
        return
    
    # Initialize RAG system for knowledge base
    print("📚 Setting up RAG system for multi-agent knowledge...")
    try:
        if RAG_AVAILABLE:
            # Create sample knowledge base
            from phase1d_basic_rag import create_sample_knowledge_base
            knowledge_dir = create_sample_knowledge_base()
            
            rag_system = BasicRAGSystem("./multi_agent_rag_db")
            success = rag_system.setup_knowledge_base(knowledge_dir)
            
            if success:
                print("✅ RAG system ready for multi-agent use")
            else:
                print("⚠️ RAG system setup failed, using mock data")
                rag_system = None
        else:
            rag_system = None
    except Exception as e:
        print(f"⚠️ RAG setup failed: {e}")
        rag_system = None
    
    # Initialize multi-agent coordinator
    print("\n🤖 Initializing multi-agent system...")
    coordinator = MultiAgentCoordinator(rag_system)
    
    print(f"✅ Multi-agent system ready with {len(coordinator.agents)} specialized agents:")
    for agent_name, agent in coordinator.agents.items():
        print(f"  • {agent_name} ({agent.role.value}): {len(agent.available_actions)} tools")
    
    # Create and execute customer service workflow
    print("\n" + "="*50)
    print("🔄 Customer Service Workflow Demonstration")
    
    workflow_steps = create_customer_service_workflow()
    workflow_id = "customer_service_demo"
    
    success = coordinator.create_workflow(workflow_id, workflow_steps)
    if not success:
        print("❌ Failed to create workflow")
        return
    
    print(f"✅ Created workflow with {len(workflow_steps)} steps:")
    for step in workflow_steps:
        deps_str = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
        print(f"  • {step.step_id} [{step.agent_role.value}]: {step.description}{deps_str}")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Return Policy Question",
            "customer_email": "john.doe@email.com",
            "customer_query": "I need to return a product I bought last week. What's the process?"
        },
        {
            "name": "Shipping Inquiry",
            "customer_email": "sarah.smith@email.com", 
            "customer_query": "How long will my order take to arrive and what are the shipping costs?"
        },
        {
            "name": "Account Issue",
            "customer_email": "customer@example.com",
            "customer_query": "I can't log into my account and need to reset my password"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"Customer: {scenario['customer_email']}")
        print(f"Query: {scenario['customer_query']}")
        
        # Execute workflow
        initial_data = {
            "customer_email": scenario["customer_email"],
            "customer_query": scenario["customer_query"]
        }
        
        print("🔄 Executing multi-agent workflow...")
        start_time = time.time()
        
        result = coordinator.execute_workflow(workflow_id, initial_data)
        
        execution_time = time.time() - start_time
        
        print(f"⏱️ Execution time: {execution_time:.2f}s")
        print(f"📊 Status: {result['status']}")
        
        if result["status"] == "completed":
            print(f"✅ Completed {result['completed_steps']}/{result['total_steps']} steps")
            
            # Show key results
            context = result.get("execution_context", {})
            if "final_response" in context:
                response = context["final_response"]
                print(f"🤖 Final Response: {response[:200]}{'...' if len(str(response)) > 200 else ''}")
            
            if "quality_score" in context:
                print(f"⭐ Quality Score: {context['quality_score']}")
                
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
        
        # Route any pending messages
        coordinator.route_messages()
    
    # Multi-agent communication demonstration
    print("\n" + "="*50)
    print("💬 Multi-Agent Communication Demo")
    
    researcher = coordinator.agents["ResearchAgent"]
    analyst = coordinator.agents["AnalystAgent"]
    
    # Create communication task
    researcher.create_task_memory("comm_demo", "Communicate findings to analyst")
    
    # Send message from researcher to analyst
    message_result = researcher.execute_action("send_message", {
        "to_agent": "AnalystAgent",
        "message_type": "research_findings",
        "content": {
            "findings": "Customer has premium tier status",
            "confidence": 0.9,
            "source": "customer_database"
        },
        "priority": 3
    })
    
    print(f"📨 Message sent: {message_result}")
    
    # Route messages
    coordinator.route_messages()
    
    # Receive messages at analyst
    analyst.create_task_memory("receive_demo", "Process incoming research findings")
    
    receive_result = analyst.execute_action("receive_messages", {
        "message_type": "research_findings"
    })
    
    print(f"📬 Messages received: {receive_result}")
    
    # System performance analysis
    print("\n" + "="*50)
    print("📊 Multi-Agent System Analysis")
    
    stats = coordinator.get_coordination_stats()
    print(f"  • Total Agents: {stats['total_agents']}")
    print(f"  • Agent Roles: {', '.join(stats['agent_roles'])}")
    print(f"  • Workflows Created: {stats['workflows_created']}")
    print(f"  • Messages Routed: {stats['messages_routed']}")
    print(f"  • Coordination Events: {stats['coordination_events']}")
    
    # Individual agent performance
    print("\n🔧 Individual Agent Performance:")
    for agent_name, agent in coordinator.agents.items():
        agent_stats = agent.get_agent_stats()
        print(f"  • {agent_name}:")
        print(f"    - Tasks: {agent_stats['total_tasks']}")
        print(f"    - Tool Executions: {agent_stats['total_tool_executions']}")
        print(f"    - Success Rate: {agent_stats['success_rate']:.1%}")
    
    # Workflow analysis
    print("\n📈 Workflow Analysis:")
    workflow = coordinator.workflows[workflow_id]
    print(f"  • Workflow Status: {workflow['status']}")
    print(f"  • Total Executions: {len(test_scenarios)}")
    
    if coordinator.coordination_log:
        print(f"  • Coordination Events: {len(coordinator.coordination_log)}")
        print("  • Recent Events:")
        for event in coordinator.coordination_log[-5:]:
            print(f"    - {event['timestamp'][:19]}: {event['agent']} completed {event['step_id']}")

def interactive_multi_agent():
    """Interactive multi-agent system for experimentation."""
    print("\n=== Interactive Multi-Agent System ===")
    print("Type 'quit' to exit, 'agents' to see agents, 'workflow' to create custom workflow")
    
    # Setup
    try:
        coordinator = MultiAgentCoordinator()
        workflow_steps = create_customer_service_workflow()
        coordinator.create_workflow("interactive_workflow", workflow_steps)
        
        print("✅ Interactive multi-agent system ready")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return
    
    while True:
        try:
            user_input = input("\n🎯 Enter customer scenario (email:query): ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'agents':
                print("\n🤖 Available Agents:")
                for name, agent in coordinator.agents.items():
                    print(f"  • {name} ({agent.role.value})")
                continue
            elif user_input.lower() == 'workflow':
                print("\n🔄 Workflow Steps:")
                for step in workflow_steps:
                    print(f"  • {step.step_id}: {step.description}")
                continue
            elif ':' not in user_input:
                print("❌ Please use format: email:query")
                continue
            
            # Parse input
            email, query = user_input.split(':', 1)
            email = email.strip()
            query = query.strip()
            
            if not email or not query:
                print("❌ Both email and query required")
                continue
            
            # Execute workflow
            print(f"\n🔄 Processing with multi-agent system...")
            
            initial_data = {
                "customer_email": email,
                "customer_query": query
            }
            
            result = coordinator.execute_workflow("interactive_workflow", initial_data)
            
            print(f"\n📊 Result: {result['status']}")
            
            if result["status"] == "completed":
                context = result.get("execution_context", {})
                if "final_response" in context:
                    print(f"🤖 Response: {context['final_response']}")
                if "quality_score" in context:
                    print(f"⭐ Quality: {context['quality_score']}")
            else:
                print(f"❌ Error: {result.get('error')}")
            
            # Route messages
            coordinator.route_messages()
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run demonstration
    demo_multi_agent_system()
    
    # Optional interactive mode
    print("\n" + "="*60)
    choice = input("Would you like to try interactive multi-agent mode? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_multi_agent()
    
    print("\n🎓 Phase 2b Complete!")
    print("Next: Phase 2c - MCP Server Implementation")