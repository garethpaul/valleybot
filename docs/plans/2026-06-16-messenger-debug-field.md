# Ignore Client-Controlled Messenger Debug Fields

## Status: Planned

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
