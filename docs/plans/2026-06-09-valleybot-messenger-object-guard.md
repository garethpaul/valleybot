# Messenger Object Guard

Status: Completed

## Context

The Messenger POST route already rejected malformed JSON and ignored unsupported
non-message events, but it did not verify the top-level Messenger webhook
`object`. Facebook page webhooks are expected to send `object: "page"`. Without
that guard, unrelated JSON shapes could flow into event parsing and be
acknowledged as valid webhook traffic.

## Plan

- Reject Messenger POST payloads whose top-level `object` is not `page`.
- Return a non-OK response before parsing entries or calling `messenger_reply`.
- Add a dependency-free route contract for non-page Messenger payloads.
- Wire the existing Messenger text and trim route contracts into the checker
  main test list so they execute under `make check`.

## Verification

- `python scripts/check_valleybot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

Legacy Python 2 `bot_tests` still run only when Python 2 and the historical
dependencies are installed; otherwise the Makefile reports the skip.
