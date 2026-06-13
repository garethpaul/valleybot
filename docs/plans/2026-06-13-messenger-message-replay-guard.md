# Messenger Message Replay Guard

## Status: In Progress

## Context

Messenger webhook deliveries can be retried with the same message ID. The app
currently ignores `message.mid`, so a retry can produce a duplicate outbound
bot response and repeat downstream work.

## Requirements

- R1. Parse a trimmed non-empty Messenger message ID with the existing first
  valid non-echo text message.
- R2. Claim IDs before outbound reply work so concurrent or sequential retries
  do not send duplicate replies.
- R3. Keep claims in a bounded, process-local, thread-safe recent-ID cache with
  a fixed maximum size and no attacker-controlled unbounded growth.
- R4. Release a claim when outbound reply work raises so a provider retry can
  recover from transient failure.
- R5. Preserve messages without IDs, debug payload behavior, echo filtering,
  signature validation, body limits, and first-valid-message semantics.
- R6. Add runtime and dependency-free coverage for replay suppression, bounded
  eviction, failure release, malformed IDs, and no-ID compatibility.
- R7. Document that process-local replay protection is not shared across
  workers or restarts.

## Scope Boundaries

- Do not add persistence, a distributed cache, dependencies, background jobs,
  or multi-message batch replies.
- Do not perform a live Messenger webhook or credentialed Graph API request.

## Verification

- Focused replay tests and full `make check`
- External-directory and space-containing-path `make check`
- Hostile mutations for ID parsing, claim ordering, duplicate suppression,
  bounded eviction, failure release, and plan status
- Python syntax, workflow YAML, `git diff --check`, generated-artifact, and
  focused secret review
