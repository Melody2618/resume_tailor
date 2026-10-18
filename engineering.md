# Resume Tailor — Engineering Design Doc

**Author:** Staff Software Engineer  
**Status:** Draft v0.1  
**Last updated:** October 17, 2026  
**Reviewers:** Team Lead, Staff Product Manager  

---

## 1. Summary

Resume Tailor is a single-process, lightweight web application that takes raw resume bullets and a target job description and returns 3–5 side-by-side rewritten bullets with explicit rationale tags and zero hallucinated facts. Following the reference architecture in `reference/moodjar-example/`, the backend is built with Python 3.12+, FastAPI, and the official `google-genai` SDK using `gemini-3-flash-preview` with native Pydantic structured output (`response_schema=TailorResponse`), while the frontend is a zero-build vanilla HTML/CSS/JavaScript single-page app served directly via FastAPI static file mounting. The defining technical challenge is enforcing absolute truthfulness (preventing the model from fabricating skills, metrics, or tools) via a dual-layer strategy: strict negative prompt constraints combined with a deterministic, zero-LLM post-generation validation audit. The app runs from the project root via `uv run uvicorn backend.main:app --reload` (or from within `backend/` via `uv run uvicorn main:app --reload`).

## 2. Assumptions

- **Target scale:** Single-instance deployment handling 100–500 active sessions per day for v1. No horizontal scaling or distributed coordination required.
- **Latency budget:** End-to-end response time under 4 seconds p95 (Gemini model generation ≤ 3.0s with a 15000ms hard timeout, network and serialization ≤ 1.0s).
- **Platform:** Modern desktop and mobile web browsers (Chrome, Safari, Firefox, Edge) supporting standard ES6+ and the Clipboard API.
- **Cost ceiling:** Model cost under $0.005 per generation request using `gemini-3-flash-preview` with compact prompt engineering.
- **Out of scope:** Database persistence, background job queues (Celery/Redis), document parsing binaries (pdftotext/antiword), and client-side build pipelines (npm/vite).

## 3. Goals & non-goals

**Goals (v1):**
- Single-endpoint API (`POST /api/tailor`) accepting raw text inputs (max 12,000 characters per field) and returning 3–5 tailored bullet comparisons in structured JSON (or fewer if fewer relevant bullets exist; never padded).
- Strict prompt-level and programmatic truthfulness enforcement ensuring rewrites only rephrase verified facts from the user's original text.
- Static file serving of the single-page frontend directly from the FastAPI root (`/`), requiring only `uv run uvicorn backend.main:app --reload` to run locally from the project root.
- 100% testable core logic using `pytest` with mocked Gemini responses for instant, zero-cost CI test runs.
- Non-functional: p95 latency < 4.0s, availability ≥ 99.5% on single-node hosting.

**Non-goals (v1):**
- No user authentication, sessions, or API tokens for end users.
- No database storage, SQLite/PostgreSQL, or past query logs (completely stateless in-memory processing).
- No file uploads or document parsing (PDF, DOCX, RTF); users paste text directly.
- No background workers or webhooks; synchronous request/response model only.
- No automated browser E2E test suites (Cypress/Playwright) in v1.

## 4. Architecture

```mermaid
flowchart LR
  subgraph Client ["Client (Browser)"]
    UI["Single-Page App (Vanilla HTML/CSS/JS)"]
    SampleBtn["Try a Sample (Local Data)"]
    Clipboard["Clipboard API (1-Click Copy)"]
  end

  subgraph Server ["FastAPI Backend (Port 8000)"]
    Static["StaticFiles Mount (/)"]
    API["POST /api/tailor"]
    Validator["Input Sanitizer (422 on &lt;15 or &gt;12,000 chars)"]
    PromptBuilder["System Prompt (Anti-Hallucination Directives)"]
    Audit["Programmatic Truthfulness Audit (Regex / Number / Tool Check)"]
  end

  subgraph Cloud ["Google AI Cloud"]
    Gemini["Gemini API (gemini-3-flash-preview via google-genai SDK, 15000ms timeout)"]
  end

  UI -->|HTTP GET /| Static
  SampleBtn --> UI
  UI -->|POST /api/tailor (JSON)| API
  API --> Validator
  Validator --> PromptBuilder
  PromptBuilder -->|generate_content (response_schema=TailorResponse)| Gemini
  Gemini -->|Structured JSON| Audit
  Audit --> API
  API -->|200 OK (3-5 Truthful Bullets)| UI
  UI --> Clipboard
```

