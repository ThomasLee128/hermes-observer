# AI Quickstart

Hermes Observer helps a local AI agent explain its own background activity without changing that activity.

Use it when a user asks:

- "What are you doing right now?"
- "Did the task finish?"
- "Why did nothing get sent?"
- "Is the queue empty because everything is done, or because the job failed?"

## Install

```powershell
git clone https://github.com/ThomasLee128/hermes-observer.git
cd hermes-observer
pip install -e .
```

## First Run

```powershell
python -m hermes_observer --config observer.config.example.json --message "What are you doing right now?"
```

For machine-readable output:

```powershell
python -m hermes_observer --config observer.config.example.json --json --no-learn
```

## Intent Classification

Use the classifier before deciding whether a natural-language message should trigger Observer:

```powershell
python -m hermes_observer --classify "What are you doing right now?"
python -m hermes_observer --classify "Fix the transcription task"
```

Status/progress/explanation messages should return `is_observer: true`.
Action/modify messages should return `is_observer: false`.

## Configure Real Sources

Copy the example:

```powershell
Copy-Item observer.config.example.json observer.config.json
```

The public example points only at synthetic files under `examples/`. For a real local integration, copy the config and set:

- an environment alias for your local Hermes runtime state
- `state_dir`: where Observer can write its own small state files
- `cron.jobs_path`: JSON file containing scheduled job state
- `json_manifests`: business status JSON files and fields to summarize
- `queues`: JSON queue files to summarize
- `wake_learning.history_jsonl`: optional recent message history for wake phrase learning

Do not commit `observer.config.json` if it contains private paths or IDs.

## Safe Integration Pattern

1. Classify the user's message.
2. If it is observer intent, run Hermes Observer.
3. Show the short report.
4. Do not start, stop, retry, resend, or mutate jobs unless the user separately asks for an action.

## MCP Tool Use

If your AI client supports MCP, use:

```powershell
python -m hermes_observer.mcp_server --config observer.config.example.json
```

See `docs/MCP_SERVER.md` for a full stdio client config and manual smoke test.

## Private Integrations

For private Hermes / agent observability integrations, open an issue or contact the maintainer.

中文：如果你需要为自己的 Hermes 或 AI Agent 做私有化状态观测集成，可以提交 issue 或联系维护者。

## Privacy Checklist

Before publishing a derived project:

```powershell
git grep -n "DOUYIN_COOKIE\\|FEISHU_APP_SECRET\\|APP_SECRET\\|TOKEN\\|COOKIE"
git grep -n "D:\\\\Hermes-Home\\|D:\\\\hermes workshop"
```

Also review:

- `observer.config.example.json`
- `docs/RISK_REVIEW.md`
- staged files with `git diff --cached`
