# Slack Agent CLI — AI Agent Guide

> This file helps AI agents (Claude, Cursor, GPT, Gemini, OpenClaw) install, authenticate, and use `slack-agent-cli` to manage Slack workspaces via terminal commands or MCP tools.

## Quick Start

```bash
# Install (requires Node 18+ and Python 3.10+)
npm install -g slack-agent-cli

# Authenticate (non-interactive — best for agents)
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_USER_TOKEN="xoxp-your-user-token"   # optional; required for search

# Verify
slack --version
slack channels list --pretty
```

**Alternative (Python-only, from source):**

```bash
git clone https://github.com/bcharleson/slack-agent-cli.git
cd slack-agent-cli
python3 -m venv venv && source venv/bin/activate
pip install -e .
slack channels list
```

## Authentication

Two tokens, resolved in this order:

1. `--bot-token` / `--user-token` flags (per-command override)
2. `SLACK_BOT_TOKEN` / `SLACK_USER_TOKEN` environment variables (recommended for agents)
3. `.env` file in the working directory (via `python-dotenv`)

| Token | Prefix | Used for |
|---|---|---|
| Bot token | `xoxb-` | Channels, messages, DMs, reactions, most user lookups |
| User token | `xoxp-` | **Search** (`search.*` commands/tools) — bot token cannot search |

