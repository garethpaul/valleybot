# Slack In-Flight Replay Claims Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Prevent replay-cache capacity from evicting a Slack signature while its bot response is still being generated.

**Architecture:** Split replay state into in-flight and completed signatures. Keep pending claims protected until each handler explicitly completes or releases them, while retaining bounded oldest-first eviction for successful claims.

**Tech Stack:** Python 3.10-3.14, Bottle, stdlib threading and collections, dependency-free contract tests, GNU Make.

---

Status: Completed

### Task 1: Prove the replay race

**Files:**
- Modify: `scripts/check_valleybot_contracts.py`

1. Add a test that calls `complete()` and verifies completed claims are bounded.
2. Add a capacity-pressure test proving an in-flight signature cannot be reclaimed.
3. Register both tests in the dependency-free test list.
4. Run `scripts/run-python.sh scripts/check_valleybot_contracts.py` and verify RED fails because `complete()` is missing.

### Task 2: Implement explicit completion

**Files:**
- Modify: `slack_replay.py`
- Modify: `app.py`
- Modify: `slack.py`

1. Store pending signatures in `_inflight` and successes in `_completed`.
2. Add `complete(signature)` to move a claim after successful bot generation.
3. Keep `release(signature)` available for retry recovery after failure.
4. Update both handlers to complete only after `bot.respond()` succeeds.
5. Run the focused dependency-free suite and verify GREEN.

### Task 3: Lock the contract and documentation

**Files:**
- Modify: `scripts/check_valleybot_contracts.py`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `AGENTS.md`
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-25-slack-inflight-replay.md`

1. Require separate state and claim/respond/complete/release ordering.
2. Add isolated hostile mutations for completion and capacity safety.
3. Document process-local replay guarantees and multi-worker limits.
4. Mark this plan completed with exact verification evidence.
5. Run `make check` and commit the focused change.

## Verification Evidence

- RED failed with `AttributeError` because `RecentSlackSignatures.complete()`
  did not exist.
- GREEN passed 75 dependency-free contracts, including completed-cache
  eviction and in-flight capacity-pressure behavior.
- Both Bottle and standalone Slack handlers retain claim, response,
  completion, and failure-release ordering.
- Six isolated hostile Slack replay mutations and five existing web-chat
  mutations were rejected.
- Python 3.14 `make check` passed the 43 Bottle/bot runtime tests, syntax and
  corpus checks, and all 40 Make target/authority cases.
- Hosted runs `28214128990` and `28214129936` passed Python 3.10, Python 3.12,
  Python 3.14, Actions CodeQL, and Python CodeQL on commit
  `8874e42b319d92f22ff930a8f4d48afbb807c697`.
- `codex review --base origin/master` was attempted but could not authenticate
  to the OpenAI API (HTTP 401); manual exact-head review found no findings.
- No live Slack webhook was sent; multi-worker global replay suppression still
  requires a shared store.
