#!/usr/bin/env python3
"""
Main application entry point for the Pathway-based Slack ingestion system.
This file integrates the Pathway database with the Flask web application.
"""

import pathway as pw
import threading
import time
import logging
from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv
from stream import push_message
from utils import is_valid_message
from rag_query_service import rag_query_service
from pathway_rag_service import initialize_pathway_rag_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Global variables for Pathway system
pathway_tables = {}
pathway_service = None
pathway_thread = None

def run_pathway_pipeline():
    """Run the Pathway pipeline in a separate thread."""
    global pathway_tables, pathway_service
    
    try:
        # Import and run the pathway pipeline
        from pathway_pipeline import PATHWAY_TABLES, processed_messages, users_table, channels_table, analytics_table, hourly_stats, rag_index
        
        # Store tables globally
        pathway_tables = PATHWAY_TABLES
        
        # Initialize Pathway RAG service
        pathway_service = initialize_pathway_rag_service(pathway_tables)
        rag_query_service.pathway_service = pathway_service
        
        logger.info("Pathway pipeline started successfully")
        
        # Run the Pathway pipeline
        pw.run()
        
    except Exception as e:
        logger.error(f"Error running Pathway pipeline: {e}")

def start_pathway_system():
    """Start the Pathway system in a background thread."""
    global pathway_thread
    
    if pathway_thread is None or not pathway_thread.is_alive():
        pathway_thread = threading.Thread(target=run_pathway_pipeline, daemon=True)
        pathway_thread.start()
        logger.info("Pathway system started in background thread")
        
        # Give it a moment to initialize
        time.sleep(2)
    else:
        logger.info("Pathway system already running")

# Initialize Flask app
app = Flask(__name__)

# Start Pathway system
start_pathway_system()

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
    """Handle Slack events and push to Pathway stream."""
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
            "channel": data["event"].get("channel", "general"),
            "message_id": f"{data['event'].get('ts', '')}_{data['event'].get('user', '')}",
            "thread_ts": data["event"].get("thread_ts", ""),
            "type": data["event"].get("type", "message")
        }

        # Filter invalid messages
        if is_valid_message(msg):
            push_message(msg)
            logger.info(f"Message pushed to Pathway stream: {msg}")
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
        
        # Get RAG response using Pathway service
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

@app.route("/api/pathway/status", methods=["GET"])
def pathway_status():
    """Get Pathway system status."""
    try:
        status = {
            "pathway_running": pathway_thread is not None and pathway_thread.is_alive(),
            "tables_available": len(pathway_tables) > 0,
            "service_initialized": pathway_service is not None,
            "tables": list(pathway_tables.keys()) if pathway_tables else []
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting Pathway status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pathway/search", methods=["POST"])
def pathway_search():
    """Search messages using Pathway database."""
    try:
        if not pathway_service:
            return jsonify({"error": "Pathway service not available"}), 503
            
        data = request.get_json()
        query_text = data.get("query", "")
        limit = data.get("limit", 10)
        channel = data.get("channel")
        
        if not query_text.strip():
            return jsonify({"error": "Query text required"}), 400
        
        messages = pathway_service.search_messages(query_text, limit=limit, channel=channel)
        return jsonify({"messages": messages})
        
    except Exception as e:
        logger.error(f"Error in Pathway search: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pathway/problems", methods=["GET"])
def pathway_problems():
    """Get problem messages using Pathway database."""
    try:
        if not pathway_service:
            return jsonify({"error": "Pathway service not available"}), 503
            
        hours = request.args.get("hours", 24, type=int)
        limit = request.args.get("limit", 20, type=int)
        
        messages = pathway_service.get_problem_messages(hours=hours, limit=limit)
        return jsonify({"messages": messages})
        
    except Exception as e:
        logger.error(f"Error getting problem messages: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pathway/questions", methods=["GET"])
def pathway_questions():
    """Get question messages using Pathway database."""
    try:
        if not pathway_service:
            return jsonify({"error": "Pathway service not available"}), 503
            
        hours = request.args.get("hours", 24, type=int)
        limit = request.args.get("limit", 20, type=int)
        
        messages = pathway_service.get_question_messages(hours=hours, limit=limit)
        return jsonify({"messages": messages})
        
    except Exception as e:
        logger.error(f"Error getting question messages: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pathway/urgent", methods=["GET"])
def pathway_urgent():
    """Get urgent messages using Pathway database."""
    try:
        if not pathway_service:
            return jsonify({"error": "Pathway service not available"}), 503
            
        hours = request.args.get("hours", 24, type=int)
        limit = request.args.get("limit", 10, type=int)
        
        messages = pathway_service.get_urgent_messages(hours=hours, limit=limit)
        return jsonify({"messages": messages})
        
    except Exception as e:
        logger.error(f"Error getting urgent messages: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Pathway-based Slack ingestion system...")
    logger.info("Pathway system: Built-in database engine")
    logger.info("No external databases required (PostgreSQL, Redis, MongoDB)")
    
    # Listen on all interfaces so ngrok can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
