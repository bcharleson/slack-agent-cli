"""Slack API client wrapper with authentication and error handling."""

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()


@dataclass
class SlackResponse:
    """Standardized response from Slack API calls."""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class SlackClientManager:
    """Manages Slack API clients for bot and user tokens."""

    _instance: "SlackClientManager | None" = None
    _bot_client: WebClient | None = None
    _user_client: WebClient | None = None

    def __new__(cls) -> "SlackClientManager":
        """Singleton pattern to ensure single client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Slack clients with tokens from environment."""
        self.refresh_clients()

    def refresh_clients(self) -> None:
        """Rebuild clients from current environment variables."""
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        self._bot_client = WebClient(token=bot_token) if bot_token else None

        user_token = os.getenv("SLACK_USER_TOKEN")
        self._user_client = WebClient(token=user_token) if user_token else None

    @property
    def bot_client(self) -> WebClient:
        """Get the bot client, raising an error if not configured."""
        if self._bot_client is None:
            raise ValueError(
                "SLACK_BOT_TOKEN environment variable is not set. "
                "Please set it to use bot-level Slack API operations."
            )
        return self._bot_client

    @property
    def user_client(self) -> WebClient:
        """Get the user client, raising an error if not configured."""
        if self._user_client is None:
            raise ValueError(
                "SLACK_USER_TOKEN environment variable is not set. "
                "Please set it to use user-level Slack API operations (like search)."
            )
        return self._user_client

    def has_bot_token(self) -> bool:
        """Check if bot token is configured."""
        return self._bot_client is not None

    def has_user_token(self) -> bool:
        """Check if user token is configured."""
        return self._user_client is not None


def get_slack_client() -> SlackClientManager:
    """Get the Slack client manager singleton."""
    return SlackClientManager()


def reset_slack_client() -> None:
    """Reset the Slack client singleton (used when CLI overrides tokens)."""
    SlackClientManager._instance = None
    SlackClientManager._bot_client = None
    SlackClientManager._user_client = None


def handle_slack_error(error: SlackApiError) -> SlackResponse:
    """Convert Slack API error to standardized response."""
    error_message = error.response.get("error", "Unknown error")
    error_detail = error.response.get("detail", "")

    full_error = error_message
    if error_detail:
        full_error = f"{error_message}: {error_detail}"

    return SlackResponse(success=False, error=full_error)


def execute_slack_call(
    func: callable,
    *args: Any,
    **kwargs: Any,
) -> SlackResponse:
    """
    Execute a Slack API call with standardized error handling.

    Args:
        func: The Slack API method to call
        *args: Positional arguments to pass to the method
        **kwargs: Keyword arguments to pass to the method

    Returns:
        SlackResponse with success status and data or error message
    """
    try:
        response = func(*args, **kwargs)
        return SlackResponse(success=True, data=response.data)
    except SlackApiError as e:
        return handle_slack_error(e)
    except ValueError as e:
        return SlackResponse(success=False, error=str(e))
    except Exception as e:
        return SlackResponse(success=False, error=f"Unexpected error: {str(e)}")

