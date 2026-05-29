"""Search operations shared by CLI and MCP."""

from typing import Any

from ..utils.slack_client import execute_slack_call, get_slack_client


def _require_user_token(client: Any) -> dict[str, Any] | None:
    if not client.has_user_token():
        return {
            "error": "Search requires a User Token (SLACK_USER_TOKEN). "
            "Bot tokens cannot perform search operations."
        }
    return None


def search_messages(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
) -> dict[str, Any]:
    """Search messages across the Slack workspace."""
    client = get_slack_client()
    token_error = _require_user_token(client)
    if token_error:
        return token_error

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


def search_files(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    types: str | None = None,
) -> dict[str, Any]:
    """Search files across the Slack workspace."""
    client = get_slack_client()
    token_error = _require_user_token(client)
    if token_error:
        return token_error

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


def search_all(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 10,
) -> dict[str, Any]:
    """Search both messages and files across the Slack workspace."""
    client = get_slack_client()
    token_error = _require_user_token(client)
    if token_error:
        return token_error

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
                    "text": msg.get("text", "")[:200],
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
