"""Channel management tools for Slack MCP Server."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..utils.slack_client import execute_slack_call, get_slack_client


def register_channel_tools(mcp: FastMCP) -> None:
    """Register all channel-related tools with the MCP server."""

    @mcp.tool()
    def list_channels(
        types: str = "public_channel,private_channel",
        exclude_archived: bool = True,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        List all accessible Slack channels in the workspace.

        Args:
            types: Comma-separated channel types to include.
                   Options: public_channel, private_channel, mpim, im
                   Default: "public_channel,private_channel"
            exclude_archived: Whether to exclude archived channels. Default: True
            limit: Maximum number of channels to return (1-1000). Default: 100

        Returns:
            Dictionary containing list of channels with their details
        """
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

    @mcp.tool()
    def get_channel_info(channel_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific Slack channel.

        Args:
            channel_id: The ID of the channel (e.g., "C01234567")

        Returns:
            Dictionary containing channel details including name, topic,
            purpose, member count, and creation date
        """
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

    @mcp.tool()
    def create_channel(name: str, is_private: bool = False) -> dict[str, Any]:
        """
        Create a new Slack channel.

        Args:
            name: Name for the new channel (max 80 chars, lowercase,
                  no spaces, use hyphens instead)
            is_private: Whether to create a private channel. Default: False

        Returns:
            Dictionary containing the created channel's details
        """
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

    @mcp.tool()
    def archive_channel(channel_id: str) -> dict[str, Any]:
        """
        Archive a Slack channel.

        Args:
            channel_id: The ID of the channel to archive (e.g., "C01234567")

        Returns:
            Dictionary indicating success or error
        """
        client = get_slack_client()
        response = execute_slack_call(
            client.bot_client.conversations_archive,
            channel=channel_id,
        )

        if not response.success:
            return {"error": response.error}

        return {"success": True, "message": f"Channel {channel_id} archived successfully"}

    @mcp.tool()
    def get_channel_history(
        channel_id: str,
        limit: int = 20,
        oldest: str | None = None,
        latest: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch message history from a Slack channel.

        Args:
            channel_id: The ID of the channel (e.g., "C01234567")
            limit: Maximum number of messages to return (1-1000). Default: 20
            oldest: Unix timestamp of oldest message to include (optional)
            latest: Unix timestamp of latest message to include (optional)

        Returns:
            Dictionary containing list of messages with sender, text,
            timestamp, and thread info
        """
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

    @mcp.tool()
    def join_channel(channel_id: str) -> dict[str, Any]:
        """
        Join a Slack channel.

        Args:
            channel_id: The ID of the channel to join (e.g., "C01234567")

        Returns:
            Dictionary indicating success or error with channel info
        """
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

    @mcp.tool()
    def leave_channel(channel_id: str) -> dict[str, Any]:
        """
        Leave a Slack channel.

        Args:
            channel_id: The ID of the channel to leave (e.g., "C01234567")

        Returns:
            Dictionary indicating success or error
        """
        client = get_slack_client()
        response = execute_slack_call(
            client.bot_client.conversations_leave,
            channel=channel_id,
        )

        if not response.success:
            return {"error": response.error}

        return {"success": True, "message": f"Left channel {channel_id} successfully"}

    @mcp.tool()
    def set_channel_topic(channel_id: str, topic: str) -> dict[str, Any]:
        """
        Set the topic for a Slack channel.

        Args:
            channel_id: The ID of the channel (e.g., "C01234567")
            topic: The new topic text for the channel

        Returns:
            Dictionary indicating success with the new topic
        """
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

