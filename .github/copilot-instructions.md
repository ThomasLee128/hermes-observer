# GitHub Copilot Instructions

Hermes Observer is a small Python CLI for read-only observability of local AI agent workflows.

When editing this repository:

- Preserve the read-only boundary. Observer can read configured files, GPU status, cron metadata, queues, and JSON manifests, but should not trigger business jobs.
- Keep public examples sanitized. Never add real API keys, cookies, chat IDs, private paths, transcript content, or account data.
- Prefer generic config-driven modules over hard-coded private Hermes paths.
- Validate changes with:

```powershell
python -m hermes_observer --classify "What are you doing right now?"
python -m hermes_observer --classify "Fix the transcription worker"
python -m hermes_observer --config observer.config.example.json --json --no-learn
```

Core files:

- `hermes_observer/cli.py` for CLI behavior
- `hermes_observer/mcp_server.py` for experimental MCP tool serving
- `hermes_observer/observer.py` for status readers and report generation
- `hermes_observer/wake.py` for natural-language intent classification
- `observer.config.example.json` for safe sample config
- `docs/RISK_REVIEW.md` for privacy checks

The public positioning is: "a read-only status interpreter for long-running local AI agents."
