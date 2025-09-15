#!/usr/bin/env python3
"""
Generate PDF versions of knowledge base documents
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

# Knowledge base documents from mcp_server.py
KNOWLEDGE_DOCS = [
    {
        "id": "policy_returns",
        "title": "Return Policy",
        "content": "Return Policy: Items can be returned within 30 days of purchase with original receipt. Products must be in original condition and packaging. Refunds processed within 5-7 business days.",
        "category": "returns",
        "keywords": ["return", "refund", "exchange", "30 days", "receipt"]
    },
    {
        "id": "policy_shipping",
        "title": "Shipping Information", 
        "content": "Shipping Information: Standard shipping takes 3-5 business days within US ($5.99). Express shipping available in 1-2 days ($15.99). Free shipping on orders over $50. International shipping 7-14 days ($19.99).",
        "category": "shipping",
        "keywords": ["shipping", "delivery", "express", "standard", "international", "free shipping"]
    },
    {
        "id": "policy_support",
        "title": "Support Hours",
        "content": "Support Hours: Technical support available Monday-Friday 9AM-6PM EST. Premium customers get 24/7 support access. Live chat during business hours. Phone: 1-800-SUPPORT.",
        "category": "support", 
        "keywords": ["support hours", "phone", "chat", "24/7", "premium", "contact"]
    },
    {
        "id": "troubleshoot_power",
        "title": "Device Power Issues",
        "content": "Device Power Issues: If device won't turn on: 1) Check power cable securely connected 2) Try different outlet 3) Hold power button 10 seconds to reset 4) Check battery level indicator.",
        "category": "troubleshooting",
        "keywords": ["power", "won't turn on", "battery", "cable", "reset", "device", "charge"]
    },
    {
        "id": "account_password", 
        "title": "Password Reset",
        "content": "Password Reset: To reset password visit login page, click 'Forgot Password', enter email address, check email for reset link (may take 5-10 minutes), follow instructions.",
        "category": "account",
        "keywords": ["password", "reset", "login", "forgot", "email", "account"]
    },
    {
        "id": "payment_methods",
        "title": "Payment Options",
        "content": "Payment Options: We accept Visa, MasterCard, American Express, Discover, PayPal, Apple Pay, Google Pay, and bank transfers. All payments processed securely.",
        "category": "payment",
        "keywords": ["payment", "credit card", "paypal", "apple pay", "visa", "secure"]
    }
]

def create_pdf(doc_data, output_dir):
    """Create a PDF document from knowledge base data"""
    filename = f"{doc_data['id']}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create document
    document = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    content_style = ParagraphStyle(
        'CustomContent', 
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        leftIndent=20,
        rightIndent=20
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor='grey',
        spaceAfter=6,
        leftIndent=20
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph(doc_data['title'], title_style))
    story.append(Spacer(1, 12))
    
    # Category
    story.append(Paragraph(f"<b>Category:</b> {doc_data['category'].title()}", meta_style))
    
    # Keywords  
    keywords_str = ", ".join(doc_data['keywords'])
    story.append(Paragraph(f"<b>Keywords:</b> {keywords_str}", meta_style))
    story.append(Spacer(1, 20))
    
    # Main content
    story.append(Paragraph("<b>Policy Details:</b>", content_style))
    story.append(Paragraph(doc_data['content'], content_style))
    
    # Build PDF
    document.build(story)
    print(f"Created: {filepath}")
    return filepath

def main():
    """Generate all PDF documents"""
    output_dir = "/Users/developer/capstone/knowledge_base_pdfs"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating {len(KNOWLEDGE_DOCS)} PDF documents...")
    
    created_files = []
    for doc in KNOWLEDGE_DOCS:
        filepath = create_pdf(doc, output_dir)
        created_files.append(filepath)
    
    print(f"\nSuccessfully created {len(created_files)} PDF files:")
    for filepath in created_files:
        print(f"  - {os.path.basename(filepath)}")
    
    print(f"\nAll PDFs saved to: {output_dir}")

if __name__ == "__main__":
    main()