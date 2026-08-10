"""Intent classification tests."""

from hypermind.intent.router import IntentRouter
from hypermind.request import HyperMindRequest


def _classify(text: str):
    return IntentRouter().classify(HyperMindRequest(raw_input=text))


def test_repo_search_is_coding():
    r = _classify("Search the repo for authentication helpers")
    assert r.intent == "coding"
    assert r.reason_code == "repo_operation"
    assert r.method == "deterministic"


def test_research_competitors():
    r = _classify("Research competitors in fintech onboarding")
    assert r.intent == "research"
    assert r.reason_code == "explicit_research_request"


def test_memory_command():
    r = _classify("Remember that the flagship case is P-006")
    assert r.intent == "memory"
    assert r.reason_code == "memory_command"


def test_design_review():
    r = _classify("Review this interface for hierarchy issues")
    assert r.intent == "design"
    assert r.reason_code == "design_review"


def test_email_is_communication():
    r = _classify("Draft an email to the hiring manager")
    assert r.intent == "communication"


def test_explicit_intent_override():
    req = HyperMindRequest(raw_input="hello world", intent="coding")
    r = IntentRouter().classify(req)
    assert r.intent == "coding"
    assert r.reason_code == "explicit_intent"
    assert r.confidence == 1.0


def test_case_study_is_design():
    r = _classify("Review P-006 case study structure")
    assert r.intent == "design"
    assert r.reason_code in {"design_review", "case_study_domain"}


def test_linkedin_about_portfolio_stays_writing():
    r = _classify("Write a LinkedIn post about P-006")
    assert r.intent == "writing"
    assert r.reason_code == "writing_action"


def test_design_coresolution_with_project_hint():
    req = HyperMindRequest(raw_input="Look at P-006 next")
    r = IntentRouter().classify(req, project_key="portfolio", project_id="P-006")
    assert r.intent == "design"
    assert r.reason_code == "case_study_domain"


def test_general_fallback():
    r = _classify("hello there")
    assert r.intent == "general"
    assert r.reason_code == "no_strong_signal"
