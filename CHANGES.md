# Changes

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
