from pathlib import Path
import json

# 定义配置目录和配置文件路径
CONFIG_DIR = Path.home() / ".weather-cli"  # Path.home()可以获取用户主目录
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config():
    """读取配置文件，如果文件不存在则返回None"""
    # 先判断配置文件是否存在
    if CONFIG_PATH.exists():  # exists()返回True或False
        with open(
            CONFIG_PATH, "r", encoding="utf-8"
        ) as f:  # open()打开文件，把json转换成字典
            return json.load(f)
    else:
        return None  # 文件不存在


def save_config(llm_key, llm_url, llm_model, qw_key, qw_host):
    """保存配置到 ~/ .weather-cli/config.json"""
    # 首先确保目录存在，如果目录不存在就创建
    # parents = True 表示如果上级目录也不存在，就一并创建
    # exist_ok = True 表示如果目录已存在，就不报错
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 构造字典来保存数据
    config = {
        "llm_api_key": llm_key,
        "llm_base_url": llm_url,
        "llm_model": llm_model,
        "qweather_key": qw_key,
        "qweather_host": qw_host,
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        # json.dump()把字典转换成JSON写入文件
        # indent = 2 让JSON格式化，方便用户自己查看和修改

    print(f"配置已保存至{CONFIG_PATH}")


def setup_config():
    """首次运行引导："""
    print("=" * 50)
    print("首次使用，请配置以下信息")
    print("=" * 50)

    # LLM配置
    llm_key = input("LLM API Key：").strip()
    llm_url = input("LLM BASE URL：").strip()
    llm_model = input("模型名称（如 deepseek-chat）：").strip()

    print("-" * 50)
    print("和风天气API配置")
    print("请参考 https://dev.qweather.com")
    print("-" * 50)

    qw_key = input("和风天气 API KEY：").strip()
    qw_host = input("和风天气 API HOST：").strip()

    # 保存
    save_config(llm_key, llm_url, llm_model, qw_key, qw_host)

    # 返回保存之后的配置
    return load_config()
