# Risk Review

This repository is a sanitized extraction of a local Hermes Observer prototype.

## Checked Risks

- No hardcoded user chat IDs
- No API tokens
- No cookies
- No `.env` contents
- No personal account holdings data
- No private transcript content
- No local business absolute paths in default runtime logic
- Example paths use placeholders or generic sample names

## Read-Only Boundary

Observer should not:

- start jobs
- stop jobs
- restart jobs
- download content
- transcribe audio
- send files
- mutate business queues

Observer may write only its own state directory:

- wake candidates
- wake patterns
- observer run records

## Upload Checklist

Before making a repository public:

- run `git grep -n "oc_[a-zA-Z0-9]"`
- run `git grep -n "DOUYIN_COOKIE\\|FEISHU_APP_SECRET\\|APP_SECRET\\|TOKEN\\|COOKIE"`
- run `git grep -n "D:\\\\Hermes-Home\\|D:\\\\hermes workshop"`
- inspect `observer.config.example.json`
- inspect git staged files with `git diff --cached`

## Known Limitations

- This is not a deep Hermes gateway router patch.
- It is a portable observer CLI plus integration guidance.
- Business-specific readers should be added as config-driven modules or private plugins.
