# Changes

## 2026-06-09

- Rejected non-text Slack command values in both the Bottle route and
  standalone adapter before response generation.
- Added dependency-free Slack command coverage for malformed text values.
- Replaced raw bot message, response, and extracted-term logs with generic
  debug traces and defaulted bot logging to warning level.
- Added static checker coverage for bot conversation log privacy.
- Guarded `bot.json_request` so malformed, missing, blank, or non-text payload
  data does not crash or call response generation.
- Added dependency-free contract coverage for the low-level bot JSON request
  guard.
- Rendered web chat user and bot replies with text-only DOM insertion and
  URL-encoded chat queries.
- Added dependency-free template coverage for web chat escaping.
- Guarded Messenger webhook text and sender IDs so non-text or blank events are
  acknowledged without response generation.
- Added safe `REQUEST_TIMEOUT` parsing so invalid, non-finite, or non-positive
  values fall back to five seconds instead of crashing startup.
- Added dependency-free settings contract coverage for request timeout parsing.
- Rejected missing and blank `/bot` chat query text before response generation
  and kept error responses JSON-shaped.
- Added dependency-free route contracts for web bot missing, blank, and trimmed
  chat query handling.

## 2026-06-08

- Rejected missing and blank Bottle Slack command text before running bot
  response generation.
- Required matching Slack tokens before the standalone Slack handler calls the bot.
- Tightened docs-plan verification to require recorded `make check` evidence.
- Added dependency-free Messenger and Slack route contract checks and a local `make verify` gate.
- Required Slack slash-command tokens before running bot commands.
- Required Messenger webhook verification tokens before echoing challenges.
- Ignored unsupported Messenger webhook events instead of raising nested JSON indexing errors.
- Sent Messenger replies with bearer-token authorization and an explicit request timeout.
