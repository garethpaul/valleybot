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

- Preserve the `bot.respond` and integration entry points
- Keep channel tokens and secrets in settings/environment configuration
- Reject blank or non-text channel commands before response generation
- Reject blank or non-text Messenger messages before response generation
- Reject empty web chat queries before response generation
- Render web chat replies as text instead of concatenated HTML
- Reject malformed low-level bot JSON requests before response generation
- Avoid logging raw inbound messages, generated responses, or extracted terms
  by default
- Keep outbound request timeout configuration bounded and non-crashing
- Maintain the response filter and tests
- Avoid expanding stereotype content without review

Next priorities:

- Add clearer moderation and content-review guidance
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
- Moderation bypasses
- Private conversation logs
- New stereotype content without review context

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
