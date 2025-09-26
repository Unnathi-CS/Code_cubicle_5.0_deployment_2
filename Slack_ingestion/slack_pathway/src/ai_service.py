import google.generativeai as genai
import os
import json
from typing import List, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        """Initialize the RAG service with Gemini API."""
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("AI_MODEL", "gemini-1.5-flash"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Gemini API."""
        try:
            # Gemini doesn't have a direct embedding API, so we'll use keyword matching instead
            # This method is kept for compatibility but will return empty list
            logger.info("Using keyword-based matching instead of embeddings")
            return []
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return []
    
    def find_relevant_messages(self, query: str, messages: List[Dict], top_k: int = 5) -> List[Dict]:
        """Find most relevant messages for a query using keyword matching."""
        if not messages:
            return []
        
        # Extract keywords from query
        query_words = set(query.lower().split())
        
        # Score messages based on keyword matches
        scored_messages = []
        for msg in messages:
            msg_text = msg.get('text', '').lower()
            msg_words = set(msg_text.split())
            
            # Calculate simple keyword overlap score
            overlap = len(query_words.intersection(msg_words))
            if overlap > 0:
                scored_messages.append((overlap, msg))
        
        # Sort by score and return top_k
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        
        # If no keyword matches, return recent messages
        if not scored_messages:
            return sorted(messages, key=lambda x: x.get('ts', ''), reverse=True)[:top_k]
        
        return [msg for _, msg in scored_messages[:top_k]]
    
    def generate_response(self, query: str, context_messages: List[Dict]) -> str:
        """Generate AI response using RAG with context from relevant messages."""
        try:
            # Prepare context
            context_text = self._prepare_context(context_messages)
            
            # Create prompt for Gemini
            prompt = f"""You are an AI assistant monitoring a hackathon in real-time. 
            You analyze live chat messages from Slack/Discord/Telegram to help organizers and participants.
            
            Your role:
            - Summarize problems teams are facing
            - Identify trending topics and common issues
            - Provide insights about team dynamics and progress
            - Answer questions about what's happening in the hackathon
            
            Be concise, helpful, and focus on actionable insights. Use emojis sparingly but effectively.

            Query: {query}

            Recent chat context:
            {context_text}

            Please provide a helpful response based on the current hackathon chat activity."""

            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I'm having trouble processing that request right now. Error: {str(e)}"
    
    def _prepare_context(self, messages: List[Dict]) -> str:
        """Prepare context string from relevant messages."""
        if not messages:
            return "No recent messages available."
        
        context_parts = []
        for i, msg in enumerate(messages, 1):
            user = msg.get('user', 'Unknown')
            text = msg.get('text', '')
            timestamp = msg.get('ts', '')
            
            # Format timestamp if available
            if timestamp:
                try:
                    dt = datetime.fromtimestamp(float(timestamp))
                    time_str = dt.strftime("%H:%M")
                except:
                    time_str = timestamp
            else:
                time_str = "Unknown time"
            
            context_parts.append(f"{i}. [{time_str}] {user}: {text}")
        
        return "\n".join(context_parts)
    
    def get_predefined_insights(self, messages: List[Dict]) -> Dict[str, str]:
        """Get predefined insights for demo purposes."""
        insights = {}
        
        # Problem analysis
        problem_keywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'not working']
        problem_messages = [msg for msg in messages 
                           if any(keyword in msg.get('text', '').lower() for keyword in problem_keywords)]
        
        if problem_messages:
            insights['problems'] = self.generate_response(
                "What are the top 3 problems teams are facing right now?", 
                problem_messages[:5]
            )
        
        # Question analysis
        question_messages = [msg for msg in messages 
                            if msg.get('text', '').strip().endswith('?')]
        
        if question_messages:
            insights['questions'] = self.generate_response(
                "Summarize the most frequently asked questions.", 
                question_messages[:5]
            )
        
        # Trending topics
        insights['trending'] = self.generate_response(
            "What topics are trending in the chat right now?", 
            messages[-10:]  # Last 10 messages
        )
        
        return insights

# Global instance
rag_service = RAGService()
