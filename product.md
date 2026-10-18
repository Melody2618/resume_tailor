# Resume Tailor — Product Design Doc

**Author:** Staff Product Manager  
**Status:** Draft v0.1  
**Last updated:** October 17, 2026  
**One-liner:** Turn raw resume bullets into 3–5 high-impact, job-aligned bullets with side-by-side proof and zero hallucinated facts.

---

## 1. The user & the moment

- **Who:** An active job applicant tailoring their resume for a specific open role. They have real experience and accomplishments, but their existing bullets are either passive, buried under jargon, or missing the exact terminology prioritized in the target job description.
- **When:** 10 minutes before submitting an application. They have their resume open in one window and the job posting in another, feeling friction and uncertainty about how to rephrase their accomplishments to resonate with the hiring manager without lying.
- **Why now:** Generic AI resume tools either hallucinate fake achievements (which fail technical screeners) or demand bloated accounts, document parsing, and expensive subscription tiers. Candidates need instant, truthful, high-signal bullet upgrades with zero setup.

## 2. The contract (I/O)

- **Input:** Two plain text areas (each capped at 12,000 characters):
  1. Resume bullets (or raw experience text).
  2. Job description text.
  Plus a 1-click **"Try a sample"** button that instantly pre-fills both areas with realistic demo content.
- **Output:** A structured side-by-side comparison card deck presenting the top 3–5 most relevant rewritten bullets (or fewer if fewer relevant bullets exist; never padded with weak or fabricated rewrites):
  - **Left column:** Original bullet.
  - **Right column:** Tailored bullet (active voice, prioritized impact, matching keywords using strictly original facts).
  - **Upgrade rationale:** A 1-line "why" tag explaining the specific alignment (e.g., *"Rephrased to emphasize proactive database optimization matching the job posting's API performance requirements"*).
  - **Action:** A dedicated 1-click "Copy" button on every tailored bullet.
- **The loop:** One-shot transformation. The user pastes or loads sample data, clicks "Tailor Bullets", reviews the side-by-side upgrades, copies the winning bullets into their resume, and leaves. No multi-page flow.

## 3. The magical moment

> "It kept every single fact in my experience 100% true, but framed my accomplishments in the exact language the hiring manager is looking for."

## 4. Scope: what we ARE building (v1)

- Two clean, unencumbered text areas with helpful placeholders and character counts, enforcing a strict 12,000-character cap per box.
- A "Try a sample" quick-fill button that immediately populates both text areas with high-quality demo data.
- An always-clickable "Tailor Bullets" action trigger with immediate inline validation and an active loading state.
- Side-by-side comparison layout presenting the top 3–5 most relevant bullets (or fewer if fewer relevant bullets exist, never padded).
- A 1-line "why" rationale badge for each bullet explaining the specific keyword and impact alignment.
- A 1-click "Copy" button for each tailored bullet with immediate visual feedback ("Copied!").
- Strict truthfulness guardrails: rewrites use only facts, metrics, and tools present in the original bullets.

## 5. Scope: what we are NOT building

- **No accounts, login, or authentication** — Eliminates friction; users should get value in under 15 seconds without creating credentials.
- **No database, saved history, or past results** — Completely stateless per session; avoids privacy concerns and storage complexity.
- **No file uploads (PDF/Word) and no resume export formatting** — Pasting text avoids brittle PDF parsers and document layout bugs; keeps the interface focused on content over layout.
- **No full resume rewrites** — Ruthlessly restricted to the top 3–5 highest-impact bullets; full-page rewrites introduce hallucination and dilute focus.
- **No padding with weak rewrites** — If the resume has only 1 or 2 bullets relevant to the role, the system returns only those; it never invents or forces irrelevant rewrites to reach an arbitrary count.
- **No job URL scraping** — Avoids broken scrapers, paywalls, dynamic JavaScript job boards, and bot blocks; pasted text is 100% reliable.
- **No cover letters, interview prep, or application tracking** — Eliminates scope creep; this tool solves one single problem exceptionally well.
- **No ATS score simulator or match percentages** — Synthetic ATS scores create false anxiety and encourage keyword stuffing; concrete before/after comparisons provide real utility.
- **No multi-page navigation or wizards** — The entire lifecycle exists on a single responsive view.

## 6. The signature detail

The **"Truthful Upgrade" Rationale**. Each tailored bullet pairs with an explicit one-line rationale badge detailing the exact keyword mapped from the job description and the structural improvement made (e.g., *"Why: Rephrased to emphasize proactive database optimization matching the job posting's API performance requirements"*). This transparency assures the user that their accomplishments were sharpened rather than fabricated.

## 7. Success: how we know it worked

- **Primary:** ≥60% of sessions that generate rewrites copy at least one tailored bullet to the clipboard within 60 seconds.
- **Secondary:** ≥30% of first-time visitors click "Try a sample" to test the tool before pasting their own resume.
- **What we're NOT measuring:** Account signups, session duration (shorter is better), or return frequency.

## 8. Open questions (Resolved)

- [x] **Character limit per input:** Resolved at 12,000 characters (~3,000 words) per box, matching backend constraints. Any text exceeding 12,000 characters displays an inline warning and disables the submit button until trimmed.
- [x] **Output volume and relevance:** Resolved at 3–5 bullets depending strictly on relevance. If the candidate's background only yields 1–2 relevant bullets, return only those; never pad with low-relevance or hallucinated rewrites.

## 9. Handoff

- **For UX:** The side-by-side comparison must stack cleanly on mobile (Original over Tailored) without crushing text into narrow columns.
- **For Eng:** Strict structured output schema and programmatic truthfulness guardrails must execute with sub-4-second p95 latency.
