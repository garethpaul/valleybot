# Fail Messenger Replies on Provider HTTP Errors

## Status: Completed

## Context

The Messenger reply path applies a timeout and bearer authentication, but it
returns the response body without checking the provider's HTTP status. A 4xx
or 5xx response is therefore treated as a successful delivery, leaving the
message ID claimed and suppressing a legitimate webhook retry.

## Requirements

- Raise on unsuccessful Messenger provider HTTP responses before returning the
  response body.
- Preserve timeout, header authentication, successful response behavior, and
  replay handling for messages without usable IDs.
- Prove that an HTTP failure propagates through the webhook path and releases
  the replay claim so the same message can be retried.
- Add fail-closed source and documentation contracts for the new boundary.

## Verification Plan

- focused dependency-free Messenger reply and replay contracts
- mutation checks that remove or reorder the HTTP status check
- repository and external-directory `make check` with bounded execution
- exact diff, generated-artifact, and credential-pattern audits

## Scope Boundaries

- Do not add retries, change provider endpoints, or change token handling.
- Do not merge or close stacked pull requests without owner authorization.

## Work Completed

- Added an explicit provider HTTP status check before reply content is accepted.
- Added dependency-free and Bottle/WebTest regressions that prove provider HTTP
  errors propagate and release replay claims for a later webhook delivery.
- Added fail-closed source-order, runtime-test, documentation, and completed-plan
  contracts, plus operator and security documentation.

## Verification

- The focused HTTP-status contracts passed, and the full dependency-free suite
  passed 52 tests.
- Repository and external-directory `make check` passed under a clean pinned
  Python 3.12 environment, with 52 contracts and 29 runtime tests in each run.
- Five targeted mutations were rejected: removed and unreachable status checks,
  a non-raising fake response, missing runtime coverage, and missing docs.
- `uv pip check` passed for all 18 installed packages. `pip-audit` reported no
  known vulnerabilities in auditable packages; the private WebOb build was
  explicitly reported as unavailable on PyPI and unauditable.
- The first ambient `make check` attempt stopped before tests because its active
  interpreter lacked TextBlob; validation was rerun with the clean pinned
  environment rather than weakening the gate.
