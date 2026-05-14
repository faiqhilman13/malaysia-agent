from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any


class HalalPrecheckError(ValueError):
    """Raised when a dossier, requirements file, or OCR artifact is invalid."""


@dataclass(frozen=True)
class CollectedDocument:
    kind: str
    path: str
    metadata: dict[str, Any]
    context: str

    @property
    def key(self) -> str:
        return _normalise_path(self.path)


def run_halal_precheck(
    *,
    dossier_path: Path,
    out_dir: Path,
    requirements_path: Path | None = None,
    ocr_dir: Path | None = None,
) -> dict[str, Any]:
    dossier = _load_json_object(dossier_path)
    ruleset = _load_json_object(requirements_path) if requirements_path else _load_default_requirements()
    ocr_records = _load_ocr_records(ocr_dir) if ocr_dir else {}

    result = evaluate_dossier(
        dossier=dossier,
        ruleset=ruleset,
        ocr_records=ocr_records,
        dossier_path=dossier_path,
    )
    write_reports(result=result, out_dir=out_dir)
    return result


def evaluate_dossier(
    *,
    dossier: dict[str, Any],
    ruleset: dict[str, Any],
    ocr_records: dict[str, dict[str, Any]] | None = None,
    dossier_path: Path | None = None,
) -> dict[str, Any]:
    application = dossier.get("application")
    if not isinstance(application, dict):
        raise HalalPrecheckError("Dossier must contain an application object.")

    application_type = str(application.get("type") or "").strip()
    if not application_type:
        raise HalalPrecheckError("Dossier application.type is required.")

    requirements = ruleset.get("requirements")
    if not isinstance(requirements, list):
        raise HalalPrecheckError("Requirements file must contain a requirements list.")

    documents = collect_documents(dossier)
    document_kinds = {item.kind for item in documents}
    ocr_records = ocr_records or {}

    requirement_results: list[dict[str, Any]] = []
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise HalalPrecheckError("Each requirement must be an object.")
        if not _requirement_applies(requirement, application_type, dossier):
            continue
        requirement_results.append(_evaluate_requirement(requirement, documents, document_kinds))

    document_checks = _evaluate_document_metadata(documents)
    ocr_results = _evaluate_ocr(documents, ocr_records)
    summary = _summarise(requirement_results, ocr_results, document_checks)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    return {
        "schema_version": "halal-precheck.v0",
        "generated_at": generated_at,
        "dossier_path": str(dossier_path) if dossier_path else None,
        "dossier_id": dossier.get("dossier_id"),
        "application": {
            "type": application_type,
            "product_name": application.get("product_name"),
            "menu_name": application.get("menu_name"),
            "oem": bool(application.get("oem")),
        },
        "applicant": _applicant_summary(dossier.get("applicant")),
        "summary": summary,
        "documents": [_document_output(item) for item in documents],
        "requirements": requirement_results,
        "document_checks": document_checks,
        "ocr_verifications": ocr_results,
    }


