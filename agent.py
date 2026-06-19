import sys
import io
import argparse
import warnings

# 确保 stdout 使用 UTF-8 编码（Windows 需要，Linux/macOS 已默认 UTF-8）
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace",
        line_buffering=True,
    )

import requests
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core._api import LangChainDeprecationWarning
from langchain_openai import ChatOpenAI

from config import load_config, setup_config
from ui import (
    console,
    make_error_panel,
    make_llm_panel,
    make_weather_panel,
    print_banner,
    print_goodbye,
    print_separator,
    print_summary,
    process_with_live,
    ask_input,
)


_config = None


@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气"""
    global _config
    qw_key = _config["qweather_key"]
    qw_host = _config["qweather_host"]
    CITY_URL = f"https://{qw_host}/geo/v2/city/lookup"
    WEATHER_URL = f"https://{qw_host}/v7/weather/now"

    params = {"location": city, "key": qw_key}
    resp = requests.get(CITY_URL, params=params, timeout=10)
    data = resp.json()
    city_list = data.get("location", [])
    if not city_list:
        return f"找不到城市：{city}"
    city_id = city_list[0]["id"]
    city_name = city_list[0]["name"]

    headers = {"X-QW-Api-Key": qw_key}
    resp_w = requests.get(
        WEATHER_URL, params={"location": city_id}, headers=headers, timeout=10
    )
    w = resp_w.json()
    if w.get("code") != "200":
        return f"查询{city_name}天气失败"
    now = w["now"]
    return f"{city_name}实时天气：天气{now['text']}，温度{now['temp']}°C，体感{now['feelsLike']}°C，{now['windDir']}{now['windScale']}级，湿度{now['humidity']}%"


def main():
    global _config

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="显示 LangChain 详细日志")
    args = parser.parse_args()

    config = load_config()
    if config is None:
        config = setup_config()
        _config = config
    else:
        _config = config

    llm_key = config["llm_api_key"]
    llm_url = config["llm_base_url"]
    llm_model = config["llm_model"]

    llm = ChatOpenAI(
        model=llm_model,
        temperature=0,
        openai_api_key=llm_key,
        openai_api_base=llm_url,
    )

    tools = [get_weather]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个智能天气助手，可以查询任意城市的实时天气。当用户询问天气时，使用 get_weather 工具查询。如果是非天气相关的闲聊，直接回答。",
            ),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    # 记忆系统：让 agent 记住对话历史（查过的城市、用户姓名等）
    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=args.debug,
        max_iterations=5,
        return_intermediate_steps=True,
    )

    print_banner(config)

    while True:
        try:
            query = ask_input()
        except (KeyboardInterrupt, EOFError):
            break

        if query.lower() in ("q", "exit", "quit"):
            break

        output, error, elapsed = process_with_live(console, config, executor, query)

        if error:
            console.print(make_error_panel(error))
        elif output and "实时天气" in output:
            panel = make_weather_panel(output)
            if panel:
                console.print(panel)
            else:
                console.print(make_llm_panel(output))
        elif output:
            console.print(make_llm_panel(output))
        else:
            console.print(make_error_panel("无返回结果"))

        print_summary(elapsed)
        print_separator()

    print_goodbye()


if __name__ == "__main__":
    main()
