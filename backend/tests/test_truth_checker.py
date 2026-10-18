"""Unit tests for truthfulness audit and verification."""

import pytest
from truth_checker import verify_factual_integrity


def test_verify_factual_integrity_sentence_capitalization():
    """Verify that standard sentence capitalization does NOT false-flag as an unmentioned tool."""
    original = "Worked on API performance and fixed database queries"
    tailored = "Improved API performance by optimizing database queries."
    is_valid, discrepancies = verify_factual_integrity(original, tailored)
    assert is_valid is True
    assert discrepancies == []


def test_verify_factual_integrity_catches_invented_metrics():
    """Verify that adding an ungrounded metric like 'by 35%' is flagged as an invention."""
    original = "Worked on API performance and fixed database queries"
    tailored = "Improved API performance by 35% by optimizing database queries."
    is_valid, discrepancies = verify_factual_integrity(original, tailored)
    assert is_valid is False
    assert any("35%" in d for d in discrepancies)


def test_verify_factual_integrity_allows_truthful_rewrite():
    """Verify that a faithful rewrite preserving original facts passes cleanly."""
    original = "Worked on API performance and fixed database queries"
    tailored = "Improved API performance by optimizing database queries."
    is_valid, discrepancies = verify_factual_integrity(original, tailored)
    assert is_valid is True
    assert len(discrepancies) == 0


def test_verify_factual_integrity_allows_terms_from_full_resume():
    """Verify that tools/terms mentioned in other parts of the resume are permitted."""
    original_bullet = "Engineered backend microservices for user transactions."
    tailored_bullet = "Engineered Python backend microservices for user transactions."
    full_resume = "Skills: Python, FastAPI, Docker, Linux\n• Worked on analytics pipeline"

    is_valid, discrepancies = verify_factual_integrity(
        original_bullet=original_bullet,
        tailored_bullet=tailored_bullet,
        full_resume_text=full_resume
    )
    assert is_valid is True
    assert len(discrepancies) == 0


def test_verify_factual_integrity_catches_invented_tools():
    """Verify that introducing an ungrounded technology or acronym is flagged."""
    original = "Worked on API performance and fixed database queries"
    tailored = "Optimized backend PostgreSQL queries and deployed to AWS."
    full_resume = "• Team lead for customer support operations"

    is_valid, discrepancies = verify_factual_integrity(
        original_bullet=original,
        tailored_bullet=tailored,
        full_resume_text=full_resume
    )
    assert is_valid is False
    # Should catch both PostgreSQL and AWS
    assert any("postgresql" in d.lower() or "aws" in d.lower() for d in discrepancies)


def test_verify_factual_integrity_catches_invented_domain_nouns():
    """
    Verify that lowercase domain/org nouns silently injected by the model are flagged.

    Exact example from the truth-check gap report:
      Original:  "Collaborated with product team"
      Tailored:  "Partnered with cross-functional product and design teams"

    The word "design" is lowercase and passes the capitalization check,
    but it is a newly invented organizational domain not present in the
    original bullet or anywhere else in the resume.
    """
    original = "Collaborated with product team"
    tailored = "Partnered with cross-functional product and design teams"
    full_resume = "• Led backend API work\n• Managed deployment pipelines"

    is_valid, discrepancies = verify_factual_integrity(
        original_bullet=original,
        tailored_bullet=tailored,
        full_resume_text=full_resume
    )
    assert is_valid is False
    assert any("design" in d for d in discrepancies)
