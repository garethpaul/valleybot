# Messenger JSON Content Type

Status: Completed

## Context

The Messenger POST route bounds and authenticates the raw body before reading
Bottle's parsed JSON value, but it does not require the request to declare a
JSON media type. A signed request with a missing, unrelated, or spoofed-prefix
content type can therefore reach framework parsing with an ambiguous body
contract.

## Plan

1. Parse the media type before reading or authenticating the webhook body.
2. Accept case-insensitive `application/json` with optional parameters.
3. Reject missing, unrelated, suffix, and prefix-spoofed values with HTTP 415.
4. Add dependency-free and Bottle/WebTest regression coverage.
5. Preserve the 1 MiB body limit, SHA-256 signature verification, page-object
   validation, and response behavior for valid Messenger requests.

## Verification

- Focused dependency-free Messenger contracts passed.
- All 9 Bottle/WebTest `TestFacebook` tests passed under an isolated Python
  3.12 environment with the pinned requirements installed.
- `make check` and an external-working-directory Make invocation passed with
  the isolated interpreter.
- Missing, unrelated, suffix, prefix-spoofed, and guard-removal mutations were
  rejected by focused or full verification.
- Python compilation and `git diff --check` passed.
