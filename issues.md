# Potential Performance Issues

This is a static review of the current Browser-Agent codebase. I did not run a full browser-agent benchmark, so the items below are potential bottlenecks to verify with timing logs.

## High Priority

### 1. MCP startup uses `npx -y @playwright/mcp@latest`

Evidence: `src/tools/mcp.py:9-13`

The Playwright MCP server is launched through `npx` and uses the floating `@latest` package tag. This can add startup latency because `npx` may check, resolve, download, or prepare the package before the agent can run. The floating version also makes performance inconsistent between runs.

Suggested fix:
- Pin the package version instead of `@latest`.
- Prefer a locally installed package/script entrypoint so startup does not depend on `npx` resolution.
- Add startup timing around `get_mcp_tools()` to confirm the impact.

### 2. All browser MCP tools are loaded before every runtime session

Evidence: `src/agent.py:71-76`, `src/tools/mcp.py:28-35`

`BrowserAgentRuntime.__aenter__()` always starts the Playwright MCP session and loads all MCP tools before the agent is available, even for simple local/report tasks. This makes the first response slow and couples every task to browser startup.

Suggested fix:
- Lazy-load browser tools only when a browser task is detected.
- Split local/report tools from browser tools.
- Keep a long-lived MCP session if the terminal app is expected to run multiple tasks.

### 3. Conversation summarization adds extra model calls during normal runs

Evidence: `src/agent.py:47-49`, `src/middleware/localcontext.py:94-143`

After the message count exceeds `keep_last=8`, `ConversationSummaryMiddleware.after_model()` calls `self.model.invoke(...)` to summarize old messages. That is an additional remote LLM call after model output. It is synchronous inside `after_model`, so each summarization can directly add user-visible latency.

Suggested fix:
- Instrument when summarization runs and how long it takes.
- Raise `keep_last` for short sessions, disable summaries for browser-only flows, or move summarization to a cheaper/faster model.
- Consider async summarization only when it is safe for the framework state model.

### 4. Orchestrator/subagent structure can double model planning

Evidence: `src/agent.py:38-67`, `src/prompt.py:4-18`

The orchestrator has the browser tools and also defines an `applier` subagent with the same browser tools. For application tasks, the orchestrator may first reason about routing, call the subagent, then validate the subagent result before replying. That adds at least one additional agent turn compared with a single browser-focused agent.

There is also a prompt mismatch: `src/prompt.py:6` says to route job search tasks to a `searcher` subagent, but only `applier` is configured in `src/agent.py:60-67`. This can cause wasted reasoning or failed routing attempts.

Suggested fix:
- Add a real `searcher` subagent or remove that routing instruction.
- For direct "apply this URL" tasks, consider bypassing orchestration and invoking the applier workflow directly.
- Give the orchestrator a smaller tool set than the applier so tool choice is simpler.

## Medium Priority

### 5. Browser profile is large

Evidence: local `browser-profile/` is about 299 MB.

The MCP server uses `--user-data-dir=./browser-profile` and `--shared-browser-context` in `src/tools/mcp.py:14-15`. A persistent profile is useful for login state, but a large profile can slow Chrome startup, page initialization, and cache/database access.

Suggested fix:
- Archive or clean unnecessary profile cache data while preserving login/session data.
- Consider separate profiles per site or task type.
- Measure Chrome/MCP startup before and after profile cleanup.

### 6. Browser snapshots are disabled and discouraged

Evidence: `src/tools/mcp.py:17`, `memory/AGENT.md:28`, `skills/orchestrator/SKILL.md:24`, `skills/applier/SKILL.md:28`, `skills/search-jobs/SKILL.md:38`

`--snapshot-mode=none` reduces response payload size, and the instructions repeatedly tell the agent not to call `browser_snapshot`. This can be faster for simple navigation, but it may also make page understanding slower if the agent has to use more granular browser actions to discover page state.

Suggested check:
- Compare task completion time with snapshots disabled versus using snapshots only at decision points.
- Keep the current restriction if snapshots are producing huge payloads, but measure it rather than assuming it is always faster.

### 7. Tool result summarization still allows large prompt growth

Evidence: `src/middleware/localcontext.py:50-51`, `src/middleware/localcontext.py:109-143`

Tool messages are truncated to 1000 characters only when building the summary prompt. The live conversation still keeps the last eight messages, which can include large tool outputs. Browser tool results can therefore inflate prompt size until summarization removes them.

Suggested fix:
- Lower `max_tool_chars` and/or reduce `keep_last` for browser-heavy flows.
- Add token/character logging per model call.
- Prefer concise tool outputs where possible.

## Low Priority / Cleanup

### 8. No timing instrumentation exists

Evidence: no timing/logging around `get_mcp_tools()`, `orchestrator(...)`, `agent.ainvoke(...)`, model calls, tool calls, or middleware summarization.

Without timing logs, it is hard to know whether slowness comes from MCP startup, browser actions, DeepSeek latency, prompt size, subagent delegation, or summarization.

Suggested fix:
- Add simple timing logs for:
  - MCP startup and `load_mcp_tools()`
  - agent construction
  - each `runtime.run(...)`
  - summarization calls
  - browser tool calls, if supported by middleware/hooks

### 9. Unused/broken code may confuse future changes

Evidence: `src/tools/evaluator.py` appears incomplete and has invalid access patterns such as `requests.state.get[...]`; `src/agent.py:8-9` imports unused symbols.

This is unlikely to be the direct runtime slowness unless imported into the agent later, but it increases maintenance risk and can lead to accidental middleware use.

Suggested fix:
- Remove or repair `src/tools/evaluator.py`.
- Remove unused imports from `src/agent.py`.

## Recommended Verification Plan

1. Add timing logs around MCP startup, agent construction, `agent.ainvoke`, and summarization.
2. Run the same browser task three times with the current config and record timings.
3. Pin/install Playwright MCP locally and repeat the same three runs.
4. Temporarily disable `ConversationSummaryMiddleware` and compare multi-turn task latency.
5. Compare a clean/smaller browser profile with the current 299 MB profile.
6. Decide whether to keep the orchestrator/subagent split based on measured overhead for common tasks.
