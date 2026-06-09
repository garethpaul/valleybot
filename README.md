# valleybot

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/valleybot` is a Python web API or service project. A chatbot for FB, Slack, Web and more that responds as a "typical" character from Silicon Valley.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (4).

## Repository Contents

- `README.md` - project overview and local usage notes
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
- Python matching the era of the project

### Setup

```bash
git clone https://github.com/garethpaul/valleybot.git
cd valleybot
python -m pip install -r requirements.txt
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Run `python app.py` after installing Python dependencies.

## Testing and Verification

- `make verify` runs syntax checks and dependency-free Messenger and Slack
  route contract checks, including Slack command token validation and web chat
  text validation, web template escaping, bot JSON request validation, plus
  request timeout parsing checks.
- `make check` runs `make verify` with bytecode cleanup before and after.
- `python scripts/check_valleybot_contracts.py` runs just the webhook and token-handling contracts.
- Completed maintenance plans live under `docs/plans` and are checked by
  `make check`.
- `python -m unittest bot_tests` runs the legacy Python 2 test suite when its dependencies are installed.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- `SLACK_TOKEN` configures the Slack integration.
- `MESSENGER_TOKEN` configures Facebook Messenger API replies.
- `MESSENGER_VERIFY_TOKEN` configures Messenger webhook verification; it falls back to `MESSENGER_TOKEN` for older deployments.
- `REQUEST_TIMEOUT` optionally overrides outbound Messenger request timeout
  seconds; invalid, non-finite, or non-positive values fall back to `5.0`.

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
- See `docs/plans/2026-06-09-valleybot-web-bot-chat.md` for web `/bot` chat
  query validation.
- See `docs/plans/2026-06-09-valleybot-request-timeout.md` for request timeout
  environment parsing guard coverage.
- See `docs/plans/2026-06-09-valleybot-json-request-guard.md` for the
  low-level bot JSON payload guard.
- See `docs/plans/2026-06-09-valleybot-web-template-escaping.md` for web chat
  URL encoding and text-only reply rendering.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
