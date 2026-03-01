from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


def _resolve_json_path(payload: dict, path: str) -> object:
    current: object = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Path '{path}' is missing in response body.")
        current = current[part]
    return current


def run_scenario(scenario_path: Path, base_url_override: str | None = None) -> int:
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    base_url = (base_url_override or scenario["base_url"]).rstrip("/")
    checks = scenario.get("checks", [])
    session = requests.Session()
    session.trust_env = False

    for check in checks:
        method = check.get("method", "GET").upper()
        path = check.get("path", "")
        url = f"{base_url}{path}"

        if method == "GET":
            response = session.get(url, timeout=15)
        elif method == "POST":
            response = session.post(url, json=check.get("json", {}), timeout=15)
        else:
            raise ValueError(f"Unsupported method '{method}' in scenario.")

        expected_status = int(check["expected_status"])
        if response.status_code != expected_status:
            raise AssertionError(
                f"{check['name']}: status {response.status_code} != {expected_status}"
            )

        contains = check.get("contains")
        if contains and contains not in response.text:
            raise AssertionError(f"{check['name']}: '{contains}' was not found in response.")

        json_path = check.get("expected_json_path")
        if json_path:
            payload = response.json()
            value = _resolve_json_path(payload, json_path)
            expected_length = check.get("expected_length")
            if expected_length is not None and len(value) != int(expected_length):
                raise AssertionError(
                    f"{check['name']}: length {len(value)} != {expected_length}"
                )

        print(f"[OK] {check['name']}")

    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run functional scenario against model API.")
    parser.add_argument(
        "--scenario",
        default="scenario.json",
        help="Path to scenario definition in JSON format.",
    )
    parser.add_argument("--base-url", default=None, help="Override base URL from scenario.json.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run_scenario(Path(args.scenario), args.base_url)


if __name__ == "__main__":
    raise SystemExit(main())
