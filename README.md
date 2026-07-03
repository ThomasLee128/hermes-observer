# Hermes Observer

## Project Background

As AI agents move from chat windows into long-running personal workflows, a new problem appears: users no longer only ask whether an agent can do something. They also need to know what the agent is doing right now.

When an assistant starts handling scheduled jobs, queues, file sync, transcription, knowledge-base exports, data refreshes, and message delivery, it becomes a small background system. Without a readable status layer, that system quickly turns into a black box.

Hermes Observer adds a read-only observer layer for Hermes Agent.

It answers natural questions such as:

- `现在咋样`
- `你在忙啥啊？`
- `跑完了吗`
- `在干嘛`
- `这啥意思`
- `怎么没发我`
- `理论上现在不是应该在做某任务吗`

Instead of dumping raw logs, Observer reads configured status sources and returns a short business-level explanation.

## Project Overview

Hermes Observer is a lightweight, read-only status interpreter for Hermes Agent setups.

It can read:

- cron job state
- GPU status
- JSON manifest files
- JSON queue files
- optional recent user-message history for wake-phrase learning

It is designed for users who run Hermes as a persistent local assistant and want to ask, in natural language:

> What is my assistant doing, and does anything need my attention?

## Core Ideas

### 1. Read-only by default

Observer should not start jobs, stop jobs, restart jobs, download content, transcribe audio, or send files.

It only answers:

> What is happening right now?

### 2. Low priority

Status checks should not interrupt the main task.

If a background job is already running, Observer only reads logs, queues, manifests, process state, and resource usage.

### 3. Business status, not raw metrics

A normal monitor might say:

```text
job status: ok
```

Observer aims to say:

```text
The backlog transcription worker is running.
The daily content queue is empty, which is normal.
Two recent items failed because their media files had no audio track.
No user action is needed right now.
```

### 4. Natural wake phrases

Users should not need to memorize a command.

Observer can classify phrases like:

- `你在忙啥啊？`
- `这个任务跑完了吗？`
- `这啥意思？`
- `怎么没发我？`

It also avoids misclassifying action requests. For example:

- `帮我修一下转写任务`
- `补发今天的内容`

These should remain normal execution requests, not read-only Observer requests.

## Features

- Natural-language status intent detection
- Read-only status summaries
- cron job status reading
- GPU status reading through `nvidia-smi`
- JSON manifest summaries
- JSON queue summaries
- bounded wake-phrase candidate learning
- configurable business modules
- Chinese-friendly output

## Quick Start

Install locally:

```powershell
git clone https://github.com/ThomasLee128/hermes-observer.git
cd hermes-observer
pip install -e .
```

Run Observer:

```powershell
python -m hermes_observer --config observer.config.example.json --message "现在咋样"
```

Classify a possible wake phrase:

```powershell
python -m hermes_observer --classify "你在忙啥啊？"
```

Expected result:

```json
{
  "is_observer": true,
  "confidence": 0.69,
  "reason": "在忙啥、忙啥"
}
```

Action requests should not trigger Observer:

```powershell
python -m hermes_observer --classify "帮我修一下转写任务"
```

Expected result:

```json
{
  "is_observer": false,
  "confidence": 0.05,
  "reason": "包含执行/修改类词"
}
```

## Configuration

Copy the example config:

```powershell
Copy-Item observer.config.example.json observer.config.json
```

Then edit `observer.config.json` to point at your own Hermes paths.

Example:

```json
{
  "env": {
    "HERMES_HOME": "%USERPROFILE%/.hermes",
    "WORKSPACE_HOME": "./examples/workspace"
  },
  "state_dir": "${HERMES_HOME}/data/hermes_observer",
  "gpu": {
    "enabled": true,
    "idle_util_pct": 20,
    "idle_memory_mb": 2500
  },
  "cron": {
    "jobs_path": "${HERMES_HOME}/cron/jobs.json"
  },
  "wake_learning": {
    "lookback_minutes": 60,
    "max_candidates": 30,
    "history_jsonl": ""
  },
  "json_manifests": [
    {
      "label": "Backlog transcription",
      "path": "${WORKSPACE_HOME}/transcripts/archive_manifest.json",
      "fields": ["completed", "failed", "pending", "updatedAt"]
    }
  ],
  "queues": [
    {
      "label": "Daily content queue",
      "path": "${HERMES_HOME}/data/daily_content_queue.json"
    }
  ]
}
```

## Output Example

```text
Hermes 当前状态

结论：
- Observer 已完成只读检查；如有业务模块配置，会按模块解释状态。

资源：
- GPU 15%，显存 10496/12288MB，当前不算空闲

业务进展：
- Backlog transcription：completed 15，failed 35，pending 3192
- Daily content queue：队列为空

Cron：
- 最近没有需要立即处理的 cron 失败

下一步：
- 近期计划：文件同步 06:30；知识库导出 07:50
```

## Wake Learning

Observer supports bounded wake-phrase candidate learning.

Design rules:

- only learn from recent user messages
- default lookback window is 60 minutes
- learn status/progress/explanation intent, not arbitrary commands
- cap candidate count
- keep action requests separate

Negative action words include:

```text
改、修、删、停、重启、补发、继续、跑一遍、执行、安装、清理、迁移
```

## Project Structure

```text
hermes-observer/
├── hermes_observer/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── observer.py
│   └── wake.py
├── docs/
│   └── RISK_REVIEW.md
├── observer.config.example.json
├── README.md
├── pyproject.toml
└── LICENSE
```

## Privacy and Safety

Do not commit your real config if it contains private paths, chat IDs, account names, or business-specific files.

Observer should not read or commit:

- API keys
- cookies
- tokens
- `.env` files
- private chat IDs
- private transcript content
- personal business data

Before publishing a derived repository, review:

```text
docs/RISK_REVIEW.md
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
