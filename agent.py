import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import load_config, setup_config

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
    resp = requests.get(CITY_URL, params=params, timeout = 10)
    data = resp.json()
    city_list = data.get("location", [])
    if not city_list:
        return f"找不到城市：{city}"
    city_id = city_list[0]["id"]
    city_name = city_list[0]["name"]

    headers = {"X-QW-Api-Key": qw_key}
    resp_w = requests.get(WEATHER_URL, params={"location": city_id}, headers=headers, timeout = 10)
    w = resp_w.json()
    if w.get("code") != "200":
        return f"查询{city_name}天气失败"
    now = w["now"]
    return f"{city_name}实时天气：天气{now['text']}，温度{now['temp']}°C，体感{now['feelsLike']}°C，{now['windDir']}{now['windScale']}级，湿度{now['humidity']}%"


def main():
    global _config

    #先加载配置，如果没有配置就首次引导
    config = load_config()
    if config is None:
        config = setup_config()
        _config = config   #赋值给全局变量，让@tool能够读到
    else:
        _config = config

    #从配置中读取各项值
    llm_key = config["llm_api_key"]
    llm_url = config["llm_base_url"]
    llm_model = config["llm_model"]
    qw_key = config["qweather_key"]
    qw_host = config["qweather_host"]

    llm = ChatOpenAI(
        model = llm_model,
        temperature = 0,
        openai_api_key = llm_key,
        openai_api_base = llm_url
    )

    tools = [get_weather]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个智能天气助手，可以查询任意城市的实时天气"),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)

    print("天气查询 Agent 已启动，输入 q 退出")
    while True:
        query = input("\n想查天气、闲聊都可以哦：")
        if query.lower() == "q":
            break
        result = executor.invoke({"input": query})
        print(f"\n{result['output']}")

if __name__ == "__main__":
    main()

