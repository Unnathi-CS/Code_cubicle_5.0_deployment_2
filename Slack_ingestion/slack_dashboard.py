from flask import Flask, request, render_template, jsonify, redirect, session, url_for
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from Slack_ingestion.ai_service import ai_service
from Slack_ingestion.utils import markdown_to_html, clean_message_text, highlight_keywords, format_user_mention
from flask import Blueprint, jsonify, render_template  # ✅ added Blueprint here
from slack_sdk import WebClient

# 🔹 Setup
slack_bp = Blueprint("slack_dashboard", __name__)
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# Regex helpers
QUESTION_REGEX = re.compile(r"\?$", re.IGNORECASE)
PROBLEM_REGEX = re.compile(r"\b(problem|error|issue|bug|stuck|help|broken)\b", re.IGNORECASE)

POSITIVE_EMOJIS = {"😂", "😄", "😃", "😀", "😊", "🙂", "😍", "🥳", "😎", "😁", "😅", "😆", "🎉"}
NEGATIVE_EMOJIS = {"😢", "😭", "😞", "😔", "😡", "😠", "😤", "😰", "😱", "😩", "😫", "😒", "😓", "😕"}


# 🔹 Utility: fetch latest messages from Slack channel
def fetch_messages(channel_id, limit=200):
    try:
        response = slack_client.conversations_history(channel=channel_id, limit=limit)
        return response.get("messages", [])
    except Exception as e:
        print(f"Error fetching Slack messages: {e}")
        return []


# 🔹 Utility: group messages by time interval
def group_by_interval(messages, minutes=5):
    buckets = defaultdict(list)
    for msg in messages:
        ts = float(msg.get("ts", datetime.now().timestamp())) * 1000
        dt = datetime.fromtimestamp(ts / 1000)
        bucket = dt.replace(second=0, microsecond=0, minute=(dt.minute // minutes) * minutes)
        key = bucket.strftime("%Y-%m-%d %H:%M")
        buckets[key].append(msg)
    return buckets


# 🔹 Utility: analyze mood based on emojis
def analyze_mood(messages):
    emoji_counts = Counter()
    positives, negatives = 0, 0
    for msg in messages:
        text = msg.get("text", "")
        for char in text:
            if char in POSITIVE_EMOJIS:
                emoji_counts[char] += 1
                positives += 1
            elif char in NEGATIVE_EMOJIS:
                emoji_counts[char] += 1
                negatives += 1

    # Pick overall mood
    if positives == negatives == 0:
        mood = "😐 Neutral"
    elif positives > negatives:
        mood = "😃 Happy"
    elif negatives > positives:
        mood = "😡 Stressed"
    else:
        mood = "🙂 Balanced"

    return {
        "emoji_counts": dict(emoji_counts),
        "positives": positives,
        "negatives": negatives,
        "mood": mood,
    }


# 🔹 Route: dashboard UI
@slack_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# 🔹 Route: AI insights
@slack_bp.route("/api/insights")
def insights():
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    messages = fetch_messages(channel_id, limit=200)

    problems = [m["text"] for m in messages if PROBLEM_REGEX.search(m.get("text", ""))]
    questions = [m["text"] for m in messages if QUESTION_REGEX.search(m.get("text", ""))]

    # Trending words (basic frequency)
    words = [w.lower() for m in messages for w in m.get("text", "").split() if len(w) > 3]
    trending = [w for w, _ in Counter(words).most_common(5)]

    return jsonify({
        "problems": problems[:10],
        "questions": questions[:10],
        "trending": trending,
    })


# 🔹 Route: timeline data
@slack_bp.route("/api/timeline")
def timeline():
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    messages = fetch_messages(channel_id, limit=500)
    buckets = group_by_interval(messages, minutes=5)

    result = {}
    for bucket, msgs in buckets.items():
        result[bucket] = {
            "total": len(msgs),
            "problems": sum(1 for m in msgs if PROBLEM_REGEX.search(m.get("text", ""))),
            "questions": sum(1 for m in msgs if QUESTION_REGEX.search(m.get("text", ""))),
        }
    return jsonify(result)


# 🔹 Route: mood meter
@slack_bp.route("/api/mood")
def mood():
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    messages = fetch_messages(channel_id, limit=300)
    analysis = analyze_mood(messages)
    return jsonify(analysis)



