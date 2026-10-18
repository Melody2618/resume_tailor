# Resume Tailor

Paste your resume bullets and a job description — get back 3–5 rewritten bullets that match the role's language, in a side-by-side before/after view, with a one-line explanation of every change and a one-click copy button. **No accounts. No uploads. No hallucinated facts.**

---

## What it does

You paste two things:

1. **Your resume bullets** — a few lines of your real experience.
2. **The job description** — the posting you're applying to.

Click **"Tailor Bullets"** and within seconds you see the top 3–5 most relevant rewrites side-by-side with your originals. Each rewrite:

- Uses **only facts already in your text** — no invented metrics, tools, or achievements.
- Surfaces keywords from the job description to help your resume read fluently to the hiring manager.
- Includes a one-line **"why"** badge explaining exactly what was changed and why it helps.
- Has a **"Copy"** button so you can grab it straight into your resume.

Not sure what to paste? Hit **"Try a sample"** to see a live demo with prefilled content.

### What it deliberately doesn't do

- No login, accounts, or API keys for users.
- No saved history — your resume text is never stored anywhere.
- No file uploads (PDF/Word) — just paste plain text.
- No full resume rewrites — only the highest-signal bullets.
- No ATS scoring, cover letters, or URL scraping.
- No multi-step wizard — the entire flow is one page.

---

## Tech stack

| Layer    | Technology                                         |
|----------|----------------------------------------------------|
| Backend  | Python 3.12+, FastAPI, Uvicorn                     |
| AI       | Google Gemini (`gemini-3-flash-preview`) via `google-genai` SDK |
| Frontend | Vanilla HTML / CSS / JavaScript (no build step)    |
| Deps     | `uv` (Python package manager)                      |

---

## Install on a new machine

### Prerequisites

- **Python 3.12+** — [python.org](https://python.org)
- **`uv`** — fast Python package manager

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd coding-jam-project
```

### 2. Install Python dependencies

```bash
cd backend
uv sync
```

This reads `pyproject.toml` and installs everything (FastAPI, Uvicorn, google-genai, etc.) into a local `.venv`.

### 3. Set your Gemini API key

Create `backend/.env` (this file is git-ignored — never commit it):

```
GEMINI_API_KEY=your_api_key_here
```

Get a free key at [aistudio.google.com](https://aistudio.google.com).

---

## Run the dev server

From the **project root**:

```bash
cd backend
uv run uvicorn main:app --reload
```

Or equivalently from the project root directory:

```bash
uv run uvicorn backend.main:app --reload --app-dir backend
```

Then open **[http://localhost:8000](http://localhost:8000)** in your browser.

The `--reload` flag restarts the server automatically when you save a Python file.

---

## Run the tests

```bash
cd backend
uv run pytest -v
```

All 16 tests run with mocked Gemini responses — no API key required, no network calls, deterministic and instant.

---

## Project structure

```
coding-jam-project/
├── backend/
│   ├── main.py              # FastAPI app — routing, validation, static serving
│   ├── gemini_service.py    # Gemini API client + structured output call
│   ├── prompts.py           # System prompt + anti-hallucination directives
│   ├── truth_checker.py     # Deterministic post-generation truthfulness audit
│   ├── schemas.py           # Pydantic request/response models
│   ├── tests/
│   │   ├── test_api_integration.py
│   │   ├── test_prompts_and_schemas.py
│   │   └── test_truth_checker.py
│   ├── pyproject.toml
│   └── .env                 # ← you create this (git-ignored)
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── product.md               # ← Product design doc (source of truth)
├── ui.md                    # ← UX design doc (source of truth)
├── engineering.md           # ← Engineering design doc (source of truth)
└── README.md
```

---

## Design docs

These three files are the **source of truth** for every decision in this project. Read them before making any significant change.

| Doc | What it covers |
|-----|---------------|
| [`product.md`](product.md) | What we're building, who it's for, the exact I/O contract, success metrics, and the full list of non-goals. |
| [`ui.md`](ui.md) | UI states (empty, loading, error, results), component layout, mobile behaviour, copy/interaction details. |
| [`engineering.md`](engineering.md) | Architecture diagram, key components, data models, API surface, truthfulness enforcement strategy, testing strategy, risks, and open questions. |
