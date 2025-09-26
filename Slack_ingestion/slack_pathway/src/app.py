from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv
from stream import push_message
from utils import is_valid_message
from rag_query_service import rag_query_service
from pathway_rag_service import initialize_pathway_rag_service
from pathway_pipeline import PATHWAY_TABLES
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Initialize Pathway RAG service
try:
    pathway_service = initialize_pathway_rag_service(PATHWAY_TABLES)
    rag_query_service.pathway_service = pathway_service
    logger.info("Pathway RAG service initialized successfully")
except Exception as e:
    logger.warning(f"Could not initialize Pathway service: {e}. Using fallback mode.")

# Root route -> serve frontend
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/chatbot")
def chatbot():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/slack/events", methods=["POST"])
@app.route("/slack/events/", methods=["POST"])
def slack_events():
    # Ensure JSON payload
    if not request.is_json:
        return {"error": "Unsupported Media Type"}, 415

    data = request.get_json()
    logger.info(f"Incoming payload: {data}")

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

        # Filter invalid messages
        if is_valid_message(msg):
            push_message(msg)
            logger.info(f"Message pushed: {msg}")
        else:
            logger.info(f"Filtered invalid message: {msg}")

    return {"ok": True}

@app.route("/api/query", methods=["POST"])
def get_response():
    """Handle RAG queries from the frontend."""
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message.strip():
            return jsonify({"reply": "Please provide a question or query."})
        
        # Get RAG response
        ai_reply = rag_query_service.query_rag(user_message)
        
        return jsonify({"reply": ai_reply})
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {e}")
        return jsonify({"reply": f"Error processing your request: {str(e)}"}), 500

@app.route("/api/insights", methods=["GET"])
def get_insights():
    """Get predefined insights for demo purposes."""
    try:
        insights = rag_query_service.get_predefined_insights()
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get message statistics."""
    try:
        stats = rag_query_service.get_message_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages", methods=["GET"])
def get_messages():
    """Get recent messages."""
    try:
        hours = request.args.get("hours", 2, type=int)
        limit = request.args.get("limit", 50, type=int)
        messages = rag_query_service.get_recent_messages(hours=hours, limit=limit)
        return jsonify({"messages": messages})
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Listen on all interfaces so ngrok can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
