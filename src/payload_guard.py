"""Validate a local webhook payload without sending any network request."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DISCORD_WEBHOOK_URL = re.compile(
    r"https://(?:discord\.com|discordapp\.com)/api/webhooks/\d+/[A-Za-z0-9._-]+",
    re.IGNORECASE,
)
TOKEN_LIKE_VALUE = re.compile(
    r"(?i)(?:ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]+|bearer\s+\S+)"
)
SENSITIVE_KEYWORDS = ("authorization", "token", "secret", "api_key", "apikey", "webhook_url")


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def load_payload(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Payload must be a JSON object.")
    return data


def find_sensitive_values(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{path}.{key}"
            normalized_key = str(key).lower().replace("-", "_")
            if any(keyword in normalized_key for keyword in SENSITIVE_KEYWORDS):
                findings.append(f"{key_path} uses a secret-bearing key name.")
            findings.extend(find_sensitive_values(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(find_sensitive_values(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        if DISCORD_WEBHOOK_URL.search(value):
            findings.append(f"{path} contains a live Discord webhook URL.")
        if TOKEN_LIKE_VALUE.search(value):
            findings.append(f"{path} contains a token-like value.")
    return findings


def validate_payload(payload: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    content = payload.get("content")
    if not isinstance(content, str) or not content.strip():
        errors.append("Payload must include a non-empty string content field.")

    unsupported_keys = sorted(set(payload) - {"content", "username", "avatar_url", "embeds", "allowed_mentions"})
    if unsupported_keys:
        errors.append(f"Payload contains unsupported top-level keys: {', '.join(unsupported_keys)}.")

    errors.extend(find_sensitive_values(payload))
    return ValidationResult(tuple(errors))


def render_preview(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, indent=2, sort_keys=True)
    return "\n".join(
        [
            "# Safe Webhook Payload Preview",
            "",
            "The payload passed local validation. This tool did not send an HTTP request.",
            "",
            "~~~json",
            serialized,
            "~~~",
            "",
        ]
    )


def write_preview(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_preview(payload), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a local webhook payload without sending it anywhere."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to JSON payload.")
    parser.add_argument("--out", type=Path, help="Optional Markdown preview output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid payload file: {exc}")
        return 2

    result = validate_payload(payload)
    if not result.is_valid:
        print("Payload validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1

    if args.out:
        write_preview(payload, args.out)
        print(f"Safe preview written to {args.out.resolve()}")
    else:
        print("Payload validation passed. No network request was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
