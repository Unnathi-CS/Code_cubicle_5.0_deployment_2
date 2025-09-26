#!/usr/bin/env python3
"""
Test script for the Pathway-based Slack ingestion system.
This script tests the Pathway database functionality without requiring external services.
"""

import json
import time
import logging
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_messages():
    """Create test messages for the Pathway system."""
    test_messages = [
        {
            "user": "alice",
            "text": "I'm having trouble with the API integration. Can anyone help?",
            "ts": str(time.time() - 3600),  # 1 hour ago
            "channel": "general",
            "message_id": f"test_1_{int(time.time())}",
            "thread_ts": "",
            "type": "message"
        },
        {
            "user": "bob",
            "text": "What's the deadline for the hackathon?",
            "ts": str(time.time() - 1800),  # 30 minutes ago
            "channel": "general",
            "message_id": f"test_2_{int(time.time())}",
            "thread_ts": "",
            "type": "message"
        },
        {
            "user": "charlie",
            "text": "Our database connection is broken! This is urgent!",
            "ts": str(time.time() - 900),   # 15 minutes ago
            "channel": "tech-support",
            "message_id": f"test_3_{int(time.time())}",
            "thread_ts": "",
            "type": "message"
        },
        {
            "user": "diana",
            "text": "Has anyone used React with TypeScript before?",
            "ts": str(time.time() - 600),   # 10 minutes ago
            "channel": "general",
            "message_id": f"test_4_{int(time.time())}",
            "thread_ts": "",
            "type": "message"
        },
        {
            "user": "eve",
            "text": "We need help with deployment. Our app won't start.",
            "ts": str(time.time() - 300),   # 5 minutes ago
            "channel": "general",
            "message_id": f"test_5_{int(time.time())}",
            "thread_ts": "",
            "type": "message"
        }
    ]
    
    # Write test messages to messages.json
    messages_file = Path("messages.json")
    with messages_file.open("w") as f:
        for msg in test_messages:
            f.write(json.dumps(msg) + "\n")
    
    logger.info(f"Created {len(test_messages)} test messages")
    return test_messages

def test_pathway_schemas():
    """Test Pathway schema definitions."""
    try:
        import pathway as pw
        from pathway_pipeline import MessageSchema, UserSchema, ChannelSchema, AnalyticsSchema
        
        logger.info("✅ Pathway schemas imported successfully")
        
        # Test schema creation
        test_msg = MessageSchema(
            user="test_user",
            text="test message",
            ts="1234567890",
            channel="test_channel"
        )
        
        logger.info("✅ MessageSchema creation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema test failed: {e}")
        return False

def test_pathway_rag_service():
    """Test the Pathway RAG service."""
    try:
        from pathway_rag_service import PathwayRAGService
        
        # Create mock tables for testing
        mock_tables = {
            'messages': None,
            'users': None,
            'channels': None,
            'analytics': None,
            'hourly_stats': None,
            'rag_index': None
        }
        
        service = PathwayRAGService(mock_tables)
        logger.info("✅ PathwayRAGService created successfully")
        
        # Test methods exist
        assert hasattr(service, 'get_recent_messages')
        assert hasattr(service, 'search_messages')
        assert hasattr(service, 'get_problem_messages')
        assert hasattr(service, 'query_rag')
        
        logger.info("✅ PathwayRAGService methods available")
        return True
        
    except Exception as e:
        logger.error(f"❌ PathwayRAGService test failed: {e}")
        return False

def test_rag_query_service():
    """Test the RAG query service with Pathway integration."""
    try:
        from rag_query_service import rag_query_service
        
        # Test that the service exists
        assert rag_query_service is not None
        logger.info("✅ RAG query service available")
        
        # Test methods exist
        assert hasattr(rag_query_service, 'get_recent_messages')
        assert hasattr(rag_query_service, 'query_rag')
        assert hasattr(rag_query_service, 'get_predefined_insights')
        assert hasattr(rag_query_service, 'get_message_stats')
        
        logger.info("✅ RAG query service methods available")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG query service test failed: {e}")
        return False

def test_ai_service():
    """Test the AI service."""
    try:
        from ai_service import rag_service
        
        # Test that the service exists
        assert rag_service is not None
        logger.info("✅ AI service available")
        
        # Test methods exist
        assert hasattr(rag_service, 'find_relevant_messages')
        assert hasattr(rag_service, 'generate_response')
        assert hasattr(rag_service, 'get_predefined_insights')
        
        logger.info("✅ AI service methods available")
        return True
        
    except Exception as e:
        logger.error(f"❌ AI service test failed: {e}")
        return False

def test_stream_processing():
    """Test the stream processing functionality."""
    try:
        from stream import push_message, read_stream
        
        # Test that functions exist
        assert callable(push_message)
        assert callable(read_stream)
        logger.info("✅ Stream processing functions available")
        
        # Test push_message with test data
        test_msg = {
            "user": "test_user",
            "text": "test message",
            "ts": str(time.time()),
            "channel": "test_channel"
        }
        
        push_message(test_msg)
        logger.info("✅ Message push successful")
        
        # Test read_stream
        messages = list(read_stream())
        assert len(messages) > 0
        logger.info(f"✅ Stream read successful: {len(messages)} messages")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Stream processing test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    try:
        import pathway as pw
        import flask
        import google.generativeai as genai
        import numpy as np
        import pandas as pd
        from dotenv import load_dotenv
        
        logger.info("✅ All dependencies available")
        logger.info(f"  - Pathway: {pw.__version__ if hasattr(pw, '__version__') else 'installed'}")
        logger.info(f"  - Flask: {flask.__version__}")
        logger.info(f"  - Google Generative AI: {genai.__version__ if hasattr(genai, '__version__') else 'installed'}")
        logger.info(f"  - NumPy: {np.__version__}")
        logger.info(f"  - Pandas: {pd.__version__}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🧪 Testing Pathway-based Slack ingestion system...")
    logger.info("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Pathway Schemas", test_pathway_schemas),
        ("Pathway RAG Service", test_pathway_rag_service),
        ("RAG Query Service", test_rag_query_service),
        ("AI Service", test_ai_service),
        ("Stream Processing", test_stream_processing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The Pathway system is ready to use.")
        logger.info("\n🚀 To start the system, run:")
        logger.info("   python src/main.py")
    else:
        logger.info("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    # Create test messages first
    create_test_messages()
    
    # Run tests
    success = main()
    
    # Clean up test messages
    try:
        Path("messages.json").unlink()
        logger.info("🧹 Cleaned up test messages")
    except:
        pass
    
    sys.exit(0 if success else 1)
