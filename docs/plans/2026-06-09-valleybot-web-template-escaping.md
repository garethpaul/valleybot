# Valleybot Web Template Escaping

## Status: Completed

## Context

The web chat template appended user input and bot replies by concatenating raw
strings into HTML. That made the browser page trust text from both the user and
the bot response, and the `/bot` query string was built without URL encoding.

## Objectives

- Preserve the existing web chat page behavior.
- URL-encode chat text before calling `/bot`.
- Insert user and bot reply text through text-only DOM APIs.
- Avoid raw string concatenation for reply HTML.
- Cover the template behavior in dependency-free checks.

## Work Completed

- Added an `appendReply` helper that builds reply nodes with jQuery.
- Inserted reply text with `.text(...)` instead of HTML string concatenation.
- URL-encoded chat query text with `encodeURIComponent`.
- Extended `scripts/check_valleybot_contracts.py` with template checks.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check: `python scripts/check_valleybot_contracts.py` failed before
  this plan was added.
- Negative check: `test_web_template_escapes_chat_strings` failed before the
  template used URL encoding and text-only insertion.
- `python scripts/check_valleybot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add clearer moderation and content-review guidance.
- Document Python version and NLTK/TextBlob setup.
