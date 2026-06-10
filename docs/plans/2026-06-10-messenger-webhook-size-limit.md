# Messenger Webhook Size Limit

Status: Completed

## Context

Messenger POST handling read the complete unauthenticated request body before
signature verification. A remote sender could therefore force unbounded memory
use without knowing the application secret.

## Changes

- Limited Messenger webhook bodies to 1 MiB.
- Rejected oversized declared content lengths before reading the stream.
- Bounded actual reads to `limit + 1` so missing or dishonest length headers
  are also rejected with HTTP 413.
- Added dependency-free and Bottle/WebTest regression coverage.
- Rooted Make commands and fixed the hosted Linux runner and action annotations.

## Verification

- `make check`
- `python3 -m py_compile scripts/check_valleybot_contracts.py`
- Mutation checks for both size-limit paths, CI, and rooted Make execution
- `git diff --check`
