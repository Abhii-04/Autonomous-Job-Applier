# Browser Agent

Browser Agent is a local job-application assistant for Abhishek Yadav. It uses a
Deep Agents orchestrator, a Playwright MCP browser worker, and local knowledge
files to discover jobs, prepare applications, and stop when user approval or
private information is required.

## Runtime Shape

- `src/agent.py` builds the agent runtime.
- `src/prompt.py` defines the orchestrator, applier, and evaluator prompts.
- `skills/orchestrator/SKILL.md` defines coordination policy.
- `skills/search-jobs/SKILL.md` defines discovery and ranking policy.
- `skills/applier/SKILL.md` defines browser application policy.
- `skills/applier/references/Naukri.md` defines Naukri-specific behavior.
- `knowledge/` stores personal facts, resume, preferences, and application
  answers used by the agent.

## Tool Policy

The orchestrator can use the local `bash` tool and can delegate browser work to
the `applier` subagent. The applier receives the Playwright MCP tools that pass
the allowlist in `src/agent.py`.

The Playwright MCP server is launched with `--snapshot-mode=none` and
`--image-responses=omit`. The `browser_snapshot` tool is still exposed by the
server, but prompts and skills should use it sparingly and avoid depending on
image responses.

## Setup

```bash
uv sync
```

Required environment variables are loaded from `.env`. The current runtime
expects:

```text
DEEPSEEK_API_KEY
```

## Run

```bash
uv run python main.py
```

The default browser profile is stored in `./browser-profile`, so login state can
persist between runs.

## Verify

Run these checks after prompt, skill, or tool changes:

```bash
uv run python -m compileall src main.py
uv run python - <<'PY'
from src.agent import PLAYWRIGHT_ALLOWED_TOOLS
print(sorted(PLAYWRIGHT_ALLOWED_TOOLS))
PY
```

To verify MCP tool availability without invoking the model:

```bash
uv run python - <<'PY'
import asyncio
from src.tools.mcp import get_mcp_tools

async def main():
    async with get_mcp_tools() as tools:
        print(sorted(tool.name for tool in tools))

asyncio.run(main())
PY
```

## Safety Boundaries

- Do not fabricate user information.
- Stop for login, OTP, CAPTCHA, payment, identity verification, unknown required
  facts, or unauthorized final submission.
- Save generated reports only under `/reports/`.
- Keep browser application work inside the applier; keep local reporting and
  coordination inside the orchestrator.
