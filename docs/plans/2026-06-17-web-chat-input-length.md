# Bound Public Web Chat Input

## Status: Completed

## Context

The public `GET /bot` route rejects missing and blank `chat` values, but it
passes every other value directly into TextBlob and NLTK response generation.
An oversized query can therefore turn a small unauthenticated request into
disproportionate parsing and tagging work. Existing Slack and Messenger body
limits do not bound this public query parameter.

## Requirements

- Define a 1,000-character maximum for accepted web-chat input, measured as
  Python Unicode code points rather than encoded bytes.
- Apply the limit after trimming so boundary behavior matches the text passed
  to `bot.respond`.
- Preserve the existing JSON response shape for accepted input.
- Return HTTP `413` with `{"error": "chat too long"}` for input over the limit
  without calling the bot.
- Accept input exactly at the configured limit.
- Keep missing and blank input behavior unchanged.
- Add mutation-sensitive coverage that rejects a removed limit, a byte-like or
  off-by-one comparison, validation after the bot call, and a non-JSON error.
- Document the public endpoint boundary without claiming that all channels,
  aggregate request rates, or TextBlob/NLTK execution time are globally
  bounded.

## Implementation Units

### U1. Enforce the route boundary

- **Files:** `app.py`, `scripts/check_valleybot_contracts.py`
- **Outcome:** The public web-chat route rejects oversized trimmed input before
  response generation and retains exact-boundary behavior.

### U2. Make the contract mutation-sensitive

- **Files:** `scripts/test_web_chat_length_contract.py`, `Makefile`,
  `scripts/check_valleybot_contracts.py`
- **Outcome:** The normal verification gate rejects weakening or reordering the
  length check and its JSON error response.

### U3. Record the operational boundary

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-17-web-chat-input-length.md`
- **Outcome:** Maintainers can distinguish the per-request public query limit
  from rate limiting, channel-wide limits, and model execution time.

## Verification

- Run focused web-chat route tests and hostile mutations.
- Run the full pinned `make check` gate in hosted verification. Locally, run
  the equivalent `make verify` gate from the repository and an external
  directory so unrelated concurrent worktree caches are not broadly deleted.
- Audit the exact diff, generated artifacts, conflict markers, and credential
  patterns.
- Require a bounded exact-head hosted snapshot after push.

## Verification Results

- Three focused Bottle route tests passed for ordinary input, exact-limit
  acceptance, and multibyte over-limit rejection before bot execution.
- Five hostile static mutations were rejected for limit expansion, encoded-byte
  measurement, an off-by-one comparison, premature bot execution, and a
  non-JSON error response.
- Fresh Python 3.12.8 environments with the exact runtime pins passed
  repository and external-directory `make verify`: 68 dependency-free
  contracts, five hostile mutations, and all 38 Bottle/unit tests.
- The disposable environment passed `pip check`, and direct-pin `pip-audit`
  reported no known vulnerabilities.
- Hosted `make check` passed on implementation head
  `8b3d051f7aba84a54394ef98d48a1520496b00a4` for push run `27723178362` and
  pull-request run `27723187298`, including Python 3.10, 3.12, 3.14 and CodeQL
  analysis lanes.
- No production traffic, rate-limit behavior, or long-running TextBlob/NLTK
  execution was exercised locally or in hosted verification.

## Scope Boundaries

- Do not alter Slack or Messenger request semantics.
- Do not add authentication, rate limiting, a shared replay store, or a new
  persistence dependency.
- Do not change response generation, moderation, templates, or NLTK corpora.
- Preserve the unrelated detached `/tmp/valleybot-mode-validation` worktree
  completely unchanged.
