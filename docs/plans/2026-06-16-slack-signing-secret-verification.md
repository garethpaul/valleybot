# Slack Signing-Secret Verification

status: in_progress

## Context

Both Slack entry points authenticate a caller-controlled form or event `token`.
Slack signing secrets provide request-body integrity and replay-resistant
timestamps, while the legacy verification-token check cannot prove the body or
request time and is no longer an adequate webhook boundary.

## Priority

Close the unauthenticated command-execution boundary before adding more Slack
features. A forged request currently reaches `bot.respond`, which can trigger
the full response-generation path.

## Requirements

- R1. Require `SLACK_SIGNING_SECRET` for both Slack entry points; do not fall
  back to the deprecated payload token.
- R2. Verify `X-Slack-Signature` as HMAC-SHA256 over Slack's exact
  `v0:{timestamp}:{raw_body}` base string using constant-time comparison.
- R3. Reject missing, malformed, future, or older-than-five-minute timestamps
  before command processing.
- R4. Preserve the exact raw request body for signature verification before
  form parsing, including API Gateway base64 bodies for the event handler.
- R5. Keep invalid requests fail-closed and prevent `bot.respond` calls.
- R6. Preserve valid command-text trimming and current response behavior after
  authentication.
- R7. Add dependency-free, Bottle/WebTest, source, documentation, and completed
  plan contracts that reject hostile mutations.
- R8. Do not log secrets, signatures, raw bodies, or command text; do not make
  live Slack, Messenger, or external network requests.

## Implementation Units

### U1. Shared Slack verifier

**File:** `slack_auth.py`

Implement one dependency-free verifier with an injectable clock, strict
timestamp parsing/freshness, exact bytes handling, versioned signature format,
and constant-time comparison.

### U2. Bottle and event entry points

**Files:** `app.py`, `slack.py`, `settings.py`

Read the signing secret from configuration, verify headers and raw bytes before
form/event command extraction, decode API Gateway base64 bodies where declared,
and remove payload-token authorization.

### U3. Maintained verification and guidance

**Files:** `bot_tests.py`, `scripts/check_valleybot_contracts.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Cover valid signatures, tampering, stale/future/malformed timestamps, missing
configuration, base64 event bodies, response suppression, source ordering, and
completed verification evidence.

## Verification

- Run focused dependency-free and Bottle/WebTest Slack signature cases.
- Run the complete dependency-free and pinned runtime suites through repository
  and external-directory Make gates.
- Reject isolated mutations for HMAC input, freshness, constant-time compare,
  deprecated-token fallback, base64 handling, response suppression, guidance,
  and plan status.
- Audit the exact diff, generated artifacts, changed lines for credentials,
  dependency/workflow drift, file modes, and whitespace before commit.

## Scope Boundaries

- Do not change Messenger behavior, dependencies, workflows, or bot response
  selection.
- Do not add a replay database or background queue; the signed timestamp window
  is the bounded replay protection in this change.
- Do not accept unsigned requests for compatibility.

## Verification Completed

Pending implementation and validation.
