# Agent Instructions

This repository contains Hermes Observer, a read-only status interpreter for long-running local AI agent workflows.

## Project Goal

Help users answer: "What is my agent doing right now?"

Observer should summarize configured status sources such as cron jobs, queues, JSON manifests, GPU status, and optional message history. It must not start, stop, restart, download, transcribe, send, or mutate the user's business workflow.

## Important Files

- `hermes_observer/cli.py`: CLI entry point
- `hermes_observer/mcp_server.py`: experimental stdio MCP server
- `hermes_observer/observer.py`: reads configured state sources and builds reports
- `hermes_observer/wake.py`: classifies natural-language status intent
- `observer.config.example.json`: safe public example config
- `docs/MCP_SERVER.md`: MCP client setup and smoke tests
- `docs/PRIVATE_INTEGRATIONS.md`: private integration and Pro direction
- `docs/RISK_REVIEW.md`: privacy and release checklist
- `docs/AI_QUICKSTART.md`: concise user and agent quickstart

## Setup

```powershell
pip install -e .
```

## Smoke Checks

```powershell
python -m hermes_observer --classify "What are you doing right now?"
python -m hermes_observer --classify "Fix the transcription worker"
python -m hermes_observer --config observer.config.example.json --json --no-learn
```

Expected behavior:

- status/progress questions classify as observer intent
- action/modify requests do not classify as observer intent
- the example config runs without private local files
- the MCP server responds to `initialize`, `tools/list`, and `tools/call`

## Safety Rules

- Do not commit real `.env` files, cookies, tokens, chat IDs, private transcript content, or local business data.
- Do not hard-code private local paths in default runtime logic or examples.
- Keep Observer read-only except for its own state directory: wake candidates, wake patterns, and observer run records.
- Prefer config-driven readers over business-specific hard-coded integrations.
- If adding examples, use synthetic data only.

## Style

- Keep the public README and examples understandable to both humans and AI coding agents.
- Use concise status-oriented wording.
- Avoid exposing raw logs when a business-level explanation would be safer.
