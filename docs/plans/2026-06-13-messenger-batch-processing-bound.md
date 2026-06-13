---
title: "fix: Bound Messenger batch processing"
type: fix
date: 2026-06-13
---

# Bound Messenger Batch Processing

## Status: Completed

## Context

Messenger webhook payloads can contain multiple entries and messaging events,
but the parser currently returns only the first valid user message. Later valid
messages are silently acknowledged without a reply. Processing every event
without a bound would create response-amplification risk, so batch support must
pair ordered iteration with an explicit per-request maximum.

## Requirements

- R1. Extract valid user messages across all entry and messaging arrays in
  payload order.
- R2. Ignore malformed events, delivery/read events, and only boolean-true echo
  messages without hiding later valid messages.
- R3. Return no more than 20 valid messages from one webhook payload.
- R4. Reply to each extracted message in order unless debug mode suppresses
  outbound requests.
- R5. Preserve replay claims per message ID and release only the failing
  message's claim when its outbound reply raises.
- R6. Continue processing messages without usable IDs without adding replay
  claims.
- R7. Add dependency-free and Bottle/WebTest coverage plus mutation-sensitive
  contracts for ordering, bounds, echo traversal, replay behavior,
  documentation, and completed-plan status.

## Implementation Units

### U1. Extract a bounded message batch

- **Files:** `app.py`
- Replace first-message return semantics with a list of sender/text/message-ID
  tuples capped by a named constant.
- Preserve text/sender trimming, optional message-ID cleanup, and existing
  malformed-event handling.

### U2. Process each message independently

- **Files:** `app.py`
- Iterate the bounded list in payload order.
- Apply replay claim, outbound reply, and exception-release handling per
  message so one retry does not duplicate earlier successful replies.

### U3. Prove batch and failure semantics

- **Files:** `bot_tests.py`, `scripts/check_valleybot_contracts.py`
- Cover ordered multi-message replies, the 20-message cap, echoes before/between
  messages, replayed IDs within a batch, ID-less messages, debug suppression,
  and release of only the failing claim.
- Preserve existing signature, media-type, size, and object validation tests.

### U4. Record the operational boundary

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Document ordered bounded processing and the intentionally process-local replay
  cache.

## Verification

- Six focused dependency-free batch tests passed for ordered replies, the
  per-webhook cap, replay suppression, ID-less compatibility, debug
  suppression, and failing-claim isolation.
- Two focused Bottle/WebTest batch tests passed in an isolated Python 3.12
  environment after the documented corpus preparation.
- The pre-completion dependency-free gate passed 48 tests and the full runtime
  suite passed 27 tests.
- Fifteen hostile mutations covering first-message regression, cap removal,
  malformed nested event acceptance, echo acceptance, replay short-circuiting,
  missing claim release, missing runtime tests, documentation drift, and stale
  plan status were rejected.
- `uv pip check` passed for all 18 installed packages. Pinned
  `pip-audit==2.10.0` reported no known vulnerabilities in `requirements.txt`;
  it explicitly skipped the pinned `webob==1.6.1.1070258` distribution because
  that distribution was not found on public PyPI.
- Final local and external-working-directory `make check` runs passed with the
  same isolated pinned interpreter under explicit five-minute timeouts after
  this completed-plan record was written.
- No live Messenger credential or provider request was used; outbound calls
  remained deterministic fakes.

## Work Completed

- Replaced first-message parsing with ordered extraction of up to 20 valid
  sender/text/message-ID tuples across all entries and messaging arrays.
- Applied replay claims, replies, and exception release independently for each
  extracted message while preserving ID-less and debug compatibility.
- Added dependency-free and Bottle/WebTest coverage for ordering, limits,
  echoes, replayed IDs, ID-less messages, debug payloads, and failure isolation.

## Scope Boundaries

- Do not add background queues, parallel replies, distributed replay storage,
  retries, new dependencies, or provider API changes.
- Do not process more than 20 valid messages from one webhook request.
- Do not merge or close any pull request without explicit owner authorization.
