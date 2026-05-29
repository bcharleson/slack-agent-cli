"""Slack CLI — terminal commands and MCP server entrypoint."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import click

from .. import __version__
from ..core.output import emit_result
from ..operations import channels, messages, search, users
from ..server import main as run_mcp_server
from ..utils.slack_client import reset_slack_client


def _configure_tokens(ctx: click.Context) -> None:
    bot_token = ctx.obj.get("bot_token")
    user_token = ctx.obj.get("user_token")

    if bot_token:
        os.environ["SLACK_BOT_TOKEN"] = bot_token
    if user_token:
        os.environ["SLACK_USER_TOKEN"] = user_token

    if bot_token or user_token:
        reset_slack_client()


def _run(ctx: click.Context, handler: Callable[..., dict[str, Any]], **kwargs: Any) -> None:
    _configure_tokens(ctx)
    emit_result(
        handler(**kwargs),
        output=ctx.obj["output"],
        pretty=ctx.obj["pretty"],
        quiet=ctx.obj["quiet"],
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="slack")
@click.option("--bot-token", envvar="SLACK_BOT_TOKEN", help="Slack bot token (xoxb-...)")
@click.option("--user-token", envvar="SLACK_USER_TOKEN", help="Slack user token (xoxp-...)")
@click.option(
    "--output",
    type=click.Choice(["json", "pretty"]),
    default="json",
    show_default=True,
    help="Output format",
)
@click.option("--pretty", is_flag=True, help="Shorthand for --output pretty")
@click.option("--quiet", is_flag=True, help="Suppress output; exit codes only")
@click.pass_context
def cli(ctx: click.Context, bot_token: str | None, user_token: str | None, output: str, pretty: bool, quiet: bool) -> None:
    """CLI and MCP server for Slack — channels, messages, DMs, search, and users."""
    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "bot_token": bot_token,
            "user_token": user_token,
            "output": "pretty" if pretty else output,
            "pretty": pretty,
            "quiet": quiet,
        }
    )


@cli.command("mcp")
def mcp_command() -> None:
    """Start the MCP (Model Context Protocol) server on stdio."""
    run_mcp_server()


@cli.group("channels")
def channels_group() -> None:
    """Manage Slack channels."""


@channels_group.command("list")
@click.option("--types", default="public_channel,private_channel", show_default=True)
@click.option("--exclude-archived/--include-archived", default=True, show_default=True)
@click.option("--limit", default=100, show_default=True, type=int)
@click.pass_context
def channels_list(ctx: click.Context, types: str, exclude_archived: bool, limit: int) -> None:
    _run(ctx, channels.list_channels, types=types, exclude_archived=exclude_archived, limit=limit)


@channels_group.command("info")
@click.argument("channel_id")
@click.pass_context
def channels_info(ctx: click.Context, channel_id: str) -> None:
    _run(ctx, channels.get_channel_info, channel_id=channel_id)


@channels_group.command("create")
@click.argument("name")
@click.option("--private", "is_private", is_flag=True, help="Create a private channel")
@click.pass_context
def channels_create(ctx: click.Context, name: str, is_private: bool) -> None:
    _run(ctx, channels.create_channel, name=name, is_private=is_private)


@channels_group.command("archive")
@click.argument("channel_id")
@click.pass_context
def channels_archive(ctx: click.Context, channel_id: str) -> None:
    _run(ctx, channels.archive_channel, channel_id=channel_id)


@channels_group.command("history")
@click.argument("channel_id")
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--oldest")
@click.option("--latest")
@click.pass_context
def channels_history(ctx: click.Context, channel_id: str, limit: int, oldest: str | None, latest: str | None) -> None:
    _run(ctx, channels.get_channel_history, channel_id=channel_id, limit=limit, oldest=oldest, latest=latest)


@channels_group.command("join")
@click.argument("channel_id")
@click.pass_context
def channels_join(ctx: click.Context, channel_id: str) -> None:
    _run(ctx, channels.join_channel, channel_id=channel_id)


@channels_group.command("leave")
@click.argument("channel_id")
@click.pass_context
def channels_leave(ctx: click.Context, channel_id: str) -> None:
    _run(ctx, channels.leave_channel, channel_id=channel_id)


@channels_group.command("set-topic")
@click.argument("channel_id")
@click.argument("topic")
@click.pass_context
def channels_set_topic(ctx: click.Context, channel_id: str, topic: str) -> None:
    _run(ctx, channels.set_channel_topic, channel_id=channel_id, topic=topic)


@cli.group("messages")
def messages_group() -> None:
    """Post and manage channel messages."""


@messages_group.command("post")
@click.argument("channel_id")
@click.argument("text")
@click.option("--thread-ts")
@click.option("--no-unfurl-links", is_flag=True)
@click.option("--no-unfurl-media", is_flag=True)
@click.pass_context
def messages_post(
    ctx: click.Context,
    channel_id: str,
    text: str,
    thread_ts: str | None,
    no_unfurl_links: bool,
    no_unfurl_media: bool,
) -> None:
    _run(
        ctx,
        messages.post_message,
        channel_id=channel_id,
        text=text,
        thread_ts=thread_ts,
        unfurl_links=not no_unfurl_links,
        unfurl_media=not no_unfurl_media,
    )


@messages_group.command("reply")
@click.argument("channel_id")
@click.argument("thread_ts")
@click.argument("text")
@click.option("--broadcast", is_flag=True)
@click.pass_context
def messages_reply(ctx: click.Context, channel_id: str, thread_ts: str, text: str, broadcast: bool) -> None:
    _run(ctx, messages.reply_to_thread, channel_id=channel_id, thread_ts=thread_ts, text=text, broadcast=broadcast)


@messages_group.command("thread")
@click.argument("channel_id")
@click.argument("thread_ts")
@click.option("--limit", default=20, show_default=True, type=int)
@click.pass_context
def messages_thread(ctx: click.Context, channel_id: str, thread_ts: str, limit: int) -> None:
    _run(ctx, messages.get_thread_replies, channel_id=channel_id, thread_ts=thread_ts, limit=limit)


@messages_group.command("react")
@click.argument("channel_id")
@click.argument("timestamp")
@click.argument("emoji")
@click.pass_context
def messages_react(ctx: click.Context, channel_id: str, timestamp: str, emoji: str) -> None:
    _run(ctx, messages.add_reaction, channel_id=channel_id, timestamp=timestamp, emoji=emoji)


@messages_group.command("unreact")
@click.argument("channel_id")
@click.argument("timestamp")
@click.argument("emoji")
@click.pass_context
def messages_unreact(ctx: click.Context, channel_id: str, timestamp: str, emoji: str) -> None:
    _run(ctx, messages.remove_reaction, channel_id=channel_id, timestamp=timestamp, emoji=emoji)


@messages_group.command("reactions")
@click.argument("channel_id")
@click.argument("timestamp")
@click.pass_context
def messages_reactions(ctx: click.Context, channel_id: str, timestamp: str) -> None:
    _run(ctx, messages.get_message_reactions, channel_id=channel_id, timestamp=timestamp)


@messages_group.command("update")
@click.argument("channel_id")
@click.argument("timestamp")
@click.argument("text")
@click.pass_context
def messages_update(ctx: click.Context, channel_id: str, timestamp: str, text: str) -> None:
    _run(ctx, messages.update_message, channel_id=channel_id, timestamp=timestamp, text=text)


@messages_group.command("delete")
@click.argument("channel_id")
@click.argument("timestamp")
@click.pass_context
def messages_delete(ctx: click.Context, channel_id: str, timestamp: str) -> None:
    _run(ctx, messages.delete_message, channel_id=channel_id, timestamp=timestamp)


@cli.group("dms")
def dms_group() -> None:
    """Direct message operations."""


@dms_group.command("send")
@click.argument("user_id")
@click.argument("text")
@click.pass_context
def dms_send(ctx: click.Context, user_id: str, text: str) -> None:
    _run(ctx, messages.send_dm, user_id=user_id, text=text)


@dms_group.command("list")
@click.option("--types", default="im,mpim", show_default=True)
@click.option("--limit", default=50, show_default=True, type=int)
@click.pass_context
def dms_list(ctx: click.Context, types: str, limit: int) -> None:
    _run(ctx, messages.list_conversations, types=types, limit=limit)


@dms_group.command("history")
@click.argument("channel_id")
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--oldest")
@click.option("--latest")
@click.pass_context
def dms_history(ctx: click.Context, channel_id: str, limit: int, oldest: str | None, latest: str | None) -> None:
    _run(ctx, messages.get_dm_history, channel_id=channel_id, limit=limit, oldest=oldest, latest=latest)


@dms_group.command("open")
@click.argument("user_ids")
@click.pass_context
def dms_open(ctx: click.Context, user_ids: str) -> None:
    _run(ctx, messages.open_dm, user_ids=user_ids)


@cli.group("search")
def search_group() -> None:
    """Search messages and files (requires user token)."""


@search_group.command("messages")
@click.argument("query")
@click.option("--sort", default="timestamp", show_default=True)
@click.option("--sort-dir", default="desc", show_default=True)
@click.option("--count", default=20, show_default=True, type=int)
@click.pass_context
def search_messages_cmd(ctx: click.Context, query: str, sort: str, sort_dir: str, count: int) -> None:
    _run(ctx, search.search_messages, query=query, sort=sort, sort_dir=sort_dir, count=count)


@search_group.command("files")
@click.argument("query")
@click.option("--sort", default="timestamp", show_default=True)
@click.option("--sort-dir", default="desc", show_default=True)
@click.option("--count", default=20, show_default=True, type=int)
@click.option("--types")
@click.pass_context
def search_files_cmd(ctx: click.Context, query: str, sort: str, sort_dir: str, count: int, types: str | None) -> None:
    _run(ctx, search.search_files, query=query, sort=sort, sort_dir=sort_dir, count=count, types=types)


@search_group.command("all")
@click.argument("query")
@click.option("--sort", default="timestamp", show_default=True)
@click.option("--sort-dir", default="desc", show_default=True)
@click.option("--count", default=10, show_default=True, type=int)
@click.pass_context
def search_all_cmd(ctx: click.Context, query: str, sort: str, sort_dir: str, count: int) -> None:
    _run(ctx, search.search_all, query=query, sort=sort, sort_dir=sort_dir, count=count)


@cli.group("users")
def users_group() -> None:
    """Workspace user operations."""


@users_group.command("list")
@click.option("--limit", default=100, show_default=True, type=int)
@click.option("--include-locale", is_flag=True)
@click.pass_context
def users_list(ctx: click.Context, limit: int, include_locale: bool) -> None:
    _run(ctx, users.list_users, limit=limit, include_locale=include_locale)


@users_group.command("info")
@click.argument("user_id")
@click.pass_context
def users_info(ctx: click.Context, user_id: str) -> None:
    _run(ctx, users.get_user_info, user_id=user_id)


@users_group.command("presence")
@click.argument("user_id")
@click.pass_context
def users_presence(ctx: click.Context, user_id: str) -> None:
    _run(ctx, users.get_user_presence, user_id=user_id)


@users_group.command("lookup")
@click.argument("email")
@click.pass_context
def users_lookup(ctx: click.Context, email: str) -> None:
    _run(ctx, users.lookup_user_by_email, email=email)


@users_group.command("profile")
@click.argument("user_id")
@click.pass_context
def users_profile(ctx: click.Context, user_id: str) -> None:
    _run(ctx, users.get_user_profile, user_id=user_id)


@cli.group("workspace")
def workspace_group() -> None:
    """Bot and workspace metadata."""


@workspace_group.command("bot")
@click.pass_context
def workspace_bot(ctx: click.Context) -> None:
    _run(ctx, users.get_bot_info)


@workspace_group.command("team")
@click.pass_context
def workspace_team(ctx: click.Context) -> None:
    _run(ctx, users.get_team_info)


def main() -> None:
    """CLI entrypoint."""
    cli(obj={})


if __name__ == "__main__":
    main()