**What's here:**
- **FastAPI Core:** Serves frontend assets and provides `/api/tailor` and `/api/health`.
- **`google-genai` Client:** Fresh per-request client instance communicating with `gemini-3-flash-preview` using `response_mime_type="application/json"`, `response_schema=TailorResponse`, and a 15000ms timeout (`http_options={"timeout": 15000}`).
- **Dual Truthfulness Guardrail:** System prompt instructions paired with a deterministic post-generation Python audit function to flag any fabricated metrics or unmentioned technologies.
- **Frontend SPA:** Single `index.html`, `style.css`, and `app.js` with zero build tools or package managers.

**What's deliberately NOT here:**
- No Redis / Memcached: Inputs and jobs are unique; caching offers near-zero hit rate for novel resume/JD pairs while adding operational overhead.
- No Celery / BullMQ: Generation completes well within HTTP timeout boundaries (15000ms client timeout), eliminating async polling complexity.
- No SQLAlchemy / ORM / Database: Completely stateless; user resumes are never persisted, respecting candidate privacy.
- No Node.js / Webpack / Vite: Eliminates node toolchain dependencies; uses native modern browser capabilities.

## 5. Key components

### 1. API Server (`backend/main.py`)
- **Responsibility:** Request routing, input validation (yielding HTTP 422 for violations), exception handling, and static file serving.
- **Tech choice:** FastAPI + Uvicorn.
- **Why this choice:** Proven in `reference/moodjar-example/`, native ASGI performance, automatic OpenAPI schema generation, and zero friction.
- **Interface:** Exposes `POST /api/tailor` and `GET /api/health`. Can be run from root via `uv run uvicorn backend.main:app --reload` or inside `backend/` via `uv run uvicorn main:app --reload`.

### 2. Prompt Configuration & Guardrails (`backend/prompts.py`)
- **Responsibility:** Defines system instructions, few-shot examples, and rules enforcing strict truthfulness.
- **Tech choice:** Python module with templated system prompts and explicit constraints.
- **Why this choice:** Keeps AI behavior decoupled from HTTP routing logic and easily unit-testable.
- **Interface:** `SYSTEM_PROMPT: str`, `create_user_prompt(resume_text: str, jd_text: str) -> str`.

### 3. Programmatic Truthfulness Audit (`backend/truth_checker.py`)
- **Responsibility:** Cheap, deterministic verification function running with zero LLM overhead. Runs three checks: (1) scans `tailored_bullet` for any numbers or percentages (`\b\d+(?:\.\d+)?%?`) not present in `original_bullet`; (2) to prevent false-flagging normal rewrites (such as sentence-starting verbs like "Improved"), ignores the first word of the sentence and common English words, only flagging capitalized terms, proper nouns, or acronyms that appear in neither `original_bullet` nor the rest of the candidate's `full_resume_text`; (3) flags lowercase domain, team, or role nouns (e.g. `design`, `engineering`, `marketing`, `leadership`) that the model may silently inject when those words appear in neither `original_bullet` nor `full_resume_text`.
- **Tech choice:** Pure Python with regular expressions, word tokenization, and set operations.
- **Why this choice:** Instant execution (<1ms), zero API cost, prevents false positives on natural sentence capitalization while reliably catching metric hallucinations (e.g. adding "by 35%") and ungrounded tech stack inventions.
- **Interface:** `verify_factual_integrity(original_bullet: str, tailored_bullet: str, full_resume_text: str = "") -> tuple[bool, list[str]]`.

