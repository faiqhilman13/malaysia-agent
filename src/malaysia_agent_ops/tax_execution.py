from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Settings
from .service import InputError, OperationsService


class TaxExecutionError(ValueError):
    """Raised when tax execution demo inputs are invalid."""


def run_tax_execution(
    *,
    settings: Settings,
    invoice_path: Path,
    out_dir: Path,
    payment_event_path: Path | None = None,
    real_provider: bool = False,
    max_steps: int | None = None,
) -> dict[str, Any]:
    invoice = _load_json_object(invoice_path)
    payment_event = _load_json_object(payment_event_path) if payment_event_path else None
    service = OperationsService(settings)

    if real_provider:
        payload = {**invoice, "execution_mode": "real"}
        response = service.invoke("invoices.submit", payload)
        summary = _summarise_real_provider_attempt(
            invoice=invoice,
            invoice_path=invoice_path,
            response=response,
        )
    else:
        if payment_event is None:
            raise TaxExecutionError("--payment-event is required for sandbox tax execution.")
        workflow_payload = {
            "action": "invoices.submit",
            "payload": {
                **invoice,
                "payment_event": payment_event,
            },
            "max_steps": max_steps or 10,
        }
        response = service.invoke("workflows.run", workflow_payload)
        summary = _summarise_sandbox_run(
            invoice=invoice,
            invoice_path=invoice_path,
            payment_event=payment_event,
            response=response,
            service=service,
        )

    write_tax_reports(summary=summary, out_dir=out_dir)
    return summary


