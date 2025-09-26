from flask import Flask, request, render_template, jsonify, redirect, session, url_for
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from authlib.integrations.flask_client import OAuth
from Slack_ingestion.ai_service import ai_service
from Slack_ingestion.utils import markdown_to_html, clean_message_text, highlight_keywords, format_user_mention


load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

# Google OAuth setup
app.config.update(
    GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID", ""),
    GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    SERVER_NAME=os.getenv("SERVER_NAME"),
    PREFERRED_URL_SCHEME=os.getenv("PREFERRED_URL_SCHEME", "http"),
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
)

# In-memory storage for messages (simple approach)
messages = []

def handle_general_question(user_message, query_lower):
    """Handle general questions about programming, technology, and skills."""
    
    # Programming skills and hackathon preparation
    if any(keyword in query_lower for keyword in ['skills', 'hackathon', 'participate', 'prepare']):
        return """<strong>Essential Skills for Hackathons:</strong><br><br>
        <strong>Technical Skills:</strong><br>
        &bull; <strong>Programming Languages:</strong> Python, JavaScript, Java, or C++<br>
        &bull; <strong>Web Development:</strong> HTML, CSS, React, Node.js<br>
        &bull; <strong>Mobile Development:</strong> React Native, Flutter, or native development<br>
        &bull; <strong>Backend:</strong> APIs, databases (SQL/NoSQL), cloud services<br>
        &bull; <strong>Tools:</strong> Git, GitHub, VS Code, command line<br><br>
        
        <strong>Soft Skills:</strong><br>
        &bull; <strong>Teamwork:</strong> Collaboration and communication<br>
        &bull; <strong>Problem-solving:</strong> Breaking down complex problems<br>
        &bull; <strong>Time management:</strong> Working under pressure<br>
        &bull; <strong>Presentation:</strong> Pitching your idea effectively<br><br>
        
        <strong>Quick Start Tips:</strong><br>
        &bull; Start with one language and master the basics<br>
        &bull; Build small projects to practice<br>
        &bull; Learn version control (Git) early<br>
        &bull; Join coding communities for support<br>
        &bull; Don't worry about being perfect - focus on learning! 🚀"""
    
    # Programming languages
    elif 'python' in query_lower:
        return """<strong>Python for Hackathons:</strong><br><br>
        <strong>Why Python is Great:</strong><br>
        &bull; Easy to learn and read<br>
        &bull; Powerful libraries (Flask, Django, Pandas, NumPy)<br>
        &bull; Great for AI/ML projects<br>
        &bull; Rapid prototyping<br><br>
        
        <strong>Essential Python Libraries:</strong><br>
        &bull; <strong>Flask/Django:</strong> Web development<br>
        &bull; <strong>Pandas:</strong> Data analysis<br>
        &bull; <strong>Requests:</strong> API calls<br>
        &bull; <strong>BeautifulSoup:</strong> Web scraping<br>
        &bull; <strong>OpenCV:</strong> Computer vision<br><br>
        
        <strong>Quick Python Tips:</strong><br>
        &bull; Use virtual environments<br>
        &bull; Learn list comprehensions<br>
        &bull; Master error handling (try/except)<br>
        &bull; Practice with real projects! 💻"""
    
    elif 'javascript' in query_lower or 'js' in query_lower:
        return """<strong>JavaScript for Hackathons:</strong><br><br>
        <strong>Why JavaScript is Powerful:</strong><br>
        &bull; Works everywhere (frontend, backend, mobile)<br>
        &bull; Huge ecosystem (React, Node.js, Express)<br>
        &bull; Real-time applications<br>
        &bull; Easy to get started<br><br>
        
        <strong>Essential JavaScript Stack:</strong><br>
        &bull; <strong>Frontend:</strong> React, Vue.js, or vanilla JS<br>
        &bull; <strong>Backend:</strong> Node.js with Express<br>
        &bull; <strong>Database:</strong> MongoDB or PostgreSQL<br>
        &bull; <strong>Tools:</strong> npm, webpack, Babel<br><br>
        
        <strong>Quick JS Tips:</strong><br>
        &bull; Learn ES6+ features<br>
        &bull; Understand async/await<br>
        &bull; Practice with APIs<br>
        &bull; Build interactive UIs! ⚡"""
    
    # Web development
    elif any(keyword in query_lower for keyword in ['web', 'website', 'frontend', 'backend']):
        return """<strong>Web Development for Hackathons:</strong><br><br>
        <strong>Frontend Technologies:</strong><br>
        &bull; <strong>HTML5:</strong> Structure and semantics<br>
        &bull; <strong>CSS3:</strong> Styling and animations<br>
        &bull; <strong>JavaScript:</strong> Interactivity and logic<br>
        &bull; <strong>Frameworks:</strong> React, Vue.js, Angular<br><br>
        
        <strong>Backend Technologies:</strong><br>
        &bull; <strong>Node.js:</strong> JavaScript on the server<br>
        &bull; <strong>Python:</strong> Flask, Django, FastAPI<br>
        &bull; <strong>Databases:</strong> MongoDB, PostgreSQL, MySQL<br>
        &bull; <strong>APIs:</strong> RESTful or GraphQL<br><br>
        
        <strong>Quick Web Dev Tips:</strong><br>
        &bull; Start with responsive design<br>
        &bull; Learn about APIs early<br>
        &bull; Use version control<br>
        &bull; Test on different devices! 🌐"""
    
    # General programming advice
    elif any(keyword in query_lower for keyword in ['learn', 'coding', 'programming', 'start']):
        return """<strong>Learning to Code for Hackathons:</strong><br><br>
        <strong>Getting Started:</strong><br>
        &bull; <strong>Choose one language</strong> and stick with it initially<br>
        &bull; <strong>Practice daily</strong> - even 30 minutes helps<br>
        &bull; <strong>Build projects</strong> - start small and grow<br>
        &bull; <strong>Join communities</strong> - Stack Overflow, Reddit, Discord<br><br>
        
        <strong>Recommended Learning Path:</strong><br>
        &bull; <strong>Week 1-2:</strong> Basic syntax and concepts<br>
        &bull; <strong>Week 3-4:</strong> Build simple projects<br>
        &bull; <strong>Week 5-6:</strong> Learn frameworks/libraries<br>
        &bull; <strong>Week 7-8:</strong> Build a complete application<br><br>
        
        <strong>Resources:</strong><br>
        &bull; <strong>Free:</strong> freeCodeCamp, Codecademy, YouTube<br>
        &bull; <strong>Practice:</strong> LeetCode, HackerRank, Codewars<br>
        &bull; <strong>Projects:</strong> GitHub, personal portfolio<br><br>
        
        Remember: <strong>Consistency beats perfection!</strong> Keep coding! 💪"""
    
    # Default general response
    else:
        return """<strong>I'm here to help with both hackathon monitoring and general tech questions!</strong><br><br>
        
        <strong>I can help you with:</strong><br>
        &bull; <strong>Hackathon insights:</strong> problems, questions, trends, summaries<br>
        &bull; <strong>Programming skills:</strong> languages, frameworks, best practices<br>
        &bull; <strong>Tech advice:</strong> learning paths, project ideas, tools<br>
        &bull; <strong>General questions:</strong> about coding, development, technology<br><br>
        
        <strong>Try asking me about:</strong><br>
        &bull; "What skills do I need for hackathons?"<br>
        &bull; "How do I learn Python?"<br>
        &bull; "What's the best way to start web development?"<br>
        &bull; "Show me hackathon problems" (for current activity)<br><br>
        
        I'm your friendly AI assistant for both hackathon monitoring and tech guidance! 🤖✨"""

