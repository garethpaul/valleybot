# valleybot

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/valleybot` is a Python web API or service project. A chatbot for FB, Slack, Web and more that responds as a "typical" character from Silicon Valley.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (4).

## Repository Contents

- `README.md` - project overview and local usage notes
- `.github/workflows/check.yml` - GitHub Actions baseline for `make check`
- `requirements.txt` - Python dependency or packaging metadata
- `app.json`
- `app.py`
- `docs` - source or example code
- `nltk_data` - source or example code
- `Procfile`
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: docs, nltk_data
- Dependency and build manifests: Procfile, app.json, requirements.txt
- Entry points or build surfaces: app.py
- Test-looking files: bot_tests.py, nltk_data/corpora/conll2000/test.txt

## Getting Started

### Prerequisites

- Git
- Python 3.10 or newer; deployment tracks the Python 3.14 line

### Setup

```bash
git clone https://github.com/garethpaul/valleybot.git
cd valleybot
python -m pip install -r requirements.txt
make prepare-corpora
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Run `python app.py` after installing Python dependencies. Bottle debug mode
  remains off unless `BOTTLE_DEBUG=true` is explicitly set for local work.

## Testing and Verification

- `make verify` runs syntax checks and dependency-free Messenger and Slack
  route contract checks, including Slack command token validation and Slack
  command text validation, web chat text validation, web template escaping, bot
  JSON request validation, bot conversation log privacy, plus request timeout
  parsing checks. Slack command text, Messenger webhook object type, Messenger
  webhook text, and Messenger sender IDs must be valid before response
  generation. Recent Messenger message IDs are claimed in a bounded in-memory
  cache so provider retries do not send duplicate replies; outbound exceptions
  release their claim for recovery. Messenger POST bodies larger than 1 MiB are rejected with HTTP
  413 before signature verification or JSON parsing. Generated responses that
  fail moderation use a reviewed generic fallback instead of failing a request.
- `make check` runs `make verify` with bytecode cleanup before and after.
  The Makefile uses make's selected directory as the repository root, so the
  same gate can run from an external working directory with `make -C`.
- `make prepare-corpora` installs the current TextBlob tokenizer and tagger
  data into the existing project-local `nltk_data` directory. Heroku runs the
  same step through `bin/post_compile`.
- `python scripts/check_valleybot_contracts.py` runs just the webhook and token-handling contracts.
- GitHub Actions installs dependencies and runs the complete gate on Python
  3.10, 3.12, and 3.14 on Ubuntu 24.04 with read-only permissions, immutable
  action pins, credential-free checkout, cancellation for superseded runs, and
  verification from outside the repository directory.
- Completed maintenance plans live under `docs/plans` and are checked by
  `make check`.
- See `docs/plans/2026-06-13-messenger-message-replay-guard.md` for the bounded
  process-local Messenger retry guard.
- `python -m unittest bot_tests` runs the real Bottle/WebTest and bot suite.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- `SLACK_TOKEN` configures the Slack integration.
- `MESSENGER_TOKEN` configures Facebook Messenger API replies.
- `MESSENGER_VERIFY_TOKEN` configures Messenger webhook verification; it falls back to `MESSENGER_TOKEN` for older deployments.
- `MESSENGER_APP_SECRET` is required to validate the `X-Hub-Signature-256`
  HMAC on Messenger POST payloads.
- `REQUEST_TIMEOUT` optionally overrides outbound Messenger request timeout
  seconds; invalid, non-finite, or non-positive values fall back to `5.0`.
- Messenger webhook request bodies are limited to 1 MiB.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include nltk_data/corpora/movie_reviews/neg/cv000_29416.txt, nltk_data/corpora/movie_reviews/neg/cv067_21192.txt, nltk_data/corpora/movie_reviews/neg/cv074_7188.txt, nltk_data/corpora/movie_reviews/neg/cv144_5010.txt, and 3 more.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include app.json, app.py, docs/bugs/p2-python-http-call-without-timeout-a07c6a4bb0ee865f.md, nltk_data/corpora/conll2000/test.txt, and 5 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include app.json, app.py, bot.py, bot_tests.py, and 6 more.
- Review changes touching database, model, or persistence code; examples from the scan include nltk_data/corpora/conll2000/test.txt, nltk_data/corpora/movie_reviews/neg/cv157_29302.txt, nltk_data/corpora/movie_reviews/neg/cv163_10110.txt.
- Review changes touching infrastructure, proxy, cloud, or deployment configuration; examples from the scan include bot_tests.py.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-valleybot-webhook-hardening.md` for the current
  webhook hardening baseline.
- See `docs/plans/2026-06-08-valleybot-standalone-slack-token.md` for the
  standalone Slack handler token contract.
- See `docs/plans/2026-06-08-valleybot-slack-command-text.md` for Bottle Slack
  command text validation.
- See `docs/plans/2026-06-09-valleybot-slack-non-text-command.md` for
  non-text Slack command rejection in both Slack entry points.
- See `docs/plans/2026-06-09-valleybot-web-bot-chat.md` for web `/bot` chat
  query validation.
- See `docs/plans/2026-06-09-valleybot-request-timeout.md` for request timeout
  environment parsing guard coverage.
- See `docs/plans/2026-06-09-valleybot-json-request-guard.md` for the
  low-level bot JSON payload guard.
- See `docs/plans/2026-06-09-valleybot-web-template-escaping.md` for web chat
  URL encoding and text-only reply rendering.
- See `docs/plans/2026-06-09-valleybot-messenger-text-guard.md` for Messenger
  sender and text validation.
- See `docs/plans/2026-06-09-valleybot-messenger-object-guard.md` for
  rejecting non-page Messenger webhook payloads before event parsing.
- See `docs/plans/2026-06-09-valleybot-bot-log-privacy.md` for bot message and
  response log privacy coverage.
- See `docs/plans/2026-06-10-ci-baseline.md` for the lightweight GitHub
  Actions baseline.
- See `docs/plans/2026-06-10-python3-runtime-modernization.md` for the Python 3,
  dependency, corpus, runtime-test, webhook-signature, and CI modernization.
- See `docs/plans/2026-06-10-messenger-webhook-size-limit.md` for the completed
  unauthenticated request-body limit.
- See `docs/plans/2026-06-10-filtered-response-fallback.md` for the completed
  moderation fallback and runtime regression coverage.
- See `docs/plans/2026-06-12-messenger-json-content-type.md` for the exact JSON
  media-type requirement on signed Messenger webhook requests.
- See `docs/plans/2026-06-13-messenger-echo-guard.md` for ignoring page echo
  messages without hiding later user messages in the same webhook payload.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
