# Webhook Troubleshooting Matrix

| Symptom | Likely cause | Validation | Corrective action |
| --- | --- | --- | --- |
| HTTP 400 | Invalid JSON or unsupported payload field | Validate the exact request body with a JSON parser | Correct quoting, commas, and required fields |
| HTTP 401 or 404 | Revoked, incomplete, or incorrect endpoint | Compare the configured endpoint with the newly issued secret | Rotate the webhook and update the source |
| HTTP 429 | Destination rate limit | Inspect response headers and delivery frequency | Honor retry guidance and reduce event volume |
| Raw placeholders appear | Source platform did not substitute variables | Send a test with one known placeholder | Correct the source platform's placeholder syntax |
| Message reaches wrong channel | Webhook was created for another destination | Review the webhook destination in Discord | Create a dedicated webhook for the intended channel |
| No event leaves source | Trigger condition did not fire | Review source-side event history | Simplify the test condition and trigger a controlled event |

## Ticket Evidence

Record the source event timestamp, HTTP status, destination, payload version, and corrective action. Never paste the full webhook URL into the ticket.
