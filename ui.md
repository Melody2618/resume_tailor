# Resume Tailor — UX Design Doc

**Designer:** Staff Product Designer  
**Status:** Draft v0.1  
**Last updated:** October 17, 2026  

---

## 1. The design bet

We are betting that side-by-side comparative proof carries the entire emotional weight and credibility of the product. Rather than asking users to trust an opaque "AI rewrite," we present the original bullet directly next to the tailored version with an explicit rationale tag. If users can scan both columns in under 3 seconds and verify that their original metrics remain untouched while the impact is sharpened, they will trust and copy the result immediately.

## 2. The defining interaction

The user pastes their text (or clicks **"Try a sample"** to watch both input boxes populate instantly with realistic text) and clicks **"Tailor Bullets"**. The primary button transitions into an unobtrusive pulsing loading state with the label *"Tailoring top bullets..."*. After ~2.5 seconds, the page smoothly scrolls down and reveals 3–5 comparison cards in a clean staggered entrance. Each card features the original bullet in muted charcoal on the left and the sharpened bullet in crisp dark slate on the right, punctuated by a prominent green-tinted rationale badge (*"Why: ..."*). The user clicks the **"Copy"** button on the tailored bullet; the button icon instantly flips to a checkmark with the label *"Copied!"* for 1.5 seconds. Total interaction time: ~4 seconds. Feels like: having an elite executive resume editor point directly at your draft and say, *"Here is how we say this so it lands."*

## 3. Screen inventory

v1 consists of exactly **one single-page responsive view**:

- **Resume Tailor Workspace** — A clean, focused single-page tool containing the header with sample loader, dual input text areas, tailor action trigger, and inline side-by-side comparison results.

## 4. Screen-by-screen specs

### Resume Tailor Workspace

**Purpose:** Allow users to provide their raw bullets and target job description, trigger AI tailoring, and immediately inspect and copy truthful, high-impact bullet rewrites.

**Layout (top to bottom):**

1. **Header & Context Bar**
   - App title (`Resume Tailor`) and clean one-line descriptor (*"Upgrade your bullets for the job. 100% truthful, zero hallucinated facts."*).
   - Right-aligned quick action button: `Try a sample` (ghost pill button with a subtle spark icon).
2. **Dual Input Grid (Side-by-side on desktop, stacked on mobile)**
   - **Left Column: Resume Experience Bullets**
     - Section label: `1. Your Experience Bullets` with helper microcopy (*"Paste 3–10 bullets from your current resume (max 12,000 characters)"*).
     - Textarea: Clean rounded container, min-height 220px, monospace-friendly sans font, placeholder text with real bullet examples.
     - Character/word count counter at bottom right with max indicator (`0 / 12,000`).
   - **Right Column: Target Job Description**
     - Section label: `2. Target Job Description` with helper microcopy (*"Paste the responsibilities and requirements (max 12,000 characters)"*).
     - Textarea: Identical styling and height to the resume box.
     - Character/word count counter at bottom right with max indicator (`0 / 12,000`).
3. **Action Bar**
   - Centered primary button: `Tailor Bullets` (solid accent background, high-contrast text, always clickable; triggers inline validation if inputs are invalid; keyboard accessible via `Cmd/Ctrl + Enter`).
   - Clear inputs text link (`Clear all`) for quick reset.
4. **Results Section (Appears below action bar once triggered)**
   - Section header: `Tailored Bullets (Top 3–5)` with a subtitle reminding the user: *"Original facts preserved. Phrasing sharpened for the role."* (Displays fewer than 3 if only 1–2 bullets are relevant; never pads with weak rewrites).
   - List of 3–5 Comparison Cards:
     - Card container: Subtle border, soft shadow, two-column split on desktop / stacked Original over Tailored on mobile.
     - Left sub-panel: Header `ORIGINAL`, muted background, italicized/softer font weight.
     - Right sub-panel: Header `TAILORED`, crisp high-contrast text, slightly elevated background.
     - Top-right of Tailored panel: `Copy` button (icon + text, accessible keyboard target).
     - Bottom footer of card: Full-width `Why this works` tag (tinted pill with brief rationale text).

**Key interactions:**

