"""User operations shared by CLI and MCP."""

from typing import Any

from ..utils.slack_client import execute_slack_call, get_slack_client


def list_users(limit: int = 100, include_locale: bool = False) -> dict[str, Any]:
    """List all users in the Slack workspace."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.users_list,
        limit=min(limit, 1000),
        include_locale=include_locale,
    )

    if not response.success:
        return {"error": response.error}

    members = response.data.get("members", [])
    return {
        "users": [
            {
                "id": user.get("id"),
                "name": user.get("name"),
                "real_name": user.get("real_name"),
                "display_name": user.get("profile", {}).get("display_name"),
                "email": user.get("profile", {}).get("email"),
                "title": user.get("profile", {}).get("title"),
                "is_admin": user.get("is_admin", False),
                "is_owner": user.get("is_owner", False),
                "is_bot": user.get("is_bot", False),
                "deleted": user.get("deleted", False),
                "tz": user.get("tz"),
            }
            for user in members
            if not user.get("deleted", False)
        ],
        "total": len([u for u in members if not u.get("deleted", False)]),
    }


def get_user_info(user_id: str) -> dict[str, Any]:
    """Get detailed information about a specific user."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.users_info,
        user=user_id,
    )

    if not response.success:
        return {"error": response.error}

    user = response.data.get("user", {})
    profile = user.get("profile", {})

    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "real_name": user.get("real_name"),
        "display_name": profile.get("display_name"),
        "email": profile.get("email"),
        "title": profile.get("title"),
        "phone": profile.get("phone"),
        "skype": profile.get("skype"),
        "status_text": profile.get("status_text"),
        "status_emoji": profile.get("status_emoji"),
        "image_url": profile.get("image_192"),
        "is_admin": user.get("is_admin", False),
        "is_owner": user.get("is_owner", False),
        "is_bot": user.get("is_bot", False),
        "is_restricted": user.get("is_restricted", False),
        "is_ultra_restricted": user.get("is_ultra_restricted", False),
        "deleted": user.get("deleted", False),
        "tz": user.get("tz"),
        "tz_label": user.get("tz_label"),
        "updated": user.get("updated"),
    }


def get_user_presence(user_id: str) -> dict[str, Any]:
    """Get the presence/online status of a user."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.users_getPresence,
        user=user_id,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "user_id": user_id,
        "presence": response.data.get("presence"),
        "online": response.data.get("online", False),
        "auto_away": response.data.get("auto_away", False),
        "manual_away": response.data.get("manual_away", False),
        "connection_count": response.data.get("connection_count"),
        "last_activity": response.data.get("last_activity"),
    }


def lookup_user_by_email(email: str) -> dict[str, Any]:
    """Find a user by their email address."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.users_lookupByEmail,
        email=email,
    )

    if not response.success:
        return {"error": response.error}

    user = response.data.get("user", {})
    profile = user.get("profile", {})

    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "real_name": user.get("real_name"),
        "display_name": profile.get("display_name"),
        "email": profile.get("email"),
        "title": profile.get("title"),
        "is_admin": user.get("is_admin", False),
        "is_bot": user.get("is_bot", False),
        "tz": user.get("tz"),
    }


def get_user_profile(user_id: str) -> dict[str, Any]:
    """Get the profile information for a user."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.users_profile_get,
        user=user_id,
    )

    if not response.success:
        return {"error": response.error}

    profile = response.data.get("profile", {})
    return {
        "user_id": user_id,
        "real_name": profile.get("real_name"),
        "display_name": profile.get("display_name"),
        "email": profile.get("email"),
        "title": profile.get("title"),
        "phone": profile.get("phone"),
        "skype": profile.get("skype"),
        "first_name": profile.get("first_name"),
        "last_name": profile.get("last_name"),
        "status_text": profile.get("status_text"),
        "status_emoji": profile.get("status_emoji"),
        "status_expiration": profile.get("status_expiration"),
        "image_24": profile.get("image_24"),
        "image_48": profile.get("image_48"),
        "image_72": profile.get("image_72"),
        "image_192": profile.get("image_192"),
        "image_512": profile.get("image_512"),
    }


def get_bot_info() -> dict[str, Any]:
    """Get information about the authenticated bot user."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.auth_test,
    )

    if not response.success:
        return {"error": response.error}

    return {
        "user_id": response.data.get("user_id"),
        "user": response.data.get("user"),
        "team_id": response.data.get("team_id"),
        "team": response.data.get("team"),
        "bot_id": response.data.get("bot_id"),
        "url": response.data.get("url"),
    }


def get_team_info() -> dict[str, Any]:
    """Get information about the Slack workspace/team."""
    client = get_slack_client()
    response = execute_slack_call(
        client.bot_client.team_info,
    )

    if not response.success:
        return {"error": response.error}

    team = response.data.get("team", {})
    return {
        "id": team.get("id"),
        "name": team.get("name"),
        "domain": team.get("domain"),
        "email_domain": team.get("email_domain"),
        "icon": team.get("icon", {}).get("image_132"),
        "enterprise_id": team.get("enterprise_id"),
        "enterprise_name": team.get("enterprise_name"),
    }
