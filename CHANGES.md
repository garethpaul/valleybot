# Changes

## 2026-06-26T20:50:03-07:00 — P1 correctness/availability — cycle: Messenger replay-heavy batch cap

### Summary

Messenger now applies its 20-message webhook limit only to events that acquire
replay ownership or have no message ID. Completed replay IDs are skipped without
consuming work capacity, so they cannot hide a later unique event in the same
signed batch.

### Work completed

- Converted Messenger event extraction from a capped intermediate list to a
  lazy payload-order iterator.
- Moved the work cap into the webhook handler and checked it before claiming the
  next unique event.
- Counted work only after a replay claim succeeds, while preserving ID-less
  compatibility, reply ordering, completion, and failure release.
- Added dependency-free and Bottle/WebTest regressions for 20 completed replay
  IDs followed by one unique event.
- Updated security, contributor, roadmap, and implementation-plan evidence.

### Files

- `app.py` — lazy Messenger parsing and owned-work accounting.
- `bot_tests.py`, `scripts/check_valleybot_contracts.py` — runtime, dependency-free,
  and source-order contracts.
- `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md` — documented replay and
  batch-limit semantics.
- `docs/plans/2026-06-26-messenger-replay-batch-cap.md` — implementation plan.

### Tests

- Focused dependency-free replay-heavy batch regression: passed after reproducing
  the prior zero-reply failure.
- `make check PYTHON=/tmp/valleybot-20260626-venv/bin/python`: passed with 82
  dependency-free contracts, 6 rejected Slack replay mutations, 5 rejected web
  chat length mutations, and 46 Bottle/WebTest runtime tests on Python 3.14.6.
- `git diff --check`: passed.

### Findings and blockers

- Bug fixed: the parser previously spent the complete 20-message budget before
  the handler checked replay ownership.
- Replay state remains process-local and does not coordinate across workers or
  process restarts.

### Next action

- Publish the exact reviewed head and merge only after hosted Python and CodeQL
  checks pass.

## 2026-06-26T12:19:26Z — P1 resilience — cycle: channel message length boundary

### Summary

Added a shared 1,000-character Slack and Messenger input boundary before
authenticated channel text can reach TextBlob/NLTK response generation.

### Work completed

- Centralized the existing web-chat limit as a channel-wide message constant.
- Rejected oversized commands in both Bottle and standalone Lambda Slack
  handlers before replay claims or bot execution.
- Skipped oversized Messenger events while preserving ordered processing of
  later valid events in the same bounded webhook batch.
- Added dependency-free and runtime regressions for both channel behaviors.
- Documented the security scope, batch semantics, and maintenance invariant.

### Threads

- None; this focused input-boundary hardening was implemented directly.

### Files changed

- `channel_limits.py`, `app.py`, and `slack.py` — shared limit and enforcement.
- `bot_tests.py`, `scripts/check_valleybot_contracts.py`, and
  `scripts/test_web_chat_length_contract.py` — behavioral, source, and mutation
  contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, and `AGENTS.md` — operator and
  contributor guidance.
- `docs/plans/2026-06-26-channel-message-length.md` — completed implementation
  plan and acceptance evidence.

### Validation

- Focused regressions failed before the guards existed and passed afterward.
- Python 3.14 `make check` passed 81 dependency-free contracts, 45 runtime
  tests, 11 existing hostile mutations, corpus verification, syntax checks,
  and the 40-case Make authority matrix from repository and external roots.
- Five focused hostile mutations were rejected, and `uv pip check` reported all
  19 installed packages compatible.

## 2026-06-26T06:23:47Z — P2 documentation/reviewability — cycle: deployment packaging boundary

### Summary

Separated deployment packaging review from bot behavior changes with an
explicit file-ownership, configuration, validation, and rollback guide.

### Work completed

- Defined `.python-version`, `requirements.txt`, `Procfile`, `app.json`, and
  `bin/post_compile` as the packaging-owned surface.
- Kept routes, authentication, moderation, responses, request limits, retries,
  and provider API behavior outside packaging-only PRs.
- Documented provider-owned secrets, runtime `PORT`, project-local corpus
  preparation, offline validation, hosted matrix evidence, and rollback scope.
