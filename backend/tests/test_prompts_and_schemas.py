"""Unit tests for prompts, Pydantic schemas, and input validation."""

import pytest
from pydantic import ValidationError

from main import TailorRequest
from prompts import SYSTEM_PROMPT, create_user_prompt
from gemini_service import BulletComparison, TailorResponse, _clean_json_text


def test_input_validation_min_length():
    """Verify TailorRequest raises validation error (yielding 422) when input is < 15 chars."""
    with pytest.raises(ValidationError):
        TailorRequest(resume_text="Too short", job_description="Valid job description with enough text here")

    with pytest.raises(ValidationError):
        TailorRequest(resume_text="Valid experience bullet points with enough length", job_description="Short")


def test_input_validation_max_length():
    """Verify TailorRequest raises validation error when text exceeds 12,000 characters."""
    oversized = "A" * 12001
    with pytest.raises(ValidationError):
        TailorRequest(resume_text=oversized, job_description="Valid job description with enough text here")

    with pytest.raises(ValidationError):
        TailorRequest(resume_text="Valid experience bullet points with enough length", job_description=oversized)


def test_clean_markdown_json():
    """Verify _clean_json_text strips markdown code fences, leading/trailing whitespace, etc."""
    raw_fenced = "```json\n{\"bullets\": []}\n```"
    assert _clean_json_text(raw_fenced) == '{"bullets": []}'

    raw_plain = '  {"bullets": []} \n'
    assert _clean_json_text(raw_plain) == '{"bullets": []}'


def test_tailor_response_validation():
    """Verify TailorResponse accepts valid 1-5 bullet objects and rejects missing fields."""
    valid_data = {
        "bullets": [
            {
                "original_bullet": "Worked on database performance",
                "tailored_bullet": "Optimized database performance to support critical queries.",
                "why": "Emphasized database query optimization matching JD"
            }
        ]
    }
    response = TailorResponse.model_validate(valid_data)
    assert len(response.bullets) == 1
    assert response.bullets[0].original_bullet == "Worked on database performance"

    # Missing 'why'
    invalid_data = {
        "bullets": [
            {
                "original_bullet": "Worked on database performance",
                "tailored_bullet": "Optimized database performance"
            }
        ]
    }
    with pytest.raises(ValidationError):
        TailorResponse.model_validate(invalid_data)

    # Empty list (min_length=1)
    with pytest.raises(ValidationError):
        TailorResponse.model_validate({"bullets": []})


def test_prompt_construction():
    """Verify create_user_prompt encapsulates inputs with clear markdown delimiters."""
    resume = "• Led backend migration to microservices"
    jd = "Seeking a Backend Engineer to lead cloud migration"

    prompt = create_user_prompt(resume, jd)
    assert resume in prompt
    assert jd in prompt
    assert '"""' in prompt


def test_system_prompt_contains_anti_hallucination_rules():
    """Verify SYSTEM_PROMPT contains 'NEVER invent' and explicit anti-hallucination constraints."""
    assert "NEVER invent" in SYSTEM_PROMPT
    assert "STRICT FACTUAL BOUNDARY" in SYSTEM_PROMPT
    assert "metrics, numbers, or percentages" in SYSTEM_PROMPT
    assert "tools or technologies" in SYSTEM_PROMPT
