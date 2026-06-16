# Require Messenger Subscription Verification Mode

## Status: Planned

## Context

The Messenger verification endpoint authenticates the verification token and
escapes the returned challenge, but it does not validate `hub.mode`. A request
with a matching token can therefore receive the challenge even when it is not
the platform's `subscribe` verification operation.

## Requirements

- Require the exact `subscribe` verification mode before returning a Messenger
  challenge.
- Reject missing, blank, differently cased, and unrelated mode values without
  reflecting the challenge.
- Preserve constant-time token comparison, escaped challenge output, and the
  existing missing-challenge behavior for valid subscription requests.
- Add dependency-free and Bottle/WebTest regressions plus fail-closed source,
  documentation, changelog, and completed-plan contracts.

## Verification Plan

- focused Messenger verification-mode contracts before and after implementation
- Bottle/WebTest coverage for valid, missing, and invalid mode values
- mutation checks for missing or weakened mode validation and removed evidence
- repository and external-directory `make check` with bounded execution
- exact diff, generated-artifact, conflict-marker, and credential-pattern audits

## Scope Boundaries

- Do not change POST signature verification, reply delivery, replay handling,
  provider endpoints, tokens, or timeout behavior.
- Do not accept case-folded or whitespace-normalized alternatives to the
  platform's exact `subscribe` mode.
- Do not merge or close stacked pull requests without owner authorization.
