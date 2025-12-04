"""Search tools for Slack MCP Server."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..utils.slack_client import execute_slack_call, get_slack_client


def register_search_tools(mcp: FastMCP) -> None:
    """Register all search-related tools with the MCP server."""

    @mcp.tool()
    def search_messages(
        query: str,
        sort: str = "timestamp",
        sort_dir: str = "desc",
        count: int = 20,
    ) -> dict[str, Any]:
        """
        Search messages across the Slack workspace.

        Note: Requires a User Token (SLACK_USER_TOKEN) as search is not
        available with bot tokens.

        Args:
            query: Search query string. Supports Slack search modifiers:
                   - "in:#channel" to search in specific channel
                   - "from:@user" to search messages from a user
                   - "has:reaction" to find messages with reactions
                   - "before:YYYY-MM-DD" or "after:YYYY-MM-DD" for date filters
                   Example: "project update in:#general from:@john"
            sort: Sort order - "timestamp" or "score". Default: "timestamp"
            sort_dir: Sort direction - "asc" or "desc". Default: "desc"
            count: Number of results to return (1-100). Default: 20

        Returns:
            Dictionary containing search results with messages and metadata
        """
        client = get_slack_client()

        if not client.has_user_token():
            return {
                "error": "Search requires a User Token (SLACK_USER_TOKEN). "
                "Bot tokens cannot perform search operations."
            }

        response = execute_slack_call(
            client.user_client.search_messages,
            query=query,
            sort=sort,
            sort_dir=sort_dir,
            count=min(count, 100),
        )

        if not response.success:
            return {"error": response.error}

        messages = response.data.get("messages", {})
        matches = messages.get("matches", [])

        return {
            "query": query,
            "total": messages.get("total", 0),
            "messages": [
                {
                    "ts": msg.get("ts"),
                    "text": msg.get("text", ""),
                    "user": msg.get("user"),
                    "username": msg.get("username"),
                    "channel": {
                        "id": msg.get("channel", {}).get("id"),
                        "name": msg.get("channel", {}).get("name"),
                    },
                    "permalink": msg.get("permalink"),
                }
                for msg in matches
            ],
            "returned": len(matches),
        }

    @mcp.tool()
    def search_files(
        query: str,
        sort: str = "timestamp",
        sort_dir: str = "desc",
        count: int = 20,
        types: str | None = None,
    ) -> dict[str, Any]:
        """
        Search files across the Slack workspace.

        Note: Requires a User Token (SLACK_USER_TOKEN) as search is not
        available with bot tokens.

        Args:
            query: Search query string. Supports Slack search modifiers:
                   - "in:#channel" to search in specific channel
                   - "from:@user" to search files from a user
                   - "type:pdf" to filter by file type
                   Example: "quarterly report type:pdf in:#finance"
            sort: Sort order - "timestamp" or "score". Default: "timestamp"
            sort_dir: Sort direction - "asc" or "desc". Default: "desc"
            count: Number of results to return (1-100). Default: 20
            types: Comma-separated file types to filter (optional)
                   Options: images, videos, pdfs, docs, snippets, etc.

        Returns:
            Dictionary containing search results with files and metadata
        """
        client = get_slack_client()

        if not client.has_user_token():
            return {
                "error": "Search requires a User Token (SLACK_USER_TOKEN). "
                "Bot tokens cannot perform search operations."
            }

        kwargs: dict[str, Any] = {
            "query": query,
            "sort": sort,
            "sort_dir": sort_dir,
            "count": min(count, 100),
        }
        if types:
            kwargs["types"] = types

        response = execute_slack_call(
            client.user_client.search_files,
            **kwargs,
        )

        if not response.success:
            return {"error": response.error}

        files = response.data.get("files", {})
        matches = files.get("matches", [])

        return {
            "query": query,
            "total": files.get("total", 0),
            "files": [
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "title": f.get("title"),
                    "filetype": f.get("filetype"),
                    "size": f.get("size"),
                    "user": f.get("user"),
                    "channels": f.get("channels", []),
                    "created": f.get("created"),
                    "url_private": f.get("url_private"),
                    "permalink": f.get("permalink"),
                }
                for f in matches
            ],
            "returned": len(matches),
        }

    @mcp.tool()
    def search_all(
        query: str,
        sort: str = "timestamp",
        sort_dir: str = "desc",
        count: int = 10,
    ) -> dict[str, Any]:
        """
        Search both messages and files across the Slack workspace.

        Note: Requires a User Token (SLACK_USER_TOKEN) as search is not
        available with bot tokens.

        Args:
            query: Search query string. Supports Slack search modifiers.
            sort: Sort order - "timestamp" or "score". Default: "timestamp"
            sort_dir: Sort direction - "asc" or "desc". Default: "desc"
            count: Number of results per type (1-100). Default: 10

        Returns:
            Dictionary containing both message and file search results
        """
        client = get_slack_client()

        if not client.has_user_token():
            return {
                "error": "Search requires a User Token (SLACK_USER_TOKEN). "
                "Bot tokens cannot perform search operations."
            }

        response = execute_slack_call(
            client.user_client.search_all,
            query=query,
            sort=sort,
            sort_dir=sort_dir,
            count=min(count, 100),
        )

        if not response.success:
            return {"error": response.error}

        messages = response.data.get("messages", {})
        files = response.data.get("files", {})

        return {
            "query": query,
            "messages": {
                "total": messages.get("total", 0),
                "matches": [
                    {
                        "ts": msg.get("ts"),
                        "text": msg.get("text", "")[:200],  # Truncate for overview
                        "user": msg.get("user"),
                        "channel_name": msg.get("channel", {}).get("name"),
                        "permalink": msg.get("permalink"),
                    }
                    for msg in messages.get("matches", [])
                ],
            },
            "files": {
                "total": files.get("total", 0),
                "matches": [
                    {
                        "id": f.get("id"),
                        "name": f.get("name"),
                        "filetype": f.get("filetype"),
                        "user": f.get("user"),
                        "permalink": f.get("permalink"),
                    }
                    for f in files.get("matches", [])
                ],
            },
        }

