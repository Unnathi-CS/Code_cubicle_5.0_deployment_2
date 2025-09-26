import json
from pathlib import Path

STREAM_FILE = Path("messages.json")

def push_message(msg):
    """Push a new message to the stream (file-based for now)."""
    STREAM_FILE.touch(exist_ok=True)
    with STREAM_FILE.open("a") as f:
        f.write(json.dumps(msg) + "\n")
    print("Message pushed to stream:", msg)

def read_stream():
    """Yield messages from the stream for Pathway consumption."""
    STREAM_FILE.touch(exist_ok=True)
    with STREAM_FILE.open() as f:
        for line in f:
            yield json.loads(line)
