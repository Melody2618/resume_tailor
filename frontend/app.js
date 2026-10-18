/**
 * Resume Tailor — Frontend Client Application
 * Handles state, validation, API communication, and clipboard interaction.
 */

// Sample Demo Data
const SAMPLE_RESUME = `• Worked on API performance and fixed database queries
• Built automated test suite for order processing service
• Collaborated with product team to ship checkout flow redesign
• Maintained CI/CD deployment pipelines on AWS infrastructure`;

const SAMPLE_JD = `Senior Backend Software Engineer

Responsibilities:
- Lead API performance optimization and database query tuning across high-traffic core services
- Expand automated test coverage and reliability for critical order processing workflows
- Partner with cross-functional product and design teams to deliver high-impact user experiences
- Manage cloud infrastructure and CI/CD deployment pipelines on AWS`;

const MAX_CHARS = 12000;
const MIN_CHARS = 15;

// DOM Elements
const resumeInput = document.getElementById("resume-input");
const jdInput = document.getElementById("jd-input");
const resumeCount = document.getElementById("resume-count");
const jdCount = document.getElementById("jd-count");
const resumeError = document.getElementById("resume-error");
const jdError = document.getElementById("jd-error");
const cardResume = document.getElementById("card-resume");
const cardJd = document.getElementById("card-jd");

const tailorBtn = document.getElementById("tailor-btn");
const clearBtn = document.getElementById("clear-btn");
const trySampleBtn = document.getElementById("try-sample-btn");
const retryBtn = document.getElementById("retry-btn");
const actionBar = document.getElementById("action-bar");

const errorBanner = document.getElementById("error-banner");
const errorMessage = document.getElementById("error-message");

const resultsSection = document.getElementById("results-section");
const skeletonContainer = document.getElementById("skeleton-container");
const cardsContainer = document.getElementById("cards-container");

// Update Character Counters & Input Limits
function updateCounter(input, countEl, cardEl, errorEl) {
  const length = input.value.length;
  countEl.textContent = `${length.toLocaleString()} / ${MAX_CHARS.toLocaleString()}`;

  if (length > MAX_CHARS) {
    countEl.classList.add("warning");
    cardEl.classList.add("has-warning");
    errorEl.textContent = `Character limit exceeded (${MAX_CHARS.toLocaleString()} max). Please trim text.`;
  } else {
    countEl.classList.remove("warning");
    cardEl.classList.remove("has-warning");
    // Clear length error if previously set
    if (errorEl.textContent.includes("Character limit exceeded")) {
      errorEl.textContent = "";
      cardEl.classList.remove("has-error");
    }
  }

  // Update button state if either is over limit
  const isOverLimit = resumeInput.value.length > MAX_CHARS || jdInput.value.length > MAX_CHARS;
  tailorBtn.disabled = isOverLimit;
}

resumeInput.addEventListener("input", () => {
  updateCounter(resumeInput, resumeCount, cardResume, resumeError);
});

jdInput.addEventListener("input", () => {
  updateCounter(jdInput, jdCount, cardJd, jdError);
});

// Clear All
clearBtn.addEventListener("click", () => {
  resumeInput.value = "";
  jdInput.value = "";
  resumeError.textContent = "";
  jdError.textContent = "";
  cardResume.classList.remove("has-error", "has-warning");
  cardJd.classList.remove("has-error", "has-warning");
  updateCounter(resumeInput, resumeCount, cardResume, resumeError);
  updateCounter(jdInput, jdCount, cardJd, jdError);
  resultsSection.classList.add("hidden");
  errorBanner.classList.add("hidden");
  cardsContainer.innerHTML = "";
  resumeInput.focus();
});

// Try a Sample
trySampleBtn.addEventListener("click", () => {
  resumeInput.value = SAMPLE_RESUME;
  jdInput.value = SAMPLE_JD;
  resumeError.textContent = "";
  jdError.textContent = "";
  cardResume.classList.remove("has-error", "has-warning");
  cardJd.classList.remove("has-error", "has-warning");
  updateCounter(resumeInput, resumeCount, cardResume, resumeError);
  updateCounter(jdInput, jdCount, cardJd, jdError);
  errorBanner.classList.add("hidden");

  // Smooth scroll to action button on small screens
  if (window.innerWidth < 768) {
    actionBar.scrollIntoView({ behavior: "smooth", block: "center" });
  }
});