def collect_documents(dossier: dict[str, Any]) -> list[CollectedDocument]:
    documents: list[CollectedDocument] = []

    def walk(value: Any, context: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                next_context = f"{context}.{key}" if context else str(key)
                if key == "documents" and isinstance(child, list):
                    for index, item in enumerate(child):
                        if not isinstance(item, dict):
                            raise HalalPrecheckError(f"Document at {next_context}[{index}] must be an object.")
                        documents.append(_document_from_dict(item, f"{next_context}[{index}]"))
                else:
                    walk(child, next_context)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{context}[{index}]")

    walk(dossier, "")
    return documents


def write_reports(*, result: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "precheck.json").write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")

    applicant_md = render_markdown_report(result, audience="applicant")
    reviewer_md = render_markdown_report(result, audience="reviewer")
    (out_dir / "applicant-report.md").write_text(applicant_md)
    (out_dir / "reviewer-report.md").write_text(reviewer_md)
    (out_dir / "applicant-report.html").write_text(render_html_report(applicant_md, "Applicant Halal Precheck Report"))
    (out_dir / "reviewer-report.html").write_text(render_html_report(reviewer_md, "Reviewer Halal Precheck Report"))


def render_markdown_report(result: dict[str, Any], *, audience: str) -> str:
    if audience not in {"applicant", "reviewer"}:
        raise HalalPrecheckError("Report audience must be applicant or reviewer.")

    summary = result["summary"]
    lines = [
        f"# {'Applicant' if audience == 'applicant' else 'Reviewer'} Halal Precheck Report",
        "",
        f"- Dossier: `{result.get('dossier_id') or 'unknown'}`",
        f"- Applicant: {result.get('applicant', {}).get('name') or 'Unknown'}",
        f"- Application type: `{result.get('application', {}).get('type')}`",
        f"- Product/menu: {result.get('application', {}).get('product_name') or result.get('application', {}).get('menu_name') or 'Not specified'}",
        f"- Generated: `{result.get('generated_at')}`",
        "",
        "## Summary",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Requirements passed: {summary['requirements_passed']}",
        f"- Requirements failed: {summary['requirements_failed']}",
        f"- Conditional requirements skipped: {summary['requirements_skipped']}",
        f"- OCR matches: {summary['ocr_matches']}",
        f"- OCR mismatches: {summary['ocr_mismatches']}",
        f"- OCR low-confidence checks: {summary['ocr_low_confidence']}",
        f"- Expired document metadata checks: {summary['expired_documents']}",
        "",
    ]

    if audience == "applicant":
        lines.extend(_applicant_sections(result))
    else:
        lines.extend(_reviewer_sections(result))

    return "\n".join(lines).rstrip() + "\n"


def render_html_report(markdown: str, title: str) -> str:
    body = _markdown_to_html(markdown)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{html.escape(title)}</title>",
            "<style>",
            "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.55;margin:0;color:#151515;background:#f7f5ef}",
            "main{max-width:1040px;margin:0 auto;padding:40px 24px 64px;background:#fff;min-height:100vh}",
            "h1,h2{line-height:1.15} h1{font-size:32px;margin-bottom:20px} h2{font-size:22px;margin-top:32px;border-top:1px solid #ddd;padding-top:20px}",
            "code{background:#f0eee8;padding:2px 5px;border-radius:4px} table{width:100%;border-collapse:collapse;margin:16px 0}",
            "th,td{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top} th{background:#f3efe4}",
            "li{margin:6px 0}",
            "</style>",
            "</head>",
            "<body><main>",
            body,
            "</main></body></html>",
            "",
        ]
    )


def _load_default_requirements() -> dict[str, Any]:
    resource = resources.files("malaysia_agent_ops.data").joinpath("halal_requirements.json")
    return json.loads(resource.read_text())


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise HalalPrecheckError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise HalalPrecheckError(f"{path} must contain a JSON object.")
    return payload


def _load_ocr_records(ocr_dir: Path) -> dict[str, dict[str, Any]]:
    if not ocr_dir.exists():
        raise HalalPrecheckError(f"OCR directory does not exist: {ocr_dir}")

    records: dict[str, dict[str, Any]] = {}
    for path in sorted(ocr_dir.rglob("*.json")):
        payload = _load_json_object(path)
        document_path = payload.get("document_path")
        if not document_path:
            raise HalalPrecheckError(f"OCR file {path} must include document_path.")
        records[_normalise_path(str(document_path))] = payload
    return records


def _document_from_dict(item: dict[str, Any], context: str) -> CollectedDocument:
    kind = str(item.get("kind") or "").strip()
    path = str(item.get("path") or "").strip()
    if not kind:
        raise HalalPrecheckError(f"Document at {context} is missing kind.")
    if not path:
        raise HalalPrecheckError(f"Document at {context} is missing path.")
    metadata = item.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise HalalPrecheckError(f"Document metadata at {context} must be an object.")
    return CollectedDocument(kind=kind, path=path, metadata=metadata, context=context)


