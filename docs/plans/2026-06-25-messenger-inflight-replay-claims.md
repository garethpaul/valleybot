# Messenger In-Flight Replay Claims

Status: Completed

## Problem

The bounded message-ID cache treated pending and successful replies identically.
When capacity eviction removed the oldest pending ID, a concurrent delivery of
that same signed message could claim it again before the first outbound reply
finished, producing duplicate bot replies.

## Change

Track in-flight IDs separately from completed IDs. Claims stay protected until
the outbound reply succeeds or fails. Success moves the ID into the bounded
completed replay cache; failure releases it for provider retry recovery.

## Verification

- RED reproduced as an `AttributeError` for the missing `complete()` transition.
- Added bounded completed-claim eviction coverage.
- Added a capacity-pressure regression proving an in-flight ID cannot be reclaimed.
- Kept claim, reply, completion, and failure-release ordering under source checks.
- Dependency-free contracts and the full `make check` passed.
- No live Messenger webhook or provider request was sent.
