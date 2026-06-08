# [P2] Verify Slack slash command requests before running bot commands

## Severity

P2 - security/webhook-verification

## Evidence

- `app.py:16`: `@app.post('/slack')`
- `app.py:17`: `def slack_handler():`
- `app.py:21`: `command_text = request.forms.get('text')`
- `app.py:22`: `return bot.respond(command_text)`

## Problem

The Slack command endpoint reads form text and returns a bot response without validating Slack's request signature or verification token. Anyone who can reach the route can forge command requests and exercise the bot outside the trusted Slack integration.

## Suggested fix

Validate `X-Slack-Signature` and `X-Slack-Request-Timestamp` with the Slack signing secret before reading command text, or at minimum compare the legacy `token` form field with a configured secret using a constant-time comparison. Reject missing or invalid verification with 401 or 403 and update tests to cover unauthenticated requests.

## Review metadata

- Repository: `garethpaul/valleybot`
- Reviewed commit: `6604570032cdbd328a8012045e97258c080c5bff`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `1246b423a1a865c0`
