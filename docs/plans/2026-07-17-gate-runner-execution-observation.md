# Gate Runner Execution Observation

Status: Completed

## Problem

Every repository gate ran from `make check`, but nothing observed that the
runners actually *executed* or that their verdicts actually *failed the build*.
The Makefile's authority hardening was thorough about *who may invoke make* and
*with what interpreter*, and `scripts/check_valleybot_contracts.py` pinned the
Makefile's authority lines whole-line. Coverage stopped one line short of the
recipe lines that invoke the gate runners themselves:

- `check:: clean verify` was not pinned at all, so `check:: clean` silently
  dropped `root-test`, `lint`, `test`, and `build`.
- The four `test::` runner invocation lines were not pinned as whole lines. The
  only pins were substrings such as `"scripts/test_slack_replay_mutations.py" in
  makefile`, which the `PYTHON_FILES` lint list already satisfies on its own, so
  the pin stayed green with the invocation deleted.
- No pin rejected `|| true` or a `-` recipe prefix on a runner line.
- Nothing rejected `continue-on-error` in the CI workflow.

`scripts/test-makefile-root.sh` did observe execution, but its fake interpreter
always exited 0, so it could not see a swallowed verdict.

Measured before this change (`make check` exit status):

| Mutation | Runner verdict | `make check` |
| --- | --- | --- |
| `|| true` on the contracts invocation | `AssertionError` printed | 0 |
| `-` prefix on the contracts invocation | `Error 1 (ignored)` | 0 |
| Delete the web-chat-length invocation | never ran | 0 |
| Delete the replay-mutation + `bot_tests.py` invocations | never ran | 0 |
| `check:: clean verify` -> `check:: clean` | nothing ran | 0 |

## Scope

- Observe execution *and* gating out-of-band, rather than asserting source text.
- Keep the observer outside the blast radius of what it detects.
- Preserve the existing Make authority boundary and all 40 authority cases.

## Work completed

- `scripts/test-makefile-root.sh`: the fake interpreter now fails on demand via
  `VALLEYBOT_FAIL_MATCH`, and 7 failure-injection cases run the real Makefile
  out-of-band, injecting a non-zero exit into exactly one runner at a time. Each
  case asserts both that `make check` *reached* the runner and that its failure
  *propagated*, plus a no-injection negative control so the assertions cannot be
  satisfied by an unconditionally red gate.
- `Makefile`: `root-test` became a direct prerequisite of `check`
  (`check:: clean root-test verify`), so severing `check -> verify` can no longer
  disconnect the observer along with everything else.
- `scripts/check_valleybot_contracts.py`: pins the prerequisite chain and all six
  runner invocation lines whole-line with exact occurrence counts, rejects `-`
  prefixes and `|| true`-style neuters on every recipe line, rejects
  `continue-on-error` in CI, and cross-guards the observer's own contract
  phrases. Both new tests are registration-guarded in `main()`.
- `.github/workflows/check.yml`: two make-independent steps invoke the gate
  observer and the contract checker directly, so a fully disconnected gate is
  still caught from outside the disconnected path.

## Verification

The repository and external-directory `make check` passed. Each mutation in the
table above now fails; the mutual cross-guard and the direct CI observers were
each exercised by hand. The one residual limit is recorded honestly: `make check`
alone cannot detect its own total disconnection (`check:: clean` with every
prerequisite removed) — an observer cannot observe its own removal — but both
direct CI steps go red on it, which is the boundary the CI workflow exists to
cover.