### 4. Gemini Integration Service (`backend/gemini_service.py`)
- **Responsibility:** Instantiates the official `genai.Client`, invokes `models.generate_content` using `gemini-3-flash-preview` with `response_schema=TailorResponse` and `http_options={"timeout": 15000}`, runs fallback string cleaning if needed, and triggers the programmatic truthfulness audit.
- **Tech choice:** `google-genai` SDK.
- **Why this choice:** Matches `reference/moodjar-example/backend/main.py`, supported natively with Google Gemini models.
- **Interface:** `async def generate_tailored_bullets(resume_text: str, jd_text: str) -> TailorResponse`.

### 5. Single-Page Application (`frontend/index.html`, `frontend/app.js`, `frontend/style.css`)
- **Responsibility:** Render dual inputs with 12,000-character counters, handle "Try a sample" quick-fill, handle mobile scroll, display loading skeletons, render side-by-side comparison cards, and handle clipboard copying.
- **Tech choice:** Vanilla JavaScript (ES6+), CSS Grid/Flexbox, native DOM APIs.
- **Why this choice:** Instant load times, zero build step, no npm dependency tree, trivial to maintain.
- **Interface:** DOM event listeners (`submit`, `click`), `fetch('/api/tailor')`, `navigator.clipboard.writeText()`.

## 6. Data model

### Backend Schemas (Pydantic v2)

```python
from pydantic import BaseModel, Field

class TailorRequest(BaseModel):
    resume_text: str = Field(..., min_length=15, max_length=12000, description="Raw resume bullets or experience text")
    job_description: str = Field(..., min_length=15, max_length=12000, description="Target job posting text")

class BulletComparison(BaseModel):
    original_bullet: str = Field(..., description="The original bullet point from the resume")
    tailored_bullet: str = Field(..., description="The sharpened, job-aligned rewrite using ONLY original facts")
    why: str = Field(..., description="One-line explanation of the keyword mapping and structural improvement")

class TailorResponse(BaseModel):
    bullets: list[BulletComparison] = Field(..., min_length=1, max_length=5, description="3 to 5 tailored bullets; fewer if fewer relevant bullets exist")

class HealthResponse(BaseModel):
    status: str = "ok"
```

### Frontend State Object (JavaScript)

```typescript
// Conceptual TypeScript interface for client-side state
interface AppState {
  isLoading: boolean;
  error: string | null;
  bullets: Array<{
    original_bullet: string;
    tailored_bullet: string;
    why: string;
  }>;
}
```

## 7. API surface

### `POST /api/tailor`

- **Description:** Accepts resume and job description text, returning 3–5 tailored bullet comparisons (or fewer if fewer relevant bullets exist; never padded with weak rewrites).
- **Input:**
  ```json
  {
    "resume_text": "• Worked on API performance and fixed database queries\n• Built automated test suite for order processing",
    "job_description": "We are seeking a Backend Engineer with experience in API performance, database optimization, and automated testing."
  }
  ```
- **Output:**
  ```json
  {
    "bullets": [
      {
        "original_bullet": "Worked on API performance and fixed database queries",
        "tailored_bullet": "Improved API performance by optimizing database queries.",
        "why": "Rephrased to emphasize proactive database optimization matching the job posting's API performance requirements."
      },
      {
        "original_bullet": "Built automated test suite for order processing",
        "tailored_bullet": "Developed automated test suite for order processing, ensuring backend reliability.",
        "why": "Highlighted automated testing alignment with the target role's backend reliability focus."
      }
    ]
  }
  ```
- **Errors:**
  - `422 Unprocessable Entity`: Input validation failure (fewer than 15 characters, exceeds 12,000 characters, or missing fields). Consistent with Pydantic standard error format.
  - `502 Bad Gateway`: Gemini API unreachable, timed out (>15000ms), or returned malformed data.
  - `500 Internal Server Error`: Internal runtime error.
- **Latency budget:** p95 < 4.0s end-to-end.

### `GET /api/health`

- **Description:** Verifies service health and API key presence.
- **Output:** `{"status": "ok"}`

## 8. Key trade-offs (with rejected alternatives)

