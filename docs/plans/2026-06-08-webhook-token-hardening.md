# Valleybot Webhook And Messenger Hardening

## Context

Repo-local findings:

- `docs/bugs/p2-python-access-token-in-url-query-9e8d7be7d1c5e1c6.md`
- `docs/bugs/p2-python-http-call-without-timeout-a07c6a4bb0ee865f.md`
- `docs/bugs/p2-python-unvalidated-webhook-json-indexing-76ec6430a57cb399.md`

GitHub issues already cover debug mode and request timeout, but the current default branch still has repo-local findings for token URL construction and webhook JSON indexing.

## Plan

1. Move the Facebook Messenger access token out of the configured URL string.
2. Send Messenger API credentials via request parameters at call time.
3. Add an explicit timeout and status check for Messenger API calls.
4. Validate Messenger webhook JSON shape before indexing nested fields.
5. Verify Messenger webhook challenge requests before echoing the challenge.
6. Gate Bottle debug mode behind `BOTTLE_DEBUG`.
7. Add source-level baseline checks and remove resolved repo-local bug files.

## Verification

- Run `scripts/check-baseline.sh`.
- Run the scanner against this repo.
- Run `git diff --check`.