Create tokens at [Slack API Apps](https://api.slack.com/apps) → your app → **OAuth & Permissions** → Install to workspace.

Minimum bot scopes: `channels:read`, `channels:write`, `channels:history`, `groups:read`, `groups:write`, `groups:history`, `chat:write`, `im:read`, `im:write`, `im:history`, `mpim:read`, `mpim:write`, `mpim:history`, `users:read`, `users:read.email`, `reactions:read`, `reactions:write`.

For search, add user scope: `search:read`.

## Output Format

All commands return **JSON** — stdout on success, stderr on error:

```bash
# Default: compact JSON (agent-optimized)
slack channels list
# → {"channels":[{"id":"C0123","name":"general",...}],"total":42}

# Pretty-printed
slack channels list --pretty
# or
slack --output pretty channels list

# Exit code only (automation)
slack --quiet channels list
```

**Exit codes:** `0` = success, `1` = error (response includes `"error": "..."` key).

## Discovering Commands

```bash
slack --help
slack channels --help
slack messages post --help
```

Command groups map 1:1 to MCP tool categories. CLI uses nested subcommands; MCP exposes flat snake_case tool names (function names from `operations/`).

## All Commands

### `channels` (8 commands)

| Command | Description |
|---|---|
| `list` | List channels (`--types`, `--exclude-archived`, `--limit`) |
| `info <channel_id>` | Channel metadata |
| `create <name>` | Create channel (`--private`) |
| `archive <channel_id>` | Archive channel |
| `history <channel_id>` | Message history (`--limit`, `--oldest`, `--latest`) |
| `join <channel_id>` | Join channel |
| `leave <channel_id>` | Leave channel |
| `set-topic <channel_id> <topic>` | Set channel topic |

### `messages` (8 commands)

| Command | Description |
|---|---|
| `post <channel_id> <text>` | Post message (`--thread-ts`, `--no-unfurl-links`, `--no-unfurl-media`) |
| `reply <channel_id> <thread_ts> <text>` | Reply in thread (`--broadcast`) |
| `thread <channel_id> <thread_ts>` | Get thread replies (`--limit`) |
| `react <channel_id> <timestamp> <emoji>` | Add reaction (emoji without colons) |
| `unreact <channel_id> <timestamp> <emoji>` | Remove reaction |
| `reactions <channel_id> <timestamp>` | List reactions on a message |
| `update <channel_id> <timestamp> <text>` | Edit message |
| `delete <channel_id> <timestamp>` | Delete message |

### `dms` (4 commands)

| Command | Description |
|---|---|
| `send <user_id> <text>` | Send DM to user |
| `list` | List DM / group DM conversations (`--types`, `--limit`) |
| `history <channel_id>` | DM history (`--limit`, `--oldest`, `--latest`) |
| `open <user_ids>` | Open DM (comma-separated user IDs) |

### `search` (3 commands — **requires user token**)

| Command | Description |
|---|---|
| `messages <query>` | Search messages (`--sort`, `--sort-dir`, `--count`) |
| `files <query>` | Search files (`--types`) |
| `all <query>` | Combined message + file search |

Slack search query syntax: `in:#channel`, `from:@user`, `has:link`, etc.

### `users` (5 commands)

| Command | Description |
|---|---|
| `list` | List workspace users (`--limit`, `--include-locale`) |
| `info <user_id>` | User by ID |
| `presence <user_id>` | Online/away status |
| `lookup <email>` | User by email |
| `profile <user_id>` | Full profile |

### `workspace` (2 commands)

| Command | Description |
|---|---|
| `bot` | Authenticated bot info |
| `team` | Workspace/team info |

### `mcp`

| Command | Description |
|---|---|
| `mcp` | Start stdio MCP server (same tools as above) |

## MCP Tools (30 total)

Registered from `src/slack_agent_cli/operations/` — tool name = Python function name:

**Channels:** `list_channels`, `get_channel_info`, `create_channel`, `archive_channel`, `get_channel_history`, `join_channel`, `leave_channel`, `set_channel_topic`

**Messages & DMs:** `post_message`, `reply_to_thread`, `get_thread_replies`, `add_reaction`, `remove_reaction`, `get_message_reactions`, `update_message`, `delete_message`, `send_dm`, `list_conversations`, `get_dm_history`, `open_dm`

**Search:** `search_messages`, `search_files`, `search_all`

**Users & workspace:** `list_users`, `get_user_info`, `get_user_presence`, `lookup_user_by_email`, `get_user_profile`, `get_bot_info`, `get_team_info`

All tools return the same JSON dict shape as the CLI.

## MCP Configuration

### Cursor / Claude Desktop (global npm install)

```json
{
  "mcpServers": {
    "slack-agent-cli": {
      "command": "slack",
      "args": ["mcp"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_USER_TOKEN": "xoxp-your-user-token"
      }
    }
  }
}
```

### npx (no global install)

```json
{
  "mcpServers": {
    "slack-agent-cli": {
      "command": "npx",
      "args": ["-y", "slack-agent-cli", "mcp"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_USER_TOKEN": "xoxp-your-user-token"
      }
    }
  }
}
```

### Local development (Python venv)

```json
{
  "mcpServers": {
    "slack-agent-cli": {
      "command": "/path/to/slack-agent-cli/venv/bin/slack",
      "args": ["mcp"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_USER_TOKEN": "xoxp-your-user-token"
      }
    }
  }
}
```

## Common Workflows (Agents)

### Post to a channel after resolving name → ID

```bash
# 1. Find channel ID
slack channels list --pretty | jq '.channels[] | select(.name=="general")'

# 2. Post message
slack messages post C01234567 "Deployment complete."
```

### Reply in a thread

```bash
# thread_ts comes from message timestamp in history
slack messages reply C01234567 1710000000.000100 "Acknowledged."
```

### DM a user by email

```bash
slack users lookup brandon@example.com --pretty
# → {"user":{"id":"U01234567",...}}

slack dms send U01234567 "Quick question from the agent."
```

### Search workspace (user token required)

```bash
export SLACK_USER_TOKEN="xoxp-..."
slack search messages "project update in:#general" --count 10 --pretty
```

## Architecture

Dual-entry pattern (same as `instantly-cli`, `ocean-agent-cli`, `smartlead-cli`):

```
src/slack_agent_cli/
  operations/     # Shared business logic — CLI + MCP call these
  tools/            # Thin MCP registrations (mcp.tool()(ops.fn))
  cli/main.py       # Click CLI groups
  server.py         # FastMCP stdio server
  utils/slack_client.py
bin/slack.js        # npm launcher → python -m slack_agent_cli.cli.main
```

**Rule:** Add new capabilities in `operations/`, register in `tools/`, wire a Click subcommand in `cli/main.py`. Never duplicate Slack API calls in CLI vs MCP layers.

## Key Slack API Facts

- **Channel IDs** start with `C`; **user IDs** with `U`; **DM channel IDs** with `D`.
- **Message timestamps** (`ts`) are strings like `1710000000.000100` — use as `thread_ts` for replies.
- **Reactions:** pass emoji name only (`thumbsup`), not `:thumbsup:`.
- **Private channels:** bot must be a member (`channels join`) to read/post.
- **Rate limits:** Slack returns `429`; client surfaces errors in `{"error": "..."}` — back off and retry.
- **Search** is the only category that requires the **user token**, not the bot token.

## npm vs Python Versions

Keep `package.json` `version`, `pyproject.toml` `version`, and `src/slack_agent_cli/__init__.py` `__version__` in sync. `npm run prepublishOnly` runs `scripts/check-version.js` to enforce this before publish.

## Security

- Never commit tokens. Use env vars or MCP config `env` blocks locally.
- Rotate tokens at [Slack API Apps](https://api.slack.com/apps) if exposed.
- See `SECURITY.md` for disclosure policy.
