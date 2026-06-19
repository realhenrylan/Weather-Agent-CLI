# Startup Animation Design

## 概述
为 weather-cli 添加启动动画：在命令执行后、Agent 就绪前，播放约 2.5 秒的全屏动画，逐行显示 figlet 大字 "WEATHER CLI" + 版本号。

## Layout

```
__        _______    _  _____ _   _ _____ ____     ____ _     ___ 
\ \      / / ____|  / \|_   _| | | | ____|  _ \   / ___| |   |_ _|
 \ \ /\ / /|  _|   / _ \ | | | |_| |  _| | |_) | | |   | |    | | 
  \ V  V / | |___ / ___ \| | |  _  | |___|  _ <  | |___| |___ | | 
   \_/\_/  |_____/_/   \_\_| |_| |_|_____|_| \_\  \____|_____|___|
                                                                    
                    v1.2.0
```

- 字体：figlet `standard`
- 大字颜色：蓝色 `#58a6ff`
- 版本号颜色：灰色 `#8b949e`

## 动画时序

| 时间 | 内容 |
|------|------|
| 0.0s | 第1行出现（从左到右扫描效果） |
| 0.4s | 第2行出现 |
| 0.8s | 第3行出现 |
| 1.2s | 第4行出现 |
| 1.6s | 第5行出现 |
| 2.0s | 版本号渐显 |
| 2.5s | 动画结束，进入主循环 `❯` |

## 技术方案

- 使用 `pyfiglet` 库在启动时生成 figlet 文本
- 使用 `rich.live.Live` 逐帧渲染
- 用 `rich.text.Text` 控制颜色和样式
- 动画结束后切换 clean 画面进入 Prompt

## 文件修改

- `pyproject.toml`：添加 `pyfiglet` 依赖
- `ui.py`：新增 `play_startup_animation(config)` 函数，删除 `print_banner`
- `agent.py`：调用 `play_startup_animation` 替代 `print_banner`
