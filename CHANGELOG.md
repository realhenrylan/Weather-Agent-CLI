# 更新日志

## [1.3.0] — 2026-06-19

### 新增
- 启动动画：`play_startup_animation()` 替代静态横幅，逐行扫描显示 figlet "WEATHER CLI" 大字 + 版本号（约 2.5s）
- 依赖：`pyfiglet>=1.0`（figlet 字体渲染）

### 修改
- `ui.py`：重构了启动展示，删除 `print_banner`，新增 `play_startup_animation`
- `agent.py`：调用 `play_startup_animation` 替代 `print_banner`

## [1.2.0] — 2026-06-19

### 新增
- 对话记忆：`ConversationBufferMemory` 使 agent 能记住历史对话（查过的城市、用户姓名等）
- 记忆清除命令：输入 `清除记忆` / `重置` / `清空记录` / `clear memory` 可清空对话历史
- 卸载命令：输入 `卸载` / `uninstall` 可删除配置、卸载 pip 包、完全移除 weather-cli

## [1.1.0] — 2026-06-18

### 新增
- Rich 驱动的 CLI 前端界面（`ui.py`）
  - 启动横幅，显示模型名（从配置读取）、版本、退出提示
  - Knight Rider 风格扫描条动画（`⬝⬝■⬝⬝⬝`），替代原有 spinner
  - 工具调用行实时显示 + 扫描条
  - 天气结果面板（双列布局，蓝色边框 `#58a6ff`）
  - LLM 回答面板（浅蓝色边框 `#79c0ff`，💬 标题）
  - 错误面板（红色边框 `#f85149`，✗ 标题）
  - 摘要脚注（`▣ 回答完成 · 耗时 Ns`）
  - 输入提示 `❯:`
  - 退出 `👋 再见！` 面板
- `--debug` 命令行参数，控制 LangChain verbose 日志
- 依赖：`rich>=13.0`

### 修改
- `agent.py`：使用 `ui.*` 替代 `print`/`input`，通过回调捕获工具调用，`Live` 实时渲染
- `pyproject.toml`：添加 `rich>=13.0` 依赖，注册 `ui` 模块

### 移除
- 独立 spinner 行
- 横幅中的 "LangChain" 文字
