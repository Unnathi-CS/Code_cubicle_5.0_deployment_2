#!/usr/bin/env python3
"""
Demo script showing Pathway database concepts for the Slack ingestion system.
This demonstrates how Pathway's built-in database engine would work.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulate Pathway Schema concepts
@dataclass
class MessageSchema:
    """Simulated Pathway Schema for messages."""
    user: str
    text: str
    ts: str
    channel: str = ""
    message_id: str = ""
    thread_ts: str = ""
    message_type: str = "message"

@dataclass
class UserSchema:
    """Simulated Pathway Schema for users."""
    user_id: str
    username: str
    display_name: str = ""
    first_seen: str = ""
    message_count: int = 0

@dataclass
class ChannelSchema:
    """Simulated Pathway Schema for channels."""
    channel_id: str
    channel_name: str
    channel_type: str = "public"
    message_count: int = 0

class PathwayDatabase:
    """
    Simulated Pathway built-in database engine.
    This demonstrates how Pathway's native database would work.
    """
    
    def __init__(self):
        self.messages = []
        self.users = {}
        self.channels = {}
        self.analytics = []
        self.indexes = {
            'by_user': defaultdict(list),
            'by_channel': defaultdict(list),
            'by_timestamp': [],
            'by_text': defaultdict(list)
        }
    
    def insert_message(self, message: MessageSchema):
        """Insert a message into the database (simulating Pathway's incremental updates)."""
        # Add to main table
        self.messages.append(message)
        
        # Update indexes (Pathway does this automatically)
        self.indexes['by_user'][message.user].append(len(self.messages) - 1)
        self.indexes['by_channel'][message.channel].append(len(self.messages) - 1)
        self.indexes['by_timestamp'].append((float(message.ts), len(self.messages) - 1))
        
        # Text search index
        words = message.text.lower().split()
        for word in words:
            self.indexes['by_text'][word].append(len(self.messages) - 1)
        
        # Update user stats
        if message.user not in self.users:
            self.users[message.user] = UserSchema(
                user_id=message.user,
                username=message.user,
                display_name=message.user,
                first_seen=message.ts,
                message_count=0
            )
        self.users[message.user].message_count += 1
        
        # Update channel stats
        if message.channel not in self.channels:
            self.channels[message.channel] = ChannelSchema(
                channel_id=message.channel,
                channel_name=message.channel,
                channel_type="public",
                message_count=0
            )
        self.channels[message.channel].message_count += 1
        
        logger.info(f"✅ Message inserted: {message.user} in {message.channel}")
    
    def query_recent_messages(self, hours: int = 24, limit: int = 100, channel: Optional[str] = None) -> List[Dict]:
        """Query recent messages (simulating Pathway's SQL-like queries)."""
        cutoff_time = time.time() - (hours * 3600)
        
        # Use timestamp index for efficient querying
        recent_indices = []
        for timestamp, idx in sorted(self.indexes['by_timestamp'], reverse=True):
            if timestamp >= cutoff_time:
                recent_indices.append(idx)
                if len(recent_indices) >= limit:
                    break
        
        results = []
        for idx in recent_indices:
            msg = self.messages[idx]
            if channel is None or msg.channel == channel:
                results.append({
                    'message_id': msg.message_id,
                    'user': msg.user,
                    'text': msg.text,
                    'channel': msg.channel,
                    'timestamp': datetime.fromtimestamp(float(msg.ts)).isoformat(),
                    'ts': msg.ts,
                    'message_length': len(msg.text),
                    'is_question': msg.text.strip().endswith('?'),
                    'has_problem_keywords': any(keyword in msg.text.lower() 
                                              for keyword in ['problem', 'issue', 'error', 'bug', 'stuck', 'help']),
                    'has_urgency': any(keyword in msg.text.lower() 
                                     for keyword in ['urgent', 'asap', 'emergency', 'critical'])
                })
        
        logger.info(f"🔍 Query returned {len(results)} recent messages")
        return results
    
    def search_messages(self, query_text: str, limit: int = 10, channel: Optional[str] = None) -> List[Dict]:
        """Search messages using text matching (simulating Pathway's search capabilities)."""
        query_words = set(query_text.lower().split())
        
        # Use text index for efficient search
        matching_indices = set()
        for word in query_words:
            if word in self.indexes['by_text']:
                matching_indices.update(self.indexes['by_text'][word])
        
        results = []
        for idx in sorted(matching_indices, reverse=True):
            msg = self.messages[idx]
            if channel is None or msg.channel == channel:
                results.append({
                    'message_id': msg.message_id,
                    'user': msg.user,
                    'text': msg.text,
                    'channel': msg.channel,
                    'timestamp': datetime.fromtimestamp(float(msg.ts)).isoformat(),
                    'ts': msg.ts,
                    'message_length': len(msg.text),
                    'is_question': msg.text.strip().endswith('?'),
                    'has_problem_keywords': any(keyword in msg.text.lower() 
                                              for keyword in ['problem', 'issue', 'error', 'bug', 'stuck', 'help']),
                    'has_urgency': any(keyword in msg.text.lower() 
                                     for keyword in ['urgent', 'asap', 'emergency', 'critical'])
                })
                if len(results) >= limit:
                    break
        
        logger.info(f"🔍 Search returned {len(results)} matching messages")
        return results
    
    def get_problem_messages(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """Get messages with problem keywords (simulating Pathway's filtering)."""
        cutoff_time = time.time() - (hours * 3600)
        problem_keywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'not working']
        
        results = []
        for idx, msg in enumerate(self.messages):
            if float(msg.ts) >= cutoff_time:
                if any(keyword in msg.text.lower() for keyword in problem_keywords):
                    results.append({
                        'message_id': msg.message_id,
                        'user': msg.user,
                        'text': msg.text,
                        'channel': msg.channel,
                        'timestamp': datetime.fromtimestamp(float(msg.ts)).isoformat(),
                        'ts': msg.ts,
                        'message_length': len(msg.text),
                        'is_question': msg.text.strip().endswith('?'),
                        'has_problem_keywords': True,
                        'has_urgency': any(keyword in msg.text.lower() 
                                         for keyword in ['urgent', 'asap', 'emergency', 'critical'])
                    })
                    if len(results) >= limit:
                        break
        
        logger.info(f"🔍 Found {len(results)} problem messages")
        return results
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics (simulating Pathway's aggregation capabilities)."""
        total_messages = len(self.messages)
        unique_users = len(self.users)
        unique_channels = len(self.channels)
        
        # Calculate message length stats
        message_lengths = [len(msg.text) for msg in self.messages]
        avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        
        # Count questions and problems
        questions_count = sum(1 for msg in self.messages if msg.text.strip().endswith('?'))
        problem_keywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'not working']
        problems_count = sum(1 for msg in self.messages 
                           if any(keyword in msg.text.lower() for keyword in problem_keywords))
        
        return {
            'total_messages': total_messages,
            'unique_users': unique_users,
            'unique_channels': unique_channels,
            'avg_message_length': round(avg_message_length, 1),
            'questions_count': questions_count,
            'problems_count': problems_count,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_channel_stats(self) -> List[Dict[str, Any]]:
        """Get statistics per channel (simulating Pathway's groupby operations)."""
        channel_stats = []
        for channel_id, channel in self.channels.items():
            channel_messages = [msg for msg in self.messages if msg.channel == channel_id]
            
            questions_count = sum(1 for msg in channel_messages if msg.text.strip().endswith('?'))
            problem_keywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'not working']
            problems_count = sum(1 for msg in channel_messages 
                               if any(keyword in msg.text.lower() for keyword in problem_keywords))
            urgent_count = sum(1 for msg in channel_messages 
                             if any(keyword in msg.text.lower() 
                                   for keyword in ['urgent', 'asap', 'emergency', 'critical']))
            
            channel_stats.append({
                'channel': channel_id,
                'message_count': len(channel_messages),
                'questions_count': questions_count,
                'problems_count': problems_count,
                'urgent_count': urgent_count
            })
        
        return channel_stats

def create_test_data():
    """Create test data to demonstrate the system."""
    test_messages = [
        MessageSchema(
            user="alice",
            text="I'm having trouble with the API integration. Can anyone help?",
            ts=str(time.time() - 3600),
            channel="general",
            message_id="test_1",
            message_type="message"
        ),
        MessageSchema(
            user="bob",
            text="What's the deadline for the hackathon?",
            ts=str(time.time() - 1800),
            channel="general",
            message_id="test_2",
            message_type="message"
        ),
        MessageSchema(
            user="charlie",
            text="Our database connection is broken! This is urgent!",
            ts=str(time.time() - 900),
            channel="tech-support",
            message_id="test_3",
            message_type="message"
        ),
        MessageSchema(
            user="diana",
            text="Has anyone used React with TypeScript before?",
            ts=str(time.time() - 600),
            channel="general",
            message_id="test_4",
            message_type="message"
        ),
        MessageSchema(
            user="eve",
            text="We need help with deployment. Our app won't start.",
            ts=str(time.time() - 300),
            channel="general",
            message_id="test_5",
            message_type="message"
        )
    ]
    return test_messages

def demo_pathway_database():
    """Demonstrate Pathway database concepts."""
    logger.info("🚀 Pathway Database Demo - Built-in Database Engine")
    logger.info("=" * 60)
    
    # Initialize the simulated Pathway database
    db = PathwayDatabase()
    
    # Insert test data
    logger.info("\n📥 Inserting test messages...")
    test_messages = create_test_data()
    for msg in test_messages:
        db.insert_message(msg)
    
    # Demonstrate queries
    logger.info("\n🔍 Demonstrating Pathway SQL-like queries...")
    
    # Recent messages query
    recent = db.query_recent_messages(hours=2, limit=10)
    logger.info(f"Recent messages (last 2 hours): {len(recent)} found")
    
    # Search query
    search_results = db.search_messages("API integration", limit=5)
    logger.info(f"Search for 'API integration': {len(search_results)} found")
    
    # Problem messages query
    problems = db.get_problem_messages(hours=24, limit=10)
    logger.info(f"Problem messages: {len(problems)} found")
    
    # Analytics query
    analytics = db.get_analytics()
    logger.info(f"Analytics: {analytics}")
    
    # Channel stats query
    channel_stats = db.get_channel_stats()
    logger.info(f"Channel stats: {len(channel_stats)} channels")
    
    logger.info("\n✅ Pathway Database Demo Complete!")
    logger.info("\nKey Benefits Demonstrated:")
    logger.info("  🔥 Built-in database engine - no external DB setup")
    logger.info("  ⚡ Real-time incremental updates")
    logger.info("  🔍 Automatic indexing for fast queries")
    logger.info("  📊 SQL-like query capabilities")
    logger.info("  🎯 Memory-efficient streaming data processing")
    
    return db

def demo_rag_integration():
    """Demonstrate RAG integration with Pathway database."""
    logger.info("\n🤖 RAG Integration Demo")
    logger.info("=" * 40)
    
    # Initialize database with test data
    db = PathwayDatabase()
    test_messages = create_test_data()
    for msg in test_messages:
        db.insert_message(msg)
    
    # Simulate RAG queries
    queries = [
        "What problems are teams facing?",
        "Who needs help with deployment?",
        "What questions are being asked?",
        "Show me urgent messages"
    ]
    
    for query in queries:
        logger.info(f"\n🔍 Query: '{query}'")
        
        # Use Pathway database to find relevant messages
        if "problem" in query.lower():
            results = db.get_problem_messages(hours=24, limit=5)
        elif "deployment" in query.lower():
            results = db.search_messages("deployment", limit=5)
        elif "question" in query.lower():
            results = db.search_messages("?", limit=5)
        elif "urgent" in query.lower():
            results = [msg for msg in db.query_recent_messages(hours=24, limit=10) 
                      if msg.get('has_urgency', False)]
        else:
            results = db.search_messages(query, limit=5)
        
        logger.info(f"  📊 Found {len(results)} relevant messages")
        for i, msg in enumerate(results[:3], 1):
            logger.info(f"    {i}. [{msg['user']}] {msg['text'][:50]}...")
    
    logger.info("\n✅ RAG Integration Demo Complete!")

def main():
    """Run the complete Pathway database demo."""
    logger.info("🎯 Pathway Built-in Database Engine Demo")
    logger.info("This demonstrates how Pathway's native database works")
    logger.info("without requiring external databases like PostgreSQL, Redis, or MongoDB")
    logger.info("=" * 80)
    
    # Run demos
    db = demo_pathway_database()
    demo_rag_integration()
    
    logger.info("\n🎉 Demo Complete!")
    logger.info("\nTo use the real Pathway system:")
    logger.info("1. Install the official Pathway package")
    logger.info("2. Use the code in src/pathway_pipeline.py")
    logger.info("3. Run: python src/main.py")
    
    return True

if __name__ == "__main__":
    main()
