# Rich CLI Frontend Implementation Plan

**Goal:** Add a Rich-powered terminal UI to the Weather Agent CLI per design spec.

**Architecture:** New `ui.py` with all Rich components (Scanner, Panels, StatusBar, Banner, Input). `agent.py` refactored to call `ui.*` instead of `print`/`input`, gains `--debug`. `pyproject.toml` adds `rich>=13.0`.

**Tech Stack:** Python 3.12+, Rich ≥13.0, threading for scanner, LangChain callbacks for tool detection.

---

### Task 1: Add `rich` to pyproject.toml

**File:** `pyproject.toml`

- [ ] **Add rich dependency**

```toml
dependencies = [
    "requests",
    "python-dotenv",
    "rich>=13.0",
    "langchain>=0.3,<0.4",
    "langchain-openai>=0.3,<0.4",
    "langchain-core>=0.3,<0.4",
]
```

---

### Task 2: Create `weather_CLI/ui.py`

**File:** `weather_CLI/ui.py` (new, ~140 lines)

Components:
- `BLUE`, `LIGHT_BLUE`, `RED`, `WHITE`, `GRAY`, `DARK`, `DARKER` color constants
- `console = Console(highlight=False)`
- `Scanner` — Knight Rider bar (⬝⬝■⬝⬝⬝), daemon-thread-driven, exposes `start()`, `stop()`, `render()` → str, `__rich__()`
- `print_banner(config)` — startup Panel with model name from `config["llm_model"]`
- `ask_input()` → `Prompt.ask()` with blue ❯ prefix
- `make_tool_call_line(name, args, scanner, elapsed)` — builds the tool-call Panel with scanner
- `weather_panel(data_text)` — parses weather data into dual-column layout, blue border
- `llm_panel(text)` — blue-bordered Panel with 💬 title
- `error_panel(detail)` — red-bordered Panel with ✗ title
- `print_summary(elapsed)` — gray footnote line
- `print_separator()` — divider line
- `status_bar(config, scanner, status, tokens)` — bottom bar with model, status tag, scanner, version, time
- `UISyncHandler(BaseCallbackHandler)` — captures tool name + args via `on_tool_start`
- `process_with_live(config, executor, input_data, callback_handler)` — runs executor in daemon thread, shows Live display (tool call + status bar), returns (result, elapsed)

Key design decisions:
- `Live(vertical_overflow="visible")` without `transient` — the processing display stays visible after completion
- Agent executor runs in daemon thread with `return_intermediate_steps=True`
- Scanner runs in its own daemon thread, shared between tool call line and status bar
- `UISyncHandler` callback is attached for ALL (not just tool starts) handlers to detect tool name at call time

---

### Task 3: Refactor `weather_CLI/agent.py`

**File:** `agent.py`

- [ ] **Add `--debug` argument** via `argparse`
- [ ] **Import** all ui functions: `from ui import console, print_banner, ask_input, process_with_live, weather_panel, llm_panel, error_panel, print_summary, print_separator, UISyncHandler`
- [ ] **Replace** `print("天气查询 Agent 已启动...")` with `print_banner(config)`
- [ ] **Replace** `input("\n想查天气、闲聊都可以哦：")` with `query = ask_input()`
- [ ] **Replace** `executor.invoke()` with `handler = UISyncHandler(); result, elapsed = process_with_live(config, executor, {"input": query}, handler)`
- [ ] **Route output**: if "实时天气" in `result["output"]` → `console.print(weather_panel(...))`, else if error → `console.print(error_panel(...))`, else → `console.print(llm_panel(...))`
- [ ] **Add** `print_summary(elapsed)`, `print_separator()`
- [ ] **Replace** exit with `console.print_goodbye()`
- [ ] **Pass** `verbose=debug` to `AgentExecutor`

---

### Task 4: Verify

- [ ] **Install rich**: `pip install rich`
- [ ] **Run without --debug**: `python agent.py`
- [ ] **Run with --debug**: `python agent.py --debug`
- [ ] **Run via installed command**: `weather-cli` (if already installed)
