# Moderation Token Boundaries

status: in progress

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

## Implementation

- Use a Unicode-aware regular expression to extract alphanumeric word tokens.
- Lowercase once during tokenization and preserve the existing prefix scan.
- Add punctuation-prefixed and newline-separated blocked-term regressions.
- Synchronize maintained security, moderation, vision, agent, README, and
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

## Verification

- Run focused punctuation/newline runtime tests under Python 3.14.
- Run all runtime and dependency-free repository checks.
- Run every Make gate from the repository and canonical external paths.
- Reject isolated tokenizer, fixture, guidance, plan-status, and evidence
  mutations.
- Run Codex review and hosted CI before merge.
