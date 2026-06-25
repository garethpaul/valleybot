# Changes

## 2026-06-25T21:16:14Z — P1 concurrency/correctness — cycle: Messenger in-flight replay claims

- Threads: inspected the explicit Apache 2.0 license, default branch, open pull
  requests and issues, hosted checks, Messenger signature and media-type gates,
  batch ordering, provider failure release, message-ID replay state, Slack
  replay state, outbound timeouts, runtime tests, and dependency-free contracts.
- Bug fixed: replay-cache capacity can no longer evict an in-flight Messenger
  message ID while its outbound reply is pending, preventing a concurrent retry
  from generating a duplicate reply.
- Files: `app.py`, `scripts/check_valleybot_contracts.py`, replay security and
  maintenance documentation, and
  `docs/plans/2026-06-25-messenger-inflight-replay-claims.md`.
- Validation: reproduced the missing completion state as an `AttributeError`,
  then passed seventy-four dependency-free contracts, forty-three Bottle/bot
  runtime tests, five web-chat mutations, full Python 3.14 `make check`, and
  dependency compatibility checks.
- Blockers: no live Messenger webhook or provider request was sent; hosted
  Python 3.10/3.12/3.14 verification remains required before merge.
- Next: load-test concurrent signed retries near replay-cache capacity and
  evaluate a shared durable replay store for multi-worker deployments.

## 2026-06-25

- Hardened final-output moderation tokenization across punctuation and
  non-space whitespace boundaries without changing reviewed response or
  blocklist content.
- In-flight Messenger message-ID claims are never capacity-evicted; only completed claims enter the bounded replay cache.

## 2026-06-21

- Documented and reproduced GNU Make 4.4's command-line `ROOT` pre-load
  expression boundary while preserving environment-root neutralization.
- Isolated Make verification authority from caller-controlled roots, shells,
  startup files, Makefile lists, unsafe execution modes, and executable Make
  syntax while preserving repository-contained bytecode cleanup.
- Added a hostile-path authority harness and invoked hosted verification
  through `/usr/bin/make`.
- Baked an absolute Python interpreter into verification recipes, rejected
  PATH-shadowed defaults and later shell false-success, and isolated startup
  from `PYTHONPATH`, user-site packages, and `sitecustomize.py`.
- Made Make and Heroku corpus preparation use and verify the same
  project-local NLTK data directory.

- Guarded NLTK resource loading against URL-encoded absolute and parent-path
  traversal while preserving fixed TextBlob corpus names, with runtime and
  static regressions for GHSA-p4gq-832x-fm9v.

## 2026-06-17

- Limited public web-chat input to 1,000 trimmed Unicode characters before
  TextBlob/NLTK response generation, with exact-boundary and hostile-mutation
  coverage.
- Suppressed repeated Slack signatures in each running process before a second
  bot call, while releasing failed claims for retry recovery.

## 2026-06-16

- Replaced deprecated Slack payload-token checks with Slack signing secret
  verification, exact-body HMAC, five-minute timestamp freshness, and signed
  API Gateway base64-body handling across both entry points.
- Removed the client-controlled Messenger `debug` reply bypass so valid signed
  messages are processed regardless of unknown top-level fields.

## 2026-06-15

- Anchored Make cleanup and verification to the loaded Makefile directory so
  external `make -f` invocations cannot target the caller's filesystem tree.
- Rejected unsuccessful Messenger provider responses before accepting reply
  content, allowing failed message-ID claims to be retried.
- Messenger GET verification requires the exact `subscribe` mode before an
  authenticated challenge is returned.

## 2026-06-14

- Escaped verified Messenger webhook challenges to close the reflected-XSS
  finding reported by CodeQL.
- Added pinned, least-privilege CodeQL analysis for GitHub Actions and Python
  to every hosted push and pull request.
- Added a mandatory human moderation checklist for response templates, blocked
  terms, reviewed fallbacks, regression boundaries, channel consistency,
  synthetic fixtures, reviewer evidence, and unresolved concerns.

## 2026-06-13

- Processed up to 20 valid Messenger user messages per signed webhook in payload
  order while preserving per-message replay claims and failure release.
- Added a bounded, thread-safe recent Messenger message-ID cache to suppress
  duplicate replies from retried webhook deliveries.
- Released replay claims after outbound exceptions and preserved messages without
  usable IDs, debug payloads, and echo filtering.
- Made external-directory checks safe for repository paths containing spaces by
  selecting the repository with GNU Make's `-C` option.

## 2026-06-12

- Required an exact `application/json` media type for Messenger POST webhooks,
  with case-insensitive parameter support and fail-closed 415 responses.
- Added dependency-free and Bottle/WebTest media-type regression coverage.

## 2026-06-10

- Contained generated-response filter rejections and returned a reviewed generic
  fallback instead of failing web, Slack, or Messenger requests.
- Limited unauthenticated Messenger webhook bodies to 1 MiB and reject both
  oversized declared and streamed payloads with HTTP 413 before parsing.
- Added dependency-free and Bottle/WebTest regressions, rooted Make execution,
  and a fixed Ubuntu 24.04 CI runner.
- Replaced the Python 2.7 runtime declaration and 2015-era dependencies with
  Python 3.14 metadata and current stable Bottle, NLTK, Requests, TextBlob, and
  WebTest releases.
- Made the real unittest/WebTest suite mandatory in `make check`.
- Disabled Bottle debug mode by default while preserving explicit local opt-in.
- Required SHA-256 Messenger webhook signatures before parsing POST events.
- Added a pinned GitHub Actions matrix that runs `make check` on every branch,
  pull request, and manual dispatch with credential-free checkout.
- Extended the contract checker to require the CI workflow and completed CI
  plan, including verification from outside the repository directory.
- Fixed recursive cleanup so external-working-directory checks use the
  repository Makefile instead of the caller's directory.

## 2026-06-09

- Rejected non-page Messenger webhook payloads before event parsing or reply
  generation.
- Added dependency-free Messenger object coverage and wired existing Messenger
  text route checks into the checker run list.
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
