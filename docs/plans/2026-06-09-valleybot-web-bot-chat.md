# Valleybot Web Bot Chat Guard

## Status: Completed

## Context

The Slack command routes reject missing or blank command text before invoking
the bot, but the public `/bot` JSON endpoint still indexed `request.query`
directly. Requests without a `chat` query could raise an exception, and blank
queries could reach response generation.

## Objectives

- Preserve the `/bot` JSON response shape for valid chat input.
- Reject missing `chat` queries with a JSON 400 response.
- Reject blank `chat` queries before response generation.
- Trim valid chat text before passing it to `bot.respond`.
- Keep dependency-free route contracts covering the web bot endpoint.

## Work Completed

- Added missing and blank `chat` query handling in `app.chat`.
- Kept valid responses as `{"data": ...}` and error responses as JSON.
- Trimmed valid chat query text before bot response generation.
- Extended `scripts/check_valleybot_contracts.py` with web bot route tests.
- Updated README, VISION, and CHANGES.

## Verification

- `python scripts/check_valleybot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add clearer moderation and content-review guidance.
- Document Python version and NLTK/TextBlob setup.
