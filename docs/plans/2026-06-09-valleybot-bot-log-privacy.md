# Valleybot Bot Log Privacy

## Status: Completed

## Context

The channel handlers avoid token leaks, but the core bot still logged raw
inbound messages, generated responses, and extracted part-of-speech terms at
info level. Those values can include private conversation text from web, Slack,
or Messenger users.

## Objectives

- Preserve bot response generation behavior.
- Default bot logging below conversation-detail verbosity.
- Replace raw message, response, and extracted-term logs with generic traces.
- Extend dependency-free checks so raw conversation logs do not return.

## Work Completed

- Changed the bot logger default level from `DEBUG` to `WARNING`.
- Replaced raw inbound message logging with a generic debug trace.
- Replaced raw generated response logging with a generic debug trace.
- Replaced extracted noun and part-of-speech value logging with generic debug
  traces.
- Extended `scripts/check_valleybot_contracts.py` with bot logging privacy
  checks and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- `python scripts/check_valleybot_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add structured request IDs for operational tracing without message contents.
- Add runtime configuration for temporary diagnostic logging in controlled
  non-production environments.
