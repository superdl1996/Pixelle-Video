# AGENTS.md

本文件为在本仓库中工作的 AI 编码代理提供项目约定、结构说明和常用命令。请在修改代码前先阅读本文件，并优先遵循已有实现风格。

## 项目概览

Pixelle-Video 是一个 AI 全自动短视频生成项目。核心流程包括文案生成、媒体生成、语音合成、分镜处理和最终视频合成。

主要技术栈：

- Python 3.11+
- uv 作为依赖与运行管理工具
- Streamlit 提供 Web UI
- FastAPI 提供 HTTP API
- Pydantic v2、Loguru、PyYAML
- OpenAI SDK 兼容 LLM 调用
- ComfyUI / RunningHub / 直连模型 API 作为图像、视频、TTS、VLM 能力来源
- ffmpeg / moviepy 处理视频合成
- Ruff 负责基础 lint 与 import 排序
- pytest 负责测试

## 目录结构

- `pixelle_video/`：核心业务包。
  - `service.py`：`PixelleVideoCore` 核心服务聚合入口。
  - `config/`：配置加载、schema 与管理逻辑。
  - `services/`：LLM、TTS、媒体生成、视频合成、历史记录、API 模型供应商等服务。
  - `pipelines/`：标准、自定义、自定义素材等视频生成流水线。
  - `models/`：媒体、进度、分镜等领域模型。
  - `prompts/`：文案、标题、图片、风格转换等提示词。
  - `utils/`：工作流、模板、系统、TTS、LLM 等工具函数。
- `web/`：Streamlit 多页 Web UI。
  - `app.py`：Web UI 入口。
  - `pages/`：Streamlit 页面。
  - `components/`：可复用 UI 组件。
  - `pipelines/`：Web 层对不同工作流的编排。
  - `state/`、`utils/`、`i18n/`：会话状态、工具与国际化资源。
- `api/`：FastAPI 服务。
  - `app.py`：API 入口。
  - `routers/`：按能力拆分的路由。
  - `schemas/`：请求和响应模型。
  - `tasks/`：异步任务管理。
- `workflows/`：ComfyUI / RunningHub 工作流 JSON。
  - `selfhost/`：本地 ComfyUI 工作流。
  - `runninghub/`：RunningHub 工作流。
- `templates/`：视频帧 HTML 模板，按分辨率和媒体类型组织。
- `docs/`：MkDocs 文档，包含中英文使用、配置、架构与 API 文档。
- `resources/`：README、文档或 UI 使用的静态资源。
- `bgm/`：默认背景音乐资源。
- `packaging/windows/`：Windows 整合包构建脚本、模板与说明。
- `.github/`：GitHub Actions 配置。
- `.devcontainer/`：开发容器启动脚本。
- `data/`、`output/`：运行时数据与生成结果目录，通常不应提交。

## 常用命令

安装依赖：

```bash
uv sync
```

启动 Web UI：

```bash
uv run streamlit run web/app.py
```

Windows 也可以运行：

```bat
start_web.bat
```

启动 FastAPI 服务：

```bash
uv run python api/app.py
```

带热重载启动 API：

```bash
uv run python api/app.py --host 0.0.0.0 --port 8000 --reload
```

运行测试：

```bash
uv run pytest
```

运行 Ruff 检查：

```bash
uv run ruff check .
```

自动修复可安全修复的问题：

```bash
uv run ruff check . --fix
```

## 配置与密钥

- 使用 `config.example.yaml` 作为配置模板。
- 本地配置文件为 `config.yaml`，包含 API Key、Base URL、代理、ComfyUI、RunningHub 等敏感信息，不要提交。
- `.env`、`config.yaml`、`data/`、`output/` 已在 `.gitignore` 中排除。
- 修改配置 schema 时，同步检查：
  - `pixelle_video/config/schema.py`
  - `pixelle_video/config/manager.py`
  - `config.example.yaml`
  - `docs/zh/reference/config-schema.md`
  - `docs/en/reference/config-schema.md`
  - Web UI 中的系统配置组件
- 不要在日志、测试快照或文档示例中写入真实 API Key。

## 代码规范

- 项目代码和代码注释使用英文，面向中文用户的文档可以使用中文。
- 遵循 PEP 8 和本项目已有风格。
- Python 目标版本为 3.11，优先使用现代类型标注。
- Ruff 配置在 `pyproject.toml` 中：
  - `line-length = 100`
  - `target-version = "py311"`
  - lint 规则选择 `E`、`F`、`I`
  - 忽略 `E501`
