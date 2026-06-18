import re
import threading
import time

from langchain_core.callbacks import BaseCallbackHandler
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

BLUE = "#58a6ff"
LIGHT_BLUE = "#79c0ff"
RED = "#f85149"
WHITE = "#e6edf3"
GRAY = "#8b949e"
DARK = "#30363d"
DARKER = "#21262d"

console = Console(highlight=False)


class Scanner:
    def __init__(self, width=8, speed=0.1):
        self.width = width
        self.speed = speed
        self._pos = 0
        self._dir = 1
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._pos = 0
        self._dir = 1
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self):
        while self._running:
            self._pos += self._dir
            if self._pos >= self.width - 1 or self._pos <= 0:
                self._dir *= -1
            time.sleep(self.speed)

    def render(self):
        chars = ["⬝"] * self.width
        chars[self._pos] = "■"
        return "".join(chars)


class ToolCaptureHandler(BaseCallbackHandler):
    def __init__(self):
        self.tool_name = None
        self.tool_args = None

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.tool_name = serialized.get("name", "tool")
        if isinstance(input_str, dict):
            val = input_str.get("city") or next(iter(input_str.values()), "")
            self.tool_args = str(val)
        else:
            self.tool_args = str(input_str)


def print_banner(config):
    model_name = config.get("llm_model", "unknown")
    version = "1.0.0"
    panel = Panel(
        f"[bold {WHITE}]☀ Weather Agent CLI[/]\n"
        f"[{GRAY}]{model_name} · Hefeng · v{version}[/]\n"
        f"[{GRAY}]输入 q 或 Ctrl+C 退出[/]",
        border_style=DARK,
        padding=(1, 2),
    )
    console.print(panel)


def ask_input():
    return Prompt.ask(f"[{BLUE}]❯[/]")


def make_weather_panel(data_text):
    parsed = _parse_weather(data_text)
    if not parsed:
        return None

    left = Table.grid(padding=(0, 2))
    left.add_column()
    left.add_row(f"[{GRAY}]天气[/]  {parsed['weather']}")
    left.add_row(f"[{GRAY}]温度[/]  [bold {WHITE}]{parsed['temp']}°C[/]")
    left.add_row(f"[{GRAY}]体感[/]  {parsed['feels_like']}°C")

    right = Table.grid(padding=(0, 2))
    right.add_column()
    right.add_row(f"[{GRAY}]风向[/]  {parsed['wind_dir']}")
    right.add_row(f"[{GRAY}]风力[/]  {parsed['wind_scale']}级")
    right.add_row(f"[{GRAY}]湿度[/]  {parsed['humidity']}%")

    body = Table.grid(padding=(0, 1))
    body.add_row(left, right)

    return Panel(
        body,
        title=f"[{WHITE}]📍 {parsed['city']} · 实时天气[/]",
        border_style=BLUE,
        padding=(1, 2),
    )


def make_llm_panel(text):
    return Panel(
        Text(text, style=WHITE),
        title=f"[{LIGHT_BLUE}]💬 LLM 回答[/]",
        border_style=LIGHT_BLUE,
        padding=(1, 2),
    )


def make_error_panel(detail):
    return Panel(
        Text(detail, style=RED),
        title=f"[{RED}]✗ 查询失败[/]",
        border_style=RED,
        padding=(1, 2),
    )


def print_summary(elapsed):
    console.print(f"[{DARK}]▣ 回答完成 · 耗时 {elapsed:.1f}s[/]")


def print_separator():
    console.print(f"[{DARKER}]──────────────────────────────────[/]")


def print_goodbye():
    console.print()
    panel = Panel(
        Text("👋 再见！", style=GRAY, justify="center"),
        border_style=DARK,
        padding=(1, 2),
    )
    console.print(panel)


def _parse_weather(text):
    m = re.match(
        r"^(.+?)实时天气：天气(.+?)，温度(-?\d+\.?\d*?)°C，体感(-?\d+\.?\d*?)°C，(.+?)(\d+)级，湿度(\d+)%$",
        text,
    )
    if not m:
        return None
    return {
        "city": m.group(1),
        "weather": m.group(2),
        "temp": m.group(3),
        "feels_like": m.group(4),
        "wind_dir": m.group(5),
        "wind_scale": m.group(6),
        "humidity": m.group(7),
    }


def _make_tool_line(tool_name, tool_args, elapsed, scanner_text):
    return Text.from_markup(
        f"● [{BLUE}]{tool_name}[white]({tool_args}) · [{BLUE}]{scanner_text}[white] [{GRAY}]{elapsed:.1f}s[/]"
    )


def _make_thinking_line(scanner_text):
    return Text.from_markup(f"● [{GRAY}]LLM 思考中[/] [{BLUE}]{scanner_text}[/]")


def process_with_live(console, config, executor, input_data):
    handler = ToolCaptureHandler()
    result = {"output": None, "error": None}
    start_time = time.time()
    scanner = Scanner()
    scanner.start()

    def run():
        try:
            res = executor.invoke(
                {"input": input_data},
                config={"callbacks": [handler]},
            )
            result["output"] = res["output"]
        except Exception as e:
            result["error"] = str(e)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    with Live(
        console=console, refresh_per_second=10, vertical_overflow="visible"
    ) as live:
        while thread.is_alive():
            elapsed = time.time() - start_time
            scanner_text = scanner.render()
            if handler.tool_name:
                line = _make_tool_line(
                    handler.tool_name, handler.tool_args, elapsed, scanner_text
                )
            else:
                line = _make_thinking_line(scanner_text)
            live.update(line)
            time.sleep(0.05)
        thread.join()

    scanner.stop()
    total_elapsed = time.time() - start_time

    if handler.tool_name:
        final_text = Text.from_markup(
            f"● [{BLUE}]{handler.tool_name}[white]({handler.tool_args}) · [{GRAY}]{total_elapsed:.1f}s[/]"
        )
    else:
        final_text = Text.from_markup(f"● [{GRAY}]处理完成 · {total_elapsed:.1f}s[/]")
    console.print(final_text)

    return result["output"], result["error"], total_elapsed
