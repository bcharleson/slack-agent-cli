"""Messaging and DM operations shared by CLI and MCP."""

from typing import Any

from ..utils.slack_client import execute_slack_call, get_slack_client


def post_message(
    channel_id: str,
    text: str,
    thread_ts: str | None = None,
    unfurl_links: bool = True,
    unfurl_media: bool = True,
) -> dict[str, Any]:
    """Post a message to a Slack channel."""
    client = get_slack_client()

    kwargs: dict[str, Any] = {
        "channel": channel_id,
        "text": text,
        "unfurl_links": unfurl_links,
        "unfurl_media": unfurl_media,
    }
    if thread_ts:
        kwargs["thread_ts"] = thread_ts

    response = execute_slack_call(
        client.bot_client.chat_postMessage,
        **kwargs,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "success": True,
        "channel": response.data.get("channel"),
        "ts": response.data.get("ts"),
        "message": response.data.get("message", {}).get("text", text),
    }


def reply_to_thread(
    channel_id: str,
    thread_ts: str,
    text: str,
    broadcast: bool = False,
) -> dict[str, Any]:
    """Reply to a message thread in Slack."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.chat_postMessage,
        channel=channel_id,
        thread_ts=thread_ts,
        text=text,
        reply_broadcast=broadcast,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "success": True,
        "channel": response.data.get("channel"),
        "ts": response.data.get("ts"),
        "thread_ts": thread_ts,
        "message": response.data.get("message", {}).get("text", text),
    }


def get_thread_replies(
    channel_id: str,
    thread_ts: str,
    limit: int = 20,
) -> dict[str, Any]:
    """Get all replies in a message thread."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_replies,
        channel=channel_id,
        ts=thread_ts,
        limit=min(limit, 1000),
    )

    if not response.success:
        return {"error": response.error}

    messages = response.data.get("messages", [])
    return {
        "messages": [
            {
                "ts": msg.get("ts"),
                "user": msg.get("user"),
                "text": msg.get("text", ""),
                "is_parent": msg.get("ts") == thread_ts,
                "reactions": [
                    {"name": r.get("name"), "count": r.get("count")}
                    for r in msg.get("reactions", [])
                ],
            }
            for msg in messages
        ],
        "has_more": response.data.get("has_more", False),
        "total": len(messages),
    }


def add_reaction(channel_id: str, timestamp: str, emoji: str) -> dict[str, Any]:
    """Add an emoji reaction to a message."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.reactions_add,
        channel=channel_id,
        timestamp=timestamp,
        name=emoji,
    )

    if not response.success:
        return {"error": response.error}

    return {"success": True, "message": f"Added :{emoji}: reaction to message"}


def remove_reaction(channel_id: str, timestamp: str, emoji: str) -> dict[str, Any]:
    """Remove an emoji reaction from a message."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.reactions_remove,
        channel=channel_id,
        timestamp=timestamp,
        name=emoji,
    )

    if not response.success:
        return {"error": response.error}

    return {"success": True, "message": f"Removed :{emoji}: reaction from message"}


def get_message_reactions(channel_id: str, timestamp: str) -> dict[str, Any]:
    """Get all reactions on a specific message."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.reactions_get,
        channel=channel_id,
        timestamp=timestamp,
    )

    if not response.success:
        return {"error": response.error}

    message = response.data.get("message", {})
    return {
        "ts": message.get("ts"),
        "text": message.get("text", ""),
        "reactions": [
            {
                "name": r.get("name"),
                "count": r.get("count"),
                "users": r.get("users", []),
            }
            for r in message.get("reactions", [])
        ],
    }


def update_message(channel_id: str, timestamp: str, text: str) -> dict[str, Any]:
    """Update an existing message."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.chat_update,
        channel=channel_id,
        ts=timestamp,
        text=text,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "success": True,
        "channel": response.data.get("channel"),
        "ts": response.data.get("ts"),
        "text": response.data.get("text", text),
    }


def delete_message(channel_id: str, timestamp: str) -> dict[str, Any]:
    """Delete a message from a channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.chat_delete,
        channel=channel_id,
        ts=timestamp,
    )

    if not response.success:
        return {"error": response.error}

    return {"success": True, "message": "Message deleted successfully"}


def send_dm(user_id: str, text: str) -> dict[str, Any]:
    """Send a direct message to a user."""
    client = get_slack_client()

    open_response = execute_slack_call(
        client.bot_client.conversations_open,
        users=[user_id],
    )

    if not open_response.success:
        return {"error": open_response.error}

    channel_id = open_response.data.get("channel", {}).get("id")
    if not channel_id:
        return {"error": "Failed to open DM channel"}

    response = execute_slack_call(
        client.bot_client.chat_postMessage,
        channel=channel_id,
        text=text,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "success": True,
        "channel": channel_id,
        "ts": response.data.get("ts"),
        "user": user_id,
        "message": text,
    }


def list_conversations(types: str = "im,mpim", limit: int = 50) -> dict[str, Any]:
    """List direct message and group DM conversations."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_list,
        types=types,
        limit=min(limit, 1000),
    )

    if not response.success:
        return {"error": response.error}

    channels = response.data.get("channels", [])
    return {
        "conversations": [
            {
                "id": ch.get("id"),
                "is_im": ch.get("is_im", False),
                "is_mpim": ch.get("is_mpim", False),
                "user": ch.get("user"),
                "name": ch.get("name", ""),
                "is_open": ch.get("is_open", False),
            }
            for ch in channels
        ],
        "total": len(channels),
    }


def get_dm_history(
    channel_id: str,
    limit: int = 20,
    oldest: str | None = None,
    latest: str | None = None,
) -> dict[str, Any]:
    """Fetch message history from a DM or group DM conversation."""
    client = get_slack_client()

    kwargs: dict[str, Any] = {
        "channel": channel_id,
        "limit": min(limit, 1000),
    }
    if oldest:
        kwargs["oldest"] = oldest
    if latest:
        kwargs["latest"] = latest

    response = execute_slack_call(
        client.bot_client.conversations_history,
        **kwargs,
    )

    if not response.success:
        return {"error": response.error}

    messages = response.data.get("messages", [])
    return {
        "messages": [
            {
                "ts": msg.get("ts"),
                "user": msg.get("user"),
                "text": msg.get("text", ""),
                "thread_ts": msg.get("thread_ts"),
                "reply_count": msg.get("reply_count", 0),
            }
            for msg in messages
        ],
        "has_more": response.data.get("has_more", False),
        "total": len(messages),
    }


def open_dm(user_ids: str) -> dict[str, Any]:
    """Open a direct message or group DM conversation."""
    client = get_slack_client()

    users = [user_id.strip() for user_id in user_ids.split(",") if user_id.strip()]
    response = execute_slack_call(
        client.bot_client.conversations_open,
        users=users,
    )

    if not response.success:
        return {"error": response.error}

    channel = response.data.get("channel", {})
    return {
        "success": True,
        "channel": {
            "id": channel.get("id"),
            "is_im": channel.get("is_im", False),
            "is_mpim": channel.get("is_mpim", False),
        },
    }
