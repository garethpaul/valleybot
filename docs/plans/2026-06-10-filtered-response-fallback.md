# Filtered Response Fallback

Status: Completed

## Context

The response filter raised an exception when generated text matched a blocked
term. Because `bot.respond` did not contain that expected moderation outcome,
all integration routes surfaced it as a server failure.

## Changes

- Route generated text through a dedicated `safe_response` boundary.
- Return one of the existing reviewed generic responses after a filter
  rejection.
- Keep the rejection diagnostic free of generated or inbound message content.
- Add runtime tests for rejected fallback and accepted passthrough behavior.

## Verification

- `make check`
- Remove the `UnacceptableUtteranceException` handler and confirm the portable
  contract fails before restoring it.
