import pathway as pw
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ai_service import rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PathwayRAGService:
    def __init__(self, pathway_tables: Dict[str, pw.Table]):
        """Initialize the Pathway-based RAG service."""
        self.tables = pathway_tables
        self.rag_service = rag_service
        
    def get_recent_messages(self, hours: int = 24, limit: int = 100, channel: Optional[str] = None) -> List[Dict]:
        """Get recent messages using Pathway SQL queries."""
        try:
            # Calculate cutoff timestamp
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Build query
            query = self.tables['rag_index'].filter(
                self.tables['rag_index'].timestamp_parsed >= cutoff_timestamp
            )
            
            # Filter by channel if specified
            if channel:
                query = query.filter(self.tables['rag_index'].channel == channel)
            
            # Order by timestamp and limit
            query = query.sort(key=query.timestamp_parsed, reverse=True)
            
            # Execute query and convert to list of dicts
            messages = []
            for row in pw.debug.compute_and_print(query):
                messages.append({
                    'message_id': row['message_id'],
                    'user': row['user'],
                    'text': row['text'],
                    'channel': row['channel'],
                    'timestamp': row['timestamp'],
                    'ts': str(row['timestamp_parsed']),
                    'message_length': row['message_length'],
                    'is_question': row['is_question'],
                    'has_problem_keywords': row['has_problem_keywords'],
                    'has_urgency': row['has_urgency']
                })
                
                if len(messages) >= limit:
                    break
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    def search_messages(self, query_text: str, limit: int = 10, channel: Optional[str] = None) -> List[Dict]:
        """Search messages using Pathway text matching."""
        try:
            # Convert query to lowercase for matching
            search_text = query_text.lower()
            
            # Build search query
            query = self.tables['rag_index'].filter(
                self.tables['rag_index'].searchable_text.str.contains(search_text)
            )
            
            # Filter by channel if specified
            if channel:
                query = query.filter(self.tables['rag_index'].channel == channel)
            
            # Order by timestamp (most recent first)
            query = query.sort(key=query.timestamp_parsed, reverse=True)
            
            # Execute query
            messages = []
            for row in pw.debug.compute_and_print(query):
                messages.append({
                    'message_id': row['message_id'],
                    'user': row['user'],
                    'text': row['text'],
                    'channel': row['channel'],
                    'timestamp': row['timestamp'],
                    'ts': str(row['timestamp_parsed']),
                    'message_length': row['message_length'],
                    'is_question': row['is_question'],
                    'has_problem_keywords': row['has_problem_keywords'],
                    'has_urgency': row['has_urgency']
                })
                
                if len(messages) >= limit:
                    break
            
            return messages
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    def get_problem_messages(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """Get messages that contain problem keywords."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            query = self.tables['rag_index'].filter(
                (self.tables['rag_index'].has_problem_keywords == True) &
                (self.tables['rag_index'].timestamp_parsed >= cutoff_timestamp)
            ).sort(key=self.tables['rag_index'].timestamp_parsed, reverse=True)
            
            messages = []
            for row in pw.debug.compute_and_print(query):
                messages.append({
                    'message_id': row['message_id'],
                    'user': row['user'],
                    'text': row['text'],
                    'channel': row['channel'],
                    'timestamp': row['timestamp'],
                    'ts': str(row['timestamp_parsed']),
                    'message_length': row['message_length'],
                    'is_question': row['is_question'],
                    'has_problem_keywords': row['has_problem_keywords'],
                    'has_urgency': row['has_urgency']
                })
                
                if len(messages) >= limit:
                    break
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting problem messages: {e}")
            return []
    
    def get_question_messages(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """Get messages that are questions."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            query = self.tables['rag_index'].filter(
                (self.tables['rag_index'].is_question == True) &
                (self.tables['rag_index'].timestamp_parsed >= cutoff_timestamp)
            ).sort(key=self.tables['rag_index'].timestamp_parsed, reverse=True)
            
            messages = []
            for row in pw.debug.compute_and_print(query):
                messages.append({
                    'message_id': row['message_id'],
                    'user': row['user'],
                    'text': row['text'],
                    'channel': row['channel'],
                    'timestamp': row['timestamp'],
                    'ts': str(row['timestamp_parsed']),
                    'message_length': row['message_length'],
                    'is_question': row['is_question'],
                    'has_problem_keywords': row['has_problem_keywords'],
                    'has_urgency': row['has_urgency']
                })
                
                if len(messages) >= limit:
                    break
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting question messages: {e}")
            return []
    
    def get_urgent_messages(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get messages marked as urgent."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            query = self.tables['rag_index'].filter(
                (self.tables['rag_index'].has_urgency == True) &
                (self.tables['rag_index'].timestamp_parsed >= cutoff_timestamp)
            ).sort(key=self.tables['rag_index'].timestamp_parsed, reverse=True)
            
            messages = []
            for row in pw.debug.compute_and_print(query):
                messages.append({
                    'message_id': row['message_id'],
                    'user': row['user'],
                    'text': row['text'],
                    'channel': row['channel'],
                    'timestamp': row['timestamp'],
                    'ts': str(row['timestamp_parsed']),
                    'message_length': row['message_length'],
                    'is_question': row['is_question'],
                    'has_problem_keywords': row['has_problem_keywords'],
                    'has_urgency': row['has_urgency']
                })
                
                if len(messages) >= limit:
                    break
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting urgent messages: {e}")
            return []
    
    def query_rag(self, query: str, context_hours: int = 2) -> str:
        """Query the RAG system using Pathway database."""
        try:
            # First try to find relevant messages using search
            relevant_messages = self.search_messages(query, limit=10)
            
            # If no search results, get recent messages
            if not relevant_messages:
                relevant_messages = self.get_recent_messages(hours=context_hours, limit=20)
            
            if not relevant_messages:
                return "No recent messages available to analyze. Please check if the chat integration is working."
            
            # Generate response using AI service
            response = self.rag_service.generate_response(query, relevant_messages)
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return f"I'm having trouble processing that request. Error: {str(e)}"
    
    def get_predefined_insights(self) -> Dict[str, str]:
        """Get predefined insights using Pathway queries."""
        try:
            # Get problem messages
            problem_messages = self.get_problem_messages(hours=6, limit=10)
            problems_insight = ""
            if problem_messages:
                problems_insight = self.rag_service.generate_response(
                    "What are the top 3 problems teams are facing right now?", 
                    problem_messages[:5]
                )
            else:
                problems_insight = "No problems detected in recent messages."
            
            # Get question messages
            question_messages = self.get_question_messages(hours=6, limit=10)
            questions_insight = ""
            if question_messages:
                questions_insight = self.rag_service.generate_response(
                    "Summarize the most frequently asked questions.", 
                    question_messages[:5]
                )
            else:
                questions_insight = "No questions detected in recent messages."
            
            # Get trending topics from recent messages
            recent_messages = self.get_recent_messages(hours=2, limit=20)
            trending_insight = ""
            if recent_messages:
                trending_insight = self.rag_service.generate_response(
                    "What topics are trending in the chat right now?", 
                    recent_messages
                )
            else:
                trending_insight = "No recent activity to analyze."
            
            return {
                'problems': problems_insight,
                'questions': questions_insight,
                'trending': trending_insight
            }
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {
                'problems': 'Unable to analyze problems at the moment.',
                'questions': 'Unable to analyze questions at the moment.',
                'trending': 'Unable to analyze trending topics at the moment.'
            }
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get message statistics using Pathway analytics."""
        try:
            # Get recent messages for stats
            recent_messages = self.get_recent_messages(hours=24, limit=1000)
            
            if not recent_messages:
                return {
                    'total_messages': 0,
                    'unique_users': 0,
                    'avg_message_length': 0,
                    'questions_count': 0,
                    'problems_count': 0,
                    'urgent_count': 0,
                    'channels_count': 0
                }
            
            # Calculate stats
            total_messages = len(recent_messages)
            unique_users = len(set(msg.get('user', '') for msg in recent_messages))
            unique_channels = len(set(msg.get('channel', '') for msg in recent_messages))
            
            # Message length analysis
            message_lengths = [msg.get('message_length', 0) for msg in recent_messages]
            avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
            
            # Question and problem analysis
            questions_count = sum(1 for msg in recent_messages if msg.get('is_question', False))
            problems_count = sum(1 for msg in recent_messages if msg.get('has_problem_keywords', False))
            urgent_count = sum(1 for msg in recent_messages if msg.get('has_urgency', False))
            
            return {
                'total_messages': total_messages,
                'unique_users': unique_users,
                'unique_channels': unique_channels,
                'avg_message_length': round(avg_message_length, 1),
                'questions_count': questions_count,
                'problems_count': problems_count,
                'urgent_count': urgent_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {
                'total_messages': 0,
                'unique_users': 0,
                'unique_channels': 0,
                'avg_message_length': 0,
                'questions_count': 0,
                'problems_count': 0,
                'urgent_count': 0,
                'error': str(e)
            }
    
    def get_channel_stats(self) -> List[Dict[str, Any]]:
        """Get statistics per channel."""
        try:
            # This would use the channels table and hourly_stats
            # For now, return basic channel info
            recent_messages = self.get_recent_messages(hours=24, limit=1000)
            
            channel_stats = {}
            for msg in recent_messages:
                channel = msg.get('channel', 'unknown')
                if channel not in channel_stats:
                    channel_stats[channel] = {
                        'channel': channel,
                        'message_count': 0,
                        'questions_count': 0,
                        'problems_count': 0,
                        'urgent_count': 0
                    }
                
                channel_stats[channel]['message_count'] += 1
                if msg.get('is_question', False):
                    channel_stats[channel]['questions_count'] += 1
                if msg.get('has_problem_keywords', False):
                    channel_stats[channel]['problems_count'] += 1
                if msg.get('has_urgency', False):
                    channel_stats[channel]['urgent_count'] += 1
            
            return list(channel_stats.values())
            
        except Exception as e:
            logger.error(f"Error getting channel stats: {e}")
            return []

# Global instance - will be initialized with tables from pathway_pipeline
pathway_rag_service = None

def initialize_pathway_rag_service(tables: Dict[str, pw.Table]):
    """Initialize the global Pathway RAG service with tables."""
    global pathway_rag_service
    pathway_rag_service = PathwayRAGService(tables)
    return pathway_rag_service
