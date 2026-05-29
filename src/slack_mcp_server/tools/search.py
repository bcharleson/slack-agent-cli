"""Search tools for Slack MCP Server."""

from mcp.server.fastmcp import FastMCP

from ..operations import search as ops


def register_search_tools(mcp: FastMCP) -> None:
    """Register all search-related tools with the MCP server."""
    mcp.tool()(ops.search_messages)
    mcp.tool()(ops.search_files)
    mcp.tool()(ops.search_all)
