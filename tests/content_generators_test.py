import pytest

from pixelle_video.utils.content_generators import (
    _parse_json,
    generate_narrations_from_topic,
)


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_generate_narrations_retries_truncated_json():
    llm = FakeLLM(
        [
            '{"narrations":["Opening line"',
            (
                '{"narrations":['
                '"Opening line",'
                '"Second line",'
                '"Third line",'
                '"Final line"'
                "]}"
            ),
        ]
    )

    narrations = await generate_narrations_from_topic(llm, "self control", n_scenes=4)

    assert narrations == ["Opening line", "Second line", "Third line", "Final line"]
    assert len(llm.calls) == 2
    assert llm.calls[1]["temperature"] == 0.3
    assert "Previous response was invalid or incomplete JSON" in llm.calls[1]["prompt"]


def test_parse_json_extracts_video_prompts_with_wrapper_text():
    result = _parse_json('Here is the JSON:\n{"video_prompts":["one","two"]}\nDone.')

    assert result == {"video_prompts": ["one", "two"]}
