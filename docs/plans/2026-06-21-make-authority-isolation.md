# Isolate Make Verification Authority

## Status: Completed

## Context

The Makefile rooted cleanup and verification at its own location, but callers
could still replace the recipe shell, load startup makefiles, override the
Makefile list, select non-executing or error-ignoring modes, or embed Make
syntax in the configurable Python executable value.

## Requirements

- Derive the repository root only from the reviewed Makefile path.
- Fix recipes to `/bin/sh` and reject injected startup makefiles.
- Reject replaced Makefile lists and dry-run, touch, question, or
  ignore-errors modes for every public target.
- Preserve caller selection of a literal Python executable, including paths
  with spaces and shell metacharacters, without evaluating Make syntax.
- Keep bytecode cleanup confined to the repository before and after the full
  gate, including when invoked from an external directory.
- Exercise all eight public targets under command-line and environment
  root/shell attacks.
- Invoke hosted root and external verification through `/usr/bin/make`.

## Scope Boundaries

- Do not change chatbot behavior, webhook authentication, replay handling,
  moderation policy, dependency versions, or NLTK resource selection.
- Do not remove the pinned corpus preparation step or real unittest suite.
- Preserve exact test secrets as synthetic local fixtures only.

## Verification

- Repository and external-directory `make check` passed 70 dependency-free
  contracts, five web-chat mutations, and 41 real unit tests.
- The authority harness passed 40 public-target/root/shell cases, a literal
  hostile Python path, two Make-syntax rejections, two Makefile-list
  rejections, two startup boundaries, caller `MAKEFLAGS`, ten unsafe modes,
  and repository cleanup containment.
- Python and shell syntax, workflow YAML, `git diff --check`, intended-path,
  artifact, and changed-line credential audits passed.
