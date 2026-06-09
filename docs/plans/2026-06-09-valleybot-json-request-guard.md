# Valleybot JSON Request Guard

## Status: Completed

## Context

The lower-level `bot.json_request` entry point directly indexed
`json_payload['data']`. Malformed Lambda-style payloads, missing `data`, blank
text, or non-text values could raise an exception or reach response generation
without the input checks already present on the web and Slack routes.

## Objectives

- Preserve valid `json_request` behavior for non-empty text payloads.
- Reject malformed, missing, blank, and non-text payload data without raising.
- Trim valid payload data before response generation.
- Cover the low-level bot entry point in dependency-free checks.

## Work Completed

- Added payload-shape and text validation to `bot.json_request`.
- Returned `None` for invalid payloads without calling `chatback`.
- Trimmed valid payload text before calling `chatback`.
- Extended `scripts/check_valleybot_contracts.py` with dependency-free
  `json_request` tests.
- Updated README, VISION, and CHANGES.

## Verification

- `python scripts/check_valleybot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add clearer moderation and content-review guidance.
- Document Python version and NLTK/TextBlob setup.
