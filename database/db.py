import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "tickets.json")


def _load():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def create_ticket(channel_id: int, user_id: int, guild_id: int, category: str = "general"):
    data = _load()
    data[str(channel_id)] = {
        "user_id": user_id,
        "guild_id": guild_id,
        "category": category,
        "status": "open",
        "opened_at": datetime.now(timezone.utc).isoformat(),
        "closed_at": None
    }
    _save(data)


def close_ticket(channel_id: int):
    data = _load()
    key = str(channel_id)
    if key in data:
        data[key]["status"] = "closed"
        data[key]["closed_at"] = datetime.now(timezone.utc).isoformat()
        _save(data)


def get_ticket(channel_id: int):
    data = _load()
    return data.get(str(channel_id))


def get_open_ticket_for_user(user_id: int, guild_id: int):
    data = _load()
    for channel_id, ticket in data.items():
        if ticket["user_id"] == user_id and ticket["guild_id"] == guild_id and ticket["status"] == "open":
            return channel_id, ticket
    return None, None


def get_all_tickets():
    return _load()
