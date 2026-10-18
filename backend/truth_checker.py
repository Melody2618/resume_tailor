"""Resume Tailor — Deterministic truthfulness audit module."""

import re

# Common English words and action verbs often capitalized at the start of bullets or phrases
COMMON_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "over", "under", "again", "further",
    "once", "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "can", "will", "with", "by",
    "across", "into", "onto", "upon", "within", "without", "between", "among",
    # Common resume action verbs / adjectives / nouns that might appear capitalized
    "improved", "optimized", "managed", "led", "developed", "built", "engineered",
    "designed", "created", "spearheaded", "orchestrated", "architected", "delivered",
    "implemented", "executed", "collaborated", "partnered", "established", "streamlined",
    "expanded", "scaled", "automated", "mentored", "trained", "authored", "standardized",
    "strengthened", "accelerated", "drove", "launched", "conducted", "analyzed",
    "senior", "lead", "staff", "principal", "junior", "associate", "team", "project",
    "product", "systems", "system", "service", "services", "backend", "frontend",
    "fullstack", "platform", "infrastructure", "performance", "database", "data",
    "high", "low", "key", "core", "cross", "functional", "end", "user", "users",
    "internal", "external", "global", "enterprise", "strategic", "technical"
}

# Lowercase domain / org / role nouns the model may silently inject.
# These are not caught by the capitalization check because they appear in lowercase.
DOMAIN_NOUNS = {
    "design", "engineering", "marketing", "leadership", "finance", "legal",
    "operations", "sales", "research", "strategy", "security", "analytics",
    "compliance", "procurement", "communications", "hr", "recruiting", "it",
    "devops", "cloud", "mobile", "growth", "partnerships", "support",
}


def _extract_numbers(text: str) -> set[str]:
    """Extract numbers, decimals, percentages, and metrics from text."""
    # Matches patterns like 35%, 10, 3.5, $100k, 2.5x, 40+
    matches = re.findall(r"\b\d+(?:\.\d+)?(?:%|x|\+)?(?!\w)|\$\d+(?:\.\d+)?(?:k|m|b)?\b", text, re.IGNORECASE)
    return {m.lower().rstrip("+") for m in matches}


def _extract_tech_terms(text: str) -> set[str]:
    """
    Extract technical terms, proper nouns, and acronyms.
    Ignores the first word of sentences and common words.
    """
    terms = set()

    # 1. Acronyms (e.g. AWS, REST, SQL, CI/CD, GCP, K8S)
    acronyms = re.findall(r"\b[A-Z]{2,}(?:/[A-Z0-9]+)?\b", text)
    for acr in acronyms:
        # Check against common words in uppercase (like IT, OR, AS)
        if acr.lower() not in COMMON_WORDS and len(acr) >= 2:
            terms.add(acr.lower())

    # 2. CamelCase / mixed-case terms (e.g. PostgreSQL, JavaScript, MongoDB, DevOps)
    camel_cases = re.findall(r"\b[A-Z][a-z]+[A-Z][a-zA-Z]*\b", text)
    for cc in camel_cases:
        terms.add(cc.lower())

    # 3. Capitalized words, ignoring sentence starters
    # Split text into sentences/clauses
    sentences = re.split(r"(?<=[.!?])\s+|[;•\n]+", text)
    for sentence in sentences:
        words = re.findall(r"\b[A-Za-z0-9+#.-]+\b", sentence)
        if not words:
            continue
        # Check words starting from index 1 (skipping sentence-initial word)
        for word in words[1:]:
            # Check if word is capitalized and not in common words
            if word[0].isupper() and word.lower() not in COMMON_WORDS and len(word) > 1:
                # Also filter out purely numeric or punctuation
                clean = word.strip(".#+-").lower()
                if clean and clean not in COMMON_WORDS:
                    terms.add(clean)

    return terms


def _extract_domain_nouns(text: str) -> set[str]:
    """Extract domain/org/role nouns from text that appear in DOMAIN_NOUNS."""
    words = re.findall(r"\b[a-z]+\b", text.lower())
    return {w for w in words if w in DOMAIN_NOUNS}


def verify_factual_integrity(
    original_bullet: str,
    tailored_bullet: str,
    full_resume_text: str = ""
) -> tuple[bool, list[str]]:
    """
    Deterministically audits a tailored bullet to ensure no metrics,
    numbers, unmentioned tools/technologies, or invented domain/org nouns
    were added.

    Returns:
        (is_valid: bool, discrepancies: list[str])
    """
    discrepancies: list[str] = []

    # Combined corpus of original candidate facts
    original_corpus = f"{original_bullet}\n{full_resume_text}".lower()

    # 1. Number / Metric check
    tailored_nums = _extract_numbers(tailored_bullet)
    original_nums = _extract_numbers(original_corpus)

    for num in tailored_nums:
        if num not in original_nums:
            discrepancies.append(f"Invented metric/number: '{num}'")

    # 2. Technology / Acronym / Capitalized Term check
    tailored_terms = _extract_tech_terms(tailored_bullet)
    for term in tailored_terms:
        # Check if the term exists anywhere in the original bullet or full resume text
        # Using word boundary check to avoid partial word match false-negatives
        pattern = rf"\b{re.escape(term)}\b"
        if not re.search(pattern, original_corpus):
            discrepancies.append(f"Unverified tool/technology: '{term}'")

    # 3. Domain / Org-Noun check
    # Flag lowercase domain nouns present in the tailored bullet but absent from the
    # original corpus (original bullet + full resume). These slip past the capitalization
    # check but represent silently invented organizational domains (e.g. "design").
    tailored_domain_nouns = _extract_domain_nouns(tailored_bullet)
    original_domain_nouns = _extract_domain_nouns(original_corpus)
    for noun in tailored_domain_nouns:
        if noun not in original_domain_nouns:
            discrepancies.append(f"Invented domain/org noun: '{noun}'")

    is_valid = len(discrepancies) == 0
    return is_valid, discrepancies
