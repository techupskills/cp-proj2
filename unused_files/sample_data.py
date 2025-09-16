"""
Sample data for Customer Support AI Agent demo
This file contains the sample knowledge base and customer data used in the demo
"""

# Company knowledge base documents
KNOWLEDGE_BASE_DOCS = [
    {
        "id": "policy_returns",
        "title": "Return Policy",
        "content": "Our return policy allows returns within 30 days of purchase with original receipt. Items must be in original condition and packaging. Refunds processed within 5-7 business days.",
        "category": "returns",
        "last_updated": "2024-11-01"
    },
    {
        "id": "policy_shipping", 
        "title": "Shipping Information",
        "content": "Standard shipping takes 3-5 business days within the US. Express shipping (1-2 days) available for additional $15 fee. International shipping available to most countries, 7-14 days.",
        "category": "shipping",
        "last_updated": "2024-11-15"
    },
    {
        "id": "policy_support",
        "title": "Support Hours", 
        "content": "Technical support available Monday-Friday 9AM-6PM EST. Premium customers get 24/7 support access via priority line. Live chat available during business hours.",
        "category": "support",
        "last_updated": "2024-10-15"
    },
    {
        "id": "troubleshoot_power",
        "title": "Device Won't Turn On",
        "content": "If device won't turn on: 1) Check power cable is securely connected 2) Try different power outlet 3) Hold power button for 10 seconds to hard reset 4) Check battery indicator if applicable",
        "category": "troubleshooting",
        "last_updated": "2024-11-20"
    },
    {
        "id": "account_password",
        "title": "Password Reset",
        "content": "To reset password: visit login page, click 'Forgot Password', enter email address, check email for reset link (may take 5-10 minutes), follow instructions in email.",
        "category": "account",
        "last_updated": "2024-10-30"
    },
    {
        "id": "warranty_info",
        "title": "Warranty Coverage",
        "content": "All products include 1-year manufacturer warranty covering defects. Extended warranty available for purchase. Warranty does not cover physical damage or normal wear.",
        "category": "warranty", 
        "last_updated": "2024-09-15"
    },
    {
        "id": "payment_methods",
        "title": "Accepted Payment Methods",
        "content": "We accept Visa, MasterCard, American Express, Discover, PayPal, Apple Pay, and Google Pay. Payment is processed securely at checkout.",
        "category": "payment",
        "last_updated": "2024-11-01"
    }
]

# Sample customer database
CUSTOMER_DATABASE = {
    "john.doe@email.com": {
        "customer_id": "CUST-001",
        "name": "John Doe",
        "tier": "Premium",
        "join_date": "2023-05-15",
        "phone": "+1-555-0123",
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY", 
            "zip": "10001"
        },
        "orders": [
            {
                "id": "ORD-001", 
                "date": "2024-11-15", 
                "product": "Wireless Headphones Pro",
                "price": 299.99,
                "status": "Delivered",
                "tracking": "1Z999AA1234567890"
            },
            {
                "id": "ORD-002", 
                "date": "2024-12-01", 
                "product": "Bluetooth Speaker Max", 
                "price": 199.99,
                "status": "Shipped",
                "tracking": "1Z999AA1234567891"
            }
        ],
        "support_tickets": [
            {
                "id": "TKT-001",
                "date": "2024-11-20",
                "issue": "Headphones audio cutting out",
                "status": "Resolved",
                "resolution": "Replaced under warranty"
            }
        ],
        "preferences": {
            "communication": "email",
            "shipping": "express",
            "notifications": True
        }
    },
    "sarah.smith@email.com": {
        "customer_id": "CUST-002", 
        "name": "Sarah Smith",
        "tier": "Standard",
        "join_date": "2024-08-22",
        "phone": "+1-555-0456",
        "address": {
            "street": "456 Oak Ave",
            "city": "Los Angeles", 
            "state": "CA",
            "zip": "90210"
        },
        "orders": [
            {
                "id": "ORD-003",
                "date": "2024-11-20", 
                "product": "USB-C Cable 6ft",
                "price": 19.99,
                "status": "Delivered",
                "tracking": "1Z999AA1234567892"
            }
        ],
        "support_tickets": [],
        "preferences": {
            "communication": "sms",
            "shipping": "standard", 
            "notifications": False
        }
    },
    "mike.johnson@email.com": {
        "customer_id": "CUST-003",
        "name": "Mike Johnson", 
        "tier": "Premium",
        "join_date": "2022-12-03",
        "phone": "+1-555-0789",
        "address": {
            "street": "789 Pine St",
            "city": "Chicago",
            "state": "IL",
            "zip": "60601"
        },
        "orders": [
            {
                "id": "ORD-004",
                "date": "2024-10-15",
                "product": "Laptop Stand Pro",
                "price": 89.99, 
                "status": "Delivered",
                "tracking": "1Z999AA1234567893"
            },
            {
                "id": "ORD-005",
                "date": "2024-11-28",
                "product": "Wireless Mouse",
                "price": 49.99,
                "status": "Processing", 
                "tracking": "TBD"
            }
        ],
        "support_tickets": [
            {
                "id": "TKT-002",
                "date": "2024-10-20", 
                "issue": "Laptop stand wobbly",
                "status": "Open",
                "resolution": "Replacement being shipped"
            }
        ],
        "preferences": {
            "communication": "phone",
            "shipping": "express",
            "notifications": True
        }
    }
}

# Sample support tickets for demo
SAMPLE_TICKETS = [
    {
        "id": "TKT-20241201-0001",
        "customer": "john.doe@email.com", 
        "type": "Product Issue",
        "priority": "Medium",
        "status": "Open",
        "created": "2024-12-01T10:30:00",
        "description": "Bluetooth speaker not connecting to iPhone",
        "agent_notes": "Customer reports pairing issues. Troubleshooting steps provided."
    },
    {
        "id": "TKT-20241201-0002",
        "customer": "sarah.smith@email.com",
        "type": "Shipping Inquiry", 
        "priority": "Low",
        "status": "Resolved",
        "created": "2024-12-01T14:15:00",
        "description": "Question about delivery timeframe",
        "agent_notes": "Provided tracking information and delivery estimate."
    }
]

def get_sample_questions():
    """Return sample customer questions for testing"""
    return [
        "How do I return an item I bought last week?",
        "When will my order ORD-002 arrive?",
        "My wireless headphones won't turn on, can you help?", 
        "I forgot my account password, how do I reset it?",
        "What are your shipping options and costs?",
        "Can I change the shipping address on my recent order?",
        "Do you offer extended warranty on electronics?",
        "What payment methods do you accept?",
        "How do I contact technical support?",
        "My device is still under warranty but not working properly"
    ]

def get_demo_scenarios():
    """Return structured demo scenarios for presentations"""
    return [
        {
            "scenario": "Return Request",
            "customer": "john.doe@email.com",
            "question": "I want to return the headphones I bought 2 weeks ago",
            "expected_outcome": "Should reference 30-day policy and customer's order history"
        },
        {
            "scenario": "Order Tracking", 
            "customer": "john.doe@email.com",
            "question": "Where is my Bluetooth speaker order?",
            "expected_outcome": "Should find ORD-002 and provide tracking information"
        },
        {
            "scenario": "Technical Support",
            "customer": "sarah.smith@email.com", 
            "question": "My device won't charge, what should I do?",
            "expected_outcome": "Should provide troubleshooting steps and offer escalation"
        },
        {
            "scenario": "New Customer",
            "customer": "new.customer@email.com",
            "question": "What's your return policy?", 
            "expected_outcome": "Should provide policy info but note no customer history"
        }
    ]
