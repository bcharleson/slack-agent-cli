"""Slack Agent CLI — MCP server entry point."""

import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .tools.channels import register_channel_tools
from .tools.messages import register_message_tools
from .tools.search import register_search_tools
from .tools.users import register_user_tools

# Load environment variables from .env file
load_dotenv()

# Create FastMCP server instance
mcp = FastMCP(
    name="Slack Agent CLI",
    instructions="CLI and MCP server for Slack API integration. "
    "Enables AI assistants to interact with Slack workspaces including "
    "channels, messages, DMs, search, and user management.",
)


def validate_environment() -> bool:
    """Validate that required environment variables are set."""
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    user_token = os.getenv("SLACK_USER_TOKEN")

    if not bot_token:
        print(
            "Warning: SLACK_BOT_TOKEN is not set. "
            "Most Slack operations will not work.",
            file=sys.stderr,
        )
        return False

    if not user_token:
        print(
            "Note: SLACK_USER_TOKEN is not set. "
            "Search functionality will not be available.",
            file=sys.stderr,
        )

    return True


def register_all_tools() -> None:
    """Register all tool modules with the MCP server."""
    register_channel_tools(mcp)
    register_message_tools(mcp)
    register_search_tools(mcp)
    register_user_tools(mcp)


# Register all tools at module load time
register_all_tools()


def main() -> None:
    """Main entry point for the Slack MCP Server."""
    validate_environment()

    # Run the server using stdio transport (default for MCP)
    mcp.run()


if __name__ == "__main__":
    main()

