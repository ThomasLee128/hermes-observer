# Private Integrations

Hermes Observer is open source, but real local agents often need private adapters, deployment guidance, and safety review.

For private Hermes / agent observability integrations, open an issue or contact the maintainer.

中文：如果你需要为自己的 Hermes 或 AI Agent 做私有化状态观测集成，可以提交 issue 或联系维护者。

## Good Private Integration Work

- map private cron/task state into the Observer config
- add safe readers for private JSON manifests or queue files
- design read-only status summaries for business-specific workflows
- connect status summaries to Feishu, DingTalk, Slack, email, or a local dashboard
- review the repo before a public or internal release
- package Observer for a team environment

## Hermes Observer Pro Direction

The open-source CLI should stay small, portable, and read-only. A hosted or private Pro layer could add:

- multi-agent dashboard
- task timeline and run history
- failure reason clustering
- notification routing
- team-level role separation
- private module marketplace
- audit logs for status checks
- MCP registry packaging and client presets

## Lead Capture

Open a private integration inquiry:

```text
https://github.com/ThomasLee128/hermes-observer/issues/new?template=private-integration.yml
```

Do not paste secrets, private logs, cookies, chat IDs, customer records, or transcript content into public issues.

## Sponsorship

If the open-source CLI is useful on its own, use the GitHub Sponsor button. Sponsorship helps keep the core observer small, safe, and maintained while private integrations fund workflow-specific adapters and Pro experiments.
