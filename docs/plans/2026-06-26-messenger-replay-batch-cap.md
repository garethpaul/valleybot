# Messenger Replay Batch Cap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Ensure replayed Messenger IDs do not consume the 20-message work limit and hide later unique signed events.

**Architecture:** Convert the nested Messenger parser into a lazy iterator. The webhook handler will stop after 20 messages that actually acquire replay ownership (or have no ID), while replayed IDs are skipped without consuming work capacity or building an unbounded intermediate list.

**Tech Stack:** Python 3, Bottle/WebTest runtime tests, dependency-free request stubs, source/mutation contracts, GNU Make.

---

Status: Completed

### Task 1: Reproduce replay starvation

**Files:**
- Modify: `bot_tests.py`
- Modify: `scripts/check_valleybot_contracts.py`

Add signed-batch tests with 20 already-completed IDs followed by one unique ID.
Run the focused dependency-free test and observe that the unique recipient is not called.

### Task 2: Count owned work lazily

**Files:**
- Modify: `app.py`

Yield normalized events from `parse_messenger_messages`, move the cap into
`messenger_post`, and increment only after a unique claim succeeds or for an
ID-less message. Check the limit before claiming the next work item.

### Task 3: Preserve contracts and evidence

**Files:**
- Modify: `AGENTS.md`
- Modify: `CHANGES.md`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `scripts/check_valleybot_contracts.py`

Run `make check` with the reviewed dependency environment, the replay mutation
suite, Python/shell syntax checks, and `git diff --check` before publishing.