def _requirement_applies(requirement: dict[str, Any], application_type: str, dossier: dict[str, Any]) -> bool:
    applies_to = requirement.get("applies_to") or []
    if not isinstance(applies_to, list):
        raise HalalPrecheckError(f"{requirement.get('requirement_id')} applies_to must be a list.")
    if "all" not in applies_to and application_type not in applies_to:
        return False

    condition = requirement.get("condition")
    if condition is None:
        return True
    if not isinstance(condition, dict):
        raise HalalPrecheckError(f"{requirement.get('requirement_id')} condition must be an object.")
    field = condition.get("field")
    if not field:
        raise HalalPrecheckError(f"{requirement.get('requirement_id')} condition.field is required.")
    expected = condition.get("equals")
    return _lookup_path(dossier, str(field)) == expected


def _evaluate_requirement(
    requirement: dict[str, Any],
    documents: list[CollectedDocument],
    document_kinds: set[str],
) -> dict[str, Any]:
    required_kinds = requirement.get("required_document_kinds") or []
    if not isinstance(required_kinds, list):
        raise HalalPrecheckError(f"{requirement.get('requirement_id')} required_document_kinds must be a list.")

    matched = [item for item in documents if item.kind in required_kinds]
    missing_kinds = [kind for kind in required_kinds if kind not in document_kinds]
    status = "pass" if matched else "fail"
    severity = str(requirement.get("severity") or "required")

    return {
        "requirement_id": requirement.get("requirement_id"),
        "title": requirement.get("title"),
        "description": requirement.get("description"),
        "status": status,
        "severity": severity,
        "evidence_class": requirement.get("evidence_class"),
        "source_id": requirement.get("source_id"),
        "source_url": requirement.get("source_url"),
        "required_document_kinds": required_kinds,
        "matched_documents": [_document_output(item) for item in matched],
        "missing_document_kinds": missing_kinds if not matched else [],
    }