### Decision 1: Model Selection
- **Chose:** `gemini-3-flash-preview`
- **Considered:** `gemini-2.5-flash`, `gemini-2.5-pro`
- **Why we picked this:** `gemini-3-flash-preview` matches the reference implementation in `reference/moodjar-example/backend/main.py`. It is currently available, exhibits superior adherence to negative constraints and structured output schemas (`response_schema`), and returns completions well under our 3.0s model latency budget at minimal cost.

### Decision 2: Truthfulness Enforcement Architecture
- **Chose:** Dual-layer enforcement (Strict prompt rules + programmatic regex/token truthfulness audit)
- **Considered:** Second LLM validation call, prompt-only enforcement
- **Why we picked this:** A second LLM call adds 2–3 seconds of latency and doubles API costs. Relying solely on prompt instructions leaves an open risk of subtle hallucinations. Combining strict prompt rules with a fast (<1ms), deterministic Python audit function (`verify_factual_integrity`) catches unmentioned numbers (like "by 35%") and invented tools with zero external latency.

### Decision 3: Frontend Architecture
- **Chose:** Vanilla HTML/CSS/JS served statically via FastAPI
- **Considered:** React / Next.js / Vite SPA
- **Why we picked this:** This is a single-page, single-action tool. Introducing npm, React, package bundlers, and node build dependencies adds immense setup and deployment overhead for zero user benefit. Vanilla JS with CSS Grid delivers 100/100 Lighthouse performance, instant page loads, and zero build tool maintenance.

## 9. Risks & unknowns

- **Model Hallucination of Metrics or Skills** — *Likelihood: Low/Medium* — **Mitigation:** The system prompt explicitly commands *"NEVER invent metrics, numbers, or percentages"*. Furthermore, `verify_factual_integrity` deterministically inspects the generated output and flags any unmentioned metrics before response delivery. Set `temperature=0.2`.
- **Input Text Overflow** — *Likelihood: Low* — **Mitigation:** Pydantic validation strictly enforces `max_length=12000` on both fields, rejecting oversized payloads with HTTP 422. The frontend counts characters and blocks submission above 12,000 characters.
- **Gemini API Timeout or Rate Limiting** — *Likelihood: Low* — **Mitigation:** Gemini API requests configure a strict 15000ms timeout (`http_options={"timeout": 15000}`). Upstream errors are caught and surfaced as HTTP 502 with actionable client retry guidance.
- **Clipboard API Browser Restrictions** — *Likelihood: Low* — **Mitigation:** The copy button uses `navigator.clipboard.writeText` inside an explicit user click handler, with a fallback to `document.execCommand('copy')` if running in restricted iframes.

## 10. Testing strategy

This test plan is directly consumed by the `test-driven-dev` skill to author production tests in `backend/tests/`.

### Unit Tests (Pure Functions & Parsers)
- **`test_input_validation_min_length`:** Verify that `TailorRequest` raises a validation error (HTTP 422) when `resume_text` or `job_description` has fewer than 15 characters.
- **`test_input_validation_max_length`:** Verify that `TailorRequest` raises a validation error (HTTP 422) when text exceeds 12,000 characters.
- **`test_clean_markdown_json`:** Verify that `_clean_json_text()` correctly strips ````json ... ```` fences, leading/trailing whitespace, and handles raw JSON strings as a fallback.
- **`test_tailor_response_validation`:** Verify that `TailorResponse` accepts valid 1–5 bullet objects and rejects objects missing `original_bullet`, `tailored_bullet`, or `why`.
- **`test_prompt_construction`:** Verify that `create_user_prompt()` properly formats and encapsulates the resume text and job description within clear markdown boundaries.
- **`test_system_prompt_contains_anti_hallucination_rules`:** Verify that `SYSTEM_PROMPT` contains `"NEVER invent"` and explicit negative constraints against fabricating tools, metrics, and numbers.
- **`test_verify_factual_integrity_sentence_capitalization`:** Verify that standard sentence-initial capitalization (e.g. starting with "Improved" when the original bullet started with "Worked") does NOT false-flag as an unmentioned tool or proper noun.
- **`test_verify_factual_integrity_catches_invented_metrics`:** Verify that `verify_factual_integrity(original="Worked on API performance and fixed database queries", tailored="Improved API performance by 35% by optimizing database queries.")` flags `"35%"` as an invented metric and returns `is_valid=False`.
- **`test_verify_factual_integrity_allows_truthful_rewrite`:** Verify that `verify_factual_integrity(original="Worked on API performance and fixed database queries", tailored="Improved API performance by optimizing database queries.")` returns `is_valid=True` with an empty discrepancy list.
- **`test_verify_factual_integrity_allows_terms_from_full_resume`:** Verify that capitalized terms or tools present in the candidate's broader resume text (e.g., "Python" mentioned in another section of `full_resume_text`) are permitted and not false-flagged.
- **`test_verify_factual_integrity_catches_invented_tools`:** Verify that when `tailored` introduces unmentioned technologies or acronyms (e.g., "PostgreSQL" or "AWS" when neither appears in the original bullet nor anywhere in `full_resume_text`), the audit detects and flags the tool name.
- **`test_verify_factual_integrity_catches_invented_domain_nouns`:** Verify that injected lowercase domain/org nouns are flagged. Exact example: `original="Collaborated with product team"`, `tailored="Partnered with cross-functional product and design teams"` — the word `design` does not appear in the original bullet or the full resume, so the audit must return `is_valid=False` and include `"design"` in the discrepancy list.

