"""
Quick Start Example for AI RAG Agent

This script demonstrates how to use the AI RAG Agent programmatically.
Make sure the server is running before running this script.

Usage:
    python examples/quick_start.py
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_health():
    """Check API health status."""
    print_section("1. Health Check")
    
    response = requests.get(f"{API_BASE_URL}/api/health")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Version: {data['version']}")
    print(f"Vector Store Initialized: {data['vector_store_initialized']}")
    print("\n✓ API is healthy and ready!")


def simple_question():
    """Test with a simple question (should answer directly without RAG)."""
    print_section("2. Simple Question (No RAG)")
    
    query = "What is 2+2?"
    print(f"Question: {query}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={"query": query}
    )
    data = response.json()
    
    print(f"\nAnswer: {data['answer']}")
    print(f"Sources: {data['sources']}")  # Should be empty
    print(f"Session ID: {data['session_id']}")
    
    return data['session_id']


def company_question():
    """Test with a company-specific question (should use RAG)."""
    print_section("3. Company Question (With RAG)")
    
    query = "What is the company's leave policy?"
    print(f"Question: {query}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={"query": query}
    )
    data = response.json()
    
    print(f"\nAnswer: {data['answer'][:200]}...")  # Truncate for display
    print(f"Sources: {', '.join(data['sources'])}")
    print(f"Session ID: {data['session_id']}")


def conversation_with_memory():
    """Test conversation continuity with session memory."""
    print_section("4. Conversation with Memory")
    
    # First message
    print("Message 1: Introducing myself")
    response1 = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={"query": "Hello! My name is Alice and I work in engineering."}
    )
    data1 = response1.json()
    session_id = data1['session_id']
    print(f"Assistant: {data1['answer']}")
    
    time.sleep(1)
    
    # Second message - test name recall
    print("\nMessage 2: Testing name recall")
    response2 = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={
            "query": "What's my name?",
            "session_id": session_id
        }
    )
    data2 = response2.json()
    print(f"Assistant: {data2['answer']}")
    
    time.sleep(1)
    
    # Third message - test context recall
    print("\nMessage 3: Testing department recall")
    response3 = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={
            "query": "Which department do I work in?",
            "session_id": session_id
        }
    )
    data3 = response3.json()
    print(f"Assistant: {data3['answer']}")
    print(f"\n✓ Session maintained across {3} messages")


def product_question():
    """Test with a product-specific question."""
    print_section("5. Product Information Question")
    
    query = "How much storage do I get with the Business plan?"
    print(f"Question: {query}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={"query": query}
    )
    data = response.json()
    
    print(f"\nAnswer: {data['answer']}")
    print(f"Sources: {', '.join(data['sources'])}")


def technical_question():
    """Test with a technical FAQ question."""
    print_section("6. Technical FAQ Question")
    
    query = "How do I access the company VPN?"
    print(f"Question: {query}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/ask",
        json={"query": query}
    )
    data = response.json()
    
    print(f"\nAnswer: {data['answer']}")
    print(f"Sources: {', '.join(data['sources'])}")


def main():
    """Run all examples."""
    print("\n" + "🚀 " * 20)
    print("AI RAG Agent - Quick Start Examples")
    print("🚀 " * 20)
    
    try:
        # 1. Health check
        check_health()
        time.sleep(1)
        
        # 2. Simple question (no RAG)
        simple_question()
        time.sleep(1)
        
        # 3. Company question (with RAG)
        company_question()
        time.sleep(1)
        
        # 4. Conversation with memory
        conversation_with_memory()
        time.sleep(1)
        
        # 5. Product question
        product_question()
        time.sleep(1)
        
        # 6. Technical question
        technical_question()
        
        # Summary
        print_section("Summary")
        print("✓ All examples completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  • Health check endpoint")
        print("  • Direct answers (no RAG for simple questions)")
        print("  • RAG-based answers with source attribution")
        print("  • Session-based conversation memory")
        print("  • Multiple document types (policies, product, technical)")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Please make sure the server is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