@app.route("/")
def landing():
    if session.get("user"):
        return render_template("landing.html")
    return render_template("login.html")

@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    # Force Google account chooser every time
    return oauth.google.authorize_redirect(redirect_uri, prompt="select_account")

@app.route("/callback")
def auth_callback():
    token = oauth.google.authorize_access_token()
    userinfo = None
    try:
        userinfo = oauth.google.parse_id_token(token)
    except Exception:
        userinfo = None
    if not userinfo:
        resp = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo")
        userinfo = resp.json() if resp else None

    if not userinfo:
        return redirect(url_for("landing"))

    session["user"] = {
        "name": userinfo.get("name"),
        "email": userinfo.get("email"),
        "picture": userinfo.get("picture"),
    }
    return redirect(url_for("landing"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

@app.route("/chatbot")
def chatbot():
    user = session.get("user")
    if not user:
        return redirect(url_for("landing"))
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("landing"))
    return render_template("dashboard.html")

@app.route("/slack/events", methods=["POST"])
@app.route("/slack/events/", methods=["POST"])
def slack_events():
    """Handle Slack events and store messages in memory."""
    # Ensure JSON payload
    if not request.is_json:
        return {"error": "Unsupported Media Type"}, 415

    data = request.get_json()
    print("Incoming payload:", data)

    # Slack URL verification
    if data.get("type") == "url_verification":
        # Must return the raw challenge string
        return data["challenge"], 200, {"Content-Type": "text/plain"}

    # Handle new message events
    if "event" in data and data["event"].get("type") == "message":
        msg = {
            "user": data["event"].get("user"),
            "text": data["event"].get("text"),
            "ts": data["event"].get("ts"),
            "channel": data["event"].get("channel", "general")
        }
        
        # Filter out bot messages and empty text
        if msg.get("text") and msg.get("user"):
            messages.append(msg)
            print("New message received:", msg)
            
            # Keep only last 1000 messages to prevent memory issues
            if len(messages) > 1000:
                messages.pop(0)

    return {"ok": True}

@app.route("/api/query", methods=["POST"])
def get_response():
    """Handle AI queries from the frontend."""
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message.strip():
            return jsonify({"reply": "Please provide a question or query."})
        
        # Get recent messages for context
        recent_messages = messages[-50:] if messages else []
        
        # Generate intelligent response based on query type
        query_lower = user_message.lower()
        
        # Check if it's a general question first
        if any(keyword in query_lower for keyword in ['skills', 'learn', 'programming', 'coding', 'technology', 'tech', 'development', 'web', 'app', 'software', 'python', 'javascript', 'react', 'node', 'database', 'api', 'git', 'github']):
            response = handle_general_question(user_message, query_lower)
        elif "problem" in query_lower or "issue" in query_lower:
            # Analyze problems
            problems = [msg for msg in recent_messages if any(keyword in msg.get('text', '').lower() 
                       for keyword in ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken'])]
            
            if problems:
                response = f"<strong>Current Problems Detected:</strong><br><br>"
                for i, problem in enumerate(problems[:3], 1):
                    text = problem.get('text', '')[:100] + "..." if len(problem.get('text', '')) > 100 else problem.get('text', '')
                    text = clean_message_text(text)
                    text = highlight_keywords(text)
                    # Capitalize first letter
                    if text and text[0].islower():
                        text = text[0].upper() + text[1:]
                    response += f"{i}. {text}<br>"
                response += f"<br><em>Total problems found: {len(problems)}</em>"
            else:
                response = "Great news! No problems detected in recent messages. Teams seem to be working smoothly! 🎉"
                
        elif "question" in query_lower or "ask" in query_lower:
            # Analyze questions
            questions = [msg for msg in recent_messages if msg.get('text', '').strip().endswith('?')]
            
            if questions:
                response = f"<strong>Recent Questions Asked:</strong><br><br>"
                for i, question in enumerate(questions[:5], 1):
                    text = question.get('text', '')[:80] + "..." if len(question.get('text', '')) > 80 else question.get('text', '')
                    text = clean_message_text(text)
                    text = highlight_keywords(text)
                    # Capitalize first letter
                    if text and text[0].islower():
                        text = text[0].upper() + text[1:]
                    response += f"{i}. {text}<br>"
                response += f"<br><em>Total questions: {len(questions)}</em>"
            else:
                response = "No questions found in recent messages. Teams might be working independently or have found their answers! 🤔"
                
        elif "trend" in query_lower or "topic" in query_lower:
            # Analyze trending topics
            if recent_messages:
                insights = ai_service.analyze_messages(recent_messages)
                response = f"**Trending Analysis:**\n\n{insights['trending']}"
            else:
                response = "No recent activity to analyze trends. Waiting for more messages... 📊"
                
        elif "summary" in query_lower or "overview" in query_lower:
            # Provide overall summary
            if recent_messages:
                insights = ai_service.analyze_messages(recent_messages)
                response = f"<strong>Hackathon Activity Summary:</strong><br><br>"
                response += f"📊 <strong>Total Messages:</strong> {len(recent_messages)}<br>"
                response += f"👥 <strong>Active Users:</strong> {len(set(msg.get('user', '') for msg in recent_messages))}<br><br>"
                response += f"<strong>Key Insights:</strong><br>{insights['problems']}<br><br>{insights['trending']}"
            else:
                response = "No recent activity to summarize. The dashboard is ready to monitor hackathon progress! 🚀"
        else:
            # General response
            if recent_messages:
                response = f"<strong>Current Status:</strong><br><br>"
                response += f"📈 <strong>Activity Level:</strong> {len(recent_messages)} messages in recent history<br>"
                response += f"👥 <strong>Active Participants:</strong> {len(set(msg.get('user', '') for msg in recent_messages))} users<br>"
                latest_text = clean_message_text(recent_messages[-1]['text'][:100])
                response += f"💬 <strong>Latest Activity:</strong> '{latest_text}...'<br><br>"
                response += "Ask me about 'problems', 'questions', 'trends', or 'summary' for detailed insights!"
            else:
                response = "Welcome to the Hackathon Assistant! 🤖<br><br>I'm ready to help analyze team communications and provide insights. Send some messages in your Slack channel and I'll start tracking the activity!<br><br>Try asking about:<br>&bull; Current problems<br>&bull; Recent questions<br>&bull; Trending topics<br>&bull; Activity summary"
        
        return jsonify({"reply": response})
        
    except Exception as e:
        return jsonify({"reply": f"Error processing your request: {str(e)}"}), 500

@app.route("/api/insights", methods=["GET"])
def get_insights():
    """Get rich AI insights from recent messages."""
    try:
        recent_messages = messages[-100:] if messages else []
        
        # Use AI service for rich analysis
        insights = ai_service.analyze_messages(recent_messages)
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get basic statistics about messages."""
    try:
        recent_messages = messages[-100:] if messages else []
        
        unique_users = len(set(msg.get('user', '') for msg in recent_messages))
        questions_count = sum(1 for msg in recent_messages if msg.get('text', '').strip().endswith('?'))
        problem_keywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'not working']
        problems_count = sum(1 for msg in recent_messages 
                           if any(keyword in msg.get('text', '').lower() for keyword in problem_keywords))
        
        return jsonify({
            'total_messages': len(recent_messages),
            'unique_users': unique_users,
            'avg_message_length': round(sum(len(msg.get('text', '')) for msg in recent_messages) / len(recent_messages) if recent_messages else 0, 1),
            'questions_count': questions_count,
            'problems_count': problems_count,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages", methods=["GET"])
def get_messages():
    """Get recent messages."""
    try:
        limit = request.args.get("limit", 50, type=int)
        recent_messages = messages[-limit:] if messages else []
        
        # Sort by timestamp (most recent first)
        recent_messages.sort(key=lambda x: float(x.get('ts', '0')), reverse=True)
        
        return jsonify({"messages": recent_messages})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Make current session user available to all templates (for navbar, etc.)
@app.context_processor
def inject_user():
    return {"session_user": session.get("user")}

if __name__ == "__main__":
    print("Starting Hackathon Slack Dashboard...")
    print("Dashboard will be available at: http://localhost:5000/dashboard")
    print("Slack webhook endpoint: http://localhost:5000/slack/events")
    print("AI-powered real-time hackathon monitoring system")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)