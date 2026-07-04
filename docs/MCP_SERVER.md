# MCP Server

Hermes Observer includes an experimental stdio MCP server so AI clients can call Observer as a tool.

The server currently exposes two tools:

- `hermes_observer_report`: run a read-only status check and return a report
- `hermes_observer_classify`: classify whether a user message is a read-only status/progress request

## Run Locally

```powershell
python -m hermes_observer.mcp_server --config observer.config.example.json
```

After installing the package, the script entry point is also available:

```powershell
hermes-observer-mcp --config observer.config.example.json
```

## Example Client Configuration

Use this shape in an MCP-capable client that supports stdio servers:

```json
{
  "mcpServers": {
    "hermes-observer": {
      "command": "python",
      "args": [
        "-m",
        "hermes_observer.mcp_server",
        "--config",
        "observer.config.example.json"
      ]
    }
  }
}
```

## Manual Smoke Test

```powershell
@'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"manual","version":"0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"hermes_observer_classify","arguments":{"text":"What are you doing right now?"}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"hermes_observer_report","arguments":{"learn":false}}}
'@ | python -m hermes_observer.mcp_server --config observer.config.example.json
```

## Safety Boundary

The MCP server inherits Observer's read-only posture. The report tool reads configured state sources and may write only Observer's own learning/run state when `learn` is explicitly set to `true`.

Keep `learn` set to `false` for AI clients unless you intentionally want wake-phrase learning state.