def _evaluate_ocr(
    documents: list[CollectedDocument],
    ocr_records: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for document in documents:
        record = ocr_records.get(document.key)
        if not record:
            if document.metadata:
                results.append(
                    {
                        "document_path": document.path,
                        "document_kind": document.kind,
                        "status": "not_evaluable",
                        "reason": "no_ocr_record",
                        "fields": [],
                    }
                )
            continue

        fields = record.get("fields") or {}
        if not isinstance(fields, dict):
            raise HalalPrecheckError(f"OCR fields for {document.path} must be an object.")

        field_results: list[dict[str, Any]] = []
        for key, declared in document.metadata.items():
            if isinstance(declared, (dict, list)):
                continue
            observed_record = fields.get(key)
            if not isinstance(observed_record, dict):
                field_results.append(
                    {
                        "field": key,
                        "declared": declared,
                        "observed": None,
                        "confidence": None,
                        "status": "missing_from_document",
                    }
                )
                continue
            observed = observed_record.get("observed")
            confidence = observed_record.get("confidence")
            status = _compare_observed(declared, observed, confidence)
            field_results.append(
                {
                    "field": key,
                    "declared": declared,
                    "observed": observed,
                    "confidence": confidence,
                    "status": status,
                }
            )

        document_status = _document_ocr_status(field_results)
        results.append(
            {
                "document_path": document.path,
                "document_kind": document.kind,
                "extractor": record.get("extractor"),
                "status": document_status,
                "fields": field_results,
            }
        )
    return results


def _evaluate_document_metadata(documents: list[CollectedDocument]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    today = date.today()
    for document in documents:
        expiry_date = document.metadata.get("expiry_date")
        if not expiry_date:
            continue
        parsed = _parse_date(str(expiry_date))
        if not parsed:
            checks.append(
                {
                    "document_path": document.path,
                    "document_kind": document.kind,
                    "field": "expiry_date",
                    "declared": expiry_date,
                    "status": "not_evaluable",
                    "reason": "unparseable_expiry_date",
                }
            )
            continue
        checks.append(
            {
                "document_path": document.path,
                "document_kind": document.kind,
                "field": "expiry_date",
                "declared": expiry_date,
                "status": "expired" if parsed < today else "valid",
                "as_of": today.isoformat(),
            }
        )
    return checks


def _compare_observed(declared: Any, observed: Any, confidence: Any) -> str:
    if observed in (None, ""):
        return "missing_from_document"
    if isinstance(confidence, (int, float)) and confidence < 0.8:
        return "low_confidence"
    if _normalise_scalar(declared) == _normalise_scalar(observed):
        return "match"
    return "mismatch"


def _document_ocr_status(fields: list[dict[str, Any]]) -> str:
    if not fields:
        return "not_evaluable"
    statuses = {item["status"] for item in fields}
    if "mismatch" in statuses:
        return "mismatch"
    if "missing_from_document" in statuses:
        return "missing_from_document"
    if "low_confidence" in statuses:
        return "low_confidence"
    if statuses == {"match"}:
        return "match"
    return "not_evaluable"


def _summarise(
    requirements: list[dict[str, Any]],
    ocr_results: list[dict[str, Any]],
    document_checks: list[dict[str, Any]],
) -> dict[str, Any]:
    requirements_failed = sum(1 for item in requirements if item["status"] == "fail" and item["severity"] != "conditional")
    conditional_skipped = sum(1 for item in requirements if item["status"] == "skipped")
    ocr_mismatches = sum(1 for item in ocr_results if item["status"] == "mismatch")
    ocr_low_confidence = sum(1 for item in ocr_results if item["status"] == "low_confidence")
    ocr_missing = sum(1 for item in ocr_results if item["status"] == "missing_from_document")
    expired_documents = sum(1 for item in document_checks if item["status"] == "expired")

    overall_status = "pass"
    if requirements_failed or ocr_mismatches or expired_documents:
        overall_status = "needs_remediation"
    elif ocr_low_confidence or ocr_missing:
        overall_status = "needs_review"

    return {
        "overall_status": overall_status,
        "requirements_total": len(requirements),
        "requirements_passed": sum(1 for item in requirements if item["status"] == "pass"),
        "requirements_failed": sum(1 for item in requirements if item["status"] == "fail"),
        "requirements_skipped": conditional_skipped,
        "ocr_total": len(ocr_results),
        "ocr_matches": sum(1 for item in ocr_results if item["status"] == "match"),
        "ocr_mismatches": ocr_mismatches,
        "ocr_low_confidence": ocr_low_confidence,
        "ocr_missing_from_document": ocr_missing,
        "document_checks_total": len(document_checks),
        "expired_documents": expired_documents,
    }


def _applicant_summary(applicant: Any) -> dict[str, Any]:
    if not isinstance(applicant, dict):
        return {}
    return {
        "name": applicant.get("name"),
        "registration_no": applicant.get("registration_no"),
        "tin": applicant.get("tin"),
    }


def _document_output(item: CollectedDocument) -> dict[str, Any]:
    return {
        "kind": item.kind,
        "path": item.path,
        "metadata": item.metadata,
        "context": item.context,
    }


def _applicant_sections(result: dict[str, Any]) -> list[str]:
    failed = [item for item in result["requirements"] if item["status"] == "fail"]
    ocr_attention = [item for item in result["ocr_verifications"] if item["status"] not in {"match", "not_evaluable"}]
    expired = [item for item in result["document_checks"] if item["status"] == "expired"]
    lines = [
        "## Fix Before Submission",
        "",
    ]
    if not failed and not ocr_attention and not expired:
        lines.append("- No required remediation found in this pre-check.")
    for item in failed:
        lines.append(
            f"- `{item['requirement_id']}` {item['title']}: add one of `{', '.join(item['required_document_kinds'])}`. Source: {item['source_id']}."
        )
    for item in expired:
        lines.append(f"- `{item['document_path']}` has expired metadata: `{item['declared']}`.")
    for item in ocr_attention:
        lines.append(f"- OCR check for `{item['document_path']}` returned `{item['status']}`.")

    lines.extend(
        [
            "",
            "## Requirement Coverage",
            "",
            "| Status | Requirement | Evidence Class | Source | Matched Documents |",
            "|---|---|---|---|---|",
        ]
    )
    for item in result["requirements"]:
        matched = ", ".join(doc["path"] for doc in item["matched_documents"]) or "-"
        lines.append(
            f"| `{item['status']}` | {item['title']} | `{item['evidence_class']}` | [{item['source_id']}]({item['source_url']}) | {matched} |"
        )
    lines.extend(_document_checks_markdown_section(result))
    lines.extend(_ocr_markdown_section(result))
    return lines


def _reviewer_sections(result: dict[str, Any]) -> list[str]:
    lines = [
        "## Dossier Inventory",
        "",
        "| Kind | Path | Metadata Fields |",
        "|---|---|---|",
    ]
    for item in result["documents"]:
        metadata_keys = ", ".join(sorted(item.get("metadata", {}).keys())) or "-"
        lines.append(f"| `{item['kind']}` | `{item['path']}` | {metadata_keys} |")

    lines.extend(
        [
            "",
            "## Requirement Matrix",
            "",
            "| Requirement | Status | Severity | Evidence Class | Source | Missing Kinds |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in result["requirements"]:
        missing = ", ".join(item["missing_document_kinds"]) or "-"
        lines.append(
            f"| `{item['requirement_id']}` {item['title']} | `{item['status']}` | `{item['severity']}` | `{item['evidence_class']}` | [{item['source_id']}]({item['source_url']}) | {missing} |"
        )

    lines.extend(_document_checks_markdown_section(result))
    lines.extend(_ocr_markdown_section(result))
    return lines


def _document_checks_markdown_section(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Document Metadata Checks",
        "",
    ]
    if not result["document_checks"]:
        lines.append("- No date-based document metadata checks were available.")
        return lines

    lines.extend(
        [
            "| Document | Field | Declared | Status | As Of |",
            "|---|---|---|---|---|",
        ]
    )
    for item in result["document_checks"]:
        lines.append(
            f"| `{item['document_path']}` | `{item['field']}` | {item.get('declared')} | `{item['status']}` | {item.get('as_of', '-')} |"
        )
    return lines


def _ocr_markdown_section(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## OCR Metadata Verification",
        "",
    ]
    if not result["ocr_verifications"]:
        lines.append("- No OCR verification records were supplied.")
        return lines

    lines.extend(
        [
            "| Document | Status | Field | Declared | Observed | Confidence |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in result["ocr_verifications"]:
        if not item.get("fields"):
            lines.append(f"| `{item['document_path']}` | `{item['status']}` | - | - | - | - |")
            continue
        for field in item["fields"]:
            lines.append(
                f"| `{item['document_path']}` | `{field['status']}` | `{field['field']}` | {field.get('declared')} | {field.get('observed')} | {field.get('confidence')} |"
            )
    return lines


def _markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    in_ul = False
    in_table = False
    table_rows: list[str] = []

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            output.append("</ul>")
            in_ul = False

    def close_table() -> None:
        nonlocal in_table, table_rows
        if not in_table:
            return
        output.append("<table>")
        for index, row in enumerate(table_rows):
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if index == 1 and all(set(cell) <= {"-", ":", " "} for cell in cells):
                continue
            tag = "th" if index == 0 else "td"
            output.append("<tr>" + "".join(f"<{tag}>{_inline_html(cell)}</{tag}>" for cell in cells) + "</tr>")
        output.append("</table>")
        table_rows = []
        in_table = False

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            close_ul()
            in_table = True
            table_rows.append(line)
            continue
        close_table()

        if line.startswith("# "):
            close_ul()
            output.append(f"<h1>{_inline_html(line[2:])}</h1>")
        elif line.startswith("## "):
            close_ul()
            output.append(f"<h2>{_inline_html(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_ul:
                output.append("<ul>")
                in_ul = True
            output.append(f"<li>{_inline_html(line[2:])}</li>")
        elif not line.strip():
            close_ul()
        else:
            close_ul()
            output.append(f"<p>{_inline_html(line)}</p>")

    close_table()
    close_ul()
    return "\n".join(output)


def _inline_html(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def _lookup_path(payload: dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _normalise_path(value: str) -> str:
    return str(Path(value)).replace("\\", "/")


def _normalise_scalar(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    parsed_date = _parse_date(text)
    return parsed_date.isoformat() if parsed_date else text


def _parse_date(value: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
