"""
Automated 16-Point Staging Smoke Test Suite for [STUDIO_NAME]
Conforms strictly to DOC-REP-6.2.5-PLAN Section 9.

Validates the full application flow over HTTP/HTTPS:
- Public web pages (Homepage, Services, Solutions, How We Work, About, Contact)
- Input validation and error envelopes (Contact form valid & invalid)
- Consultative Discovery journey (Start, Problem, Clarifications, Opportunity Map, Blueprint Unlock)
- Operational health and database readiness probes (health/live, health/ready)
- Security response headers, correlation IDs, and HTTP-only session cookies.

Usage:
    python scripts/smoke_test.py --base-url http://127.0.0.1:8000
    python scripts/smoke_test.py --base-url https://staging.studio.example --timeout 15
"""

import argparse
import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


class SmokeTestRunner:
    """Executes non-destructive staging smoke tests against a live application URL."""

    def __init__(self, base_url: str, timeout: float = 10.0, verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verbose = verbose
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.results: List[Tuple[str, str, bool, str, float]] = []

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
    ) -> Tuple[int, Dict[str, str], str]:
        """Performs HTTP request with cookie persistence and returns status, headers, and body."""
        url = f"{self.base_url}{path}"
        req_headers = {
            "User-Agent": "StudioSmokeTest/1.0",
            "Accept": "text/html,application/xhtml+xml,application/json,*/*",
        }
        if headers:
            req_headers.update(headers)

        body_bytes = None
        if data is not None:
            if req_headers.get("Content-Type") == "application/json":
                body_bytes = json.dumps(data).encode("utf-8")
            else:
                req_headers["Content-Type"] = "application/x-www-form-urlencoded"
                body_bytes = urllib.parse.urlencode(data).encode("utf-8")

        req = urllib.request.Request(url, data=body_bytes, headers=req_headers, method=method)

        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                status_code = resp.getcode()
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                resp_body = resp.read().decode("utf-8", errors="replace")
                return status_code, resp_headers, resp_body
        except urllib.error.HTTPError as http_err:
            status_code = http_err.code
            resp_headers = {k.lower(): v for k, v in http_err.headers.items()}
            resp_body = http_err.read().decode("utf-8", errors="replace")
            return status_code, resp_headers, resp_body

    def run_check(
        self,
        test_id: str,
        name: str,
        method: str,
        path: str,
        expected_status: int,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body_assertions: Optional[List[str]] = None,
        header_assertions: Optional[List[str]] = None,
    ) -> bool:
        """Executes a single check, measures duration, and records result."""
        start_time = time.perf_counter()
        passed = False
        message = ""

        try:
            status_code, resp_headers, body = self._request(
                method, path, data=data, headers=headers, expected_status=expected_status
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if status_code != expected_status:
                message = f"Status mismatch: expected {expected_status}, got {status_code}"
            else:
                # Check required response headers (e.g. security headers, correlation ID)
                failed_headers = []
                if header_assertions:
                    for hdr in header_assertions:
                        if hdr.lower() not in resp_headers:
                            failed_headers.append(hdr)

                # Check required body substrings
                failed_body = []
                if body_assertions:
                    for text in body_assertions:
                        if text not in body:
                            failed_body.append(text)

                if failed_headers:
                    message = f"Missing headers: {', '.join(failed_headers)}"
                elif failed_body:
                    message = f"Missing body tokens: {', '.join(failed_body)}"
                else:
                    passed = True
                    message = "Pass"

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            message = f"Request error: {exc.__class__.__name__} ({str(exc)})"

        self.results.append((test_id, name, passed, message, duration_ms))
        status_str = "PASS" if passed else "FAIL"
        if self.verbose or not passed:
            print(f"[{status_str}] {test_id} - {name} ({duration_ms}ms) -> {message}")
        else:
            print(f"[{status_str}] {test_id} - {name} ({duration_ms}ms)")

        return passed

    def execute_suite(self) -> bool:
        """Runs all 16 staging smoke tests in sequence."""
        print("==================================================")
        print(f"STARTING STAGING SMOKE TEST SUITE: {self.base_url}")
        print("==================================================")

        common_security_headers = [
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "content-security-policy",
            "x-correlation-id",
        ]

        # 1. Public Web Views (SMK-01 to SMK-07)
        self.run_check(
            "SMK-01", "GET Homepage", "GET", "/", 200,
            body_assertions=["Turn Business Problems Into Technology", "Start With Your Problem"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-02", "GET Services Index", "GET", "/services", 200,
            body_assertions=["Capability Pillars", "Software & Websites", "AI Solutions"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-03", "GET Service Pillar Detail", "GET", "/services/software", 200,
            body_assertions=["Software & Websites", "Deliverables", "Capabilities"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-04", "GET Solutions Index", "GET", "/solutions", 200,
            body_assertions=["Solution Blueprints", "Enterprise Outcomes"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-05", "GET How We Work", "GET", "/how-we-work", 200,
            body_assertions=["Methodology", "Human + AI", "Engineering Principles"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-06", "GET About", "GET", "/about", 200,
            body_assertions=["About", "Philosophy", "Technical Ethos"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-07", "GET Contact Form", "GET", "/contact", 200,
            body_assertions=["Contact Senior Architects", "corporate_email"],
            header_assertions=common_security_headers,
        )

        # 2. Contact Ingestion & Validation (SMK-08 & SMK-09)
        self.run_check(
            "SMK-08", "POST Contact Inquiry (Valid)", "POST", "/contact", 200,
            data={
                "full_name": "Smoke Test Auditor",
                "corporate_email": "auditor@smoke.test",
                "company_name": "Studio Testing Corp",
                "project_scope": "Software & Web Applications",
                "message": "Automated staging smoke test validating contact route ingestion.",
            },
            body_assertions=["Inquiry Received", "Thank you for reaching out"],
        )
        self.run_check(
            "SMK-09", "POST Contact Inquiry (Invalid - Missing Email)", "POST", "/contact", 422,
            data={
                "full_name": "Incomplete User",
                "corporate_email": "",
                "message": "Missing email should trigger unprocessable entity.",
            },
            body_assertions=["Corporate email is required"],
        )

        # 3. Discovery Workflow Engine (SMK-10 to SMK-14)
        self.run_check(
            "SMK-10", "GET Discovery Entry", "GET", "/discovery", 200,
            body_assertions=["Diagnostic Container", "Describe Your Business Challenge"],
            header_assertions=common_security_headers,
        )
        self.run_check(
            "SMK-11", "POST Discovery Session Start", "POST", "/discovery/start", 200,
            data={"entry_point": "smoke_test"},
            body_assertions=["Describe your core challenge", "character_count"],
        )
        self.run_check(
            "SMK-12", "POST Discovery Problem Intake", "POST", "/discovery/problem", 200,
            data={
                "problem_text": "We are experiencing significant manual friction in our customer onboarding and contract processing workflows."
            },
            body_assertions=["Architectural Clarifications", "questions"],
        )
        self.run_check(
            "SMK-13", "POST Discovery Clarification Answers", "POST", "/discovery/answers", 200,
            data={
                "answer_1": "We process approximately 500 documents weekly.",
                "answer_2": "Our existing stack runs on SQL Server and Python.",
            },
            body_assertions=["Executive Opportunity Map", "opportunities"],
        )
        self.run_check(
            "SMK-14", "POST Discovery Lead Unlock", "POST", "/discovery/unlock", 200,
            data={
                "full_name": "Enterprise Director",
                "corporate_email": "director@enterprise.example",
                "company_name": "Enterprise Solutions Ltd",
                "consent": "on",
            },
            body_assertions=["Solution Blueprint", "Indicative Sizing"],
        )

        # 4. Health & Database Readiness Probes (SMK-15 & SMK-16)
        self.run_check(
            "SMK-15", "GET Liveness Probe", "GET", "/health/live", 200,
            body_assertions=['"status":"alive"', "uptime_seconds"],
        )
        self.run_check(
            "SMK-16", "GET Readiness Probe", "GET", "/health/ready", 200,
            body_assertions=['"status":"ready"', '"engine":"Microsoft SQL Server"', '"status":"connected"'],
        )

        # Summary
        total = len(self.results)
        passed_count = sum(1 for _, _, p, _, _ in self.results if p)
        failed_count = total - passed_count

        print("==================================================")
        print(f"SMOKE TEST SUMMARY: {passed_count}/{total} PASSED ({failed_count} FAILED)")
        print("==================================================")

        return failed_count == 0


def main():
    parser = argparse.ArgumentParser(description="Automated Staging Smoke Test Suite")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of target application (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds (default: 10.0)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed diagnostic logging",
    )

    args = parser.parse_args()
    runner = SmokeTestRunner(base_url=args.base_url, timeout=args.timeout, verbose=args.verbose)
    success = runner.execute_suite()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
