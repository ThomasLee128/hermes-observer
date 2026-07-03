# Hermes Observer

Hermes Observer is a read-only status layer for long-running Hermes Agent setups.

It helps a user ask natural questions such as:

- `现在咋样`
- `你在忙啥啊？`
- `跑完了吗`
- `这啥意思`
- `怎么没发我`
- `理论上现在不是应该在做某任务吗`

The observer replies with a short business-status summary instead of raw cron logs.

## Design Goals

- Read-only by default
- Low priority
- No task start/stop/restart
- No GPU competition
- No secrets in logs
- Configurable business modules
- Small wake-phrase learning layer with bounded candidates

## Quick Start

```powershell
python -m hermes_observer --config observer.config.example.json --message "现在咋样"
```

Classify a possible wake phrase:

```powershell
python -m hermes_observer --classify "你在忙啥啊？"
```

## Configuration

Copy `observer.config.example.json` and point it at your own Hermes paths.

Supported generic sources:

- Hermes cron jobs JSON
- GPU state via `nvidia-smi`
- JSON manifest files
- JSON queue files with `items[*].status`
- Optional user-message history JSONL for wake-phrase learning

## Wake Learning

Observer can learn candidate wake expressions from recent user messages, but it is deliberately bounded:

- look back window defaults to 60 minutes
- action words such as `改`, `修`, `停`, `重启`, `补发`, `继续`, `执行` are negative examples
- candidates are capped
- learned expressions are intent patterns, not arbitrary command execution

## Privacy

Do not commit your real config if it contains private paths, chat IDs, account names, or business-specific files.

Use the example config as a template.

## Hermes Integration

Add a Hermes skill or persona instruction that routes status-like questions to:

```powershell
python -m hermes_observer --config <your-config.json> --message "<user message>"
```

Keep action requests separate. Requests like `帮我修一下` or `补发今天内容` should not be routed to Observer.
