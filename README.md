# 6to9 for coding agents

Your coding agent, working in your product's repo, can ask [6to9](https://6to9.ai) what strong competitors do before it builds your landing page, signup, onboarding, pricing page or core flows. It gets ranked recommendations grounded in 6to9's competitor research for your product, and build-ready specs: the same prompt and references you pick in the 6to9 portal.

You need a 6to9 account with your product added, and an API key from **https://product.6to9.ai/settings/api-keys**.

Everything connects to one hosted MCP server: `https://mcp.6to9.ai/mcp` (streamable HTTP, `Authorization: Bearer <your key>`).

## Claude Code

```
/plugin marketplace add 6to9-ai/6to9-plugin
/plugin install 6to9@6to9
```

Claude Code asks for your 6to9 API key when the plugin is enabled. The key is stored in your system keychain, not in a settings file. Restart Claude Code and check that `6to9` shows as connected in `/mcp`.

From a shell instead: `claude plugin marketplace add 6to9-ai/6to9-plugin` then `claude plugin install 6to9@6to9`.

The plugin adds a `6to9` skill that tells Claude when to consult 6to9 and how, plus the MCP server.

Updates: turn on auto-update in `/plugin` → Marketplaces → 6to9 (off by default for third-party marketplaces), or update manually with `/plugin marketplace update 6to9`, `claude plugin update 6to9@6to9`, then `/reload-plugins`.

## Cursor

1. Add the server to `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project). Copy [`clients/cursor/mcp.json`](clients/cursor/mcp.json):

   ```json
   {
     "mcpServers": {
       "6to9": {
         "url": "https://mcp.6to9.ai/mcp",
         "headers": { "Authorization": "Bearer ${env:SIXTO9_API_KEY}" }
       }
     }
   }
   ```

   and set `SIXTO9_API_KEY` in the environment Cursor starts from. If Cursor shows the server but every call says the key was rejected, your Cursor build is sending the `${env:...}` text literally (reported for remote servers on the Cursor forum). Put the key itself in `~/.cursor/mcp.json` instead. Never put a literal key in a project's `.cursor/mcp.json`: that file is usually committed.
2. Copy [`clients/cursor/6to9.mdc`](clients/cursor/6to9.mdc) to `.cursor/rules/6to9.mdc` in your repo. It is an "Apply Intelligently" rule: Cursor's agent pulls it in when a task matches its description.

## Codex

1. Add to `~/.codex/config.toml` (see [`clients/codex/config.toml`](clients/codex/config.toml)):

   ```toml
   [mcp_servers.sixto9]
   url = "https://mcp.6to9.ai/mcp"
   bearer_token_env_var = "SIXTO9_API_KEY"
   ```

   or run `codex mcp add sixto9 --url https://mcp.6to9.ai/mcp --bearer-token-env-var SIXTO9_API_KEY`, and export `SIXTO9_API_KEY`.
2. Paste [`clients/codex/AGENTS.snippet.md`](clients/codex/AGENTS.snippet.md) into your repo's `AGENTS.md` (or `~/.codex/AGENTS.md`). To update it later, replace everything between `<!-- 6to9:start -->` and `<!-- 6to9:end -->`.

## Any other MCP client

Connect to `https://mcp.6to9.ai/mcp` over streamable HTTP with the header `Authorization: Bearer <your key>`. The server's own instructions tell the agent when to use it.

## Try it

- "Our landing page gets visits but few signups. What do strong competitors do differently?"
- "What should we build next for onboarding?"
- "How do our competitors do their pricing pages?"

The first time, the agent asks which 6to9 product this repo is and saves the answer to `.6to9.json` at the repo root (commit it or ignore it). Your key's row at https://product.6to9.ai/settings/api-keys shows when it was last used.

## What your agent sends

Only what a tool call needs: your product id, the area you're working on, and optionally a one-line goal in your words. When you report back after shipping, that's `report_build_result`'s `metrics` (aggregate numbers, e.g. "signup rate +12% over 2 weeks") and `note` — never user-level data. The guidance tells agents to send aggregate numbers only everywhere (never user-level data, secrets or code), and every tool works without a goal or a build report.

## Tools

| Tool | Use it for |
|---|---|
| `list_my_products` | which 6to9 product this repo is (once per repo) |
| `recommend_features` | what to build or change, ranked, with why and which rivals back it |
| `get_build_spec` | the build-ready prompt for one item, as the portal's "Copy prompt" gives it |
| `get_mvp_brief` | the minimum to ship for one audience segment |
| `get_competitors` | who you're up against |
| `get_market_updates` | what changed in your market, plus the latest weekly brief |
| `mark_event` | mark a market event seen, dismissed or acted on |
| `report_build_result` | report what shipped and how it did |
| `start_research` | get a quote for new research (product, audience, feature or angle), then start it |
| `get_research_status` | check on research that's running in the background |

## Maintaining this repo

`guide/agent-guide.md` is the single source. `python scripts/generate.py` writes the Claude Code skill, the Cursor rule, the Codex block and `generated/server_instructions.md`; CI runs `python scripts/generate.py --check`. After changing the guide, copy `generated/server_instructions.md` into the MCP service's `mcp/server_instructions.md` and redeploy it, so every client hears the same thing.

Trigger evals: `cd plugins/6to9 && claude plugin eval .` (Claude Code v2.1.269 or later; mocked MCP answers, no key needed).

### Releasing

Installed plugins update only when the computed version changes — the `version` field in `plugins/6to9/.claude-plugin/plugin.json` wins. If plugin content changes but that field doesn't, users never receive it.

1. Edit `guide/agent-guide.md`.
2. Regenerate: `python scripts/generate.py`.
3. Bump `version` in `plugins/6to9/.claude-plugin/plugin.json` (semver).
4. Push and tag the release: `vX.Y.Z`.

CI (`.github/workflows/check.yml`) fails a PR or push that changes anything under `plugins/6to9/` (excluding `plugins/6to9/evals/`, which never ships) without bumping `version`.
