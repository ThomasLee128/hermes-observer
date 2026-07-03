# Hermes Observer

如果你已经有自己的 Hermes Agent，可以尝试把这个项目链接直接发给它：`github.com/ThomasLee128/hermes-observer，帮我安装这个`。

## 项目背景

作为一名拥有十年投资经验、最近投身 AI 创业的从业者，我一直在尝试把 AI 更深地放进自己的真实工作流里。

从 [llm-api-detector](https://github.com/ThomasLee128/llm-api-detector) 到 [Sprite-Illustra](https://github.com/ThomasLee128/Sprite-Illustra)，我逐渐意识到一个问题：AI 系统真正进入长期使用后，用户关心的不只是“它能不能做事”，而是“它此刻到底在做什么”。

我们同时运营着 GPU 分时租赁平台和 OpenAI 兼容 API 聚合服务。我一直认为，作为产品使用者去深度使用自己的产品，是发现真实问题、改进产品体验的最好方式。

在我自己的本地 Hermes Agent 使用过程中，随着定时任务、队列处理、文件同步、资料转写、知识库归档、数据刷新、消息投递等任务越来越多，Hermes 已经不再只是一个聊天机器人，而更像一个长期运行的个人后台系统。

这时新的问题出现了：

- 它现在在忙什么？
- 某个任务跑完了吗？
- 为什么没有发我结果？
- 这条 cron 提醒是什么意思？
- GPU 是不是被占用了？
- 队列为空是正常，还是任务没跑？
- 某个失败是否需要我介入？

如果用户只能从零散日志、cron 输出和消息提醒里猜答案，自动化系统会重新变成一个黑箱。

Hermes Observer 就是为了解决这个问题而做的：给 Hermes Agent 增加一个低优先级、只读、不打断主任务的“业务状态观察员”。

## 项目概述

Hermes Observer 是一个面向 Hermes Agent 的轻量只读状态解释器。

它允许用户用自然语言询问：

- `现在咋样`
- `你在忙啥啊？`
- `跑完了吗`
- `在干嘛`
- `这啥意思`
- `怎么没发我`
- `理论上现在不是应该在做某任务吗`

Observer 会读取配置好的 cron、队列、JSON 状态文件、GPU 状态和可选的用户消息历史，并生成一份简短、可读、面向业务语义的状态汇报，而不是直接把原始日志扔给用户。

## 核心理念

### 1. 默认只读

Observer 不应该启动任务、停止任务、重启任务、下载内容、执行转写或发送文件。

它只回答：

> 当前正在发生什么？

### 2. 低优先级

状态查询不应该打断正在运行的主任务。

如果后台任务正在运行，Observer 只读取日志、队列、状态文件、进程状态和资源占用。

### 3. 业务状态，而不是原始指标

普通监控可能只会说：

```text
job status: ok
```

Observer 更希望回答：

```text
资料转写队列正在运行。
每日内容队列为空，这是正常情况。
最近有 2 条内容失败，原因是媒体文件没有音轨。
当前不需要用户介入。
```

### 4. 自然唤醒

用户不需要记住固定命令。

Observer 可以识别这些口语化表达：

- `你在忙啥啊？`
- `这个任务跑完了吗？`
- `这啥意思？`
- `怎么没发我？`

同时它会避免把执行类请求误判为只读状态查询。例如：

- `帮我修一下转写任务`
- `补发今天的内容`

这些应该继续走普通任务执行流程，而不是 Observer。

## 功能

- 自然语言状态意图识别
- 只读业务状态汇报
- cron 任务状态读取
- GPU 状态读取（通过 `nvidia-smi`）
- JSON manifest 状态汇总
- JSON queue 队列状态汇总
- 有边界的唤醒词候选学习
- 可配置业务模块
- 中文友好的状态输出

## 快速开始

### 1. 安装

```powershell
git clone https://github.com/ThomasLee128/hermes-observer.git
cd hermes-observer
pip install -e .
```

### 2. 运行 Observer

```powershell
python -m hermes_observer --config observer.config.example.json --message "现在咋样"
```

### 3. 测试唤醒识别

```powershell
python -m hermes_observer --classify "你在忙啥啊？"
```

示例输出：

```json
{
  "is_observer": true,
  "confidence": 0.69,
  "reason": "在忙啥、忙啥"
}
```

执行类请求不会误触发：

```powershell
python -m hermes_observer --classify "帮我修一下转写任务"
```

示例输出：

```json
{
  "is_observer": false,
  "confidence": 0.05,
  "reason": "包含执行/修改类词"
}
```

## 配置示例

复制示例配置：

```powershell
Copy-Item observer.config.example.json observer.config.json
```

然后修改 `observer.config.json`，指向你自己的 Hermes 路径、队列文件和状态文件。

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

## 输出示例

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

## 唤醒词学习

Observer 支持轻量的唤醒词候选学习。

设计原则：

- 只学习近期用户表达
- 默认回看窗口为 60 分钟
- 学习状态、进度、异常解释类意图
- 不学习任意命令
- 候选数量有上限
- 执行类请求保持独立

负例词包括：

```text
改、修、删、停、重启、补发、继续、跑一遍、执行、安装、清理、迁移
```

## 项目结构

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

## 隐私与安全

不要提交包含私有路径、chat id、账号名或业务文件路径的真实配置。

Observer 不应该读取或提交：

- API Key
- Cookie
- Token
- `.env` 文件
- 私有 chat id
- 私有转写内容
- 个人业务数据

发布派生项目之前，请检查：

```text
docs/RISK_REVIEW.md
```

## 开发说明

本项目采用 vibecoding 模式开发，来源于我本地 Hermes Agent 的真实使用需求。

当 AI 助理从“聊天工具”变成“个人后台系统”后，最需要补上的不一定是更多自动化，而是一个可以随时回答“它在干嘛”的观察层。

后续可以继续扩展为：

- Hermes 插件
- 更丰富的业务模块适配器
- 本地网页任务驾驶舱
- 任务时间线
- 失败原因聚类
- 每日工作复盘

## 许可证

MIT License

---

# Hermes Observer

If you already run your own Hermes Agent, try sending this project link directly to it: `github.com/ThomasLee128/hermes-observer, help me install this`.

## Project Background

As a professional with ten years of investment experience who has recently ventured into AI entrepreneurship, I have been trying to embed AI more deeply into real daily workflows.

From [llm-api-detector](https://github.com/ThomasLee128/llm-api-detector) to [Sprite-Illustra](https://github.com/ThomasLee128/Sprite-Illustra), I gradually realized that once AI systems enter long-term use, users no longer only care whether an agent can do something. They also care what the agent is doing right now.

We operate both a GPU time-sharing rental platform and an OpenAI-compatible API aggregation service. I firmly believe that deeply using our own products as real users is one of the best ways to discover product problems and improve the experience.

In my own local Hermes Agent setup, as scheduled jobs, queues, file sync, transcription, knowledge-base exports, data refreshes, and message delivery tasks increased, Hermes became more than a chat assistant. It became a small personal background system.

That created a new set of questions:

- What is it doing right now?
- Did a task finish?
- Why did it not send me the result?
- What does this cron notification mean?
- Is the GPU occupied?
- Is an empty queue normal, or did the job fail to run?
- Does a failure need my attention?

If the user has to infer the answer from scattered logs, cron outputs, and message notifications, the automation system becomes a black box again.

Hermes Observer is built to solve this problem: it adds a low-priority, read-only business-status observer layer to Hermes Agent.

## Project Overview

Hermes Observer is a lightweight read-only status interpreter for Hermes Agent setups.

It lets users ask natural questions such as:

- `What are you doing right now?`
- `Are you busy?`
- `Did the task finish?`
- `Why did I get this cron message?`
- `Why did it not send me the result?`
- `Should it be running this task now?`

Observer reads configured cron state, queue files, JSON manifests, GPU status, and optional user-message history. It then returns a short business-level explanation instead of raw logs.

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

- `What are you doing right now?`
- `Did this task finish?`
- `What does this mean?`
- `Why did it not send me the result?`

It also avoids misclassifying action requests. For example:

- `Fix the transcription task`
- `Resend today's content`

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

### 1. Install

```powershell
git clone https://github.com/ThomasLee128/hermes-observer.git
cd hermes-observer
pip install -e .
```

### 2. Run Observer

```powershell
python -m hermes_observer --config observer.config.example.json --message "What are you doing right now?"
```

### 3. Test Wake Classification

```powershell
python -m hermes_observer --classify "What are you doing right now?"
```

Example output:

```json
{
  "is_observer": true,
  "confidence": 0.72,
  "reason": "what are you doing"
}
```

Action requests should not trigger Observer:

```powershell
python -m hermes_observer --classify "Fix the transcription task"
```

Example output:

```json
{
  "is_observer": false,
  "confidence": 0.05,
  "reason": "contains action/modify words"
}
```

## Configuration Example

Copy the example config:

```powershell
Copy-Item observer.config.example.json observer.config.json
```

Then edit `observer.config.json` to point at your own Hermes paths, queue files, and status files.

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
Hermes Status

Conclusion:
- Observer completed a read-only check. Configured business modules are summarized below.

Resources:
- GPU 15%, memory 10496/12288MB, currently not idle

Business progress:
- Backlog transcription: completed 15, failed 35, pending 3192
- Daily content queue: empty

Cron:
- No recent cron failures need immediate attention

Next:
- Upcoming: file sync 06:30; knowledge-base export 07:50
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
fix, modify, delete, stop, restart, resend, continue, run again, execute, install, clean, migrate
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

## Development Notes

This project was developed through a vibecoding workflow and comes from a real need that appeared after running a local Hermes Agent as a persistent personal background system.

When an AI assistant becomes more than a chat tool, one of the most important missing layers is not more automation, but a way to ask:

> What are you doing right now?

Future directions:

- Hermes plugin packaging
- richer business module adapters
- local web dashboard
- task timeline
- failure reason clustering
- daily work recap

## License

MIT License
