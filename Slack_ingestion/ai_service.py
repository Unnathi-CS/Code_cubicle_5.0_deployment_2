import re
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any

class AIService:
    def __init__(self):
        self.problem_keywords = [
            'problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 
            'not working', 'failed', 'trouble', 'difficult', 'confused',
            'timeout', 'connection', 'authentication', 'deployment', 'database'
        ]
        
        self.question_keywords = [
            'how', 'what', 'where', 'when', 'why', 'can', 'could', 'would',
            'should', 'is there', 'does', 'do you', 'help me', 'explain'
        ]
        
        self.urgency_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'blocking', 'stuck',
            'deadline', 'emergency', 'priority'
        ]

    def analyze_messages(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze messages and generate rich insights."""
        if not messages:
            return self._get_empty_insights()
        
        # Categorize messages
        problems = self._find_problems(messages)
        questions = self._find_questions(messages)
        trending = self._find_trending_topics(messages)
        
        # Generate insights
        insights = {
            'problems': self._format_problems(problems),
            'questions': self._format_questions(questions),
            'trending': self._format_trending(trending)
        }
        
        return insights
    
    def _find_problems(self, messages: List[Dict]) -> List[Dict]:
        """Find problem-related messages with context."""
        problems = []
        
        for msg in messages:
            text = msg.get('text', '').lower()
            if any(keyword in text for keyword in self.problem_keywords):
                # Extract context
                context = self._extract_context(text, msg)
                problems.append({
                    'message': msg,
                    'context': context,
                    'urgency': self._assess_urgency(text),
                    'category': self._categorize_problem(text)
                })
        
        return sorted(problems, key=lambda x: x['urgency'], reverse=True)[:5]
    
    def _find_questions(self, messages: List[Dict]) -> List[Dict]:
        """Find question messages with context."""
        questions = []
        
        for msg in messages:
            text = msg.get('text', '')
            if (text.strip().endswith('?') or 
                any(keyword in text.lower() for keyword in self.question_keywords)):
                context = self._extract_context(text, msg)
                questions.append({
                    'message': msg,
                    'context': context,
                    'category': self._categorize_question(text)
                })
        
        return questions[:5]
    
    def _find_trending_topics(self, messages: List[Dict]) -> Dict[str, Any]:
        """Find trending topics and themes."""
        # Extract words and phrases
        all_text = ' '.join([msg.get('text', '') for msg in messages])
        
        # Clean and extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_counts = Counter(meaningful_words)
        
        # Extract themes
        themes = self._extract_themes(messages)
        
        return {
            'top_words': word_counts.most_common(10),
            'themes': themes,
            'team_activity': self._analyze_team_activity(messages)
        }
    
    def _extract_context(self, text: str, msg: Dict) -> str:
        """Extract meaningful context from message."""
        # Import here to avoid circular imports
        from Slack_ingestion.utils import get_slack_user_info
        
        # Clean up user mentions and convert to real usernames
        def replace_user_mention(match):
            user_id = match.group(1)
            user_info = get_slack_user_info(user_id)
            return user_info['display_name']
        
        text = re.sub(r'<@([A-Z0-9]+)>', replace_user_mention, text)
        
        # Extract key phrases
        sentences = text.split('.')
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Capitalize first letter of each sentence
        formatted_sentences = []
        for sentence in key_sentences[:2]:
            if sentence:
                sentence = sentence.strip()
                if sentence and not sentence[0].isupper():
                    sentence = sentence[0].upper() + sentence[1:]
                formatted_sentences.append(sentence)
        
        return '. '.join(formatted_sentences) if formatted_sentences else self._capitalize_first_letter(text[:100])
    
    def _capitalize_first_letter(self, text: str) -> str:
        """Capitalize the first letter of a text."""
        if not text:
            return text
        return text[0].upper() + text[1:] if text and not text[0].isupper() else text
    
    def _assess_urgency(self, text: str) -> int:
        """Assess urgency level (1-5)."""
        urgency_score = 1
        
        if any(keyword in text for keyword in self.urgency_keywords):
            urgency_score += 2
        
        if 'blocking' in text or 'stuck' in text:
            urgency_score += 1
            
        if '?' in text:
            urgency_score += 1
            
        return min(urgency_score, 5)
    
    def _categorize_problem(self, text: str) -> str:
        """Categorize the type of problem."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['database', 'connection', 'timeout']):
            return 'Database/Infrastructure'
        elif any(word in text_lower for word in ['authentication', 'login', 'auth']):
            return 'Authentication'
        elif any(word in text_lower for word in ['deployment', 'deploy', 'hosting']):
            return 'Deployment'
        elif any(word in text_lower for word in ['problem', 'statement', 'understanding']):
            return 'Problem Understanding'
        elif any(word in text_lower for word in ['api', 'endpoint', 'request']):
            return 'API Issues'
        else:
            return 'General Technical'
    
    def _categorize_question(self, text: str) -> str:
        """Categorize the type of question."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['how', 'tutorial', 'guide']):
            return 'How-to'
        elif any(word in text_lower for word in ['what', 'explain', 'clarify']):
            return 'Clarification'
        elif any(word in text_lower for word in ['where', 'find', 'location']):
            return 'Resource Location'
        else:
            return 'General Question'
    
    def _extract_themes(self, messages: List[Dict]) -> List[Dict]:
        """Extract common themes from messages."""
        themes = []
        
        # Problem statement confusion
        problem_statement_msgs = [msg for msg in messages 
                                if 'problem statement' in msg.get('text', '').lower()]
        if problem_statement_msgs:
            themes.append({
                'name': 'Problem Statement Clarification',
                'description': 'Multiple participants are struggling to understand the problem statement.',
                'count': len(problem_statement_msgs),
                'urgency': 'high'
            })
        
        # API/Authentication issues
        auth_msgs = [msg for msg in messages 
                    if any(word in msg.get('text', '').lower() 
                          for word in ['authentication', 'api', 'auth', 'login'])]
        if auth_msgs:
            themes.append({
                'name': 'API & Authentication Issues',
                'description': 'Several teams are reporting problems with API authentication and general authentication flows.',
                'count': len(auth_msgs),
                'urgency': 'high'
            })
        
        # Deployment issues
        deploy_msgs = [msg for msg in messages 
                      if any(word in msg.get('text', '').lower() 
                            for word in ['deployment', 'deploy', 'hosting', 'database connection'])]
        if deploy_msgs:
            themes.append({
                'name': 'Deployment & Infrastructure',
                'description': 'Questions about deploying apps and database connection timeouts highlight infrastructure challenges.',
                'count': len(deploy_msgs),
                'urgency': 'medium'
            })
        
        return themes
    
    def _analyze_team_activity(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze team activity patterns."""
        user_activity = {}
        for msg in messages:
            user = msg.get('user', 'unknown')
            user_activity[user] = user_activity.get(user, 0) + 1
        
        return {
            'most_active_users': sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5],
            'total_active_users': len(user_activity),
            'activity_level': 'high' if len(user_activity) > 3 else 'medium' if len(user_activity) > 1 else 'low'
        }
    
    def _format_problems(self, problems: List[Dict]) -> str:
        """Format problems for display."""
        if not problems:
            return "No problems detected recently. Great job! 🎉"
        
        formatted = "<strong>Top Problems Identified:</strong><br><br>"
        
        for i, problem in enumerate(problems, 1):
            urgency_icon = "🚨" if problem['urgency'] >= 4 else "⚠️" if problem['urgency'] >= 3 else ""
            category = problem['category']
            context = problem['context'][:100] + "..." if len(problem['context']) > 100 else problem['context']
            
            formatted += f"{i}. <strong>{category}:</strong> {context} {urgency_icon}<br>"
        
        return formatted
    
    def _format_questions(self, questions: List[Dict]) -> str:
        """Format questions for display."""
        if not questions:
            return "No questions found recently. Teams seem to be working smoothly! 👍"
        
        # Group by category
        categories = {}
        for q in questions:
            cat = q['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(q)
        
        formatted = "<strong>Top Questions by Category:</strong><br><br>"
        
        for category, qs in list(categories.items()):
            formatted += f"<strong>{category}:</strong><br>"
            for q in qs:
                context = q['context'][:80] + "..." if len(q['context']) > 80 else q['context']
                formatted += f"&bull; {context}<br>"
            formatted += "<br>"
        
        return formatted
    
    def _format_trending(self, trending: Dict[str, Any]) -> str:
        """Format trending topics for display."""
        if not trending['themes']:
            return "No trending topics identified. Activity seems steady! 📊"
        
        formatted = "<strong>Current Trends:</strong><br><br>"
        
        for theme in trending['themes']:
            urgency_icon = "🚨" if theme['urgency'] == 'high' else "⚠️" if theme['urgency'] == 'medium' else "📈"
            formatted += f"<strong>{theme['name']}:</strong> {theme['description']} {urgency_icon}<br><br>"
        
        # Add top words
        if trending['top_words']:
            top_words = [word for word, count in trending['top_words'][:5]]
            formatted += f"<strong>Key Terms:</strong> {', '.join(top_words)}"
        
        return formatted
    
    def _get_empty_insights(self) -> Dict[str, str]:
        """Return empty insights when no messages."""
        return {
            'problems': "No recent activity to analyze. Waiting for messages...",
            'questions': "No questions detected yet. Teams might be working independently.",
            'trending': "No trending topics identified. Activity level is low."
        }

# Global instance
ai_service = AIService()


