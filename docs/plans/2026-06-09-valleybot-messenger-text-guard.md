# Valleybot Messenger Text Guard

Status: Completed

## Context

Messenger webhook parsing already ignored unsupported event shapes, but a truthy
non-string `message.text` value could still be stringified and passed into bot
response generation. Sender IDs were also accepted without trimming.

## Objectives

- Require Messenger sender IDs and message text to be textual and nonblank.
- Trim sender IDs and message text before sending replies.
- Acknowledge malformed Messenger text events without calling response
  generation.
- Keep the dependency-free static route contracts as the local verification
  surface.

## Work Completed

- Updated `parse_messenger_message` to trim sender IDs and message text.
- Ignored non-text or blank Messenger text values before response generation.
- Added contract coverage for invalid text values and trimmed successful
  replies.
- Updated README, SECURITY, VISION, and CHANGES with the guardrail.

## Verification

- `python scripts/check_valleybot_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
