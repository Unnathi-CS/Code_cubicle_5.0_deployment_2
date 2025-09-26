#!/usr/bin/env python3
"""
Test script for the Hackathon RAG System
This script tests the core functionality without requiring external APIs.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_test_messages():
    """Create test messages for testing."""
    test_messages = [
        {
            "user": "team_alpha",
            "text": "We're having trouble with the API authentication. Anyone know how to fix this?",
            "ts": str(datetime.now().timestamp()),
            "channel": "general"
        },
        {
            "user": "team_beta", 
            "text": "Our database connection keeps timing out. Help!",
            "ts": str(datetime.now().timestamp()),
            "channel": "general"
        },
        {
            "user": "team_gamma",
            "text": "What's the best way to deploy a React app?",
            "ts": str(datetime.now().timestamp()),
            "channel": "general"
        },
        {
            "user": "team_delta",
            "text": "We're stuck on the authentication flow. Any suggestions?",
            "ts": str(datetime.now().timestamp()),
            "channel": "general"
        },
        {
            "user": "team_epsilon",
            "text": "Great progress today! We finished the user interface.",
            "ts": str(datetime.now().timestamp()),
            "channel": "general"
        }
    ]
    
    # Write to messages.json
    messages_file = Path("messages.json")
    with messages_file.open("w") as f:
        for msg in test_messages:
            f.write(json.dumps(msg) + "\n")
    
    print(f"✅ Created {len(test_messages)} test messages")
    return test_messages

def test_stream_reading():
    """Test stream reading functionality."""
    print("\n🔄 Testing stream reading...")
    
    try:
        from stream import read_stream
        messages = list(read_stream())
        print(f"✅ Successfully read {len(messages)} messages from stream")
        return True
    except Exception as e:
        print(f"❌ Stream reading failed: {e}")
        return False

def test_message_validation():
    """Test message validation."""
    print("\n🔄 Testing message validation...")
    
    try:
        from utils import is_valid_message
        
        # Test valid message
        valid_msg = {"user": "test_user", "text": "Hello world"}
        assert is_valid_message(valid_msg), "Valid message should pass validation"
        
        # Test invalid messages
        invalid_msg1 = {"user": "test_user", "text": ""}
        assert not is_valid_message(invalid_msg1), "Empty text should fail validation"
        
        invalid_msg2 = {"user": None, "text": "Hello world"}
        assert not is_valid_message(invalid_msg2), "None user should fail validation"
        
        print("✅ Message validation tests passed")
        return True
    except Exception as e:
        print(f"❌ Message validation failed: {e}")
        return False

def test_rag_service():
    """Test RAG service (without OpenAI API)."""
    print("\n🔄 Testing RAG service...")
    
    try:
        from ai_service import RAGService
        
        # Create service instance
        rag_service = RAGService()
        
        # Test message processing
        test_messages = [
            {"user": "test", "text": "We have a problem with authentication", "ts": "1234567890"},
            {"user": "test2", "text": "How do we deploy this app?", "ts": "1234567891"}
        ]
        
        # Test embedding (will use local embedder if OpenAI fails)
        embedding = rag_service.get_embedding("test query")
        if embedding:
            print("✅ Embedding generation works")
        else:
            print("⚠️ Embedding generation failed (expected without API key)")
        
        # Test context preparation
        context = rag_service._prepare_context(test_messages)
        assert len(context) > 0, "Context should not be empty"
        print("✅ Context preparation works")
        
        return True
    except Exception as e:
        print(f"❌ RAG service test failed: {e}")
        return False

def test_rag_query_service():
    """Test RAG query service."""
    print("\n🔄 Testing RAG query service...")
    
    try:
        from rag_query_service import RAGQueryService
        
        query_service = RAGQueryService()
        
        # Test message retrieval
        messages = query_service.get_recent_messages(hours=24, limit=10)
        print(f"✅ Retrieved {len(messages)} recent messages")
        
        # Test stats calculation
        stats = query_service.get_message_stats()
        assert 'total_messages' in stats, "Stats should include total_messages"
        print("✅ Stats calculation works")
        
        return True
    except Exception as e:
        print(f"❌ RAG query service test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization."""
    print("\n🔄 Testing Flask app...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test landing page
            response = client.get('/')
            assert response.status_code == 200, "Landing page should load"
            
            # Test chatbot page
            response = client.get('/chatbot')
            assert response.status_code == 200, "Chatbot page should load"
            
            # Test dashboard page
            response = client.get('/dashboard')
            assert response.status_code == 200, "Dashboard page should load"
            
            # Test API endpoints
            response = client.get('/api/stats')
            assert response.status_code == 200, "Stats API should work"
            
            response = client.get('/api/messages')
            assert response.status_code == 200, "Messages API should work"
        
        print("✅ Flask app tests passed")
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Hackathon RAG System")
    print("=" * 50)
    
    # Create test data
    create_test_messages()
    
    # Run tests
    tests = [
        test_stream_reading,
        test_message_validation,
        test_rag_service,
        test_rag_query_service,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n📋 Next steps:")
        print("1. Set up your .env file with API keys")
        print("2. Run: python src/app.py")
        print("3. Visit: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
