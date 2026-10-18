"""Resume Tailor — Gemini API integration and response processing."""

import json
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from prompts import SYSTEM_PROMPT, create_user_prompt
from truth_checker import verify_factual_integrity

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

MODEL = "gemini-3-flash-preview"


class BulletComparison(BaseModel):
    original_bullet: str = Field(..., description="The original bullet point from the resume")
    tailored_bullet: str = Field(..., description="The sharpened, job-aligned rewrite using ONLY original facts")
    why: str = Field(..., description="One-line explanation of the keyword mapping and structural improvement")


class TailorResponse(BaseModel):
    bullets: list[BulletComparison] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="3 to 5 tailored bullets; fewer if fewer relevant bullets exist"
    )


def _clean_json_text(text: str) -> str:
    """Clean markdown code fences and whitespace from raw JSON text."""
    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.split("\n", 1)
        if len(lines) > 1:
            clean = lines[1]
        if clean.endswith("```"):
            clean = clean.rsplit("```", 1)[0]
    return clean.strip()


def create_gemini_client() -> genai.Client:
    """Create a fresh Gemini client for each request."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project:
        return genai.Client(
            vertexai=True,
            project=project,
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    return genai.Client(api_key="unconfigured_api_key")


def generate_tailored_bullets(
    resume_text: str,
    jd_text: str,
    client: genai.Client | None = None
) -> TailorResponse:
    """
    Calls Gemini API with structured output and executes the programmatic
    truthfulness audit on all candidate rewrites.
    """
    if client is None:
        client = create_gemini_client()

    user_prompt = create_user_prompt(resume_text, jd_text)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}],
                }
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=TailorResponse,
                http_options={"timeout": 15000},
            ),
        )

        response_text = _clean_json_text(response.text)
        data_dict = json.loads(response_text)
        raw_response = TailorResponse.model_validate(data_dict)

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Gemini API or validation error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Unable to tailor bullets right now. Your text is safe — click Retry to try again."
        )

    # Programmatic Truthfulness Audit
    verified_bullets: list[BulletComparison] = []
    for bullet in raw_response.bullets:
        is_valid, discrepancies = verify_factual_integrity(
            original_bullet=bullet.original_bullet,
            tailored_bullet=bullet.tailored_bullet,
            full_resume_text=resume_text
        )
        if is_valid:
            verified_bullets.append(bullet)
        else:
            print(f"Audit dropped bullet due to discrepancies: {discrepancies}")

    # If every bullet failed the audit, return HTTP 502 with friendly error
    if not verified_bullets:
        print("Audit rejected all bullets due to hallucinated facts or metrics.")
        raise HTTPException(
            status_code=502,
            detail="Unable to tailor bullets truthfully right now. Your text is safe — click Retry to try again."
        )

    return TailorResponse(bullets=verified_bullets)
