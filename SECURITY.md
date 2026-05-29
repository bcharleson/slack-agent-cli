# Security

## Reporting vulnerabilities

If you discover a security issue, please report it privately rather than opening a public GitHub issue.

## Secrets and credentials

Never commit Slack tokens or other credentials to this repository.

- Store tokens in environment variables (`SLACK_BOT_TOKEN`, `SLACK_USER_TOKEN`) or a local `.env` file.
- `.env` is gitignored. Use `.env.example` as a template only.
- Do not paste real tokens into README files, MCP client configs checked into git, or issue/PR comments.

If a token is accidentally committed or exposed, revoke it immediately in your [Slack app settings](https://api.slack.com/apps) and rotate to a new token.
