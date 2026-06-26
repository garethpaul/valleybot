# Deployment Packaging Boundary

status: completed

## Context

Valleybot's deployment files were individually inspectable, but the repository
did not state which changes are packaging-only or when a change crosses into
routes, authentication, moderation, response generation, or provider behavior.

## Requirements

- Inventory every deployment packaging file and its responsibility.
- Keep secrets in provider configuration rather than repository packaging.
- Identify behavior-owned files that packaging-only changes must not edit.
- Document offline syntax, corpus, runtime, and hosted-matrix verification.
- Keep packaging rollback independent from bot behavior rollback.
- Remove the completed separation item from the roadmap.

## Work Completed

- Added `DEPLOYMENT.md` with packaging ownership, configuration, validation,
  hosted evidence, and rollback boundaries.
- Linked the guide from repository contents and local usage guidance.
- Replaced the final roadmap item with an evidence-driven future-work rule.
- Added a dependency-free documentation contract and changelog record.

## Verification Completed

- Reproduced the missing guide and plan as a failing dependency-free contract.
- Ran the focused deployment packaging documentation contract.
- Ran `python -m json.tool app.json` and `bash -n bin/post_compile`.
- Ran `make check` with the documented Python 3.14 virtual environment.
- Passed 77 dependency-free contracts, 43 Bottle/bot runtime tests, six Slack
  replay mutations, five web-chat length mutations, corpus verification, and
  the 40-case Make authority matrix.
- Confirmed `git diff --check` passes.
