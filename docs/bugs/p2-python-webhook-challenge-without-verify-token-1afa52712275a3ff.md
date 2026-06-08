# [P2] Validate webhook verification tokens before echoing challenges

## Severity

P2 - security/webhook-verification

## Evidence

- `app.py:26`: `@app.get('/messenger/webhook')`
- `app.py:27`: `def messenger_webhook():`
- `app.py:31`: `challenge = request.query.get("hub.challenge")`
- `app.py:32`: `return challenge`

## Problem

The webhook verification handler echoes the platform challenge without checking the shared `hub.verify_token`. That means the endpoint does not enforce the setup secret and cannot distinguish a legitimate platform verification request from an arbitrary caller probing the webhook URL.

## Suggested fix

Read `hub.verify_token`, compare it with a configured secret using a constant-time comparison where practical, return the challenge only on match, and reject mismatches with a deterministic 403 or 400 response.

## Status

Fixed on 2026-06-08. The Messenger verification route now compares `hub.verify_token` with `MESSENGER_VERIFY_TOKEN` before returning the challenge, and rejects mismatches with 403.

## Review metadata

- Repository: `garethpaul/valleybot`
- Reviewed commit: `6df2bcf1a11e7ca64a4f52b279385ea7d13a33a2`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `1afa52712275a3ff`
