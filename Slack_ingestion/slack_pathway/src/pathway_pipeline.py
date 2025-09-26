import pathway as pw
from stream import read_stream
from ai_service import rag_service
import json
import logging
from typing import Dict, Any
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define comprehensive schemas for Pathway database
class MessageSchema(pw.Schema):
    user: str
    text: str
    ts: str
    channel: str = ""
    message_id: str = ""
    thread_ts: str = ""
    message_type: str = "message"

class UserSchema(pw.Schema):
    user_id: str
    username: str
    display_name: str = ""
    first_seen: str = ""
    message_count: int = 0

class ChannelSchema(pw.Schema):
    channel_id: str
    channel_name: str
    channel_type: str = "public"
    message_count: int = 0

class AnalyticsSchema(pw.Schema):
    metric_name: str
    metric_value: float
    timestamp: str
    channel: str = ""

# Custom Subject to push messages from read_stream()
class MessageSubject(pw.io.python.ConnectorSubject):
    def run(self):
        for msg in read_stream():
            # Generate unique message ID if not present
            message_id = msg.get("message_id", f"{msg.get('ts', '')}_{msg.get('user', '')}")
            
            self.next(
                user=msg.get("user", ""), 
                text=msg.get("text", ""), 
                ts=msg.get("ts", ""),
                channel=msg.get("channel", "general"),
                message_id=message_id,
                thread_ts=msg.get("thread_ts", ""),
                message_type=msg.get("type", "message")
            )

# Read messages into Pathway table
messages_table = pw.io.python.read(MessageSubject(), schema=MessageSchema)

# Filter and process messages
valid_messages = messages_table.filter(
    (messages_table.text != "") & 
    (messages_table.user != "") & 
    (messages_table.text.str.len() > 3)
)

# Enhanced message processing with more analytics
processed_messages = valid_messages.select(
    user=valid_messages.user,
    text=valid_messages.text,
    ts=valid_messages.ts,
    channel=valid_messages.channel,
    message_id=valid_messages.message_id,
    thread_ts=valid_messages.thread_ts,
    message_type=valid_messages.message_type,
    # Computed fields for analytics
    message_length=pw.cast(int, valid_messages.text.str.len()),
    is_question=valid_messages.text.str.contains("?"),
    has_problem_keywords=valid_messages.text.str.contains("problem|issue|error|bug|stuck|help", regex=True),
    has_urgency=valid_messages.text.str.contains("urgent|asap|emergency|critical", regex=True),
    word_count=pw.cast(int, valid_messages.text.str.split().str.len()),
    timestamp_parsed=pw.cast(float, valid_messages.ts),
    # Create timestamp for indexing
    created_at=pw.cast(str, pw.apply(lambda ts: datetime.fromtimestamp(float(ts)).isoformat() if ts else "", valid_messages.ts))
)

# Create users table from messages
users_table = processed_messages.groupby(processed_messages.user).reduce(
    user_id=processed_messages.user,
    username=processed_messages.user,
    display_name=processed_messages.user,
    first_seen=pw.reducers.min(processed_messages.created_at),
    message_count=pw.reducers.count()
)

# Create channels table from messages
channels_table = processed_messages.groupby(processed_messages.channel).reduce(
    channel_id=processed_messages.channel,
    channel_name=processed_messages.channel,
    channel_type=pw.cast(str, "public"),
    message_count=pw.reducers.count()
)

# Create real-time analytics
analytics_table = processed_messages.select(
    metric_name=pw.cast(str, "message_count"),
    metric_value=pw.cast(float, 1.0),
    timestamp=processed_messages.created_at,
    channel=processed_messages.channel
)

# Create aggregated analytics
hourly_stats = processed_messages.groupby(
    processed_messages.channel,
    pw.apply(lambda ts: datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:00") if ts else "", processed_messages.ts)
).reduce(
    channel=processed_messages.channel,
    hour=pw.apply(lambda ts: datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:00") if ts else "", processed_messages.ts),
    message_count=pw.reducers.count(),
    avg_message_length=pw.reducers.avg(processed_messages.message_length),
    questions_count=pw.reducers.sum(pw.cast(int, processed_messages.is_question)),
    problems_count=pw.reducers.sum(pw.cast(int, processed_messages.has_problem_keywords))
)

# Create RAG-ready message index
rag_index = processed_messages.select(
    message_id=processed_messages.message_id,
    user=processed_messages.user,
    text=processed_messages.text,
    channel=processed_messages.channel,
    timestamp=processed_messages.created_at,
    message_length=processed_messages.message_length,
    is_question=processed_messages.is_question,
    has_problem_keywords=processed_messages.has_problem_keywords,
    has_urgency=processed_messages.has_urgency,
    # Create searchable text field
    searchable_text=pw.apply(lambda text: text.lower().strip(), processed_messages.text)
)

# Global tables for access from other modules
PATHWAY_TABLES = {
    'messages': processed_messages,
    'users': users_table,
    'channels': channels_table,
    'analytics': analytics_table,
    'hourly_stats': hourly_stats,
    'rag_index': rag_index
}

# Print processed messages for debugging
pw.debug.compute_and_print(processed_messages)

# Run the pipeline
if __name__ == "__main__":
    pw.run()
