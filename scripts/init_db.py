#!/usr/bin/env python3
"""
Initialize database with sample FAQs and Qdrant vector store
Run this script to set up the knowledge base for the RAG chatbot
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DevelopmentConfig
from models import Database, FAQModel
from agents.rag_agents import RAGAgentSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample FAQ Data
SAMPLE_FAQS = [
    {
        'question': 'What is Ajeer Dashboard?',
        'answer': 'Ajeer Dashboard is a comprehensive financial management platform designed to help users track, convert, and manage their money across different currencies based on their country of residence.',
        'category': 'General'
    },
    {
        'question': 'How do I convert currencies on Ajeer?',
        'answer': 'Simply navigate to the Currency Converter card on your dashboard, enter the amount you want to convert, select your source and target currencies, and click the Convert button. The conversion will use real-time exchange rates.',
        'category': 'Currency'
    },
    {
        'question': 'Which currencies does Ajeer support?',
        'answer': 'Ajeer supports all major currencies including USD, EUR, GBP, JPY, INR, AED, SAR, and many more. Your preferred currency is automatically set based on your country during registration.',
        'category': 'Currency'
    },
    {
        'question': 'How is my country detected?',
        'answer': 'Your country is automatically detected based on your IP address during account registration. This helps us set your preferred currency and provide localized services.',
        'category': 'Account'
    },
    {
        'question': 'Can I change my preferred currency?',
        'answer': 'Yes! You can change your preferred currency anytime from your user profile settings. Go to your profile page and update your currency preference.',
        'category': 'Account'
    },
    {
        'question': 'What is the Chatbot Assistant?',
        'answer': 'The Chatbot Assistant is an intelligent AI-powered helper that can answer frequently asked questions and provide support. It uses advanced RAG (Retrieval-Augmented Generation) technology with multiple agents to provide accurate responses.',
        'category': 'Support'
    },
    {
        'question': 'How does the Chatbot work?',
        'answer': 'The Chatbot uses a multi-agent system powered by LangGraph. When you ask a question, it first searches our FAQ database for similar questions (FAQ Agent), and if no match is found, it uses the General Agent with the Gemini LLM to generate a helpful response.',
        'category': 'Support'
    },
    {
        'question': 'Is the Chatbot available 24/7?',
        'answer': 'Yes! The Chatbot Assistant is available 24/7 to help you with your questions. You can access it anytime from the dashboard.',
        'category': 'Support'
    },
    {
        'question': 'How is my data secured?',
        'answer': 'Your data is securely stored in our MongoDB database with proper encryption. We use industry-standard security practices to protect your personal information and transaction history.',
        'category': 'Security'
    },
    {
        'question': 'Can I export my transaction history?',
        'answer': 'This feature is coming soon! In the future, you will be able to export your transaction history in various formats including CSV and PDF.',
        'category': 'Features'
    },
    {
        'question': 'What payment methods are supported?',
        'answer': 'Ajeer currently supports various payment methods depending on your region. Contact our support team for more information about payment options in your country.',
        'category': 'Payments'
    },
    {
        'question': 'How do I reset my password?',
        'answer': 'Click on the "Forgot Password?" link on the login page. Enter your email address, and we\'ll send you a password reset link to your inbox.',
        'category': 'Account'
    }
]


def init_qdrant_faqs(rag_system):
    """Initialize Qdrant with FAQ embeddings"""
    print("[v0] Initializing Qdrant with FAQ embeddings...")
    
    for idx, faq in enumerate(SAMPLE_FAQS):
        try:
            success = rag_system.add_faq_to_kb(
                faq_id=idx,
                question=faq['question'],
                answer=faq['answer']
            )
            
            if success:
                print(f"[v0] Added FAQ {idx + 1}/{len(SAMPLE_FAQS)}: {faq['question'][:50]}...")
            else:
                print(f"[v0] Failed to add FAQ {idx + 1}: {faq['question']}")
        except Exception as e:
            print(f"[v0] Error adding FAQ {idx}: {e}")
    
    print(f"[v0] Qdrant initialization complete!")


def init_mongodb_faqs(db):
    """Initialize MongoDB with FAQ metadata"""
    print("[v0] Initializing MongoDB with FAQ metadata...")
    
    # Clear existing FAQs
    db.faqs.delete_many({})
    
    for idx, faq in enumerate(SAMPLE_FAQS):
        try:
            FAQModel.create_faq_record(
                db,
                qdrant_id=idx,
                question=faq['question'],
                answer=faq['answer'],
                category=faq['category']
            )
            print(f"[v0] Added FAQ metadata {idx + 1}/{len(SAMPLE_FAQS)}")
        except Exception as e:
            print(f"[v0] Error adding FAQ metadata {idx}: {e}")
    
    print(f"[v0] MongoDB initialization complete!")


def main():
    """Main initialization function"""
    print("[v0] Starting Ajeer Dashboard initialization...")
    print("[v0] =============================================\n")
    
    # Load configuration
    config = DevelopmentConfig()
    
    # Initialize MongoDB
    try:
        print("[v0] Connecting to MongoDB...")
        db_connection = Database(config.MONGODB_URI)
        db_connection.init_collections()
        db = db_connection.db
        print("[v0] ✓ MongoDB connected successfully\n")
    except Exception as e:
        print(f"[v0] ✗ Failed to connect to MongoDB: {e}")
        print("[v0] Make sure MongoDB is running at:", config.MONGODB_URI)
        return False
    
    # Initialize RAG System
    try:
        print("[v0] Initializing RAG System...")
        rag_system = RAGAgentSystem(
            qdrant_url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
            google_api_key=config.GOOGLE_API_KEY
        )
        print("[v0] ✓ RAG System initialized successfully\n")
    except Exception as e:
        print(f"[v0] ✗ Failed to initialize RAG System: {e}")
        print("[v0] Make sure Qdrant is running at:", config.QDRANT_URL)
        print("[v0] And GOOGLE_API_KEY is set in your .env file")
        return False
    
    # Initialize FAQs
    try:
        init_mongodb_faqs(db)
        print()
        init_qdrant_faqs(rag_system)
        print()
    except Exception as e:
        print(f"[v0] ✗ Failed to initialize FAQs: {e}")
        return False
    
    # Close database connection
    db_connection.close()
    
    print("[v0] =============================================")
    print("[v0] ✓ Initialization complete!")
    print("[v0] Ajeer Dashboard is ready to use.")
    print("[v0] Start the Flask app with: python app.py")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
