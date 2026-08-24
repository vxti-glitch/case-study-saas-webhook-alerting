import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payload_guard import find_sensitive_values, render_preview, validate_payload


class PayloadGuardTests(unittest.TestCase):
    def test_valid_payload_passes(self) -> None:
        result = validate_payload(
            {
                "content": "Alert: {{event_name}}",
                "allowed_mentions": {"parse": []},
            }
        )

        self.assertTrue(result.is_valid)

    def test_live_webhook_url_is_rejected(self) -> None:
        findings = find_sensitive_values(
            {"content": "https://discord.com/api/webhooks/1234567890/example_token_value"}
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("live Discord webhook URL", findings[0])

    def test_secret_bearing_key_is_rejected(self) -> None:
        result = validate_payload({"content": "Test", "webhook_url": "placeholder"})

        self.assertFalse(result.is_valid)
        self.assertIn("unsupported top-level keys", result.errors[0])
        self.assertTrue(any("secret-bearing key name" in error for error in result.errors))

    def test_preview_states_that_no_request_was_sent(self) -> None:
        preview = render_preview({"content": "Synthetic test"})

        self.assertIn("did not send an HTTP request", preview)
        self.assertIn("Synthetic test", preview)


if __name__ == "__main__":
    unittest.main()
