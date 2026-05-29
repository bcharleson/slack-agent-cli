"""User management tools for Slack MCP Server."""

from mcp.server.fastmcp import FastMCP

from ..operations import users as ops


def register_user_tools(mcp: FastMCP) -> None:
    """Register all user-related tools with the MCP server."""
    mcp.tool()(ops.list_users)
    mcp.tool()(ops.get_user_info)
    mcp.tool()(ops.get_user_presence)
    mcp.tool()(ops.lookup_user_by_email)
    mcp.tool()(ops.get_user_profile)
    mcp.tool()(ops.get_bot_info)
    mcp.tool()(ops.get_team_info)
