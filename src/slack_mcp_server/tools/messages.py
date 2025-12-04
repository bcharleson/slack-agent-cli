"""Messaging tools for Slack MCP Server including DMs, threads, and reactions."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..utils.slack_client import execute_slack_call, get_slack_client


def register_message_tools(mcp: FastMCP) -> None:
    """Register all message-related tools with the MCP server."""

    @mcp.tool()
    def post_message(
        channel_id: str,
        text: str,
        thread_ts: str | None = None,
        unfurl_links: bool = True,
        unfurl_media: bool = True,
    ) -> dict[str, Any]:
        """
        Post a message to a Slack channel.

        Args:
            channel_id: The ID of the channel to post to (e.g., "C01234567")
            text: The message text to post (supports Slack markdown)
            thread_ts: Optional thread timestamp to reply in a thread
            unfurl_links: Whether to unfurl text-based URLs. Default: True
            unfurl_media: Whether to unfurl media URLs. Default: True

        Returns:
            Dictionary containing the posted message details including timestamp
        """
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

    @mcp.tool()
    def reply_to_thread(
        channel_id: str,
        thread_ts: str,
        text: str,
        broadcast: bool = False,
    ) -> dict[str, Any]:
        """
        Reply to a message thread in Slack.

        Args:
            channel_id: The ID of the channel containing the thread (e.g., "C01234567")
            thread_ts: The timestamp of the parent message to reply to
            text: The reply message text (supports Slack markdown)
            broadcast: Whether to also post the reply to the channel. Default: False

        Returns:
            Dictionary containing the posted reply details
        """
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

    @mcp.tool()
    def get_thread_replies(
        channel_id: str,
        thread_ts: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get all replies in a message thread.

        Args:
            channel_id: The ID of the channel containing the thread (e.g., "C01234567")
            thread_ts: The timestamp of the parent message
            limit: Maximum number of replies to return (1-1000). Default: 20

        Returns:
            Dictionary containing the thread messages
        """
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

    @mcp.tool()
    def add_reaction(
        channel_id: str,
        timestamp: str,
        emoji: str,
    ) -> dict[str, Any]:
        """
        Add an emoji reaction to a message.

        Args:
            channel_id: The ID of the channel containing the message (e.g., "C01234567")
            timestamp: The timestamp of the message to react to
            emoji: The emoji name without colons (e.g., "thumbsup", "heart", "rocket")

        Returns:
            Dictionary indicating success or error
        """
        client = get_slack_client()
        response = execute_slack_call(
            client.bot_client.reactions_add,
            channel=channel_id,
            timestamp=timestamp,
            name=emoji,
        )

        if not response.success:
            return {"error": response.error}

        return {
            "success": True,
            "message": f"Added :{emoji}: reaction to message",
        }

    @mcp.tool()
    def remove_reaction(
        channel_id: str,
        timestamp: str,
        emoji: str,
    ) -> dict[str, Any]:
        """
        Remove an emoji reaction from a message.

        Args:
            channel_id: The ID of the channel containing the message (e.g., "C01234567")
            timestamp: The timestamp of the message
            emoji: The emoji name without colons (e.g., "thumbsup", "heart", "rocket")

        Returns:
            Dictionary indicating success or error
        """
        client = get_slack_client()
        response = execute_slack_call(
            client.bot_client.reactions_remove,
            channel=channel_id,
            timestamp=timestamp,
            name=emoji,
        )

        if not response.success:
            return {"error": response.error}

        return {
            "success": True,
            "message": f"Removed :{emoji}: reaction from message",
        }

    @mcp.tool()
    def get_message_reactions(
        channel_id: str,
        timestamp: str,
    ) -> dict[str, Any]:
        """
        Get all reactions on a specific message.

        Args:
            channel_id: The ID of the channel containing the message (e.g., "C01234567")
            timestamp: The timestamp of the message

        Returns:
            Dictionary containing the message and its reactions
        """
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

    @mcp.tool()
    def update_message(
        channel_id: str,
        timestamp: str,
        text: str,
    ) -> dict[str, Any]:
        """
        Update an existing message.

        Args:
            channel_id: The ID of the channel containing the message (e.g., "C01234567")
            timestamp: The timestamp of the message to update
            text: The new message text

        Returns:
            Dictionary indicating success with updated message details
        """
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

    @mcp.tool()
    def delete_message(
        channel_id: str,
        timestamp: str,
    ) -> dict[str, Any]:
        """
        Delete a message from a channel.

        Args:
            channel_id: The ID of the channel containing the message (e.g., "C01234567")
            timestamp: The timestamp of the message to delete

        Returns:
            Dictionary indicating success or error
        """
        client = get_slack_client()
        response = execute_slack_call(
            client.bot_client.chat_delete,
            channel=channel_id,
            ts=timestamp,
        )

        if not response.success:
            return {"error": response.error}

        return {
            "success": True,
            "message": "Message deleted successfully",
        }

    # DM (Direct Message) Tools

    @mcp.tool()
    def send_dm(
        user_id: str,
        text: str,
    ) -> dict[str, Any]:
        """
        Send a direct message to a user.

        Args:
            user_id: The ID of the user to message (e.g., "U01234567")
            text: The message text to send (supports Slack markdown)

        Returns:
            Dictionary containing the sent message details
        """
        client = get_slack_client()

        # First, open a DM channel with the user
        open_response = execute_slack_call(
            client.bot_client.conversations_open,
            users=[user_id],
        )

        if not open_response.success:
            return {"error": open_response.error}

        channel_id = open_response.data.get("channel", {}).get("id")
        if not channel_id:
            return {"error": "Failed to open DM channel"}

        # Send the message
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

    @mcp.tool()
    def list_conversations(
        types: str = "im,mpim",
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        List direct message and group DM conversations.

        Args:
            types: Comma-separated conversation types. Default: "im,mpim"
                   Options: im (1:1 DMs), mpim (group DMs)
            limit: Maximum number of conversations to return. Default: 50

        Returns:
            Dictionary containing list of DM conversations
        """
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
                    "user": ch.get("user"),  # For 1:1 DMs
                    "name": ch.get("name", ""),  # For group DMs
                    "is_open": ch.get("is_open", False),
                }
                for ch in channels
            ],
            "total": len(channels),
        }

    @mcp.tool()
    def get_dm_history(
        channel_id: str,
        limit: int = 20,
        oldest: str | None = None,
        latest: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch message history from a DM or group DM conversation.

        Args:
            channel_id: The ID of the DM conversation (e.g., "D01234567")
            limit: Maximum number of messages to return (1-1000). Default: 20
            oldest: Unix timestamp of oldest message to include (optional)
            latest: Unix timestamp of latest message to include (optional)

        Returns:
            Dictionary containing list of messages
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
                }
                for msg in messages
            ],
            "has_more": response.data.get("has_more", False),
            "total": len(messages),
        }

    @mcp.tool()
    def open_dm(user_ids: str) -> dict[str, Any]:
        """
        Open a direct message or group DM conversation.

        Args:
            user_ids: Comma-separated user IDs to open a conversation with
                      (e.g., "U01234567" for DM, "U01234567,U07654321" for group DM)

        Returns:
            Dictionary containing the conversation channel details
        """
        client = get_slack_client()

        users = [u.strip() for u in user_ids.split(",")]
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