- Linked the guide from README and closed the final explicit roadmap item.
- Added a dependency-free deployment documentation contract and completed plan.

### Threads

- None; this focused documentation boundary was implemented directly.

### Files changed

- `DEPLOYMENT.md` — packaging ownership and validation guide.
- `README.md`, `VISION.md`, and `CHANGES.md` — navigation and roadmap state.
- `scripts/check_valleybot_contracts.py` — frozen documentation contract.
- `docs/plans/2026-06-25-deployment-packaging-boundary.md` — completed plan.

### Validation

- Focused deployment documentation contract passed after failing on the
  missing guide and plan.
- Python 3.14 `make check` passed 77 dependency-free contracts, 43 runtime
  tests, 11 hostile mutations, corpus verification, and the 40-case Make
  authority matrix; JSON and shell syntax checks also passed.

## 2026-06-26T06:20:42Z — P2 documentation/reproducibility — cycle: Python and NLTK setup

### Summary

Documented same-interpreter Python and NLTK setup so virtual-environment
dependency installs cannot silently diverge from Make's `/usr/bin/python3`
default.

### Work completed

- Made Python 3.14 the deployment-equivalent local recommendation while
  retaining the tested Python 3.10 and 3.12 support boundary.
- Added virtual-environment creation, activation, dependency installation,
  project-local TextBlob corpus preparation, and full verification commands.
- Explained the required absolute `PYTHON` Make override, downloaded `lite`
  resources, network boundary, and missing-resource recovery path.
- Closed the completed Python and NLTK/TextBlob documentation roadmap item.
- Added a dependency-free contract and completed maintenance plan.

### Threads

- None; this focused documentation contract was implemented directly.

### Files changed

- `README.md`, `VISION.md`, and `CHANGES.md` — setup and roadmap guidance.
- `scripts/check_valleybot_contracts.py` — frozen documentation contract.
- `docs/plans/2026-06-25-python-nltk-setup.md` — completed plan and evidence.

### Validation

- Focused setup documentation contract passed after failing on the missing
  plan and setup guidance.
- The documented Python 3.14 `.venv` path passed full `make check`: 76
  dependency-free contracts, 43 runtime tests, 11 hostile mutations, corpus
  verification, and the 40-case Make authority matrix.

## 2026-06-26T02:53:26Z — P1 concurrency/correctness — cycle: Slack in-flight replay claims

### Summary

The bounded Slack replay cache could evict a signature while its bot response
was still running, allowing a concurrent exact retry to execute the command a
second time.

### Work completed

- Split process-local Slack replay state into in-flight and completed claims.
- Added explicit success completion to both Bottle and standalone handlers.
- Preserved duplicate acknowledgement and failure-release retry recovery.
- Added completed-cache eviction, capacity-pressure, source-order, and six
  hostile-mutation regressions.

### Threads

- None; the focused repository change was implemented directly.

### Files changed

- `slack_replay.py`, `app.py`, and `slack.py` — explicit replay ownership.
- `scripts/check_valleybot_contracts.py` and
  `scripts/test_slack_replay_mutations.py` — behavior and mutation proof.
- Security, vision, agent, README, plan, and Make verification documentation.

### Validation

- Dependency-free contracts — 75 tests passed after RED failed on the missing
  `complete()` transition.
- Slack replay mutation contract — six hostile mutations rejected.
- Make authority matrix — all 40 target/authority cases and documented hostile
  startup and override cases passed.
- Python 3.14 `make check` — 75 dependency-free contracts, 43 Bottle/bot
  runtime tests, five existing web-chat mutations, syntax, and corpus checks passed.
- Hosted runs `28214128990` and `28214129936` — Python 3.10/3.12/3.14 and
  Actions/Python CodeQL passed on the reviewed implementation head.
- Codex review — attempted as requested but blocked by OpenAI API HTTP 401;
  manual exact-head concurrency, security, and regression review found no findings.

### Bugs / findings

- P1: completed-cache capacity previously applied to pending Slack claims.

### Blockers

- No live Slack webhook was sent; multi-worker global replay suppression still
  requires a shared store.

### Next action

- Merge the final hosted-green head, then load-test concurrent valid retries
  near replay-cache capacity.

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
