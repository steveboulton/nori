import json
from pathlib import Path
from datetime import datetime
from config import DATA_DIR, MAX_CONVERSATION_HISTORY


def get_user_dir(user_id: str) -> Path:
    """Get or create user data directory."""
    user_dir = DATA_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def load_conversations(user_id: str) -> list[dict]:
    """Load conversation history for a user."""
    conv_file = get_user_dir(user_id) / "conversations.json"
    if conv_file.exists():
        return json.loads(conv_file.read_text())
    return []


def save_conversation_turn(user_id: str, role: str, content: str):
    """Save a single conversation turn."""
    conversations = load_conversations(user_id)
    conversations.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    conv_file = get_user_dir(user_id) / "conversations.json"
    conv_file.write_text(json.dumps(conversations, indent=2))


def get_recent_history(user_id: str, limit: int = None) -> list[dict]:
    """Get recent conversation history formatted for Claude API."""
    limit = limit or MAX_CONVERSATION_HISTORY
    conversations = load_conversations(user_id)
    recent = conversations[-limit:]

    # Format for Claude API (just role and content)
    return [{"role": c["role"], "content": c["content"]} for c in recent]


def clear_history(user_id: str):
    """Clear conversation history for a user."""
    conv_file = get_user_dir(user_id) / "conversations.json"
    if conv_file.exists():
        conv_file.write_text("[]")
