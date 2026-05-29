"""Channel management tools for Slack MCP Server."""

from mcp.server.fastmcp import FastMCP

from ..operations import channels as ops


def register_channel_tools(mcp: FastMCP) -> None:
    """Register all channel-related tools with the MCP server."""
    mcp.tool()(ops.list_channels)
    mcp.tool()(ops.get_channel_info)
    mcp.tool()(ops.create_channel)
    mcp.tool()(ops.archive_channel)
    mcp.tool()(ops.get_channel_history)
    mcp.tool()(ops.join_channel)
    mcp.tool()(ops.leave_channel)
    mcp.tool()(ops.set_channel_topic)
