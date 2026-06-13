# Messenger Echo Guard

Status: Completed

## Context

Messenger can deliver messages sent by the page itself with
`message.is_echo` set to `true`. The current parser treats those events as
user messages, which can send another reply and create a reply loop. An echo
event can also appear before a valid user message in the same payload.

## Plan

1. Ignore Messenger message events explicitly marked as echoes.
2. Continue scanning the payload so a later valid user message is handled.
3. Add dependency-free and Bottle/WebTest regression coverage.
4. Preserve signature, content-type, body-size, page-object, sender, and text
   validation for normal Messenger messages.

## Verification

- The 36 dependency-free contracts passed, including an echo followed by a
  valid user message and a non-boolean echo flag.
- All 25 Bottle/WebTest and bot tests passed, including a pure echo and an echo
  before a later valid message.
- The full `make check` gate passed under an isolated Python 3.12 environment
  with all 18 pinned packages installed.
- Three hostile mutations were rejected: removing the guard, returning early
  after an echo, and accepting arbitrary truthy echo values.
- Python compilation and `git diff --check` passed.