// Validation
function validateInputs() {
  let isValid = true;
  const resumeVal = resumeInput.value.trim();
  const jdVal = jdInput.value.trim();

  if (resumeVal.length < MIN_CHARS) {
    resumeError.textContent = `Please enter at least ${MIN_CHARS} characters of your experience bullets.`;
    cardResume.classList.add("has-error");
    isValid = false;
  } else if (resumeInput.value.length > MAX_CHARS) {
    resumeError.textContent = `Character limit exceeded (${MAX_CHARS.toLocaleString()} max). Please trim text.`;
    cardResume.classList.add("has-warning");
    isValid = false;
  } else {
    resumeError.textContent = "";
    cardResume.classList.remove("has-error", "has-warning");
  }

  if (jdVal.length < MIN_CHARS) {
    jdError.textContent = `Please enter at least ${MIN_CHARS} characters of the job description.`;
    cardJd.classList.add("has-error");
    isValid = false;
  } else if (jdInput.value.length > MAX_CHARS) {
    jdError.textContent = `Character limit exceeded (${MAX_CHARS.toLocaleString()} max). Please trim text.`;
    cardJd.classList.add("has-warning");
    isValid = false;
  } else {
    jdError.textContent = "";
    cardJd.classList.remove("has-error", "has-warning");
  }

  return isValid;
}

// Copy to Clipboard
async function copyToClipboard(text, button) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      // Fallback for older or restricted environments
      const tempTextArea = document.createElement("textarea");
      tempTextArea.value = text;
      tempTextArea.style.position = "fixed";
      tempTextArea.style.left = "-999999px";
      document.body.appendChild(tempTextArea);
      tempTextArea.focus();
      tempTextArea.select();
      document.execCommand("copy");
      document.body.removeChild(tempTextArea);
    }

    button.classList.add("copied");
    button.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
      Copied!
    `;
    setTimeout(() => {
      button.classList.remove("copied");
      button.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
        </svg>
        Copy
      `;
    }, 1500);
  } catch (err) {
    console.error("Failed to copy:", err);
  }
}

// Render Comparison Cards
function renderCards(bullets) {
  cardsContainer.innerHTML = "";

  bullets.forEach((b, index) => {
    const card = document.createElement("article");
    card.className = "comparison-card";
    card.setAttribute("aria-label", `Comparison bullet ${index + 1}`);

    card.innerHTML = `
      <div class="card-split">
        <div class="panel panel-original">
          <div class="panel-header">
            <span class="panel-label">Original</span>
          </div>
          <p class="bullet-text">${escapeHtml(b.original_bullet)}</p>
        </div>
        <div class="panel panel-tailored">
          <div class="panel-header">
            <span class="panel-label">Tailored</span>
            <button type="button" class="btn-copy" aria-label="Copy tailored bullet">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              Copy
            </button>
          </div>
          <p class="bullet-text">${escapeHtml(b.tailored_bullet)}</p>
        </div>
      </div>
      <footer class="card-why">
        <p class="card-why-text"><strong>Why this works:</strong> ${escapeHtml(b.why)}</p>
      </footer>
    `;

    const copyBtn = card.querySelector(".btn-copy");
    copyBtn.addEventListener("click", () => {
      copyToClipboard(b.tailored_bullet, copyBtn);
    });

    cardsContainer.appendChild(card);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Form Submission / Tailor Bullets
async function handleTailor() {
  if (!validateInputs()) {
    return;
  }

  // Set Loading State
  tailorBtn.classList.add("loading");
  tailorBtn.disabled = true;
  tailorBtn.querySelector(".btn-text").textContent = "Tailoring top bullets...";
  errorBanner.classList.add("hidden");

  // Show Skeletons in Results Section
  cardsContainer.innerHTML = "";
  skeletonContainer.classList.remove("hidden");
  resultsSection.classList.remove("hidden");

  // Smooth scroll to results
  resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

  try {
    const response = await fetch("/api/tailor", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resume_text: resumeInput.value.trim(),
        job_description: jdInput.value.trim(),
      }),
    });

    if (!response.ok) {
      let detail = "Unable to tailor bullets right now. Your text is safe — click Retry to try again.";
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          detail = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch (e) {
        // Fallback to default message
      }
      throw new Error(detail);
    }

    const data = await response.json();

    if (!data.bullets || data.bullets.length === 0) {
      throw new Error("No truthful matching bullets could be identified. Try adjusting your input text.");
    }

    skeletonContainer.classList.add("hidden");
    renderCards(data.bullets);

  } catch (err) {
    console.error("Tailor error:", err);
    skeletonContainer.classList.add("hidden");
    resultsSection.classList.add("hidden");
    errorMessage.textContent = err.message || "Unable to tailor bullets right now. Your text is safe — click Retry to try again.";
    errorBanner.classList.remove("hidden");
    errorBanner.scrollIntoView({ behavior: "smooth", block: "center" });
  } finally {
    tailorBtn.classList.remove("loading");
    tailorBtn.disabled = false;
    tailorBtn.querySelector(".btn-text").textContent = "Tailor Bullets";
  }
}

tailorBtn.addEventListener("click", handleTailor);
retryBtn.addEventListener("click", handleTailor);

// Keyboard Shortcut: Cmd/Ctrl + Enter
window.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
    if (document.activeElement === resumeInput || document.activeElement === jdInput) {
      handleTailor();
    }
  }
});
