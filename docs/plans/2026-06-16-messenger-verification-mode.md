# Require Messenger Subscription Verification Mode

## Status: Completed

## Context

The Messenger verification endpoint authenticates the verification token and
escapes the returned challenge, but it does not validate `hub.mode`. A request
with a matching token can therefore receive the challenge even when it is not
the platform's `subscribe` verification operation.

## Requirements

- Require the exact `subscribe` verification mode before returning a Messenger
  challenge.
- Reject missing, blank, differently cased, and unrelated mode values without
  reflecting the challenge.
- Preserve constant-time token comparison, escaped challenge output, and the
  existing missing-challenge behavior for valid subscription requests.
- Add dependency-free and Bottle/WebTest regressions plus fail-closed source,
  documentation, changelog, and completed-plan contracts.

## Verification Plan

- focused Messenger verification-mode contracts before and after implementation
- Bottle/WebTest coverage for valid, missing, and invalid mode values
- mutation checks for missing or weakened mode validation and removed evidence
- repository and external-directory `make check` with bounded execution
- exact diff, generated-artifact, conflict-marker, and credential-pattern audits

## Scope Boundaries

- Do not change POST signature verification, reply delivery, replay handling,
  provider endpoints, tokens, or timeout behavior.
- Do not accept case-folded or whitespace-normalized alternatives to the
  platform's exact `subscribe` mode.
- Do not merge or close stacked pull requests without owner authorization.

## Work Completed

- Required the exact `subscribe` mode after token authentication and before
  challenge validation or reflection.
- Added dependency-free and Bottle/WebTest regressions for valid, missing,
  blank, differently cased, unrelated, and whitespace-wrapped mode values.
- Added fail-closed source, test-registration, documentation, changelog, and
  completed-plan contracts.

## Verification

- `test_messenger_verification_requires_exact_subscribe_mode` passed as part
  of the 54-test dependency-free contract gate.
- All 30 Bottle/WebTest tests passed under Python 3.12, the supported runtime
  for the repository's pinned legacy WebOb dependency.
- repository and external-directory `make check` passed with bounded
  execution.
- Six hostile mutations were rejected, covering inverted and normalized mode
  checks plus removed dependency-free, Bottle/WebTest, documentation, and plan
  evidence.
