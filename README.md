# Weather Agent CLI

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.x-green)](https://python.langchain.com/)

A CLI weather agent powered by **DeepSeek LLM** + **LangChain** + **Hefeng (QWeather) API**. Ask about the weather in any city in natural language—the agent automatically decides when to call the weather tool and returns a formatted answer.

> Designed as a general-purpose CLI agent framework: **swap in any OpenAI-compatible LLM** (DeepSeek, OpenAI, Groq, etc.) by changing the config. The weather tool is just one example—add your own tools easily.

---

## Features

- Natural language weather queries: `"北京今天冷吗？"` / `"What's the weather in Tokyo?"`
- Multi-turn conversation with memory via LangChain AgentExecutor
- Configurable LLM backend (any OpenAI-compatible API)
- First-run guided setup, config stored at `~/.weather-cli/config.json`
- Extensible tool system—add your own `@tool` functions

---

## Installation

### Prerequisites

- Python 3.10+
- [和风天气 / QWeather](https://dev.qweather.com/) API key (free tier works)

### One-Command Install (Unix / Git Bash)

```bash
curl -fsSL https://raw.githubusercontent.com/realhenrylan/Weather-Agent-CLI/main/install.sh | bash
```

### Manual Install

```bash
# Install directly from GitHub via pip
pip install git+https://github.com/realhenrylan/Weather-Agent-CLI.git

# Or clone and install locally
git clone https://github.com/realhenrylan/Weather-Agent-CLI.git
cd Weather-Agent-CLI
pip install .
```

> Windows: use `pip install git+https://github.com/realhenrylan/Weather-Agent-CLI.git` in PowerShell (管理员) or use Git Bash for the one-command script.

### Configure

First run will prompt you for:

```
LLM API Key:         sk-xxx                          # DeepSeek / OpenAI key
LLM BASE URL:        https://api.deepseek.com/v1     # Base URL for your LLM
Model Name:          deepseek-chat                    # Model identifier

QWeather API Key:    your_qweather_key
QWeather API Host:   your_subdomain.re.qweatherapi.com
```

Or create `~/.weather-cli/config.json` manually:

```json
{
  "llm_api_key": "sk-xxx",
  "llm_base_url": "https://api.deepseek.com/v1",
  "llm_model": "deepseek-chat",
  "qweather_key": "your_qweather_key",
  "qweather_host": "your_subdomain.re.qweatherapi.com"
}
```

### Usage

```bash
weather-cli
```

Then type your query:

```
天气查询 Agent 已启动，输入 q 退出

想查天气、闲聊都可以哦：北京今天冷吗？
> 北京实时天气：天气多云，温度22°C，体感21°C，南风2级，湿度45%

想查天气、闲聊都可以哦：q
```

---

## Project Structure

```
Weather-Agent-CLI/
├── __init__.py           # Package marker
├── agent.py              # Main agent loop (LangChain AgentExecutor)
├── config.py             # Config load/save/setup
├── __main__.py           # Entry point: python -m weather_CLI
├── pyproject.toml        # Package definition & dependencies
└── .gitignore
```

---

## Extending the Agent

Add a new tool in `agent.py`:

```python
from langchain.tools import tool

@tool
def get_news(category: str) -> str:
    """获取指定分类的新闻摘要"""
    # Your API call here
    return f"今日{category}新闻：..."
```

Then add it to the `tools` list in `main()`:

```python
tools = [get_weather, get_news]
```

---

## License

MIT