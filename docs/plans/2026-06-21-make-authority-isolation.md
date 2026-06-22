# Isolate Make Verification Authority

## Status: Completed

## Context

The Makefile rooted cleanup and verification at its own location, but callers
could still replace the recipe shell, load startup makefiles, override the
Makefile list, select non-executing or error-ignoring modes, or embed Make
syntax in the configurable Python executable value.

This plan covers repository-controlled Make invocations. Caller-supplied Make
programs are outside this trust boundary. That includes `MAKEFILES` startup
files, extra `-f` makefiles, global or target-specific `override` directives,
replacement or double-colon recipes, and caller-selected `SHELL`,
`.SHELLFLAGS`, `PATH`, or tool variables.

GNU Make 4.4 also expands Make syntax in a command-line `ROOT` value while
processing a simultaneous command-line `PYTHON` override, before this Makefile
can replace `ROOT`. That pre-load expression is caller authority; environment
`ROOT` values remain neutralized without expansion.

## Requirements

- Derive the repository root only from the reviewed Makefile path.
- Fix recipes to `/bin/sh` for repository-controlled invocations.
- Reject replaced Makefile lists and dry-run, touch, question, or
  ignore-errors modes for every public target when no caller-supplied Make
  programs are loaded.
- Treat startup files, extra makefiles, override directives, replacement
  recipes, double-colon recipes, and caller-selected tools as caller authority
  rather than as authenticated repository verification.
- Preserve caller selection of a literal Python executable, including paths
  with spaces and shell metacharacters, without evaluating Make syntax.
- Require absolute Python executables, bake the reviewed selection into recipes,
  and enforce isolated startup with `-I -B`.
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
- Do not claim GNU Make can prevent parse-time execution of caller-supplied
  startup or extra makefiles. They are rejected or characterized only after GNU
  Make has already accepted them as caller programs.

## Verification

- Repository and external-directory `make check` passed 70 dependency-free
  contracts, five web-chat mutations, and 41 real unit tests.
- The authority harness passed 40 public-target/root/shell cases, a literal
  hostile Python path, four Make-syntax controls including the GNU Make 4.4
  command-root pre-load boundary, two Makefile-list
  rejections, two startup boundaries, caller `MAKEFLAGS`, ten unsafe modes,
  repository cleanup containment, global-override shell rejection, PATH-Python
  rejection, and a hostile `sitecustomize.py` isolation proof.
- Python and shell syntax, workflow YAML, `git diff --check`, intended-path,
  artifact, and changed-line credential audits passed.
