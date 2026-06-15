# Fail Messenger Replies on Provider HTTP Errors

## Status: In Progress

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

## Work Pending

- Add the provider HTTP status boundary and mutation-sensitive regression.
- Update operator and security documentation.
- Run the planned bounded validation and record the actual evidence.