def write_tax_reports(*, summary: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n")
    markdown = render_tax_markdown(summary)
    (out_dir / "summary.md").write_text(markdown)


def render_tax_markdown(summary: dict[str, Any]) -> str:
    invoice = summary["invoice"]
    lines = [
        "# Tax Execution Summary",
        "",
        f"- Invoice: `{invoice.get('invoice_number')}`",
        f"- Supplier TIN: `{invoice.get('supplier_tin')}`",
        f"- Buyer TIN: `{invoice.get('buyer_tin')}`",
        f"- Total amount: `{invoice.get('currency', 'MYR')} {invoice.get('total_amount')}`",
        f"- Execution mode: `{summary['execution_mode']}`",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Workflow status: `{summary.get('workflow_status')}`",
        f"- Blocking reason: `{summary.get('blocking_reason')}`",
        "",
        "## Result",
        "",
    ]

    if summary["execution_mode"] == "real_provider":
        lines.append("- No live MyInvois submission was performed.")
        lines.append(f"- The run stopped at `{summary.get('blocking_reason')}`.")
        if summary.get("next_action"):
            lines.append(f"- Next action: `{summary['next_action']}`.")
    else:
        lines.extend(
            [
                f"- Run ID: `{summary.get('run_id')}`",
                f"- Submission ID: `{summary.get('submission_id')}`",
                f"- Payment request ID: `{summary.get('payment_request_id')}`",
                f"- Final invoice status: `{summary.get('final_invoice_status')}`",
                f"- Final payment status: `{summary.get('final_payment_status')}`",
                f"- Exceptions: `{len(summary.get('exceptions', []))}`",
            ]
        )

    lines.extend(
        [
            "",
            "## Execution Steps",
            "",
            "| Step | Action | Status | Next Action | Blocking Reason | Resource |",
            "|---|---|---|---|---|---|",
        ]
    )
    for step in summary.get("steps", []):
        lines.append(
            f"| {step['step']} | `{step['action']}` | `{step['status']}` | `{step.get('next_action')}` | `{step.get('blocking_reason')}` | `{step.get('resource_id')}` |"
        )

    if summary.get("notes"):
        lines.extend(["", "## Notes", ""])
        for note in summary["notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines).rstrip() + "\n"


def render_tax_html(summary: dict[str, Any]) -> str:
    markdown = render_tax_markdown(summary)
    lines = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            lines.append(f"<p>{html.escape(line[2:])}</p>")
        elif line.startswith("|"):
            lines.append(f"<pre>{html.escape(line)}</pre>")
        elif line:
            lines.append(f"<p>{html.escape(line)}</p>")
    return "\n".join(lines)


def _summarise_sandbox_run(
    *,
    invoice: dict[str, Any],
    invoice_path: Path,
    payment_event: dict[str, Any],
    response: dict[str, Any],
    service: OperationsService,
) -> dict[str, Any]:
    data = response.get("data") or {}
    execution_log = data.get("execution_log") or []
    steps = [_step_summary(item) for item in execution_log]
    submission_id = _first_response_data(execution_log, "submission_id")
    payment_request_id = _first_response_data(execution_log, "request_id")

    final_invoice_status = None
    if submission_id:
        try:
            final_invoice_status = service.invoice_status({"submission_id": submission_id})["data"]["submission_status"]
        except Exception:
            final_invoice_status = None

    final_payment_status = None
    if payment_request_id:
        payment = service.repo.get_payment_request(str(payment_request_id))
        final_payment_status = payment.get("workflow_status") if payment else None

    exceptions = service.list_exceptions({})["data"]["items"]
    workflow_status = data.get("workflow_status")
    final_response = data.get("final_response") or {}

    return {
        "schema_version": "tax-execution.v0",
        "generated_at": _now(),
        "execution_mode": "sandbox",
        "invoice_path": str(invoice_path),
        "invoice": _invoice_summary(invoice),
        "payment_event": payment_event,
        "overall_status": "pass" if workflow_status == "completed" and final_invoice_status == "paid" else "needs_review",
        "workflow_status": workflow_status,
        "blocking_reason": response.get("blocking_reason"),
        "next_action": response.get("next_action"),
        "run_id": data.get("run_id"),
        "steps_executed": data.get("steps_executed"),
        "submission_id": submission_id,
        "payment_request_id": payment_request_id,
        "final_invoice_status": final_invoice_status,
        "final_payment_status": final_payment_status,
        "exceptions": exceptions,
        "final_response": final_response,
        "steps": steps,
        "notes": [
            "Sandbox execution used local deterministic MyInvois-shaped and DuitNow-shaped workflow state.",
            "No live MyInvois submission was performed.",
        ],
    }


def _summarise_real_provider_attempt(
    *,
    invoice: dict[str, Any],
    invoice_path: Path,
    response: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "tax-execution.v0",
        "generated_at": _now(),
        "execution_mode": "real_provider",
        "invoice_path": str(invoice_path),
        "invoice": _invoice_summary(invoice),
        "overall_status": "blocked_honestly" if response.get("status") == "blocked" else "needs_review",
        "workflow_status": "blocked",
        "blocking_reason": response.get("blocking_reason"),
        "next_action": response.get("next_action"),
        "resource_id": response.get("resource_id"),
        "final_response": response,
        "steps": [
            {
                "step": 1,
                "action": "invoices.submit",
                "status": response.get("status"),
                "next_action": response.get("next_action"),
                "blocking_reason": response.get("blocking_reason"),
                "resource_id": response.get("resource_id"),
            }
        ],
        "notes": [
            "No live MyInvois submission was performed.",
            "Real-provider execution is intentionally approval-gated and credential-gated.",
        ],
    }


def _step_summary(log_item: dict[str, Any]) -> dict[str, Any]:
    response = log_item.get("response") or {}
    return {
        "step": log_item.get("step"),
        "action": log_item.get("action"),
        "status": response.get("status"),
        "next_action": response.get("next_action"),
        "blocking_reason": response.get("blocking_reason"),
        "resource_id": response.get("resource_id"),
    }


def _first_response_data(execution_log: list[dict[str, Any]], key: str) -> Any:
    for item in execution_log:
        data = (item.get("response") or {}).get("data") or {}
        if data.get(key):
            return data[key]
    return None


def _invoice_summary(invoice: dict[str, Any]) -> dict[str, Any]:
    return {
        "invoice_number": invoice.get("invoice_number"),
        "issue_date": invoice.get("issue_date"),
        "supplier_tin": invoice.get("supplier_tin"),
        "buyer_tin": invoice.get("buyer_tin"),
        "currency": invoice.get("currency") or "MYR",
        "total_amount": invoice.get("total_amount"),
        "line_item_count": len(invoice.get("line_items") or []),
    }


def _load_json_object(path: Path | None) -> dict[str, Any]:
    if path is None:
        raise TaxExecutionError("JSON path is required.")
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise TaxExecutionError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise TaxExecutionError(f"{path} must contain a JSON object.")
    return payload


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