- Click `Try a sample` → Both text areas populate simultaneously with pre-crafted demo data; on mobile/small screens, the view smooth-scrolls down to the `Tailor Bullets` button to cue the immediate next action.
- Click `Tailor Bullets` (or press `Cmd/Ctrl + Enter`) → If valid, button enters loading state; results area displays skeleton loader if first run, or updates smoothly. If invalid, displays inline validation alerts without submitting.
- Click `Copy` on any tailored bullet → Text copies to system clipboard; button swaps to checkmark + *"Copied!"* for 1500ms before returning to default state.
- Click `Clear all` → Clears both text areas and hides results section; focuses the first textarea.

**States:**

- **Default / Initial State:** Both text areas are empty with muted placeholder prompts (`• Led team of 4 engineers...` and `Looking for a Senior Software Engineer with...`). The results section is hidden. The `Tailor Bullets` button is always present and clickable.
- **Empty / Validation State:** If the user clicks `Tailor Bullets` while either text area has fewer than 15 characters, submission is blocked and inline validation alerts highlight the offending textarea with an amber border and concise notice (*"Please enter at least 15 characters of your experience bullets"* or *"Please enter at least 15 characters of the job description"*).
- **Edge / "Too Much Text" State:** If either input exceeds the 12,000-character limit, an amber warning badge appears directly beneath the offending box: *"Character limit exceeded (12,000 max). Please trim your text to continue."* The `Tailor Bullets` button is disabled and blocked from submission until the text is within the 12,000-character limit. No silent soft-truncation.
- **Loading State:** The `Tailor Bullets` button is disabled during an in-flight request, showing a spinning ring indicator and the text *"Tailoring top bullets..."*. Below the button, 3 skeleton comparison cards render with a smooth shimmer gradient, maintaining layout stability without layout shift.
- **Results State:** The skeleton cards transition into rendered comparison cards. The view smoothly scrolls so the top comparison card is positioned in comfortable reading view. Each card displays original bullet, tailored bullet, rationale badge, and copy button.
- **Error State:** If the network request fails or the backend rejects the input (e.g. HTTP 422, 502), an inline error banner appears directly above the results area with a retry trigger: *"Unable to tailor bullets right now. Your text is safe — click Retry to try again."* Inputs remain intact so no user work is lost.

## 5. The user journey

A candidate arrives at Resume Tailor with 15 minutes before their application deadline. On the clean, focused page, they immediately see the two text areas and notice the **"Try a sample"** button in the header. Curious about how it works without committing their own data yet, they click "Try a sample". Instantly, realistic software engineering bullets appear in the left box and a target Job Description appears in the right box. On their mobile device, the screen smoothly scrolls to highlight the "Tailor Bullets" button.

They tap the blue **"Tailor Bullets"** button. The button displays a gentle pulse, and skeleton cards shimmer below. Within 2.5 seconds, tailored bullets appear. The user reads the first card: on the left, their original bullet *"Worked on API performance and fixed database queries"*; on the right, *"Improved API performance by optimizing database queries."* Below it, the rationale badge clarifies: *"Why: Rephrased to emphasize proactive database optimization matching the job posting's API performance requirements."*

Seeing that the tool strictly preserved their original achievements without hallucinating fake technologies, unmentioned tools, or fabricated metrics, the user's skepticism vanishes. They click "Clear all", paste their actual bullet points and target job description from their open tabs, and click "Tailor Bullets" again. Within seconds, their tailored bullets appear. They click "Copy" on each tailored card, paste them directly into their resume document, and submit their application with total confidence.

## 6. Component & visual notes

The visual language is a clean, editorial **"one-page proposal"** — the kind a thoughtful executive editor would hand you. No shadows, no gradients, no rounded "app" cards. Sections are separated by thin rules. Type and whitespace do the work.

### Layout
- **Sidebar (≈280px, soft sage `#D5E8E3`):** Holds the app title, tagline, "Try a sample", "Clear all", and the "Zero Hallucinated Facts" badge. Fixed on desktop; collapses to a horizontal top band on mobile (< 640px).
- **Main area (warm cream `#F3EEE7`):** All input text areas, the action bar, and results. Fills the remaining width.
- **Result cards:** Flat, white panels separated by a thin rule (`#D9D2C7`). No card shadows, no rounded borders on result rows.

### Color palette
| Token | Value | Usage |
|---|---|---|
| `--bg-sidebar` | `#D5E8E3` | Sidebar background |
| `--bg-main` | `#F3EEE7` | Main content area |
| `--bg-card` | `#FFFFFF` | Text area and result panel backgrounds |
| `--forest` | `#1F4D40` | Title, section headings, primary button, "Why" border |
| `--charcoal` | `#2B2B2B` | All body text |
| `--gray-helper` | `#7A7A7A` | Microcopy and helper labels |
| `--rule` | `#D9D2C7` | Dividers between sections and panels |
| `--error-*` | unchanged | Amber/red validation states (unchanged) |