### Integration Tests (API Endpoints via `TestClient`)
- **`test_tailor_endpoint_success`:** Send a valid payload to `POST /api/tailor` with the Gemini API call mocked to return sample valid JSON. Assert HTTP 200, content-type `application/json`, and assert response matches `TailorResponse` schema with valid items.
- **`test_tailor_endpoint_validation_error`:** Send payload with fewer than 15 characters or missing `job_description`. Assert HTTP 422 Unprocessable Entity.
- **`test_tailor_endpoint_exceeds_max_length`:** Send payload with >12,000 characters. Assert HTTP 422 Unprocessable Entity.
- **`test_tailor_endpoint_gemini_error_handling`:** Mock Gemini API raising an exception or timing out (>15000ms). Assert `POST /api/tailor` returns HTTP 502 with a user-friendly error message.
- **`test_health_endpoint`:** Send `GET /api/health`. Assert HTTP 200 and `{"status": "ok"}`.

### Deliberately NOT Tested (and why)
- **Live Gemini API Calls in CI:** Non-deterministic, requires network credentials, incurs cost, and risks flakiness; all CI tests use mocked client responses.
- **Visual CSS Layout & Animation Timing:** Visual styling and card transitions are verified manually in-browser; adding headless browser suites would violate our lightweight v1 scope.
- **Native Clipboard OS Integration:** Interacting with the operating system clipboard in headless CI environments requires fragile OS permissions and is omitted.

## 11. How the Prompt and Audit Enforce Truthfulness

Truthfulness is guaranteed through a combined prompt and algorithmic verification pipeline:

### 1. System Prompt Anti-Hallucination Directives
```python
SYSTEM_PROMPT = """You are an elite, truth-bound resume editor. Your sole mission is to tailor a candidate's existing experience bullets to align with a target job description.

CRITICAL TRUTHFULNESS DIRECTIVES:
1. STRICT FACTUAL BOUNDARY: You may ONLY use facts, tools, programming languages, companies, and quantifiable metrics explicitly mentioned in the candidate's original bullets.
2. ABSOLUTELY ZERO INVENTIONS:
   - NEVER invent metrics, numbers, or percentages (e.g., if the user wrote "improved speed", NEVER write "reduced latency by 35%").
   - NEVER invent tools or technologies (e.g., if the user did not mention Docker, do NOT add Docker, even if the job description repeatedly asks for Docker).
   - NEVER invent leadership responsibilities or job titles not in the text.
3. ALIGNMENT STRATEGY:
   - Identify the top 3 to 5 most relevant bullets in the resume that correspond to requirements in the job description (return fewer if fewer relevant bullets exist; NEVER pad with weak rewrites).
   - Rephrase each bullet using strong active verbs and relevant industry terminology already justified by their experience.
   - Front-load the action and the real result.
4. RATIONALE TAG: For each rewrite, provide a concise 1-line 'why' explaining which JD requirement was targeted and what structural improvement was made.
"""
```

