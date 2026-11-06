"""Check report structure and local citations, never the truth of AI judgments."""
from pathlib import Path
from urllib.parse import urlparse

from .contracts import ContractError

KINDS = {"file-backed", "check-backed", "external-backed", "user-stated", "inferred", "missing"}


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{name} must be non-empty text")
    return value


def objects(value, name):
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ContractError(f"{name} must be a list of objects")
    return value


def refs(value, allowed, name):
    if not isinstance(value, list) or not value or any(not isinstance(ref, str) or ref not in allowed for ref in value):
        raise ContractError(f"{name} must reference existing IDs and not be empty")


def check_report(request, root: Path):
    evidence = objects(request.get("evidence"), "evidence")
    findings = objects(request.get("findings", []), "findings")
    suggestions = objects(request.get("suggestions", []), "suggestions")
    if not evidence:
        raise ContractError("evidence must not be empty")
    evidence_ids = set()
    for item in evidence:
        identifier = text(item.get("id"), "evidence.id")
        if identifier in evidence_ids:
            raise ContractError("duplicate evidence.id")
        evidence_ids.add(identifier)
        if not isinstance(item.get("kind"), str) or item["kind"] not in KINDS:
            raise ContractError("unknown evidence.kind")
        text(item.get("detail"), "evidence.detail")
        source = text(item.get("source"), "evidence.source")
        if item["kind"] == "file-backed":
            path = root.expanduser().resolve() / source
            line = item.get("line")
            if isinstance(line, bool) or not isinstance(line, int) or line < 1:
                raise ContractError("file-backed evidence.line must be a positive integer")
            if not path.is_file() or line > len(path.read_text(encoding="utf-8").splitlines()):
                raise ContractError(f"file-backed citation does not resolve: {source}:{line}")
        elif item["kind"] == "external-backed":
            url = urlparse(source)
            if url.scheme not in {"http", "https"} or not url.netloc:
                raise ContractError("external-backed source must be an HTTP(S) URL")
    finding_ids = set()
    for item in findings:
        identifier = text(item.get("id"), "finding.id")
        if identifier in finding_ids:
            raise ContractError("duplicate finding.id")
        finding_ids.add(identifier)
        text(item.get("detail"), "finding.detail")
        refs(item.get("evidence_ids"), evidence_ids, "finding.evidence_ids")
    covered = set()
    for item in suggestions:
        text(item.get("detail"), "suggestion.detail")
        refs(item.get("finding_ids"), finding_ids, "suggestion.finding_ids")
        covered.update(item["finding_ids"])
    if covered != finding_ids:
        raise ContractError("every finding needs a linked suggestion, including requests for missing evidence or decisions")
    return evidence, findings, suggestions
