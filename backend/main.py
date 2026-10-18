import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure backend/.env is loaded across both local and root execution contexts
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

try:
    from gemini_service import generate_tailored_bullets, TailorResponse
except ImportError:
    from backend.gemini_service import generate_tailored_bullets, TailorResponse

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify environment configuration and GEMINI_API_KEY at server startup."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        masked = key[:6] + "..." if len(key) >= 6 else "***"
        print(f"Startup check: GEMINI_API_KEY detected ({masked})")
    else:
        print("Startup warning: GEMINI_API_KEY not configured in environment.")
    yield


app = FastAPI(title="Resume Tailor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TailorRequest(BaseModel):
    resume_text: str = Field(
        ...,
        min_length=15,
        max_length=12000,
        description="Raw resume bullets or experience text"
    )
    job_description: str = Field(
        ...,
        min_length=15,
        max_length=12000,
        description="Target job posting text"
    )


@app.post("/api/tailor", response_model=TailorResponse)
def tailor(request: TailorRequest):
    """
    Tailor resume bullets to align with the provided job description.
    Preserves strict factual truthfulness.
    """
    return generate_tailored_bullets(
        resume_text=request.resume_text,
        jd_text=request.job_description
    )


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Mount frontend static files (checked across both root and backend execution contexts)
potential_paths = [
    os.path.join(os.path.dirname(__file__), "..", "frontend"),
    os.path.join(os.path.dirname(__file__), "frontend"),
    os.path.abspath("frontend"),
]

for frontend_path in potential_paths:
    if os.path.exists(frontend_path):
        app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
        break
