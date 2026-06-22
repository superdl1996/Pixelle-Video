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
Content input components for web UI (left column)
"""

import streamlit as st

from pixelle_video.config import config_manager
from web.i18n import tr
from web.utils.async_helpers import get_project_version

DEFAULT_QUICK_CREATE_TEXT_TEMPLATE = (
    "$title 的书评,整体要根据分镜总时长评论完整,不要戛然而止,"
    "必须以 今天要分享的是 $title ,为视频开头,并且占用一个分镜"
)

DEFAULT_FIRST_FRAME_TEXT_TEMPLATE = "今天要分享的是 $title"


def _apply_quick_create_template(template: str, title_value: str) -> str:
    """Apply quick-create variable values to a text template."""
    return (template or "").replace("$title", title_value or "")


def _sync_first_frame_scene_count():
    enabled = bool(st.session_state.get("quick_create_first_frame_enabled", False))
    previous = bool(st.session_state.get("_quick_create_first_frame_enabled_previous", enabled))

    if enabled == previous:
        return

    current = int(st.session_state.get("quick_create_n_scenes", 5) or 5)
    if enabled:
        st.session_state.quick_create_n_scenes = min(30, current + 1)
    else:
        st.session_state.quick_create_n_scenes = max(3, current - 1)
    st.session_state._quick_create_first_frame_enabled_previous = enabled


def render_content_input():
    """Render content input section (left column) with batch support"""
    saved_ui = config_manager.get_quick_create_ui_config()

    with st.container(border=True):
        st.markdown(f"**{tr('section.content_input')}**")
        
        # ====================================================================
        # Step 1: Batch mode toggle (highest priority)
        # ====================================================================
        batch_mode = st.checkbox(
            tr("batch.mode_label"),
            value=bool(saved_ui.get("batch_mode", False)),
            help=tr("batch.mode_help"),
            key="quick_create_batch_mode"
        )
        
        if not batch_mode:
            # ================================================================
            # Single task mode (original logic, unchanged)
            # ================================================================
            # Processing mode selection
            mode = st.radio(
                "Processing Mode",
                ["generate", "fixed"],
                horizontal=True,
                format_func=lambda x: tr(f"mode.{x}"),
                index=0 if saved_ui.get("mode", "generate") == "generate" else 1,
                label_visibility="collapsed",
                key="quick_create_mode"
            )

            first_frame_enabled = bool(saved_ui.get("first_frame_enabled", False))
            if "_quick_create_first_frame_enabled_previous" not in st.session_state:
                st.session_state._quick_create_first_frame_enabled_previous = first_frame_enabled

            first_frame_enabled = st.checkbox(
                "启用首帧分镜",
                value=first_frame_enabled,
                help="勾选后，会把下方文字作为第一个分镜的旁白和字幕；可使用 $title 引用变量值。",
                key="quick_create_first_frame_enabled",
                on_change=_sync_first_frame_scene_count,
            )

            auto_template_enabled = st.checkbox(
                "启用变量模板自动填充",
                value=bool(saved_ui.get("auto_template_enabled", True)),
                help="勾选后，填写变量值和模板会自动生成下面的文本输入与标题；取消勾选后可手动编辑。",
                key="quick_create_auto_template_enabled",
            )

            template_variable = saved_ui.get("template_variable", "")
            text_template = saved_ui.get("text_template") or DEFAULT_QUICK_CREATE_TEXT_TEMPLATE

            if auto_template_enabled:
                variable_col, template_col = st.columns([1, 2])
                with variable_col:
                    template_variable = st.text_input(
                        "变量值（$title）",
                        value=template_variable,
                        placeholder="终身成长",
                        help="这里填写会替换模板里的 $title，例如：终身成长。",
                        key="quick_create_template_variable",
                    )
                with template_col:
                    text_template = st.text_area(
                        "文本模板",
                        value=text_template,
                        height=96,
                        help="可使用 $title 作为变量占位符，例如：$title 的书评...",
                        key="quick_create_text_template",
                    )

                generated_text = _apply_quick_create_template(text_template, template_variable)
                generated_title = template_variable
                st.session_state["quick_create_text"] = generated_text
                st.session_state["quick_create_title"] = generated_title
            else:
                if "quick_create_template_variable" not in st.session_state:
                    st.session_state.quick_create_template_variable = template_variable
                if "quick_create_text_template" not in st.session_state:
                    st.session_state.quick_create_text_template = text_template
                template_variable = st.session_state.get("quick_create_template_variable", template_variable)
                text_template = st.session_state.get("quick_create_text_template", text_template)
                generated_text = None
                generated_title = None

            author_enabled = st.checkbox(
                "显示作者",
                value=bool(saved_ui.get("author_enabled", False)),
                help="勾选后，会在书名下方显示作者；位置会随书名高度自动调整。",
                key="quick_create_author_enabled",
            )
            author = saved_ui.get("author", "")
            if author_enabled:
                author = st.text_input(
                    "作者",
                    value=author,
                    placeholder="请输入作者姓名",
                    help="作者会使用与书名匹配的字体、描边和阴影样式。",
                    key="quick_create_author",
                )
            else:
                if "quick_create_author" not in st.session_state:
                    st.session_state.quick_create_author = author
                author = st.session_state.get("quick_create_author", author)

            first_frame_text_template = saved_ui.get(
                "first_frame_text_template",
                DEFAULT_FIRST_FRAME_TEXT_TEMPLATE,
            )
            if first_frame_enabled:
                first_frame_text_template = st.text_area(
                    "首帧分镜文字",
                    value=first_frame_text_template,
                    height=68,
                    placeholder="今天要分享的是 $title",
                    help="这段文字会固定作为第一个分镜的配音和字幕。支持 $title，会优先替换为变量值。",
                    key="quick_create_first_frame_text_template",
                )
            else:
                if "quick_create_first_frame_text_template" not in st.session_state:
                    st.session_state.quick_create_first_frame_text_template = first_frame_text_template
                first_frame_text_template = st.session_state.get(
                    "quick_create_first_frame_text_template",
                    first_frame_text_template,
                )
            
            # Text input (unified for both modes)
            text_placeholder = tr("input.topic_placeholder") if mode == "generate" else tr("input.content_placeholder")
            text_height = 120 if mode == "generate" else 200
            text_help = tr("input.text_help_generate") if mode == "generate" else tr("input.text_help_fixed")
            
            text = st.text_area(
                tr("input.text"),
                value=generated_text if auto_template_enabled else saved_ui.get("text", ""),
                placeholder=text_placeholder,
                height=text_height,
                help=text_help,
                key="quick_create_text",
                disabled=auto_template_enabled,
            )
            
            # Split mode selector (only show in fixed mode)
            if mode == "fixed":
                split_mode_options = {
                    "paragraph": tr("split.mode_paragraph"),
                    "line": tr("split.mode_line"),
                    "sentence": tr("split.mode_sentence"),
                }
                split_mode = st.selectbox(
                    tr("split.mode_label"),
                    options=list(split_mode_options.keys()),
                    format_func=lambda x: split_mode_options[x],
                    index=list(split_mode_options.keys()).index(
                        saved_ui.get("split_mode", "paragraph")
                        if saved_ui.get("split_mode", "paragraph") in split_mode_options
                        else "paragraph"
                    ),
                    help=tr("split.mode_help"),
                    key="quick_create_split_mode"
                )
            else:
                split_mode = "paragraph"  # Default for generate mode (not used)
            
            # Title input (optional for both modes)
            title = st.text_input(
                tr("input.title"),
                value=generated_title if auto_template_enabled else saved_ui.get("title", ""),
                placeholder=tr("input.title_placeholder"),
                help=tr("input.title_help"),
                key="quick_create_title",
                disabled=auto_template_enabled,
            )
            
            # Number of scenes (only show in generate mode)
            if mode == "generate":
                saved_n_scenes = int(saved_ui.get("n_scenes", 5) or 5)
                if first_frame_enabled:
                    current_n_scenes = int(st.session_state.get(
                        "quick_create_n_scenes",
                        saved_n_scenes,
                    ) or 5)
                    if current_n_scenes < 4:
                        st.session_state.quick_create_n_scenes = 4
                    saved_n_scenes = max(4, saved_n_scenes)

                n_scenes = st.slider(
                    tr("video.frames"),
                    min_value=4 if first_frame_enabled else 3,
                    max_value=30,
                    value=saved_n_scenes,
                    help=tr("video.frames_help"),
                    label_visibility="collapsed",
                    key="quick_create_n_scenes"
                )
                st.caption(tr("video.frames_label", n=n_scenes))
            else:
                # Fixed mode: n_scenes is ignored, set default value
                n_scenes = 5
                st.info(tr("video.frames_fixed_mode_hint"))

            first_frame_title_value = template_variable or title or ""
            first_frame_text = _apply_quick_create_template(
                first_frame_text_template,
                first_frame_title_value,
            ).strip()
            
            return {
                "batch_mode": False,
                "mode": mode,
                "auto_template_enabled": auto_template_enabled,
                "template_variable": template_variable,
                "text_template": text_template,
                "author_enabled": author_enabled,
                "author": author,
                "first_frame_enabled": first_frame_enabled,
                "first_frame_text_template": first_frame_text_template,
                "first_frame_text": first_frame_text,
                "first_frame_title_value": first_frame_title_value,
                "text": text,
                "title": title,
                "n_scenes": n_scenes,
                "split_mode": split_mode
            }
        
        else:
            # ================================================================
            # Batch mode (simplified YAGNI version)
            # ================================================================
            st.markdown(f"**{tr('batch.section_title')}**")
            
            # Batch rules info
            st.info(f"""
