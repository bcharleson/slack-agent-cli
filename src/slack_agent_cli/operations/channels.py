"""Channel operations shared by CLI and MCP."""

from typing import Any

from ..utils.slack_client import execute_slack_call, get_slack_client


def list_channels(
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
    limit: int = 100,
) -> dict[str, Any]:
    """List all accessible Slack channels in the workspace."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_list,
        types=types,
        exclude_archived=exclude_archived,
        limit=min(limit, 1000),
    )

    if not response.success:
        return {"error": response.error}

    channels = response.data.get("channels", [])
    return {
        "channels": [
            {
                "id": ch.get("id"),
                "name": ch.get("name"),
                "is_private": ch.get("is_private", False),
                "is_archived": ch.get("is_archived", False),
                "num_members": ch.get("num_members", 0),
                "topic": ch.get("topic", {}).get("value", ""),
                "purpose": ch.get("purpose", {}).get("value", ""),
            }
            for ch in channels
        ],
        "total": len(channels),
    }


def get_channel_info(channel_id: str) -> dict[str, Any]:
    """Get detailed information about a specific Slack channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_info,
        channel=channel_id,
        include_num_members=True,
    )

    if not response.success:
        return {"error": response.error}

    ch = response.data.get("channel", {})
    return {
        "id": ch.get("id"),
        "name": ch.get("name"),
        "is_private": ch.get("is_private", False),
        "is_archived": ch.get("is_archived", False),
        "is_member": ch.get("is_member", False),
        "num_members": ch.get("num_members", 0),
        "topic": ch.get("topic", {}).get("value", ""),
        "purpose": ch.get("purpose", {}).get("value", ""),
        "created": ch.get("created"),
        "creator": ch.get("creator"),
    }


def create_channel(name: str, is_private: bool = False) -> dict[str, Any]:
    """Create a new Slack channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_create,
        name=name,
        is_private=is_private,
    )

    if not response.success:
        return {"error": response.error}

    ch = response.data.get("channel", {})
    return {
        "success": True,
        "channel": {
            "id": ch.get("id"),
            "name": ch.get("name"),
            "is_private": ch.get("is_private", False),
        },
    }


def archive_channel(channel_id: str) -> dict[str, Any]:
    """Archive a Slack channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_archive,
        channel=channel_id,
    )

    if not response.success:
        return {"error": response.error}

    return {"success": True, "message": f"Channel {channel_id} archived successfully"}


def get_channel_history(
    channel_id: str,
    limit: int = 20,
    oldest: str | None = None,
    latest: str | None = None,
) -> dict[str, Any]:
    """Fetch message history from a Slack channel."""
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


def join_channel(channel_id: str) -> dict[str, Any]:
    """Join a Slack channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_join,
        channel=channel_id,
    )

    if not response.success:
        return {"error": response.error}

    ch = response.data.get("channel", {})
    return {
        "success": True,
        "channel": {
            "id": ch.get("id"),
            "name": ch.get("name"),
        },
    }


def leave_channel(channel_id: str) -> dict[str, Any]:
    """Leave a Slack channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_leave,
        channel=channel_id,
    )

    if not response.success:
        return {"error": response.error}

    return {"success": True, "message": f"Left channel {channel_id} successfully"}


def set_channel_topic(channel_id: str, topic: str) -> dict[str, Any]:
    """Set the topic for a Slack channel."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.conversations_setTopic,
        channel=channel_id,
        topic=topic,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "success": True,
        "topic": response.data.get("topic", topic),
    }
