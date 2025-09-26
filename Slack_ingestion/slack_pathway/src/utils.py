def is_valid_message(msg):
    """Filter out bot messages or empty text."""
    if not msg.get("text"):
        return False
    if msg.get("user") is None:  # Ignore messages without user
        return False
    return True
