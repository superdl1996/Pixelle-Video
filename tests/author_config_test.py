from pathlib import Path

from pixelle_video.config.schema import QuickCreateUIConfig
from pixelle_video.services.frame_html import HTMLFrameGenerator


def test_quick_create_author_defaults_to_hidden():
    config = QuickCreateUIConfig()

    assert config.author_enabled is False
    assert config.author == ""


def test_image_full_renders_author_below_title():
    template_path = Path("templates/1080x1920/image_full.html")
    generator = HTMLFrameGenerator(template_path)

    rendered = generator._replace_parameters(
        generator.template,
        {
            "title": "等一切风平浪静",
            "text": "测试文案",
            "image": "test.png",
            "author": "麦家",
        },
    )

    assert '<div class="book-author">麦家</div>' in rendered
    assert "@Pixelle.AI" not in rendered


def test_image_full_keeps_empty_author_element_hidden_by_css():
    template_path = Path("templates/1080x1920/image_full.html")
    generator = HTMLFrameGenerator(template_path)

    rendered = generator._replace_parameters(generator.template, {"author": ""})

    assert '<div class="book-author"></div>' in rendered
    assert ".book-author:empty" in rendered
