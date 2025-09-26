import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from ai_service import rag_service
from pathway_rag_service import pathway_rag_service, initialize_pathway_rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGQueryService:
    def __init__(self):
        """Initialize the RAG query service."""
        self.messages_file = Path("messages.json")
        self.rag_service = rag_service
        self.pathway_service = pathway_rag_service
        
    def get_recent_messages(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get recent messages from the stream."""
        # Use Pathway service if available
        if self.pathway_service:
            try:
                return self.pathway_service.get_recent_messages(hours=hours, limit=limit)
            except Exception as e:
                logger.error(f"Error using Pathway service: {e}")
                # Fall back to file-based approach
        
        # Fallback to file-based approach
        messages = []
        
        if not self.messages_file.exists():
            return messages
            
        try:
            with self.messages_file.open() as f:
                for line in f:
                    if line.strip():
                        msg = json.loads(line.strip())
                        messages.append(msg)
            
            # Sort by timestamp (most recent first)
            messages.sort(key=lambda x: float(x.get('ts', '0')), reverse=True)
            
            # Filter by time if needed
            if hours < 24:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                filtered_messages = []
                for msg in messages:
                    try:
                        msg_time = datetime.fromtimestamp(float(msg.get('ts', '0')))
                        if msg_time >= cutoff_time:
                            filtered_messages.append(msg)
                    except:
                        continue
                messages = filtered_messages
            
            return messages[:limit]
            
        except Exception as e:
            logger.error(f"Error reading messages: {e}")
            return []
    
    def query_rag(self, query: str, context_hours: int = 2) -> str:
        """Query the RAG system with recent context."""
        # Use Pathway service if available
        if self.pathway_service:
            try:
                return self.pathway_service.query_rag(query, context_hours)
            except Exception as e:
                logger.error(f"Error using Pathway service: {e}")
                # Fall back to original approach
        
        # Fallback to original approach
        try:
            # Get recent messages for context
            recent_messages = self.get_recent_messages(hours=context_hours, limit=50)
            
            if not recent_messages:
                return "No recent messages available to analyze. Please check if the chat integration is working."
            
            # Find relevant messages
            relevant_messages = self.rag_service.find_relevant_messages(query, recent_messages, top_k=10)
            
            # Generate response
            response = self.rag_service.generate_response(query, relevant_messages)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return f"I'm having trouble processing that request. Error: {str(e)}"
    
    def get_predefined_insights(self) -> Dict[str, str]:
        """Get predefined insights for demo purposes."""
        # Use Pathway service if available
        if self.pathway_service:
            try:
                return self.pathway_service.get_predefined_insights()
            except Exception as e:
                logger.error(f"Error using Pathway service: {e}")
                # Fall back to original approach
        
        # Fallback to original approach
        try:
            recent_messages = self.get_recent_messages(hours=6, limit=100)
            return self.rag_service.get_predefined_insights(recent_messages)
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {
                'problems': 'Unable to analyze problems at the moment.',
                'questions': 'Unable to analyze questions at the moment.',
                'trending': 'Unable to analyze trending topics at the moment.'
            }
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get basic statistics about messages."""
        # Use Pathway service if available
        if self.pathway_service:
            try:
                return self.pathway_service.get_message_stats()
            except Exception as e:
                logger.error(f"Error using Pathway service: {e}")
                # Fall back to original approach
        
        # Fallback to original approach
        try:
            messages = self.get_recent_messages(hours=24, limit=1000)
            
            if not messages:
                return {
                    'total_messages': 0,
                    'unique_users': 0,
                    'avg_message_length': 0,
                    'questions_count': 0,
                    'problems_count': 0
                }
            
            # Calculate stats
            total_messages = len(messages)
            unique_users = len(set(msg.get('user', '') for msg in messages))
            
            # Message length analysis
            message_lengths = [len(msg.get('text', '')) for msg in messages]
            avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
            
            # Question and problem analysis
            questions_count = sum(1 for msg in messages if msg.get('text', '').strip().endswith('?'))
            problem_keywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'not working']
            problems_count = sum(1 for msg in messages 
                               if any(keyword in msg.get('text', '').lower() for keyword in problem_keywords))
            
            return {
                'total_messages': total_messages,
                'unique_users': unique_users,
                'avg_message_length': round(avg_message_length, 1),
                'questions_count': questions_count,
                'problems_count': problems_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {
                'total_messages': 0,
                'unique_users': 0,
                'avg_message_length': 0,
                'questions_count': 0,
                'problems_count': 0,
                'error': str(e)
            }

# Global instance
rag_query_service = RAGQueryService()