### Typography
- **App title:** Large, bold, uppercase `RESUME TAILOR` in deep forest green (`#1F4D40`), preceded by a thick (4px) vertical forest-green bar.
- **Section headings** (`YOUR EXPERIENCE BULLETS`, `TARGET JOB DESCRIPTION`, `TAILORED BULLETS`, `ORIGINAL`, `TAILORED`): Small, bold, uppercase, `#1F4D40`, generous letter-spacing (`0.1em`).
- **Body text:** Dark charcoal (`#2B2B2B`), `Inter` sans-serif, line-height `1.6`.
- **Helper / microcopy:** Small, gray (`#7A7A7A`).

### Controls
- **Text areas:** White background (`#FFFFFF`), thin `1px` border (`#D9D2C7`), no border-radius (or very subtle `2px`). Focus ring uses forest green.
- **"Tailor Bullets" button:** Solid forest green (`#1F4D40`) fill, cream (`#F3EEE7`) text, square corners (`border-radius: 0`). Visually distinct and clearly enabled when idle — no opacity reduction unless actually loading.
- **"Try a sample" / "Clear all":** Plain text links in the sidebar; no pill or ghost-button styling.
- **Copy button:** Small, flat, forest-green text with an underline or minimal border. On copy: swaps to checkmark + "Copied!" for 1500ms.

### "Why this works" rationale
- Forest green italic text (`#1F4D40`) with a thin `3px` left border in forest green.
- **No pill or tinted background.** Reads like a margin annotation, not a badge.

### Motion
- Comparison rows enter with a 150ms fade-and-slide-up. Copy state transition is immediate.
- Full `@media (prefers-reduced-motion: reduce)` support: all animations disabled.

### Microcopy voice
- *"Tailor Bullets"* (not *"Unleash AI Magic"*).
- *"Why: Rephrased to emphasize proactive database optimization matching the job posting's API performance requirements."*
- *"Copied!"*

## 7. Accessibility & inclusion

- **Screen Readers:** Semantically structured `<main>`, `<section>`, and `<article>` tags. Each comparison card uses clear ARIA labels (`aria-label="Original bullet"` and `aria-label="Tailored bullet"`). The copy button announces state changes (`aria-live="polite"`).
- **Keyboard Navigation:** Full tab order flow: Resume textarea → Job Description textarea → "Tailor Bullets" button → Sequential "Copy" buttons. Shortcut `Cmd + Enter` / `Ctrl + Enter` submits from within text areas.
- **Visual & Contrast:** All body text meets WCAG AAA contrast ratio (≥7:1); rationale badge meets WCAG AA (≥4.5:1). Focus rings are prominently visible with high-contrast outlines.
- **Motion Preferences:** Full `@media (prefers-reduced-motion: reduce)` support disabling skeleton shimmering and card slide-ins.

## 8. What we are NOT designing

- **No login, registration, or profile modal** — No avatar, no password fields, no session menus.
- **No document preview / PDF viewer canvas** — No paper page rendering, zoom sliders, or pagination controls.
- **No ATS score dial or circular progress bars** — No gamified score meters or arbitrary percentages.
- **No rich-text WYSIWYG editor** — No bold/italic toolbars, font pickers, or margin adjusters.
- **No multi-tab or navigation drawer** — No sidebar navigation, settings panels, or history drawers.
- **No export format picker modal** — No Word, PDF, or Markdown download dialogs.

## 9. Open design questions (Resolved)

- [x] **Mobile viewport layout (<640px):** Resolved to stack Original directly over Tailored within each card (no toggle segment) with a distinct visual divider, preserving quick side-by-side verification on narrow screens.
- [x] **"Try a sample" interaction on small screens:** Resolved to automatically smooth-scroll the viewport down to the "Tailor Bullets" action button after loading sample text so mobile users immediately see the next step.

## 10. Handoff to engineering

The side-by-side comparison cards require rigid alignment between the original bullet, tailored bullet, and rationale badge across desktop viewports (`grid-template-columns: 1fr 1fr`), collapsing to stacked blocks on mobile (`<640px`). Form validation must block submission when inputs are <15 or >12,000 characters. Ensure that the `Copy` button clipboard interaction uses `navigator.clipboard.writeText` with an immediate visual fallback in case permissions are restricted.
