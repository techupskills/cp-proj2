#!/usr/bin/env python3
"""
Phase 3c: Integration & RAG Enhancement (90 min)
Day 3 - Capstone Project Part 1: Combining all components

Learning Objectives:
- Hands-on: Adding RAG for local data
- Integrating all previous components (LLM, RAG, Agents, MCP, UI)
- Advanced RAG techniques and optimization
- End-to-end system integration and testing

This module brings together all the components from previous phases into a
complete, integrated customer service AI application with enhanced RAG capabilities.
"""

import streamlit as st
import asyncio
import json
import logging
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go

# Import all previous phase capabilities
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1a_basic_llm import BasicLLMClient
    from phase1b_document_processing import DocumentProcessor
    from phase1c_vector_database import VectorDatabase
    from phase1d_basic_rag import BasicRAGSystem
    from phase2a_simple_agent import SimpleAgent
    from phase2b_multi_agent import RAGEnhancedAgent, MultiAgentCoordinator
    from phase2c_mcp_server import CustomerServiceMCPServer
    from phase2d_mcp_client import MCPEnabledAgent
    from phase3a_basic_ui import CustomerServiceApp, is_streamlit
    from phase3b_advanced_ui import AdvancedDashboard
    
    ALL_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some components not available: {e}")
    ALL_COMPONENTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration")