**{tr('batch.rules_title')}**
- ✅ {tr('batch.rule_1')}
- ✅ {tr('batch.rule_2')}
- ✅ {tr('batch.rule_3')}
            """)
            
            # Batch topics input
            text_input = st.text_area(
                tr("batch.topics_label"),
                value=saved_ui.get("topics_text", ""),
                height=300,
                placeholder=tr("batch.topics_placeholder"),
                help=tr("batch.topics_help"),
                key="quick_create_topics_text"
            )
            
            # Split topics by newline
            if text_input:
                # Simple split by newline, filter empty lines
                topics = [
                    line.strip() 
                    for line in text_input.strip().split('\n') 
                    if line.strip()
                ]
                
                if topics:
                    # Check count limit
                    if len(topics) > 100:
                        st.error(tr("batch.count_error", count=len(topics)))
                        topics = []
                    else:
                        st.success(tr("batch.count_success", count=len(topics)))
                        
                        # Preview topics list
                        with st.expander(tr("batch.preview_title"), expanded=False):
                            for i, topic in enumerate(topics, 1):
                                st.markdown(f"`{i}.` {topic}")
                else:
                    topics = []
            else:
                topics = []
            
            st.markdown("---")
            
            # Title prefix (optional)
            title_prefix = st.text_input(
                tr("batch.title_prefix_label"),
                value=saved_ui.get("title_prefix", ""),
                placeholder=tr("batch.title_prefix_placeholder"),
                help=tr("batch.title_prefix_help"),
                key="quick_create_title_prefix"
            )
            
            # Number of scenes (unified for all videos)
            n_scenes = st.slider(
                tr("batch.n_scenes_label"),
                min_value=3,
                max_value=30,
                value=int(saved_ui.get("n_scenes", 5)),
                help=tr("batch.n_scenes_help"),
                key="quick_create_batch_n_scenes"
            )
            st.caption(tr("batch.n_scenes_caption", n=n_scenes))
            
            # Config info
            st.info(f"📌 {tr('batch.config_info')}")
            
            return {
                "batch_mode": True,
                "topics": topics,
                "topics_text": text_input,
                "mode": "generate",  # Fixed to AI generate content
                "title_prefix": title_prefix,
                "n_scenes": n_scenes,
                "author_enabled": bool(saved_ui.get("author_enabled", False)),
                "author": saved_ui.get("author", ""),
            }


def render_bgm_section(key_prefix=""):
    """Render BGM selection section"""
    saved_ui = config_manager.get_quick_create_ui_config()

    with st.container(border=True):
        st.markdown(f"**{tr('section.bgm')}**")
        
        with st.expander(tr("help.feature_description"), expanded=False):
            st.markdown(f"**{tr('help.what')}**")
            st.markdown(tr("bgm.what"))
            st.markdown(f"**{tr('help.how')}**")
            st.markdown(tr("bgm.how"))
        
        # Dynamically scan bgm folder for music files (merged from bgm/ and data/bgm/)
        from pixelle_video.utils.os_util import list_resource_files
        
        try:
            all_files = list_resource_files("bgm")
            # Filter to audio files only
            audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')
            bgm_files = sorted([f for f in all_files if f.lower().endswith(audio_extensions)])
        except Exception as e:
            st.warning(f"Failed to load BGM files: {e}")
            bgm_files = []
        
        # Add special "None" option
        bgm_options = [tr("bgm.none")] + bgm_files
        
        # Default to "default.mp3" if exists, otherwise first option
        default_index = 0
        saved_bgm_path = saved_ui.get("bgm_path")
        if saved_bgm_path is None:
            default_index = 0
        elif saved_bgm_path in bgm_options:
            default_index = bgm_options.index(saved_bgm_path)
        elif "default.mp3" in bgm_files:
            default_index = bgm_options.index("default.mp3")
        
        bgm_choice = st.selectbox(
            "BGM",
            bgm_options,
            index=default_index,
            label_visibility="collapsed",
            key=f"{key_prefix}bgm_selector"
        )
        
        # BGM volume slider (only show when BGM is selected)
        if bgm_choice != tr("bgm.none"):
            bgm_volume = st.slider(
                tr("bgm.volume"),
                min_value=0.0,
                max_value=0.5,
                value=float(saved_ui.get("bgm_volume", 0.2)),
                step=0.01,
                format="%.2f",
                key=f"{key_prefix}bgm_volume_slider",
                help=tr("bgm.volume_help")
            )
        else:
            bgm_volume = 0.2  # Default value when no BGM selected
        
        # BGM preview button (only if BGM is not "None")
        if bgm_choice != tr("bgm.none"):
            if st.button(tr("bgm.preview"), key=f"{key_prefix}preview_bgm", use_container_width=True):
                from pixelle_video.utils.os_util import get_resource_path, resource_exists
                try:
                    if resource_exists("bgm", bgm_choice):
                        bgm_file_path = get_resource_path("bgm", bgm_choice)
                        st.audio(bgm_file_path)
                    else:
                        st.error(tr("bgm.preview_failed", file=bgm_choice))
                except Exception as e:
                    st.error(f"{tr('bgm.preview_failed', file=bgm_choice)}: {e}")
        
        # Use full filename for bgm_path (including extension)
        bgm_path = None if bgm_choice == tr("bgm.none") else bgm_choice
    
    return {
        "bgm_path": bgm_path,
        "bgm_volume": bgm_volume
    }


def render_version_info():
    """Render version info and GitHub link"""
    with st.container(border=True):
        st.markdown(f"**{tr('version.title')}**")
        version = get_project_version()
        github_url = "https://github.com/AIDC-AI/Pixelle-Video"
        
        # Version and GitHub link in one line
        github_url = "https://github.com/AIDC-AI/Pixelle-Video"
        badge_url = "https://img.shields.io/github/stars/AIDC-AI/Pixelle-Video"

        st.markdown(
            f'{tr("version.current")}: `{version}` &nbsp;&nbsp; '
            f'<a href="{github_url}" target="_blank">'
            f'<img src="{badge_url}" alt="GitHub stars" style="vertical-align: middle;">'
            f'</a>',
            unsafe_allow_html=True)