- 保持模块边界清晰：
  - 核心业务逻辑放在 `pixelle_video/services/` 或 `pixelle_video/pipelines/`。
  - Web 展示和交互逻辑放在 `web/`。
  - HTTP API 只放路由、schema、任务管理和依赖注入相关逻辑。
  - 通用配置逻辑放在 `pixelle_video/config/`。
- 优先扩展现有服务、pipeline、schema 和组件，不要为相同职责另起一套抽象。
- 异步服务保持 async 调用链，不要在事件循环中直接加入长时间阻塞操作。
- 文件、路径和跨平台逻辑优先使用 `pathlib.Path`。
- 日志使用 `loguru.logger`，避免 `print`，入口脚本中的启动提示除外。
- 面向用户的错误信息要可操作；内部异常应保留足够上下文，便于排查配置或供应商调用问题。
- 生成的注释语言以中文为主

## Web UI 约定

- Streamlit 入口是 `web/app.py`，页面在 `web/pages/`。
- 新增页面时，检查 `st.navigation` 中是否需要注册该页面。
- 可复用 UI 放入 `web/components/`，状态管理放入 `web/state/`。
- 国际化文案放入 `web/i18n/locales/zh_CN.json` 和 `web/i18n/locales/en_US.json`，避免在复杂组件中散落硬编码文案。
- Web 层应尽量调用已有 pipeline 或 service，不要复制核心生成逻辑。

## API 约定

- FastAPI 入口是 `api/app.py`。
- 新增能力时通常需要同步：
  - `api/routers/`
  - `api/schemas/`
  - `api/app.py` 中的 router 注册
  - `docs/zh/user-guide/api.md` 或 `docs/*/reference/api-overview.md`
- 请求和响应模型使用 Pydantic schema，避免裸 dict 在路由层大面积传播。
- 长任务优先走 `api/tasks/` 的任务管理机制，避免同步接口长时间阻塞。

## 工作流与模板约定

- `workflows/selfhost/` 用于本地 ComfyUI，`workflows/runninghub/` 用于 RunningHub。
- 工作流文件命名应体现能力类型，例如 `image_*.json`、`video_*.json`、`tts_*.json`、`analyse_*.json`。
- 修改或新增工作流时，检查 `config.example.yaml` 中的默认工作流、Web UI 选择项和相关文档。
- `templates/` 中的 HTML 模板按分辨率组织，例如 `1080x1920/`、`1920x1080/`、`1080x1080/`。
- 模板命名约定：
  - `static_*.html`：静态模板，不依赖 AI 生成媒体。
  - `image_*.html`：需要 AI 生成图片。
  - `video_*.html`：需要 AI 生成视频。
- 新模板应确保文本不会溢出，画面比例与目录分辨率一致，并在 Web UI 中可预览或选择。
- 每次你的修改是否需要重启才能生效，需要在回答的最后明确告知。

## 测试与验证

- `pyproject.toml` 中 pytest 的默认目录为 `tests`。当前仓库可能没有现成测试目录；新增高风险逻辑时应补充对应测试。
- 推荐验证顺序：
  1. 运行与修改相关的最小测试。
  2. 运行 `uv run ruff check .`。
  3. 对 Web UI 修改，启动 `uv run streamlit run web/app.py` 并手动确认关键页面。
  4. 对 API 修改，启动 `uv run python api/app.py --reload` 并检查 `/health`、`/docs` 或相关接口。
- 依赖外部模型、ComfyUI、RunningHub 或网络的功能，测试时应说明所需配置；不要把真实密钥写入测试。
- 生成媒体、音频或视频结果通常落在 `output/` 或 `data/`，不要将运行产物提交。

## 文档约定

- 中文文档在 `docs/zh/`，英文文档在 `docs/en/`。
- 用户可见行为、配置项、API 入参或工作流默认值发生变化时，同步更新对应文档。
- README 面向快速理解和上手，详细说明优先放入 `docs/`。
- MkDocs 配置在 `mkdocs.yml`，文档依赖在 `requirements-docs.txt`。

## 提交前检查清单

- 代码是否符合当前模块边界，没有把 Web、API、核心服务逻辑混在一起。
- 是否避免提交 `config.yaml`、`.env`、`data/`、`output/`、生成媒体和日志。
- 是否运行了与改动相关的测试或手动验证。
- 是否运行了 Ruff 检查，或说明无法运行的原因。
- 修改配置、API、模板或工作流时，是否同步更新示例配置和文档。
- 新增依赖时，是否更新 `pyproject.toml` 和锁文件，并确认 Windows 打包依赖是否也需要同步。

