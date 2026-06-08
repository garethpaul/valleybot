# [P2] Set explicit timeouts on outbound HTTP calls

## Severity

P2 - reliability/availability

## Evidence

- `app.py:61`: `resp = requests.post(settings.messenger_url, json=data)`

## Problem

Python HTTP clients default to waiting forever when no timeout is set. If an upstream service accepts the connection and then stalls, request handlers, bot callbacks, or data download scripts can hang indefinitely.

## Suggested fix

Pass a bounded `timeout` to each `requests` or `urlopen` call, choose separate connect/read values where useful, and handle timeout exceptions with a clear retry or error path.

## Status

Fixed on 2026-06-08. Messenger replies now pass a configurable `REQUEST_TIMEOUT` value to `requests.post`.

## Review metadata

- Repository: `garethpaul/valleybot`
- Reviewed commit: `77eec190be8944b666da694e0b15f38814c29e12`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `a07c6a4bb0ee865f`
