"""A test-only stand-in for the MyInvois API, served through httpx.MockTransport.

It checks what the real API would: client credentials, the onbehalfof header, bearer tokens, the
document hash, and that intermediaries only submit for the taxpayer they logged in for.
"""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs

import httpx


@dataclass
class FakeMyInvois:
    clients: dict[str, str] = field(default_factory=lambda: {"client-1": "secret-1"})
    registered_tins: dict[str, tuple[str, str]] = field(default_factory=dict)  # tin -> (id_type, id_value)
    reject_codes: set[str] = field(default_factory=set)  # code numbers rejected at submission
    invalid_codes: set[str] = field(default_factory=set)  # code numbers that fail async validation
    pending_codes: set[str] = field(default_factory=set)  # code numbers still being validated
    throttle_next: int = 0  # number of upcoming API calls to answer with 429
    tokens: dict[str, tuple[str, str | None]] = field(default_factory=dict)
    submissions: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    calls: list[tuple[str, str]] = field(default_factory=list)
    logins: list[str | None] = field(default_factory=list)
    received: dict[str, dict[str, Any]] = field(default_factory=dict)  # uuid -> details for documents we received
    clock: Any = None  # callable returning "now"; defaults to real time

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handle)

    def handle(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        self.calls.append((request.method, path))
        if path == "/connect/token":
            return self._login(request)
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if token not in self.tokens:
            return httpx.Response(401)
        if self.throttle_next > 0:
            self.throttle_next -= 1
            return httpx.Response(429, headers={"Retry-After": "1"})
        _, on_behalf_of = self.tokens[token]
        if path.startswith("/api/v1.0/taxpayer/validate/"):
            tin = path.rsplit("/", 1)[-1]
            expected = self.registered_tins.get(tin)
            query = request.url.params
            ok = expected is not None and expected == (query.get("idType"), query.get("idValue"))
            return httpx.Response(200 if ok else 404)
        if path == "/api/v1.0/taxpayer/search/tin":
            for tin, ident in self.registered_tins.items():
                if ident == (request.url.params.get("idType"), request.url.params.get("idValue")):
                    return httpx.Response(200, json={"tin": tin})
            return httpx.Response(404)
        if path == "/api/v1.0/documentsubmissions/" and request.method == "POST":
            return self._submit(json.loads(request.content), on_behalf_of)
        if path.startswith("/api/v1.0/documentsubmissions/"):
            return self._get_submission(path.rsplit("/", 1)[-1])
        if path.endswith("/details"):
            doc_uuid = path.split("/")[-2]
            if doc_uuid in self.received:
                return httpx.Response(200, json=self.received[doc_uuid])
            doc = self.documents.get(doc_uuid)
            if doc is None:
                return httpx.Response(404)
            details = {"uuid": doc_uuid, "status": doc["status"], "receiverId": doc["buyer_tin"]}
            if doc["status"] == "Invalid":
                details["validationResults"] = {
                    "status": "Invalid",
                    "validationSteps": [
                        {
                            "status": "Invalid",
                            "name": "Step03-Taxpayer TIN Validator",
                            "error": {
                                "propertyPath": "Invoice.AccountingCustomerParty",
                                "error": "Buyer TIN not found",
                            },
                        }
                    ],
                }
            return httpx.Response(200, json=details)
        if path.startswith("/api/v1.0/documents/state/"):
            doc_uuid = path.split("/")[-2]
            body = json.loads(request.content)
            target = self.documents.get(doc_uuid) or self.received.get(doc_uuid)
            if target is None:
                return httpx.Response(404)
            target["status"] = body["status"].capitalize()
            target["reason"] = body["reason"]
            return httpx.Response(200, json={"uuid": doc_uuid, "status": body["status"]})
        return httpx.Response(404, json={"error": "unknown path"})

    def _login(self, request: httpx.Request) -> httpx.Response:
        form = parse_qs(request.content.decode())
        client_id = form.get("client_id", [""])[0]
        if self.clients.get(client_id) != form.get("client_secret", [""])[0]:
            return httpx.Response(400, json={"error": "invalid_client"})
        on_behalf_of = request.headers.get("onbehalfof")
        self.logins.append(on_behalf_of)
        token = f"tok-{uuid.uuid4().hex[:8]}"
        self.tokens[token] = (client_id, on_behalf_of)
        return httpx.Response(200, json={"access_token": token, "expires_in": 3600, "token_type": "Bearer"})

    def _submit(self, body: dict[str, Any], on_behalf_of: str | None) -> httpx.Response:
        accepted, rejected = [], []
        submission_uid = uuid.uuid4().hex[:26].upper()
        for entry in body["documents"]:
            raw = base64.b64decode(entry["document"])
            code = entry["codeNumber"]
            if hashlib.sha256(raw).hexdigest() != entry["documentHash"]:
                rejected.append(
                    {"invoiceCodeNumber": code, "error": {"code": "IncorrectHash", "message": "Hash mismatch"}}
                )
                continue
            invoice = json.loads(raw)["Invoice"][0]
            supplier_tin = invoice["AccountingSupplierParty"][0]["Party"][0]["PartyIdentification"][0]["ID"][0]["_"]
            buyer_tin = invoice["AccountingCustomerParty"][0]["Party"][0]["PartyIdentification"][0]["ID"][0]["_"]
            doc_type = invoice["InvoiceTypeCode"][0]["_"]
            issuer = buyer_tin if doc_type in ("11", "12", "13", "14") else supplier_tin
            if on_behalf_of and issuer != on_behalf_of:
                rejected.append(
                    {"invoiceCodeNumber": code, "error": {"code": "Forbidden", "message": "Not your taxpayer"}}
                )
                continue
            if code in self.reject_codes:
                rejected.append(
                    {
                        "invoiceCodeNumber": code,
                        "error": {
                            "code": "BadStructure",
                            "message": "Validation error",
                            "details": [{"propertyPath": "Invoice.ID", "message": "Duplicate"}],
                        },
                    }
                )
                continue
            doc_uuid = uuid.uuid4().hex[:26].upper()
            status = "Invalid" if code in self.invalid_codes else "Submitted" if code in self.pending_codes else "Valid"
            self.documents[doc_uuid] = {
                "code": code,
                "status": status,
                "buyer_tin": buyer_tin,
                "raw": raw,
                "submission": submission_uid,
                "signed": "UBLExtensions" in invoice,
            }
            accepted.append({"uuid": doc_uuid, "invoiceCodeNumber": code})
        self.submissions[submission_uid] = accepted
        return httpx.Response(
            202, json={"submissionUid": submission_uid, "acceptedDocuments": accepted, "rejectedDocuments": rejected}
        )

    def _get_submission(self, submission_uid: str) -> httpx.Response:
        if submission_uid not in self.submissions:
            return httpx.Response(404)
        summary = []
        for item in self.submissions[submission_uid]:
            doc = self.documents[item["uuid"]]
            entry = {"uuid": item["uuid"], "internalId": doc["code"], "status": doc["status"]}
            if doc["status"] == "Valid":
                entry["longId"] = f"LONG{item['uuid']}"
                entry["dateTimeValidated"] = (self.clock() if self.clock else datetime.now(timezone.utc)).isoformat()
            summary.append(entry)
        overall = "InProgress" if any(d["status"] == "Submitted" for d in summary) else "Valid"
        return httpx.Response(
            200, json={"submissionUid": submission_uid, "overallStatus": overall, "documentSummary": summary}
        )