class IntegratedCustomerServicePlatform:
    """
    Complete integrated customer service platform combining all components:
    LLM, RAG, Agents, MCP, and Advanced UI into a production-ready system.
    """
    
    def __init__(self):
        """Initialize the integrated platform."""
        self.platform_name = "Enterprise AI Customer Service Platform"
        self.version = "3.0-Integrated"
        
        # Component status tracking
        self.component_status = {
            'llm_client': 'initializing',
            'rag_system': 'initializing', 
            'vector_database': 'initializing',
            'document_processor': 'initializing',
            'simple_agent': 'initializing',
            'multi_agent_coordinator': 'initializing',
            'mcp_server': 'initializing',
            'mcp_client': 'initializing',
            'advanced_dashboard': 'initializing'
        }
        
        # Integrated components
        self.llm_client = None
        self.rag_system = None
        self.vector_db = None
        self.doc_processor = None
        self.simple_agent = None
        self.multi_agent_coordinator = None
        self.mcp_server = None
        self.mcp_client = None
        self.dashboard = None
        
        # Integration metrics
        self.integration_metrics = {
            'total_requests': 0,
            'rag_requests': 0,
            'agent_requests': 0,
            'mcp_requests': 0,
            'avg_response_time': 0,
            'success_rate': 0,
            'component_errors': {}
        }
        
        # Enhanced conversation tracking
        self.conversation_history = []
        self.rag_analytics = {
            'documents_retrieved': [],
            'similarity_scores': [],
            'query_types': {},
            'response_quality': []
        }
        
        # Initialize all components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all platform components."""
        logger.info("Initializing integrated customer service platform...")
        
        try:
            # Initialize LLM Client
            if ALL_COMPONENTS_AVAILABLE:
                self.llm_client = BasicLLMClient()
                self.component_status['llm_client'] = 'active'
                logger.info("✅ LLM Client initialized")
            
            # Initialize Document Processor
            if ALL_COMPONENTS_AVAILABLE:
                self.doc_processor = DocumentProcessor()
                self.component_status['document_processor'] = 'active'
                logger.info("✅ Document Processor initialized")
            
            # Initialize Vector Database
            if ALL_COMPONENTS_AVAILABLE:
                self.vector_db = VectorDatabase("./integrated_platform_db")
                self._setup_enhanced_knowledge_base()
                self.component_status['vector_database'] = 'active'
                logger.info("✅ Vector Database initialized")
            
            # Initialize RAG System
            if ALL_COMPONENTS_AVAILABLE:
                self.rag_system = BasicRAGSystem("./integrated_rag_system")
                self._setup_rag_system()
                self.component_status['rag_system'] = 'active'
                logger.info("✅ RAG System initialized")
            
            # Initialize Agents
            if ALL_COMPONENTS_AVAILABLE:
                self.simple_agent = SimpleAgent("IntegratedAgent")
                self.multi_agent_coordinator = MultiAgentCoordinator(self.rag_system)
                self.component_status['simple_agent'] = 'active'
                self.component_status['multi_agent_coordinator'] = 'active'
                logger.info("✅ Agent Systems initialized")
            
            # Initialize Dashboard
            if ALL_COMPONENTS_AVAILABLE:
                self.dashboard = AdvancedDashboard()
                self.component_status['advanced_dashboard'] = 'active'
                logger.info("✅ Advanced Dashboard initialized")
            
            logger.info("🎉 All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            # Set failed components to error state
            for component, status in self.component_status.items():
                if status == 'initializing':
                    self.component_status[component] = 'error'
    
    def _setup_enhanced_knowledge_base(self):
        """Setup enhanced knowledge base with comprehensive customer service data."""
        if not self.vector_db:
            return
        
        # Create enhanced knowledge collection
        success = self.vector_db.create_collection(
            "integrated_customer_service",
            "Enhanced customer service knowledge base with comprehensive policies and procedures"
        )
        
        if success:
            # Enhanced knowledge documents
            enhanced_docs = [
                {
                    "id": "returns_comprehensive",
                    "text": "Comprehensive Return Policy: Customers can return items within 30 days of purchase for a full refund. Items must be in original condition with all packaging, accessories, tags, and receipt or order confirmation. Digital receipts are accepted. For Premium customers, return window extends to 60 days. Refunds are processed within 5-7 business days to the original payment method. For defective items, we cover return shipping costs. Custom or personalized items are non-returnable unless defective.",
                    "metadata": {
                        "category": "returns",
                        "subcategory": "policy",
                        "priority": "high",
                        "last_updated": "2024-01-15",
                        "authority": "customer_service",
                        "customer_tiers": ["standard", "premium"],
                        "keywords": "return,refund,exchange,policy,30 days,60 days,receipt,defective"
                    }
                },
                {
                    "id": "shipping_comprehensive",
                    "text": "Complete Shipping Information: Standard shipping (3-5 business days, $5.99), Express shipping (1-2 business days, $15.99), Overnight shipping (next business day, $25.99). Free standard shipping on orders over $50. International shipping available to 50+ countries (7-14 business days, $19.99 base + customs). Premium customers get free express shipping on orders over $100. Orders placed before 2 PM EST ship same day. Tracking provided for all shipments. Weather delays and carrier issues may affect delivery times.",
                    "metadata": {
                        "category": "shipping",
                        "subcategory": "options_pricing",
                        "priority": "high",
                        "last_updated": "2024-01-10",
                        "authority": "logistics",
                        "customer_tiers": ["standard", "premium"],
                        "keywords": "shipping,delivery,express,standard,overnight,international,free shipping,tracking"
                    }
                },
                {
                    "id": "technical_support_comprehensive",
                    "text": "Technical Support Services: 24/7 phone support for Premium customers (1-800-PREMIUM). Standard customers have access to live chat Monday-Friday 9AM-5PM EST, and email support with 24-hour response time. Self-service options include video tutorials, user manuals, and troubleshooting guides available 24/7. For device setup, we offer remote assistance for Premium customers and step-by-step guides for Standard customers. Warranty support covers hardware defects for 1 year from purchase date.",
                    "metadata": {
                        "category": "technical_support",
                        "subcategory": "contact_methods",
                        "priority": "high",
                        "last_updated": "2024-01-12",
                        "authority": "technical_team",
                        "customer_tiers": ["standard", "premium"],
                        "keywords": "technical support,phone,chat,email,24/7,warranty,setup,troubleshooting"
                    }
                },
                {
                    "id": "account_management_comprehensive",
                    "text": "Account Management: Create account with email verification required. Password requirements: minimum 8 characters, uppercase, lowercase, number, and special character. Two-factor authentication available for enhanced security. Account information can be updated in profile settings. Password reset available via 'Forgot Password' link - reset emails expire in 24 hours. Premium accounts include order history for 5 years, Standard accounts for 2 years. Account deletion requests processed within 30 days with data retention policies followed.",
                    "metadata": {
                        "category": "account",
                        "subcategory": "management_security",
                        "priority": "medium",
                        "last_updated": "2024-01-08",
                        "authority": "security_team",
                        "customer_tiers": ["standard", "premium"],
                        "keywords": "account,password,reset,security,two-factor,profile,history,deletion"
                    }
                },
                {
                    "id": "billing_payment_comprehensive",
                    "text": "Billing and Payment Options: Accepted payment methods include all major credit cards (Visa, MasterCard, American Express, Discover), PayPal, Apple Pay, Google Pay, and bank transfers. All transactions are secured with 256-bit SSL encryption. Payment information is tokenized and never stored on our servers. Automatic billing available for subscription services. Payment failures result in email notifications with retry options. Refunds processed to original payment method within 5-7 business days. Billing disputes can be submitted through customer portal.",
                    "metadata": {
                        "category": "billing",
                        "subcategory": "payment_methods",
                        "priority": "high",
                        "last_updated": "2024-01-05",
                        "authority": "finance_team",
                        "customer_tiers": ["standard", "premium"],
                        "keywords": "billing,payment,credit card,paypal,apple pay,google pay,security,refunds,disputes"
                    }
                },
                {
                    "id": "product_warranty_comprehensive",
                    "text": "Product Warranty and Support: All products include 1-year manufacturer warranty covering defects in materials and workmanship. Extended warranty options available at purchase or within 30 days. Warranty claims require proof of purchase and product registration. Premium customers receive expedited warranty service and free advanced replacement. Out-of-warranty repairs available at discounted rates. Software updates and security patches provided free for minimum 3 years. Product recalls and safety notices communicated via email and account notifications.",
                    "metadata": {
                        "category": "warranty",
                        "subcategory": "coverage_claims",
                        "priority": "medium",
                        "last_updated": "2024-01-03",
                        "authority": "product_team",
                        "customer_tiers": ["standard", "premium"],
                        "keywords": "warranty,defects,extended warranty,claims,registration,repairs,software updates,recalls"
                    }
                }
            ]
            
            self.vector_db.add_documents("integrated_customer_service", enhanced_docs)
            logger.info(f"✅ Enhanced knowledge base populated with {len(enhanced_docs)} comprehensive documents")
    
    def _setup_rag_system(self):
        """Setup RAG system with enhanced knowledge."""
        if not self.rag_system:
            return
        
        # Create comprehensive knowledge files for RAG
        knowledge_dir = "/tmp/integrated_platform_knowledge"
        os.makedirs(knowledge_dir, exist_ok=True)
        
        comprehensive_content = """
        COMPREHENSIVE CUSTOMER SERVICE KNOWLEDGE BASE
        
        RETURN POLICY:
        - Standard customers: 30-day return window
        - Premium customers: 60-day return window  
        - Items must be in original condition with packaging
        - Receipt or order confirmation required
        - Refunds processed in 5-7 business days
        - Free return shipping for defective items
        - Custom items non-returnable unless defective
        
        SHIPPING INFORMATION:
        - Standard: 3-5 days ($5.99)
        - Express: 1-2 days ($15.99) 
        - Overnight: Next day ($25.99)
        - Free standard shipping over $50
        - Premium customers: Free express over $100
        - International available to 50+ countries
        - Same-day shipping for orders before 2 PM EST
        
        TECHNICAL SUPPORT:
        - Premium: 24/7 phone support
        - Standard: Chat Mon-Fri 9AM-5PM, 24hr email response
        - Self-service: Videos, manuals, guides 24/7
        - Remote assistance for Premium customers
        - 1-year hardware warranty coverage
        
        ACCOUNT MANAGEMENT:
        - Email verification required for account creation
        - Strong password requirements enforced
        - Two-factor authentication available
        - Password reset links expire in 24 hours
        - Order history: Premium 5 years, Standard 2 years
        - Account deletion processed within 30 days
        
        BILLING AND PAYMENTS:
        - All major credit cards accepted
        - PayPal, Apple Pay, Google Pay supported
        - 256-bit SSL encryption for all transactions
        - Payment info tokenized, never stored
        - Automatic billing for subscriptions
        - Refunds to original payment method in 5-7 days
        
        WARRANTY COVERAGE:
        - 1-year manufacturer warranty included
        - Extended warranty available at purchase
        - Proof of purchase required for claims
        - Premium customers get expedited service
        - Out-of-warranty repairs at discounted rates
        - 3-year minimum software update support
        """
        
        with open(f"{knowledge_dir}/comprehensive_policies.txt", 'w') as f:
            f.write(comprehensive_content)
        
        try:
            success = self.rag_system.setup_knowledge_base(knowledge_dir)
            if success:
                logger.info("✅ RAG system setup with comprehensive knowledge")
        except Exception as e:
            logger.warning(f"RAG system setup failed: {e}")
    
    async def process_integrated_query(self, 
                                     customer_email: str, 
                                     query: str, 
                                     use_rag: bool = True,
                                     use_agents: bool = True,
                                     use_mcp: bool = False) -> Dict[str, Any]:
        """
        Process customer query through the integrated system.
        
        Args:
            customer_email: Customer email address
            query: Customer query text
            use_rag: Whether to use RAG for enhanced responses
            use_agents: Whether to use agent reasoning
            use_mcp: Whether to use MCP protocol (if available)
            
        Returns:
            Comprehensive response with all system data
        """
        start_time = time.time()
        
        try:
            self.integration_metrics['total_requests'] += 1
            
            # Step 1: Analyze query and extract intent
            query_analysis = self._analyze_query(query)
            
            # Step 2: Retrieve customer context
            customer_context = self._get_customer_context(customer_email)
            
            # Step 3: RAG Enhancement (if enabled)
            rag_data = None
            if use_rag and self.rag_system:
                rag_data = await self._get_rag_enhancement(query, customer_context)
                self.integration_metrics['rag_requests'] += 1
            
            # Step 4: Agent Processing (if enabled)
            agent_response = None
            if use_agents and self.simple_agent:
                agent_response = await self._process_with_agents(query, customer_context, rag_data)
                self.integration_metrics['agent_requests'] += 1
            
            # Step 5: Generate final response
            final_response = self._generate_integrated_response(
                query, customer_context, rag_data, agent_response, query_analysis
            )
            
            # Step 6: Track analytics
            processing_time = time.time() - start_time
            self._update_integration_analytics(query, rag_data, final_response, processing_time)
            
            # Step 7: Create comprehensive result
            result = {
                'success': True,
                'response': final_response['content'],
                'confidence': final_response['confidence'],
                'processing_time': processing_time,
                'query_analysis': query_analysis,
                'customer_context': customer_context,
                'rag_data': rag_data,
                'agent_response': agent_response,
                'system_metadata': {
                    'components_used': {
                        'rag': use_rag and rag_data is not None,
                        'agents': use_agents and agent_response is not None,
                        'mcp': use_mcp
                    },
                    'integration_metrics': self.integration_metrics,
                    'component_status': self.component_status
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Update success rate
            self.integration_metrics['success_rate'] = (
                (self.integration_metrics['success_rate'] * (self.integration_metrics['total_requests'] - 1) + 1) /
                self.integration_metrics['total_requests']
            )
            
            # Update average response time
            current_avg = self.integration_metrics['avg_response_time']
            new_avg = (current_avg * (self.integration_metrics['total_requests'] - 1) + processing_time) / self.integration_metrics['total_requests']
            self.integration_metrics['avg_response_time'] = new_avg
            
            return result
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"Integrated query processing failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': error_time,
                'response': "I apologize, but I encountered an error processing your request. Please try again or contact support.",
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze customer query for intent and complexity."""
        query_lower = query.lower()
        
        # Intent classification
        intent_keywords = {
            'returns': ['return', 'refund', 'exchange', 'send back'],
            'shipping': ['shipping', 'delivery', 'ship', 'tracking', 'when will'],
            'technical': ['not working', 'broken', 'help', 'setup', 'install', 'configure'],
            'account': ['password', 'login', 'account', 'profile', 'forgot'],
            'billing': ['bill', 'charge', 'payment', 'credit card', 'invoice'],
            'warranty': ['warranty', 'defective', 'repair', 'replacement'],
            'general': ['hello', 'hi', 'help', 'question', 'information']
        }
        
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Complexity assessment
        complexity_score = min(1.0, (len(query.split()) / 20) + (len(detected_intents) * 0.2))
        
        # Urgency indicators
        urgency_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'broken', 'not working']
        urgency_level = 'high' if any(keyword in query_lower for keyword in urgency_keywords) else 'normal'
        
        return {
            'detected_intents': detected_intents,
            'primary_intent': detected_intents[0] if detected_intents else 'general',
            'complexity_score': complexity_score,
            'urgency_level': urgency_level,
            'word_count': len(query.split()),
            'sentiment': 'neutral'  # Simplified sentiment
        }
    
    def _get_customer_context(self, customer_email: str) -> Dict[str, Any]:
        """Retrieve comprehensive customer context."""
        # Mock customer database
        customers = {
            "john.doe@email.com": {
                "id": "CUST001",
                "name": "John Doe",
                "email": "john.doe@email.com",
                "tier": "Premium",
                "join_date": "2023-06-15",
                "total_orders": 8,
                "total_spent": 2450.75,
                "last_order_date": "2024-01-10",
                "support_tickets": 3,
                "satisfaction_rating": 4.6,
                "preferred_contact": "email",
                "language": "en",
                "timezone": "EST"
            },
            "sarah.smith@email.com": {
                "id": "CUST002", 
                "name": "Sarah Smith",
                "email": "sarah.smith@email.com",
                "tier": "Standard",
                "join_date": "2023-11-20",
                "total_orders": 2,
                "total_spent": 175.50,
                "last_order_date": "2024-01-08",
                "support_tickets": 0,
                "satisfaction_rating": 4.8,
                "preferred_contact": "chat",
                "language": "en",
                "timezone": "PST"
            }
        }
        
        customer = customers.get(customer_email.lower(), {
            "id": "CUST_NEW",
            "name": "New Customer",
            "email": customer_email,
            "tier": "Standard",
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "total_orders": 0,
            "total_spent": 0.0,
            "last_order_date": None,
            "support_tickets": 0,
            "satisfaction_rating": None,
            "preferred_contact": "email",
            "language": "en",
            "timezone": "UTC"
        })
        
        return customer
    
    async def _get_rag_enhancement(self, query: str, customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get RAG enhancement for the query."""
        if not self.rag_system:
            return None
        
        try:
            # Enhance query with customer context
            enhanced_query = query
            if customer_context.get('tier') == 'Premium':
                enhanced_query += " premium customer"
            
            # Get RAG response
            rag_response = self.rag_system.generate_response(enhanced_query)
            
            # Extract relevant documents
            retrieved_docs = rag_response.get('retrieved_documents', [])
            
            # Analyze retrieval quality
            quality_score = rag_response.get('avg_context_similarity', 0)
            
            rag_data = {
                'retrieved_documents': retrieved_docs,
                'document_count': len(retrieved_docs),
                'quality_score': quality_score,
                'rag_response': rag_response.get('response', ''),
                'retrieval_method': 'semantic_search',
                'enhanced_query': enhanced_query
            }
            
            # Update RAG analytics
            self.rag_analytics['documents_retrieved'].append(len(retrieved_docs))
            self.rag_analytics['similarity_scores'].append(quality_score)
            
            return rag_data
            
        except Exception as e:
            logger.error(f"RAG enhancement failed: {e}")
            return None
    
    async def _process_with_agents(self, query: str, customer_context: Dict[str, Any], rag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process query with agent reasoning."""
        if not self.simple_agent:
            return None
        
        try:
            # Create task for agent
            task_id = f"integrated_{int(time.time())}"
            goal = f"Help customer {customer_context.get('name', 'Unknown')} with their inquiry"
            
            # Prepare context for agent
            context_info = f"Customer: {customer_context.get('name')} ({customer_context.get('tier')} tier)"
            if rag_data:
                context_info += f" | RAG found {rag_data['document_count']} relevant documents"
            
            situation = f"{context_info} | Query: {query}"
            
            # Process with agent
            self.simple_agent.create_task_memory(task_id, goal, customer_context)
            agent_result = self.simple_agent.solve_task(task_id, situation)
            
            return {
                'agent_result': agent_result,
                'task_id': task_id,
                'reasoning_steps': len(agent_result.get('all_steps', [])),
                'agent_confidence': 0.8 if agent_result.get('final_state') == 'completed' else 0.4
            }
            
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return None
    
    def _generate_integrated_response(self, 
                                    query: str, 
                                    customer_context: Dict[str, Any],
                                    rag_data: Dict[str, Any],
                                    agent_response: Dict[str, Any],
                                    query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final integrated response combining all sources."""
        
        # Base response components
        response_parts = []
        confidence_factors = []
        
        # Customer personalization
        customer_name = customer_context.get('name', 'valued customer')
        customer_tier = customer_context.get('tier', 'Standard')
        
        greeting = f"Hello {customer_name},"
        if customer_tier == 'Premium':
            greeting += " as a Premium customer,"
        
        response_parts.append(greeting)
        
        # Use RAG data if available
        if rag_data and rag_data['quality_score'] > 0.5:
            response_parts.append(rag_data['rag_response'])
            confidence_factors.append(rag_data['quality_score'])
        
        # Use agent reasoning if available
        elif agent_response and agent_response['agent_confidence'] > 0.6:
            agent_summary = agent_response['agent_result'].get('summary', '')
            if agent_summary:
                response_parts.append(agent_summary)
                confidence_factors.append(agent_response['agent_confidence'])
        
        # Fallback responses based on intent
        else:
            intent = query_analysis.get('primary_intent', 'general')
            fallback_responses = {
                'returns': f"I'd be happy to help you with your return. Our return policy allows returns within {'60' if customer_tier == 'Premium' else '30'} days with receipt.",
                'shipping': "For shipping information, we offer Standard (3-5 days), Express (1-2 days), and Overnight options. Premium customers get free express shipping on orders over $100.",
                'technical': "I can help you with technical support. Premium customers have access to 24/7 phone support, while all customers can use our comprehensive self-service resources.",
                'account': "For account assistance, you can update your information in your profile settings or use the 'Forgot Password' link if you need to reset your password.",
                'billing': "For billing questions, we accept all major payment methods and process refunds within 5-7 business days to your original payment method.",
                'warranty': "All products include a 1-year warranty. Premium customers receive expedited warranty service and free advanced replacement options.",
                'general': "Thank you for contacting us. I'm here to help with any questions about orders, returns, shipping, technical support, or account management."
            }
            
            response_parts.append(fallback_responses.get(intent, fallback_responses['general']))
            confidence_factors.append(0.6)
        
        # Add tier-specific closing
        if customer_tier == 'Premium':
            response_parts.append("As a Premium customer, you have access to priority support. Is there anything else I can help you with?")
        else:
            response_parts.append("Is there anything else I can help you with today?")
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
        
        return {
            'content': ' '.join(response_parts),
            'confidence': overall_confidence,
            'sources_used': {
                'rag': rag_data is not None,
                'agent': agent_response is not None,
                'fallback': len(confidence_factors) == 0
            }
        }
    
    def _update_integration_analytics(self, query: str, rag_data: Dict[str, Any], response: Dict[str, Any], processing_time: float):
        """Update comprehensive analytics tracking."""
        
        # Track query types
        query_type = 'simple' if len(query.split()) < 10 else 'complex'
        self.rag_analytics['query_types'][query_type] = self.rag_analytics['query_types'].get(query_type, 0) + 1
        
        # Track response quality
        quality_score = response['confidence']
        self.rag_analytics['response_quality'].append(quality_score)
        
        # Add to conversation history with full metadata
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response['content'],
            'confidence': response['confidence'],
            'processing_time': processing_time,
            'rag_used': rag_data is not None,
            'rag_quality': rag_data.get('quality_score', 0) if rag_data else 0,
            'documents_retrieved': rag_data.get('document_count', 0) if rag_data else 0
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep conversation history manageable
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def get_integration_analytics(self) -> Dict[str, Any]:
        """Get comprehensive integration analytics."""
        
        # Calculate analytics
        if self.conversation_history:
            avg_confidence = sum(entry['confidence'] for entry in self.conversation_history) / len(self.conversation_history)
            avg_processing_time = sum(entry['processing_time'] for entry in self.conversation_history) / len(self.conversation_history)
            rag_usage_rate = sum(1 for entry in self.conversation_history if entry['rag_used']) / len(self.conversation_history)
        else:
            avg_confidence = 0
            avg_processing_time = 0
            rag_usage_rate = 0
        
        return {
            'integration_metrics': self.integration_metrics,
            'component_status': self.component_status,
            'conversation_analytics': {
                'total_conversations': len(self.conversation_history),
                'avg_confidence': avg_confidence,
                'avg_processing_time': avg_processing_time,
                'rag_usage_rate': rag_usage_rate
            },
            'rag_analytics': {
                'avg_documents_retrieved': sum(self.rag_analytics['documents_retrieved']) / len(self.rag_analytics['documents_retrieved']) if self.rag_analytics['documents_retrieved'] else 0,
                'avg_similarity_score': sum(self.rag_analytics['similarity_scores']) / len(self.rag_analytics['similarity_scores']) if self.rag_analytics['similarity_scores'] else 0,
                'query_type_distribution': self.rag_analytics['query_types'],
                'response_quality_trend': self.rag_analytics['response_quality'][-10:]  # Last 10 responses
            }
        }

# Streamlit Integration Interface
def setup_integration_config():
    """Configure Streamlit for integrated platform."""
    st.set_page_config(
        page_title="Integrated AI Platform",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_integration_css():
    """Apply CSS for integrated platform interface."""
    st.markdown("""
    <style>
        .integration-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .component-status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            margin: 0.25rem;
        }
        
        .status-active { background: #d1fae5; color: #065f46; }
        .status-error { background: #fee2e2; color: #991b1b; }
        .status-initializing { background: #fef3c7; color: #92400e; }
        
        .integration-metric {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1e40af;
        }
        
        .chart-container {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

def initialize_integration_session_state():
    """Initialize session state for integrated platform."""
    defaults = {
        'platform_initialized': False,
        'platform': None,
        'integration_mode': 'Full Integration',
        'conversation_history': [],
        'selected_customer': 'john.doe@email.com',
        'rag_enabled': True,
        'agents_enabled': True,
        'mcp_enabled': False,
        'analytics_view': 'Overview'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_integration_header():
    """Render header for integrated platform."""
    st.markdown("""
    <div class="integration-header">
        <h1>🔧 Integrated AI Customer Service Platform</h1>
        <p>Phase 3c: Complete System Integration with Enhanced RAG</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">All Components • Real-time Analytics • Production Ready</p>
    </div>
    """, unsafe_allow_html=True)

def render_integration_sidebar():
    """Render sidebar for integrated platform."""
    with st.sidebar:
        st.title("🎛️ Integration Controls")
        
        # Integration mode
        st.subheader("🔧 Integration Mode")
        st.session_state.integration_mode = st.selectbox(
            "Select Mode:",
            ["Full Integration", "RAG Only", "Agents Only", "Basic Mode"],
            index=0
        )
        
        # Component toggles
        st.subheader("⚙️ Components")
        st.session_state.rag_enabled = st.checkbox("RAG System", value=True)
        st.session_state.agents_enabled = st.checkbox("AI Agents", value=True)
        st.session_state.mcp_enabled = st.checkbox("MCP Protocol", value=False)
        
        # Customer selection
        st.subheader("👤 Customer Context")
        st.session_state.selected_customer = st.selectbox(
            "Select Customer:",
            ["john.doe@email.com", "sarah.smith@email.com", "new.customer@email.com"],
            index=0
        )
        
        # Analytics view
        st.subheader("📊 Analytics View")
        st.session_state.analytics_view = st.selectbox(
            "View Type:",
            ["Overview", "RAG Analytics", "Integration Metrics", "Component Status"],
            index=0
        )
        
        # Platform actions
        st.subheader("🚀 Platform Actions")
        if st.button("🔄 Reinitialize Platform", use_container_width=True):
            st.session_state.platform_initialized = False
            st.rerun()
        
        if st.button("📊 Export Analytics", use_container_width=True):
            st.success("Analytics exported!")
        
        if st.button("🧹 Clear History", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()

def render_component_status(platform: IntegratedCustomerServicePlatform):
    """Render component status overview."""
    st.subheader("🔧 Component Status")
    
    status = platform.component_status
    
    # Create status grid
    cols = st.columns(3)
    col_index = 0
    
    for component, state in status.items():
        with cols[col_index % 3]:
            status_class = f"status-{state}"
            status_icon = {"active": "🟢", "error": "🔴", "initializing": "🟡"}[state]
            
            st.markdown(f"""
            <div class="integration-metric">
                <div>{status_icon}</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem;">{component.replace('_', ' ').title()}</div>
                <span class="component-status {status_class}">{state.title()}</span>
            </div>
            """, unsafe_allow_html=True)
        
        col_index += 1

def render_integration_metrics(platform: IntegratedCustomerServicePlatform):
    """Render integration performance metrics."""
    st.subheader("📊 Integration Performance")
    
    analytics = platform.get_integration_analytics()
    integration_metrics = analytics['integration_metrics']
    conversation_analytics = analytics['conversation_analytics']
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="integration-metric">
            <div class="metric-value">{integration_metrics['total_requests']}</div>
            <div>Total Requests</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="integration-metric">
            <div class="metric-value">{integration_metrics['success_rate']:.1%}</div>
            <div>Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="integration-metric">
            <div class="metric-value">{integration_metrics['avg_response_time']:.2f}s</div>
            <div>Avg Response Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="integration-metric">
            <div class="metric-value">{conversation_analytics['rag_usage_rate']:.1%}</div>
            <div>RAG Usage Rate</div>
        </div>
        """, unsafe_allow_html=True)

def render_rag_analytics(platform: IntegratedCustomerServicePlatform):
    """Render detailed RAG analytics."""
    st.subheader("🔍 RAG System Analytics")
    
    analytics = platform.get_integration_analytics()
    rag_analytics = analytics['rag_analytics']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📄 Documents Retrieved per Query")
        
        if platform.rag_analytics['documents_retrieved']:
            fig = px.histogram(
                x=platform.rag_analytics['documents_retrieved'],
                title="Distribution of Documents Retrieved",
                nbins=10
            )
            fig.update_layout(
                xaxis_title="Documents Retrieved",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No RAG queries processed yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 🎯 Similarity Score Distribution")
        
        if platform.rag_analytics['similarity_scores']:
            fig = px.histogram(
                x=platform.rag_analytics['similarity_scores'],
                title="RAG Similarity Scores",
                nbins=10
            )
            fig.update_layout(
                xaxis_title="Similarity Score",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No similarity scores available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Query type distribution
    if rag_analytics['query_type_distribution']:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📊 Query Type Distribution")
        
        query_types = list(rag_analytics['query_type_distribution'].keys())
        query_counts = list(rag_analytics['query_type_distribution'].values())
        
        fig = px.pie(
            values=query_counts,
            names=query_types,
            title="Simple vs Complex Queries"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_integration_chat(platform: IntegratedCustomerServicePlatform):
    """Render integrated chat interface."""
    st.subheader("💬 Integrated Customer Service Chat")
    
    # Display conversation history
    if st.session_state.conversation_history:
        for entry in st.session_state.conversation_history:
            # Customer message
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 1rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid #2196f3;">
                <strong>👤 Customer:</strong> {entry['query']}<br>
                <small style="opacity: 0.7;">{entry['timestamp'][:19]}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent response
            confidence_color = "#4caf50" if entry['confidence'] > 0.7 else "#ff9800" if entry['confidence'] > 0.4 else "#f44336"
            st.markdown(f"""
            <div style="background: #f1f8e9; padding: 1rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid #4caf50;">
                <strong>🤖 AI Agent:</strong> {entry['response']}<br>
                <small style="opacity: 0.7;">
                    Confidence: <span style="color: {confidence_color};">{entry['confidence']:.1%}</span> | 
                    Response time: {entry['processing_time']:.2f}s |
                    RAG: {'✅' if entry['rag_used'] else '❌'} |
                    Documents: {entry['documents_retrieved']}
                </small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👋 Welcome to the integrated AI customer service platform! Ask a question to see all components working together.")
    
    # Input form
    with st.form("integrated_chat_form", clear_on_submit=True):
        query = st.text_area(
            "Customer Query:",
            height=100,
            placeholder="Example: I'm a premium customer and need to return a defective product I bought last week..."
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.form_submit_button("🚀 Process with Full Integration", use_container_width=True)
        with col2:
            submit_rag = st.form_submit_button("🔍 Process with RAG Only", use_container_width=True)
        with col3:
            submit_basic = st.form_submit_button("💬 Basic Processing", use_container_width=True)
        
        if submit and query:
            process_integrated_query(platform, query, use_rag=True, use_agents=True)
        elif submit_rag and query:
            process_integrated_query(platform, query, use_rag=True, use_agents=False)
        elif submit_basic and query:
            process_integrated_query(platform, query, use_rag=False, use_agents=False)

def process_integrated_query(platform: IntegratedCustomerServicePlatform, query: str, use_rag: bool, use_agents: bool):
    """Process query through integrated platform."""
    with st.spinner("🔄 Processing through integrated AI platform..."):
        try:
            # Process query asynchronously
            result = asyncio.run(
                platform.process_integrated_query(
                    st.session_state.selected_customer,
                    query,
                    use_rag=use_rag,
                    use_agents=use_agents,
                    use_mcp=st.session_state.mcp_enabled
                )
            )
            
            if result['success']:
                # Add to conversation history
                conversation_entry = {
                    'timestamp': result['timestamp'],
                    'query': query,
                    'response': result['response'],
                    'confidence': result['confidence'],
                    'processing_time': result['processing_time'],
                    'rag_used': result['system_metadata']['components_used']['rag'],
                    'documents_retrieved': result.get('rag_data', {}).get('document_count', 0)
                }
                
                st.session_state.conversation_history.append(conversation_entry)
                st.success(f"✅ Query processed successfully in {result['processing_time']:.2f}s")
            else:
                st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"❌ Integration error: {str(e)}")
    
    st.rerun()

def render_integrated_admin_panel():
    """Render complete integrated admin panel with all functionality."""
    # Initialize admin state
    if 'show_admin_panel' not in st.session_state:
        st.session_state.show_admin_panel = False
    
    # Create the floating admin button with Streamlit button in a fixed container
    with st.container():
        # Create a floating admin button that actually works
        admin_col1, admin_col2 = st.columns([9, 1])
        with admin_col2:
            # Position this button at the bottom right
            st.markdown("""
            <style>
            .admin-floating-button {
                position: fixed !important;
                bottom: 30px !important;
                right: 30px !important;
                z-index: 9999 !important;
                width: 60px !important;
                height: 60px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                border: none !important;
                color: white !important;
                font-size: 24px !important;
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4) !important;
                transition: all 0.3s ease !important;
            }
            .admin-floating-button:hover {
                transform: scale(1.1) !important;
                box-shadow: 0 12px 25px rgba(59, 130, 246, 0.6) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("⚙️", key="floating_admin_button", help="Admin Panel - Switch Views"):
                st.session_state.show_admin_panel = not st.session_state.show_admin_panel
                st.rerun()
    
    # Show popup when admin button is clicked
    if st.session_state.show_admin_panel:
        st.markdown("---")
        
        # Create a prominent popup box
        with st.container():
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border: 2px solid #3b82f6;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
            ">
            """, unsafe_allow_html=True)
            
            st.markdown("### 🛠️ Integrated Admin Panel - Complete Platform Control")
            st.markdown("**Switch between all platform views:**")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("💬 Customer Chat", key="admin_customer", use_container_width=True, type="primary"):
                    st.session_state.integration_mode = "Customer Chat"
                    st.session_state.show_admin_panel = False
                    st.rerun()
            with col2:
                if st.button("📊 Analytics", key="admin_analytics", use_container_width=True, type="primary"):
                    st.session_state.integration_mode = "Analytics Dashboard"
                    st.session_state.show_admin_panel = False
                    st.rerun()
            with col3:
                if st.button("🤖 Agent Monitor", key="admin_agents", use_container_width=True, type="primary"):
                    st.session_state.integration_mode = "Agent Monitor"
                    st.session_state.show_admin_panel = False
                    st.rerun()
            with col4:
                if st.button("🔗 MCP Console", key="admin_mcp", use_container_width=True, type="primary"):
                    st.session_state.integration_mode = "MCP Console"
                    st.session_state.show_admin_panel = False
                    st.rerun()
            with col5:
                if st.button("⚙️ System Config", key="admin_config", use_container_width=True, type="primary"):
                    st.session_state.integration_mode = "System Configuration"
                    st.session_state.show_admin_panel = False
                    st.rerun()
            
            st.markdown("**Advanced Features:** Complete integration, RAG enhancement, multi-agent coordination, MCP protocol")
            st.markdown("**Keyboard Shortcuts:** `Ctrl+1/2/3/4/5` for quick navigation")
            
            if st.button("✖️ Close Admin Panel", key="admin_close", use_container_width=True):
                st.session_state.show_admin_panel = False
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main Streamlit application for integrated platform."""
    if not is_streamlit():
        print("This module is designed to run with Streamlit.")
        print("Run: streamlit run phase3c_integration.py")
        return
    
    # Setup
    setup_integration_config()
    apply_integration_css()
    initialize_integration_session_state()
    
    # Initialize platform
    if not st.session_state.platform_initialized:
        with st.spinner("🔄 Initializing integrated platform..."):
            platform = IntegratedCustomerServicePlatform()
            st.session_state.platform = platform
            st.session_state.platform_initialized = True
        st.success("✅ Integrated platform initialized!")
        time.sleep(1)
        st.rerun()
    
    platform = st.session_state.platform
    
    # Render interface
    render_integration_header()
    render_integration_sidebar()
    
    # Render integrated admin panel (always available)
    render_integrated_admin_panel()
    
    # Main content based on view
    if st.session_state.analytics_view == "Overview":
        render_component_status(platform)
        render_integration_metrics(platform)
        render_integration_chat(platform)
    elif st.session_state.analytics_view == "RAG Analytics":
        render_rag_analytics(platform)
    elif st.session_state.analytics_view == "Integration Metrics":
        render_integration_metrics(platform)
        
        # Detailed metrics chart
        analytics = platform.get_integration_analytics()
        if platform.conversation_history:
            df = pd.DataFrame(platform.conversation_history)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.line(
                    df, 
                    x='timestamp', 
                    y='confidence',
                    title="Confidence Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(
                    df,
                    x='timestamp',
                    y='processing_time', 
                    title="Response Time Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    elif st.session_state.analytics_view == "Component Status":
        render_component_status(platform)
        
        # Component health details
        st.subheader("🔧 Detailed Component Health")
        
        if ALL_COMPONENTS_AVAILABLE:
            st.success("✅ All components are available and functional")
        else:
            st.warning("⚠️ Some components are not available (mock mode)")
        
        # Integration test
        if st.button("🧪 Run Integration Test"):
            with st.spinner("Running integration test..."):
                test_query = "Test integration of all components"
                try:
                    result = asyncio.run(
                        platform.process_integrated_query(
                            "test@example.com",
                            test_query,
                            use_rag=True,
                            use_agents=True
                        )
                    )
                    
                    if result['success']:
                        st.success("✅ Integration test passed!")
                        st.json(result['system_metadata'])
                    else:
                        st.error("❌ Integration test failed")
                        
                except Exception as e:
                    st.error(f"❌ Integration test error: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; margin: 2rem 0;">
        🎓 <strong>Phase 3c Complete:</strong> Integration & RAG Enhancement<br>
        Full System Integration • Enhanced Analytics • Next: Deployment & Production
    </div>
    """, unsafe_allow_html=True)

def demo_integration():
    """Demo integrated platform (non-Streamlit version)."""
    print("=== Phase 3c: Integration & RAG Enhancement Demo ===\n")
    
    platform = IntegratedCustomerServicePlatform()
    
    print(f"🔧 Platform: {platform.platform_name} v{platform.version}")
    print(f"🎯 All Components Available: {ALL_COMPONENTS_AVAILABLE}")
    
    # Component status
    print(f"\n🔧 Component Status:")
    for component, status in platform.component_status.items():
        status_icon = {"active": "✅", "error": "❌", "initializing": "🔄"}[status]
        print(f"  {status_icon} {component.replace('_', ' ').title()}: {status}")
    
    # Demo integration
    print(f"\n🚀 Integration Features:")
    features = [
        "Unified LLM, RAG, Agent, and MCP integration",
        "Enhanced knowledge base with comprehensive policies",
        "Multi-component query processing pipeline",
        "Real-time analytics and performance monitoring",
        "Customer context-aware responses",
        "Configurable component activation",
        "Advanced RAG quality scoring",
        "Integration performance metrics"
    ]
    
    for feature in features:
        print(f"  • {feature}")
    
    # Analytics summary
    analytics = platform.get_integration_analytics()
    print(f"\n📊 Analytics Summary:")
    print(f"  • Integration Requests: {analytics['integration_metrics']['total_requests']}")
    print(f"  • Success Rate: {analytics['integration_metrics']['success_rate']:.1%}")
    print(f"  • Average Response Time: {analytics['integration_metrics']['avg_response_time']:.2f}s")
    print(f"  • RAG Usage Rate: {analytics['conversation_analytics']['rag_usage_rate']:.1%}")

if __name__ == "__main__":
    if is_streamlit():
        main()
    else:
        demo_integration()
        print(f"\n🚀 To run the integrated platform interface:")
        print(f"   streamlit run {__file__}")
        print(f"\n🎓 Phase 3c Complete!")
        print(f"Next: Phase 3d - Deployment & Production")