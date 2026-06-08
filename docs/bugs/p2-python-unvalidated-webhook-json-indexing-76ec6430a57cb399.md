# [P2] Validate webhook JSON before indexing nested message fields

## Severity

P2 - correctness/api

## Evidence

- `app.py:40`: `data = request.json`
- `app.py:42`: `msg_data = data['entry'][0]['messaging'][0]`
- `app.py:43`: `sender = msg_data['sender']['id']`
- `app.py:44`: `message = msg_data['message']['text']`
- `app.py:46`: `if not data['debug']:`

## Problem

The webhook handler reads `request.json` and immediately indexes nested fields such as `entry`, `messaging`, `message`, or `text`. Normal webhook traffic can include verification, postback, delivery, read, malformed, or missing-message events, so those requests can raise `KeyError` or `TypeError` and return 500 instead of a stable acknowledgement.

## Suggested fix

Check that the payload is a dictionary, validate the expected object and messaging shape with `.get()` or schema checks, gracefully ignore unsupported event types, and return a deterministic 2xx/4xx response instead of indexing missing keys.

## Review metadata

- Repository: `garethpaul/valleybot`
- Reviewed commit: `5c3c174fac553dc1809079ab552629334c1967e3`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `76ec6430a57cb399`
