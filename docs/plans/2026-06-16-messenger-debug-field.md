# Ignore Client-Controlled Messenger Debug Fields

## Status: Completed

## Context

The Messenger POST handler treats a top-level `debug` value in the signed JSON
body as a command to suppress every outbound reply. That field exists only to
support tests, but it is part of the external webhook request contract and can
silently acknowledge otherwise valid messages without processing them.

## Requirements

- Process valid Messenger messages regardless of unknown top-level `debug`
  fields.
- Preserve signature, content-type, size, page-object, echo, replay, batch,
  timeout, and provider-status behavior.
- Replace payload-controlled test suppression with explicit reply stubbing.
- Add dependency-free and Bottle/WebTest regressions plus mutation-sensitive
  source, guidance, registration, and completed-plan contracts.

## Scope Boundaries

- Do not change Messenger authentication, endpoints, tokens, reply payloads,
  replay IDs, or batch limits.
- Do not merge or close stacked pull requests without owner authorization.

## Verification

- Run focused debug-field contracts and the full repository/external
  `make check` gates with explicit timeouts.
- Reject mutations that restore payload suppression, remove runtime tests,
  weaken guidance, unregister the focused check, or reopen the plan.
- Audit the exact diff, generated artifacts, conflicts, file modes, and
  credential-like additions before committing.

## Work Completed

- Removed request-body `debug` branching from the Messenger POST handler.
- Replaced payload-controlled test suppression with explicit reply stubs.
- Added dependency-free and Bottle/WebTest regressions proving unknown
  top-level fields do not suppress valid replies.
- Added source, documentation, registration, and completed-plan contracts.

## Verification Completed

- `python3 -m py_compile app.py bot_tests.py scripts/check_valleybot_contracts.py`
- Focused dependency-free debug-field contracts passed.
- Focused Bottle/WebTest regression passed in an isolated environment created
  from the exact pinned `requirements.txt`.
- The first full Bottle run exposed shared replay-cache state between the new
  positive regression and the sample webhook test; `TestFacebook.setUp` now
  creates a fresh bounded replay cache for every case.
- The second run exposed a content-type test that implicitly relied on payload
  suppression; it now stubs reply delivery explicitly.
- Repository and external-directory non-cleaning `make verify` passed all 55
  dependency-free checks and 31 Bottle/WebTest cases with the pinned runtime.
- Five isolated mutations were rejected for payload suppression restoration,
  Bottle regression removal, dependency-free test unregistration, README
  guidance removal, and stale plan status.
