"""Messaging tools for Slack MCP Server including DMs, threads, and reactions."""

from mcp.server.fastmcp import FastMCP

from ..operations import messages as ops


def register_message_tools(mcp: FastMCP) -> None:
    """Register all message-related tools with the MCP server."""
    mcp.tool()(ops.post_message)
    mcp.tool()(ops.reply_to_thread)
    mcp.tool()(ops.get_thread_replies)
    mcp.tool()(ops.add_reaction)
    mcp.tool()(ops.remove_reaction)
    mcp.tool()(ops.get_message_reactions)
    mcp.tool()(ops.update_message)
    mcp.tool()(ops.delete_message)
    mcp.tool()(ops.send_dm)
    mcp.tool()(ops.list_conversations)
    mcp.tool()(ops.get_dm_history)
    mcp.tool()(ops.open_dm)
