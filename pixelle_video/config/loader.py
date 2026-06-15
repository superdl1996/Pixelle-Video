# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Configuration loader - Pure YAML

Handles loading and saving configuration from/to YAML files.
"""
from pathlib import Path
from typing import Any
import yaml
from loguru import logger


CONFIG_COMMENTS = {
    ("project_name",): "项目名称，仅用于显示和识别当前配置。",
    ("llm",): "LLM 配置，支持任何 OpenAI SDK 兼容接口。",
    ("llm", "api_key"): "LLM API Key。请填写你的模型服务密钥，不要提交到 Git。",
    ("llm", "base_url"): "LLM API Base URL，例如 https://api.openai.com/v1。",
    ("llm", "model"): "LLM 模型名称，例如 gpt-4o、qwen-max、deepseek-chat。",
    ("api_providers",): "直连图像、视频、VLM 等模型供应商配置，不影响上面的 LLM 配置。",
    ("api_providers", "common"): "直连模型供应商的通用配置。",
    ("api_providers", "common", "print_model_input"): "是否在终端打印图像/视频模型请求参数，用于调试。",
    ("api_providers", "common", "local_proxy"): "本地代理地址。留空表示不使用代理，例如 http://127.0.0.1:9090。",
    ("api_providers", "openai"): "OpenAI / GPT Image 供应商配置。",
    ("api_providers", "openai", "api_key"): "OpenAI API Key。",
    ("api_providers", "openai", "base_url"): "OpenAI Base URL，通常为 https://api.openai.com/v1。",
    ("api_providers", "openai", "use_proxy"): "OpenAI 是否使用 common.local_proxy。",
    ("api_providers", "dashscope"): "DashScope / 通义万相 / Wan 等供应商配置。",
    ("api_providers", "dashscope", "api_key"): "DashScope API Key。",
    ("api_providers", "dashscope", "base_url"): "DashScope Base URL。",
    ("api_providers", "dashscope", "use_proxy"): "DashScope 是否使用 common.local_proxy。",
    ("api_providers", "deepseek"): "DeepSeek 供应商配置，保留给兼容接口使用。",
    ("api_providers", "deepseek", "api_key"): "DeepSeek API Key。",
    ("api_providers", "deepseek", "base_url"): "DeepSeek Base URL。",
    ("api_providers", "deepseek", "use_proxy"): "DeepSeek 是否使用 common.local_proxy。",
    ("api_providers", "gemini"): "Gemini 供应商配置，保留给兼容接口使用。",
    ("api_providers", "gemini", "api_key"): "Gemini API Key。",
    ("api_providers", "gemini", "base_url"): "Gemini Base URL。",
    ("api_providers", "gemini", "use_proxy"): "Gemini 是否使用 common.local_proxy。",
    ("api_providers", "ark"): "Volcengine ARK / Seedream / Seedance 供应商配置。",
    ("api_providers", "ark", "api_key"): "ARK API Key。",
    ("api_providers", "ark", "base_url"): "ARK Base URL。",
    ("api_providers", "ark", "use_proxy"): "ARK 是否使用 common.local_proxy。",
    ("api_providers", "kling"): "Kling AI / 可灵供应商配置。",
    ("api_providers", "kling", "base_url"): "Kling Base URL。",
    ("api_providers", "kling", "access_key"): "Kling Access Key。",
    ("api_providers", "kling", "secret_key"): "Kling Secret Key。",
    ("api_providers", "kling", "use_proxy"): "Kling 是否使用 common.local_proxy。",
    ("comfyui",): "ComfyUI / RunningHub 工作流配置。",
    ("comfyui", "comfyui_url"): "本地 ComfyUI 服务地址。",
    ("comfyui", "comfyui_api_key"): "ComfyUI API Key，可选。",
    ("comfyui", "runninghub_api_key"): "RunningHub API Key，使用 RunningHub 工作流时需要。",
    ("comfyui", "runninghub_concurrent_limit"): "RunningHub 并发数，范围 1-10。",
    ("comfyui", "runninghub_instance_type"): "RunningHub 机器类型。留空为普通 24G，plus 表示 48G。",
    ("comfyui", "tts"): "TTS 相关默认配置。",
    ("comfyui", "tts", "inference_mode"): "默认 TTS 模式：local 或 comfyui。",
    ("comfyui", "tts", "local"): "本地 Edge TTS 默认配置。",
    ("comfyui", "tts", "local", "voice"): "本地 Edge TTS 默认音色 ID。",
    ("comfyui", "tts", "local", "speed"): "本地 Edge TTS 默认语速，范围 0.5-2.0。",
    ("comfyui", "tts", "comfyui"): "ComfyUI TTS 默认配置。",
    ("comfyui", "tts", "comfyui", "default_workflow"): "默认 ComfyUI TTS 工作流 key。",
    ("comfyui", "image"): "图片生成默认配置。",
    ("comfyui", "image", "default_workflow"): "默认图片生成工作流 key。",
    ("comfyui", "image", "prompt_prefix"): "图片生成 prompt 前缀，会拼到每个图片提示词前。",
    ("comfyui", "video"): "视频生成默认配置。",
    ("comfyui", "video", "default_workflow"): "默认视频生成工作流 key。",
    ("comfyui", "video", "prompt_prefix"): "视频生成 prompt 前缀，会拼到每个视频提示词前。",
    ("template",): "全局模板默认配置。",
    ("template", "default_template"): "默认帧模板路径，相对于 templates/ 或 data/templates/。",
    ("web_ui",): "Web 页面配置。刷新页面后会用这里的值恢复控件选择。",
    ("web_ui", "quick_create"): "首页“快速创作”标签页保存的控件配置。",
    ("web_ui", "quick_create", "batch_mode"): "是否启用批量生成模式。",
    ("web_ui", "quick_create", "mode"): "单视频处理模式：generate 表示 AI 创作，fixed 表示自行创作。",
    ("web_ui", "quick_create", "text"): "单视频文本输入。AI 创作为主题，自行创作为完整文案。",
    ("web_ui", "quick_create", "title"): "单视频标题，可留空。",
    ("web_ui", "quick_create", "split_mode"): "自行创作模式的分割方式：paragraph、line 或 sentence。",
    ("web_ui", "quick_create", "n_scenes"): "分镜数量，范围 3-30。",
    ("web_ui", "quick_create", "topics_text"): "批量生成主题，每行一个。",
    ("web_ui", "quick_create", "title_prefix"): "批量生成标题前缀，可留空。",
    ("web_ui", "quick_create", "bgm_path"): "背景音乐文件名。null 表示不使用 BGM。",
    ("web_ui", "quick_create", "bgm_volume"): "背景音乐音量，范围 0.0-0.5。",
    ("web_ui", "quick_create", "tts_inference_mode"): "配音合成方式：local 或 comfyui。",
    ("web_ui", "quick_create", "tts_voice"): "本地 Edge TTS 音色 ID。",
    ("web_ui", "quick_create", "tts_speed"): "本地 Edge TTS 语速，范围 0.5-2.0。",
    ("web_ui", "quick_create", "tts_workflow"): "ComfyUI TTS 工作流 key。",
    ("web_ui", "quick_create", "template_type"): "模板类型：static、image 或 video。",
    ("web_ui", "quick_create", "frame_template"): "当前选择的分镜模板路径。",
    ("web_ui", "quick_create", "template_params"): "模板自定义参数。键名来自模板文件，可按需手动修改。",
    ("web_ui", "quick_create", "media_workflow"): "图片或视频生成工作流 key。",
    ("web_ui", "quick_create", "prompt_prefix"): "当前页面使用的媒体生成 prompt 前缀。",
}


def _comment_for_path(path: tuple[str, ...]) -> str | None:
    if (
        len(path) == 4
        and path[:3] == ("web_ui", "quick_create", "template_params")
    ):
        return f"模板自定义参数 {path[-1]}，来自当前选择的 HTML 模板。"
    return CONFIG_COMMENTS.get(path)


def _dump_scalar(value: Any) -> str:
    dumped = yaml.safe_dump(
        value,
        allow_unicode=True,
        default_flow_style=True,
        sort_keys=False,
        width=1_000_000,
    )
    lines = [line for line in dumped.splitlines() if line.strip() != "..."]
    return "\n".join(lines).strip()


def _dump_commented_yaml(data: dict[str, Any], path: tuple[str, ...] = (), indent: int = 0) -> list[str]:
    lines = []
    spaces = " " * indent

    for key, value in data.items():
        key_path = (*path, str(key))
        comment = _comment_for_path(key_path)
        if comment:
            lines.append(f"{spaces}# {comment}")

        if isinstance(value, dict):
            lines.append(f"{spaces}{key}:")
            if value:
                lines.extend(_dump_commented_yaml(value, key_path, indent + 2))
            else:
                lines[-1] = f"{spaces}{key}: {{}}"
        else:
            lines.append(f"{spaces}{key}: {_dump_scalar(value)}")

        if indent == 0:
            lines.append("")

    return lines


def dump_config_with_comments(config: dict) -> str:
    """Dump configuration to YAML with human-readable comments."""
    header = [
        "# Pixelle-Video Configuration",
        "# 这个文件由 Web UI 保存生成，也可以手动编辑。",
        "# 注意：请不要把包含真实 API Key 的 config.yaml 提交到 Git。",
        "",
    ]
    return "\n".join(header + _dump_commented_yaml(config)).rstrip() + "\n"


def load_config_dict(config_path: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        logger.info(f"Configuration loaded from {config_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def save_config_dict(config: dict, config_path: str = "config.yaml"):
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        config_path: Path to config file
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(dump_config_with_comments(config))
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise

