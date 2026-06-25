## Valleybot Vision

Valleybot is a Python chatbot based on valley stereotypes, with web, Slack,
Facebook, terminal, Heroku, and AWS Lambda integration paths.

The repository is useful as a chatbot experiment that combines TextBlob/NLTK
parsing, response construction, basic filtering, webhook-style integrations,
and screenshots of multiple channels.

The goal is to keep the bot inspectable and playful while making moderation,
tokens, and deployment boundaries explicit.

The current focus is:

Priority:

- Keep the service on supported Python 3 and current audited dependencies
- Require Slack signing secret verification before command execution
- Suppress repeated Slack signatures with bounded process-local state
- Require authenticated Messenger POST payloads before event parsing
- Bound unauthenticated Messenger request bodies before signature verification
- Run the complete runtime suite across supported Python versions in CI

- Preserve the `bot.respond` and integration entry points
- Keep channel tokens and secrets in settings/environment configuration
- Reject blank or non-text channel commands before response generation
- Reject non-page Messenger webhook payloads before event parsing
- Reject blank or non-text Messenger messages before response generation
- Suppress duplicate Messenger replies from retried message IDs with bounded
  process-local state
- In-flight Messenger message-ID claims are never capacity-evicted; only completed claims enter the bounded replay cache.
- Process Messenger message batches in order with a fixed per-webhook cap
- Keep Messenger reply behavior independent of client-controlled debug fields
- Fail Messenger replies on provider HTTP errors so webhook retries remain
  recoverable
- Reject empty web chat queries before response generation
- Bound public web chat input before TextBlob/NLTK response generation
- Render web chat replies as text instead of concatenated HTML
- Reject malformed low-level bot JSON requests before response generation
- Avoid logging raw inbound messages, generated responses, or extracted terms
  by default
- Keep outbound request timeout configuration bounded and non-crashing
- Maintain the response filter and tests
- Keep blocked-prefix checks effective across punctuation and non-space
  whitespace boundaries
- Keep the dependency-free `make check` baseline running in GitHub Actions
- Keep pinned CodeQL coverage for GitHub Actions and Python with job-scoped
  upload permission
- Escape verified Messenger challenge responses before reflecting them
- Messenger GET verification requires the exact `subscribe` mode after token
  authentication
- Return reviewed fallback text when a generated response fails moderation
- Avoid expanding stereotype content without review
- Require auditable human review of response templates, blocked terms,
  fallbacks, fixtures, channel consistency, privacy, and unresolved concerns

Next priorities:

- Document Python version and NLTK/TextBlob setup
- Separate deployment packaging from bot behavior changes

Contribution rules:

- One PR = one focused response, parser, integration, test, or documentation change.
- Do not commit Slack, Facebook, or deployment secrets.
- Add tests for response-generation changes.
- Keep offensive-content filters visible and easy to audit.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Bots can produce harmful or inappropriate responses and can expose channel
tokens. Changes should preserve filtering, avoid logging private messages by
default, and keep deployment credentials out of source control.

## What We Will Not Merge (For Now)

- Checked-in bot tokens or webhook secrets
- Messenger webhook payloads that bypass page-object validation
- Moderation bypasses
- Private conversation logs
- Unbounded webhook request bodies
- New stereotype content without review context

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
