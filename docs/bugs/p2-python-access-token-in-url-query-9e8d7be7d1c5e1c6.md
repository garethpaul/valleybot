# [P2] Send API access tokens outside URL query strings

## Severity

P2 - security/credential-exposure

## Evidence

- `settings.py:4`: `messenger_url = "https://graph.facebook.com/v2.6/me/messages?access_token=" + messenger_token`
- `app.py:61`: `resp = requests.post(settings.messenger_url, json=data)`

## Problem

The code builds API request URLs with `access_token` in the query string. Query strings are commonly captured by server logs, proxy logs, analytics, crash reports, and referrer headers, so bearer-style tokens can leak outside the process that needs them.

## Suggested fix

Pass tokens in an `Authorization` header or the provider SDK's credential field when supported. If the provider requires query parameters, keep the token scoped and short-lived, redact URLs before logging, and avoid storing the full tokenized URL in module-level constants.

## Review metadata

- Repository: `garethpaul/valleybot`
- Reviewed commit: `c345bdb5d09473604d1c02092204745341d375e4`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `9e8d7be7d1c5e1c6`
