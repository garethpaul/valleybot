# Messenger Challenge Escaping

## Status: Completed

## Context

The new Python CodeQL analysis identified the verified Messenger webhook
challenge response as reflected user input. A valid verification token should
not allow markup in `hub.challenge` to be rendered as HTML.

## Priority

Preserve legitimate verification challenges while neutralizing reflected
markup before Bottle writes the response.

## Requirements

- Escape the validated challenge with Python's standard HTML escaping helper.
- Preserve numeric and ordinary text challenges unchanged.
- Keep token mismatch and missing-challenge responses unchanged.
- Add dependency-free and Bottle/WebTest regressions for hostile markup.
- Record the boundary in repository security and maintenance guidance.

## Verification

- Focused dependency-free and Bottle/WebTest challenge regressions passed.
- The repository and external-directory `make check` passed.
- A hostile source mutation that restored the raw challenge return was
  rejected by the contract gate.
- Final artifact, credential, exact-diff, and exact-head CodeQL closure remain
  the shipping gate.

## Scope Boundary

This change does not alter verification-token comparison, POST webhook
handling, message generation, moderation, or live provider credentials.
