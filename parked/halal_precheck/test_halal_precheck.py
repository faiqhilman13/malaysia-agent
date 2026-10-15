"""Tests for the parked halal precheck, ported from the v0 suite.

Expiry checks are pinned to AS_OF so the results do not change as the sample certificates age.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from halal_precheck import DEFAULT_REQUIREMENTS_PATH, evaluate_dossier, main  # noqa: E402

AS_OF = date(2026, 6, 1)
EXAMPLES = HERE / "examples"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _ocr(*paths: str) -> dict[str, dict]:
    records = [_load(EXAMPLES / "ocr" / p) for p in paths]
    return {record["document_path"]: record for record in records}


class HalalPrecheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requirements = _load(DEFAULT_REQUIREMENTS_PATH)

    def test_sample_dossier_passes_with_ocr(self) -> None:
        result = evaluate_dossier(
            dossier=_load(EXAMPLES / "barakah-curry-paste.dossier.json"),
            ruleset=self.requirements,
            ocr_records=_ocr("barakah/supplier-a-coconut-cert.json", "barakah/supplier-b-chili-cert.json"),
            as_of=AS_OF,
        )
        self.assertEqual(result["summary"]["overall_status"], "pass")
        self.assertGreaterEqual(result["summary"]["requirements_passed"], 10)
        self.assertEqual(result["summary"]["ocr_mismatches"], 0)
        requirement_ids = {item["requirement_id"] for item in result["requirements"]}
        self.assertIn("MY-HALAL-APP-SSM-001", requirement_ids)
        self.assertIn("MY-HALAL-INGREDIENT-CERT-001", requirement_ids)

    def test_expiry_is_evaluated_against_as_of(self) -> None:
        # The sample chili certificate expires on 2026-10-15; one day later it must be flagged.
        result = evaluate_dossier(
            dossier=_load(EXAMPLES / "barakah-curry-paste.dossier.json"),
            ruleset=self.requirements,
            ocr_records=_ocr("barakah/supplier-a-coconut-cert.json", "barakah/supplier-b-chili-cert.json"),
            as_of=date(2026, 10, 16),
        )
        self.assertEqual(result["summary"]["expired_documents"], 1)
        self.assertEqual(result["summary"]["overall_status"], "needs_remediation")

    def test_failing_dossier_surfaces_remediation(self) -> None:
        result = evaluate_dossier(
            dossier=_load(EXAMPLES / "barakah-curry-paste-incomplete.dossier.json"),
            ruleset=self.requirements,
            ocr_records=_ocr(
                "barakah-failing/supplier-a-coconut-cert.json",
                "barakah-failing/supplier-b-chili-cert-expired.json",
            ),
            as_of=AS_OF,
        )
        self.assertEqual(result["summary"]["overall_status"], "needs_remediation")
        self.assertGreaterEqual(result["summary"]["requirements_failed"], 2)
        self.assertEqual(result["summary"]["ocr_mismatches"], 1)
        self.assertEqual(result["summary"]["expired_documents"], 1)
        failed_ids = {item["requirement_id"] for item in result["requirements"] if item["status"] == "fail"}
        self.assertIn("MY-HALAL-PROCESS-001", failed_ids)
        self.assertIn("MY-HALAL-FINANCIAL-001", failed_ids)

    def test_restaurant_dossier_uses_food_premise_rules(self) -> None:
        result = evaluate_dossier(
            dossier=_load(EXAMPLES / "seri-melaka-restaurant.dossier.json"),
            ruleset=self.requirements,
            ocr_records=_ocr("seri-melaka/supplier-c-stock-cert.json"),
            as_of=AS_OF,
        )
        self.assertEqual(result["summary"]["overall_status"], "pass")
        requirement_ids = {item["requirement_id"] for item in result["requirements"]}
        self.assertIn("MY-HALAL-FOODPREM-MENU-001", requirement_ids)
        self.assertIn("MY-HALAL-KKM-FOODPREM-001", requirement_ids)
        self.assertNotIn("MY-HALAL-PROCESS-001", requirement_ids)

    def test_cli_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir) / "reports"
            code = main(
                [
                    "--file",
                    str(EXAMPLES / "barakah-curry-paste.dossier.json"),
                    "--ocr-dir",
                    str(EXAMPLES / "ocr" / "barakah"),
                    "--out-dir",
                    str(out_dir),
                    "--as-of",
                    AS_OF.isoformat(),
                ]
            )
            self.assertEqual(code, 0)
            for filename in [
                "precheck.json",
                "applicant-report.md",
                "reviewer-report.md",
                "applicant-report.html",
                "reviewer-report.html",
            ]:
                self.assertTrue((out_dir / filename).exists(), filename)
            self.assertEqual(_load(out_dir / "precheck.json")["summary"]["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
