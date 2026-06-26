# Channel Message Length Boundary

Status: Completed

## Problem

The public web-chat route already bounded normalized user input before
TextBlob/NLTK processing, and Slack and Messenger bounded raw request bodies.
An authenticated Slack command or one normalized Messenger message could still
consume nearly the full request-body allowance during bot response generation.

## Scope

- Share the existing 1,000-character normalized-message policy across web,
  Slack, and Messenger entry points.
- Reject oversized Slack commands before replay claims and bot execution.
- Skip an oversized Messenger event without aborting later valid events in the
  same already-bounded batch.
- Preserve authentication, body-size, replay, moderation, and response behavior
  for messages at or below the limit.

## Implementation

- Added `channel_limits.py` as the single policy source.
- Applied the policy after Slack form normalization in both Slack handlers.
- Applied the policy while extracting Messenger text events.
- Added dependency-free and real-runtime regression coverage.
- Documented the security boundary and channel-specific response semantics.

## Acceptance

- Exactly 1,000 normalized Unicode characters remain accepted.
- Slack text over the limit returns `text too long` without calling the bot.
- Messenger text over the limit produces no reply, and a later valid event in
  the same batch still receives a reply.
- Existing web-chat behavior remains unchanged.
- `make check` passes.
