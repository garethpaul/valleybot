# Slack Request Replay Guard

status: completed

## Context

Slack signatures authenticate the exact body and reject timestamps outside a
five-minute window, but the same valid signed request can still execute
`bot.respond` repeatedly during that window. Slack retries make this a
practical duplicate-execution path in both the Bottle and event handlers.

## Requirements

- R1. Claim a verified Slack signature before bot execution in both handlers.
- R2. A repeated in-process signature must return a successful acknowledgement
  without another `bot.respond` call.
- R3. Release a claim when bot processing raises so a provider retry can
  recover.
- R4. Bound process-local signature state and make claim/release thread-safe.
- R5. Preserve signature, timestamp, body-size, text-validation, and successful
  first-request behavior.
- R6. Document that separate processes or evicted entries still require a
  shared persistent replay store for global suppression.
- R7. Add registered dependency-free, Bottle/WebTest, source, documentation,
  and completed-plan contracts with hostile mutation coverage.

## Implementation Units

### U1. Bounded signature claims

**Files:** `slack_replay.py`, `app.py`, `slack.py`

Add a dependency-free bounded claim set. Apply it after authentication and
text validation but before bot execution, and release only failed processing
claims.

### U2. Runtime and static contracts

**Files:** `bot_tests.py`, `scripts/check_valleybot_contracts.py`, `Makefile`

Cover duplicate suppression, failure recovery, bounded eviction, ordering in
both handlers, test registration, and completed plan evidence.

### U3. Security guidance

**Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, this plan

Record process-local replay suppression and its cross-process limitation.

## Verification Plan

- Run focused replay cases and the complete dependency-free suite.
- Run repository and external-directory `make verify` without invoking the
  live worktree's broad cleanup target.
- Run full `make check` only in an isolated disposable copy.
- Reject isolated mutations for Bottle and event claims, duplicate
  acknowledgements, failure release, bounded eviction, registration,
  documentation, and plan completion.
- Audit the exact diff, generated artifacts, file modes, conflict markers, and
  credential-like additions before commit.

## Scope Boundaries

- Do not add a database, queue, cache service, dependency, workflow change, or
  live Slack request.
- Do not claim cross-process or durable replay prevention.
- Do not change Messenger behavior or bot response selection.

## Work Completed

- Added a 1,024-entry thread-safe process-local Slack signature claim set.
- Claimed verified signatures after text validation and before bot execution in
  both entry points, acknowledged duplicates without a second bot call, and
  released claims after processing failures.
- Added dependency-free, Bottle/WebTest, source-ordering, registration,
  bounded-eviction, documentation, and completed-plan contracts.
- Documented that workers, restarts, and evicted entries still require shared
  persistent state for global replay suppression.

## Verification Completed

- Python compilation passed for the changed runtime and checker modules.
- Six focused dependency-free replay, failure-release, eviction, ordering, and
  registration cases passed.
- Two focused Bottle/WebTest replay and failure-release cases passed in the
  pinned Python 3.12 environment.
- Repository-root and external-directory `make verify` passed with 66
  dependency-free contract tests and 36 pinned Bottle/WebTest tests.
- An isolated disposable copy passed the full cleanup-wrapped `make check`
  without running broad cleanup in the preserved live worktree.
- Nine independently restored hostile mutations were rejected for Bottle and
  event claims, failure release, duplicate acknowledgement, bounded eviction,
  registration, documentation, and plan completion.
- `uv pip check --python /tmp/valleybot-clean-venv/bin/python` confirmed all 18
  installed packages are compatible.
