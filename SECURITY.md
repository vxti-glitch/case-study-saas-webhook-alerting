# Security Policy

## Sensitive Data

Do not submit live webhook URLs, tokens, account identifiers, private channel names, or production alert content in issues or pull requests.

## If a Webhook Is Exposed

1. Delete or rotate the webhook in the destination platform.
2. Update the source platform with the new endpoint.
3. Review recent destination messages for unauthorized use.
4. Remove the secret from files and Git history.
5. Document the incident without repeating the secret.

The endpoint shown in documentation must use explicit placeholders such as `WEBHOOK_ID` and `WEBHOOK_TOKEN`.
