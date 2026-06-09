# Request Timeout Parsing Guard

## Status: Completed

## Context

`settings.py` parsed `REQUEST_TIMEOUT` with a direct `float(...)` call during
module import. Invalid values could crash service startup, while zero,
negative, or non-finite values could pass an unusable timeout to outbound
Messenger requests.

## Objectives

- Preserve positive numeric `REQUEST_TIMEOUT` overrides.
- Fall back to the default timeout for invalid env values.
- Reject zero, negative, NaN, and infinite timeout values.
- Cover timeout parsing with dependency-free contract checks.

## Work Completed

- Added `positive_float_from_env` to parse bounded positive finite floats.
- Kept the default outbound request timeout at `5.0` seconds.
- Added dependency-free tests for valid, invalid, non-positive, and non-finite
  timeout env values.
- Updated README, VISION, and CHANGES.

## Verification

- `python scripts/check_valleybot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add deployment notes for recommended production timeout values.
- Add retry/backoff behavior around transient Messenger API failures.
