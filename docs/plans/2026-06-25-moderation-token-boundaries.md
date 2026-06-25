# Moderation Token Boundaries

status: completed

## Context

`bot.filter_response` split generated text only on literal spaces. A known
blocked prefix preceded by punctuation or separated from earlier text by a
newline could therefore bypass the final-output guard.

## Requirements

- Extract Unicode word tokens across punctuation and all whitespace boundaries.
- Preserve the existing blocked-prefix matching behavior for each token.
- Keep `safe_response` as the single final generated-text boundary.
- Do not add, remove, or edit response templates, fallback text, or blocked
  terms.
- Add synthetic rejected-boundary runtime tests and dependency-free source
  contracts.
- Record the required human content review scope and unresolved concerns.

## Work Completed

- Used a Unicode-aware regular expression to extract alphanumeric word tokens.
- Lowercased once during tokenization and preserved the existing prefix scan.
- Added punctuation-prefixed and newline-separated blocked-term regressions.
- Synchronized maintained security, moderation, vision, agent, README, and
  changelog guidance.

## Human Review Record

- Reviewer: Codex maintenance agent acting under the repository's mandatory
  moderation checklist.
- Review date: 2026-06-25.
- Changed content scope: token-boundary parsing and synthetic fixtures only.
- Response templates changed: none.
- Fallback responses changed: none.
- Blocked terms changed: none.
- Channel boundary: `safe_response` remains shared by web, Slack, Messenger,
  terminal, and low-level JSON response generation.
- Privacy: no conversation transcripts or user identifiers were added.
- Unresolved harmful-content concerns: none introduced by this parsing-only
  change; the historical chatbot remains subject to the limitations in
  `MODERATION.md`.

## Verification Completed

- Focused punctuation/newline tests passed under Python 3.14, followed by all
  43 runtime tests.
- All 73 dependency-free contract tests and the existing five-mutation web-chat
  contract passed.
- All five Make gates passed with the disposable Python 3.14 interpreter:
  `make lint`, `make test`, `make build`, `make verify`, and `make check`.
- The external absolute-Makefile `make check` passed, and the Make authority
  suite passed all documented target, override, preload, startup, and unsafe
  mode cases.
- Six isolated hostile mutations were rejected across tokenization, both
  runtime fixtures, guidance, completed plan status, and hosted evidence.
- Python and shell syntax checks passed, `git diff --check` passed, and
  `config.py` remained unchanged so reviewed response and blocklist content did
  not change.
- Hosted workflow runs `28165931656` and `28165933669` passed Python 3.10,
  Python 3.12, Python 3.14, GitHub Actions CodeQL, and Python CodeQL.
- Codex review reported no actionable diff-introduced findings; its separate
  default-system-Python probe lacked installed TextBlob, while the required
  parallel Python 3.14 `make check` passed.