### 2. Programmatic Post-Generation Audit (`verify_factual_integrity`)
Before any response is returned to the client, the backend runs each candidate rewrite through `verify_factual_integrity()`:
1. **Numbers and Metrics Check:** Extracts all numbers and percentages (`\b\d+(?:\.\d+)?%?`) from `tailored_bullet` and confirms every detected number exists in `original_bullet`.
2. **Technology and Acronym Check:** Identifies capitalized terms, acronyms, or proper nouns. To avoid false-flagging normal rewrites, it ignores the first word of the sentence (sentence-casing) and common English words. It permits any term that appears in either the specific `original_bullet` or the broader `full_resume_text`, flagging only terms found in neither.
3. **Domain / Org-Noun Check:** Flags new lowercase domain, team, or role nouns that the model may silently inject — words such as `design`, `engineering`, `marketing`, `leadership`, `finance`, `legal`, `operations`, `product`, `sales`, `data`, `research`, `strategy`, `security` — when they do not appear in either `original_bullet` or `full_resume_text`. This closes the gap where a model rewrites *"Collaborated with product team"* as *"Partnered with cross-functional product and design teams"*: the word `design` is lowercase and passes the capitalization check, but it is a newly invented organizational domain not found in the original text.
4. **Audit Failure Policy:** If a tailored bullet fails the audit (e.g. contains an unverified metric like "35%", an unmentioned tool, or an invented domain noun like "design"), **that bullet is dropped from the response**. If *every* bullet fails the audit (resulting in 0 valid bullets), the backend logs the failure and returns an **HTTP 502 Bad Gateway** with the user-friendly retry message: *"Unable to tailor bullets truthfully right now. Your text is safe — click Retry to try again."*

## 12. Rollout & monitoring

- **Execution Command:**
  - From project root: `uv run uvicorn backend.main:app --reload`
  - From backend directory: `cd backend && uv run uvicorn main:app --reload`
- **Monitoring (Top 3 Signals):**
  1. **HTTP 5xx Rate:** Any spike in 500 or 502 responses alerts on Gemini API connectivity, timeouts (>15000ms), or schema degradation.
  2. **Latency (p95):** Latency exceeding 4.5 seconds indicates upstream API throttling or payload bloat.
  3. **422 Validation Rate:** Monitors whether users are hitting character thresholds (<15 or >12,000) or sending malformed payloads.
- **Rollback:** Stateless single artifact; immediate rollback to previous git commit.

## 13. Cost & capacity

- **Model Pricing:** `gemini-3-flash-preview` is ~$0.075 per million input tokens and ~$0.30 per million output tokens.
- **Per-Request Cost:** Average request is ~1,000 input tokens + ~400 output tokens = ~$0.0002 per generation.
- **Monthly Budget at v1 Scale (500 runs/day = 15,000 runs/month):**
  $15,000 \times \$0.0002 = \$3.00\text{/month}$ for LLM inference.
- **What breaks at 10× scale:** Gemini API tier rate limits (RPM). At 10×, we would request a quota increase from Google Cloud.

## 14. Open questions (Resolved)

- [x] **Structured output support:** Resolved to use `response_schema=TailorResponse` with `response_mime_type="application/json"` in `types.GenerateContentConfig`. Retain `_clean_json_text` as a resilient fallback parser.
- [x] **Request timeout:** Resolved to set a 15-second hard timeout on Gemini client requests (`http_options={"timeout": 15000}`) to satisfy the minimum API deadline requirement.

## 15. Out of scope (will not do)

- **No Authentication Service:** No user tokens, JWTs, OAuth, or user records.
- **No Database Engine:** No SQLite, PostgreSQL, or disk-backed databases.
- **No Document Parsing Libraries:** No `pypdf`, `python-docx`, or text extraction OCR libraries.
- **No Background Task Queues:** No Redis, Celery, or background worker processes.
- **No Full Resume Re-formatting:** No resume layout builders, template pickers, or styling engines.
