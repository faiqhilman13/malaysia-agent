from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import Settings, myinvois_environment_name


class RemoteApiError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _parse_response_body(raw: bytes) -> Any:
    text = raw.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


class RemoteApiClient:
    def request_json(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        form_body: dict[str, Any] | None = None,
        timeout: int = 20,
    ) -> Any:
        body = None
        merged_headers = dict(headers or {})
        if json_body is not None and form_body is not None:
            raise ValueError("Provide either json_body or form_body, not both.")
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            merged_headers.setdefault("Content-Type", "application/json")
        elif form_body is not None:
            body = urlencode(form_body).encode("utf-8")
            merged_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

        request = Request(url=url, data=body, headers=merged_headers, method=method.upper())
        try:
            with urlopen(request, timeout=timeout) as response:
                raw = response.read()
            return _parse_response_body(raw)
        except HTTPError as exc:
            body_data = _parse_response_body(exc.read())
            raise RemoteApiError(
                f"Remote API request failed with status {exc.code}",
                status_code=exc.code,
                body=body_data,
            ) from exc
        except URLError as exc:
            raise RemoteApiError(f"Remote API request failed: {exc.reason}") from exc


@dataclass
class MyInvoisClient:
    settings: Settings
    environment: str
    http: RemoteApiClient | None = None

    def __post_init__(self) -> None:
        self.environment = myinvois_environment_name(self.environment)
        self.http = self.http or RemoteApiClient()

    @property
    def api_base(self) -> str:
        if self.environment == "sandbox":
            return self.settings.myinvois_sandbox_api_base.rstrip("/")
        return self.settings.myinvois_production_api_base.rstrip("/")

    @property
    def identity_base(self) -> str:
        if self.environment == "sandbox":
            return self.settings.myinvois_sandbox_identity_base.rstrip("/")
        return self.settings.myinvois_production_identity_base.rstrip("/")

    def default_credentials(self) -> tuple[str | None, str | None]:
        if self.environment == "sandbox":
            return (
                self.settings.myinvois_sandbox_client_id,
                self.settings.myinvois_sandbox_client_secret,
            )
        return (
            self.settings.myinvois_production_client_id,
            self.settings.myinvois_production_client_secret,
        )

    def login_taxpayer(self, *, client_id: str, client_secret: str, scope: str = "InvoicingAPI") -> Any:
        return self.http.request_json(
            method="POST",
            url=f"{self.identity_base}/connect/token",
            form_body={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "scope": scope,
            },
        )

    def login_intermediary(
        self,
        *,
        client_id: str,
        client_secret: str,
        onbehalfof: str,
        scope: str = "InvoicingAPI",
    ) -> Any:
        return self.http.request_json(
            method="POST",
            url=f"{self.identity_base}/connect/token",
            headers={"onbehalfof": onbehalfof},
            form_body={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "scope": scope,
            },
        )

    def get_document_types(self, *, access_token: str) -> Any:
        return self.http.request_json(
            method="GET",
            url=f"{self.api_base}/api/v1.0/documenttypes",
            headers=self._bearer_headers(access_token),
        )

    def validate_tin(
        self,
        *,
        access_token: str,
        tin: str,
        id_type: str,
        id_value: str,
    ) -> Any:
        query = urlencode({"idType": id_type, "idValue": id_value})
        return self.http.request_json(
            method="GET",
            url=f"{self.api_base}/api/v1.0/taxpayer/validate/{tin}?{query}",
            headers=self._bearer_headers(access_token),
        )

    def search_tin(
        self,
        *,
        access_token: str,
        id_type: str,
        id_value: str,
        entity_type: str | None = None,
    ) -> Any:
        params = {"idType": id_type, "idValue": id_value}
        if entity_type:
            params["entityType"] = entity_type
        query = urlencode(params)
        return self.http.request_json(
            method="GET",
            url=f"{self.api_base}/api/v1.0/taxpayer/search/tin?{query}",
            headers=self._bearer_headers(access_token),
        )

    def submit_documents(self, *, access_token: str, documents: list[Any]) -> Any:
        return self.http.request_json(
            method="POST",
            url=f"{self.api_base}/api/v1.0/documentsubmissions/",
            headers=self._bearer_headers(access_token),
            json_body={"documents": documents},
        )

    def get_submission(
        self,
        *,
        access_token: str,
        submission_uid: str,
        page_no: int = 1,
        page_size: int = 100,
    ) -> Any:
        query = urlencode({"pageNo": page_no, "pageSize": page_size})
        return self.http.request_json(
            method="GET",
            url=f"{self.api_base}/api/v1.0/documentsubmissions/{submission_uid}?{query}",
            headers=self._bearer_headers(access_token),
        )

    def cancel_document(
        self,
        *,
        access_token: str,
        document_uuid: str,
        reason: str,
    ) -> Any:
        return self.http.request_json(
            method="PUT",
            url=f"{self.api_base}/api/v1.0/documents/state/{document_uuid}/state",
            headers=self._bearer_headers(access_token),
            json_body={"status": "cancelled", "reason": reason},
        )

    @staticmethod
    def _bearer_headers(access_token: str) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }


@dataclass
class CIDBClient:
    settings: Settings
    http: RemoteApiClient | None = None

    def __post_init__(self) -> None:
        self.http = self.http or RemoteApiClient()

    @property
    def api_base(self) -> str:
        return self.settings.cidb_api_base.rstrip("/")

    def get_states(self, *, access_token: str) -> Any:
        return self.http.request_json(
            method="GET",
            url=f"{self.api_base}/internal/states",
            headers=self._headers(access_token),
        )

    def get_labour_wage_rate(
        self,
        *,
        access_token: str,
        state_id: int,
        state_name: str,
        year: int,
    ) -> Any:
        return self.http.request_json(
            method="POST",
            url=f"{self.api_base}/internal/products/labour-wage-rate",
            headers=self._headers(access_token, include_json=True),
            json_body={
                "selectedStates": [{"id": state_id, "name": state_name}],
                "option": "two",
                "year": year,
            },
        )

    def get_building_material_price(
        self,
        *,
        access_token: str,
        state_id: int,
        state_name: str,
        year: int,
    ) -> Any:
        return self.http.request_json(
            method="POST",
            url=f"{self.api_base}/internal/products/building-material-price",
            headers=self._headers(access_token, include_json=True),
            json_body={
                "selectedStates": [{"id": state_id, "name": state_name}],
                "option": "two",
                "year": year,
            },
        )

    def get_machinery_rates(
        self,
        *,
        access_token: str,
        state_id: int,
        state_name: str,
        year: int,
    ) -> Any:
        return self.http.request_json(
            method="POST",
            url=f"{self.api_base}/internal/products/machinery-hire-rate-equipment-purchase-price",
            headers=self._headers(access_token, include_json=True),
            json_body={
                "selectedStates": [{"id": state_id, "name": state_name}],
                "option": "two",
                "year": year,
            },
        )

    @staticmethod
    def _headers(access_token: str, *, include_json: bool = False) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        if include_json:
            headers["Content-Type"] = "application/json"
        return headers

