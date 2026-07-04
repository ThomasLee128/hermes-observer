# Hermes Observer

Hermes Observer is a read-only status interpreter for long-running local AI agents. It turns cron jobs, queues, JSON manifests, GPU state, and optional message history into a short human-readable progress report.

If you already run a local AI agent, you can give it this prompt:

```text
Install https://github.com/ThomasLee128/hermes-observer and help me configure it to explain what my local agent is doing, without starting, stopping, or mutating any jobs.
```

## Why It Exists

As AI agents become persistent background systems, users need a quick answer to a simple question:

> What is my agent doing right now?

Hermes Observer adds an observability layer for that moment. It does not run the main workflow. It reads status signals and explains them in plain language.

中文一句话：Hermes Observer 是一个给长期运行的本地 AI Agent 使用的只读状态观察器，用来把日志、队列、cron、GPU 和业务状态整理成“现在在干什么”的简短说明。

## Good Fit

- Local-first AI agents and personal automation systems
- Long-running transcription, sync, export, delivery, or queue workers
- Workflows where users ask natural questions like `What are you doing right now?`
- Teams that want status summaries without exposing raw logs or private payloads

## Core Boundaries

- Read-only by default
- Low priority, so status checks do not interrupt main jobs
- Business-level summaries instead of raw metrics
- Natural wake phrase classification for status/progress/explanation questions
- No API keys, cookies, chat IDs, private transcript text, or real business data in the public repo

## Quick Start

```powershell
git clone https://github.com/ThomasLee128/hermes-observer.git
cd hermes-observer
pip install -e .
```

Run a status report with the example config:

```powershell
python -m hermes_observer --config observer.config.example.json --message "What are you doing right now?"
```

Classify whether a message should trigger Observer:

```powershell
python -m hermes_observer --classify "What are you doing right now?"
python -m hermes_observer --classify "Fix the transcription worker"
```

Emit JSON for another agent or dashboard:

```powershell
python -m hermes_observer --config observer.config.example.json --json --no-learn
```

## Example Output

```text
Hermes Status

Conclusion:
- Observer completed a read-only check. Configured business modules are summarized below.

Resources:
- GPU status not available

Business progress:
- Example backlog transcription: completed 15, failed 1, pending 3, updatedAt 2026-07-05T08:00:00+08:00
- Example daily queue: done 1, pending 2

Cron:
- No recent cron failure needs attention

Next:
- Upcoming: Example file sync 2026-07-05T06:30:00+08:00; Example daily recap 2026-07-05T08:00:00+08:00
```

## Configuration

Copy the sample config and point it at your own status files:

```powershell
Copy-Item observer.config.example.json observer.config.json
```

The public example uses generic placeholders:

```json
{
  "env": {
    "OBSERVER_EXAMPLE_HOME": "./examples/demo-hermes",
    "OBSERVER_EXAMPLE_WORKSPACE": "./examples/workspace"
  },
  "state_dir": "${OBSERVER_EXAMPLE_HOME}/state/hermes_observer",
  "gpu": {
    "enabled": true,
    "idle_util_pct": 20,
    "idle_memory_mb": 2500
  },
  "cron": {
    "jobs_path": "${OBSERVER_EXAMPLE_HOME}/cron/jobs.json"
  },
  "wake_learning": {
    "lookback_minutes": 60,
    "max_candidates": 30,
    "history_jsonl": ""
  },
  "json_manifests": [
    {
      "label": "Example backlog transcription",
      "path": "${OBSERVER_EXAMPLE_WORKSPACE}/example_transcripts/archive_manifest.json",
      "fields": ["completed", "failed", "pending", "updatedAt"]
    }
  ],
  "queues": [
    {
      "label": "Example daily queue",
      "path": "${OBSERVER_EXAMPLE_HOME}/fixtures/example_daily_queue.json"
    }
  ]
}
```

Do not commit your real `observer.config.json` if it contains private paths, chat IDs, account names, or business-specific files.

## AI-Friendly Entry Points

- [AGENTS.md](AGENTS.md): instructions for coding agents working in this repo
- [.github/copilot-instructions.md](.github/copilot-instructions.md): GitHub Copilot repository instructions
- [docs/AI_QUICKSTART.md](docs/AI_QUICKSTART.md): short guide for AI assistants and automation users
- [llms.txt](llms.txt): compact map of the most important docs and commands
- [docs/RISK_REVIEW.md](docs/RISK_REVIEW.md): privacy and release checklist

## Architecture

```text
hermes-observer/
|-- hermes_observer/
|   |-- __main__.py
|   |-- cli.py
|   |-- observer.py
|   `-- wake.py
|-- docs/
|   |-- AI_QUICKSTART.md
|   `-- RISK_REVIEW.md
|-- observer.config.example.json
|-- AGENTS.md
|-- llms.txt
|-- pyproject.toml
`-- README.md
```

`observer.py` reads configured state sources and builds the report. `wake.py` classifies natural-language status intent. `cli.py` exposes both paths through `python -m hermes_observer`.

## Development

Install locally:

```powershell
pip install -e .
```

Smoke checks:

```powershell
python -m hermes_observer --classify "What are you doing right now?"
python -m hermes_observer --config observer.config.example.json --json --no-learn
```

Privacy checks before release:

```powershell
git grep -n "DOUYIN_COOKIE\\|FEISHU_APP_SECRET\\|APP_SECRET\\|TOKEN\\|COOKIE"
git grep -n "D:\\\\Hermes-Home\\|D:\\\\hermes workshop"
```

## Roadmap

- Hermes plugin packaging
- richer business module adapters
- local web dashboard
- task timeline
- failure reason clustering
- daily work recap

## License

MIT License
