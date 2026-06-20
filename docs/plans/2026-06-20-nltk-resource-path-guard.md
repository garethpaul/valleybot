---
title: Guard NLTK resource paths
status: completed
date: 2026-06-20
---

# Guard NLTK Resource Paths

## Problem

NLTK 3.9.4 has no published patched release for GHSA-p4gq-832x-fm9v. Its
resource loader checks traversal syntax before URL decoding, so encoded path
separators can escape configured NLTK data roots when an attacker controls a
resource identifier.

Valleybot passes user messages to TextBlob, not to `nltk.data.load()`, but the
dependency remains part of the public request path. The application needs a
local defense that does not change normal fixed corpus lookup behavior.

## Implementation

- Wrap `nltk.data.load()` before importing TextBlob.
- Repeatedly decode resource identifiers and reject POSIX absolute paths,
  Windows drive-qualified paths, or `..` segments after normalizing path
  separators.
- Keep fixed tokenizer and tagger resource names valid.
- Compile the guard during `make lint` and enforce its installation through the
  dependency-free contract suite.
- Add runtime regressions for encoded absolute paths, encoded traversal,
  encoded separators, and repeated encoding.

## Verification

- Repository-root `make check` passed in a clean exact-head checkout.
- External-directory `make check` passed through the absolute Makefile path.
- The focused unittest suite rejected every hostile resource identifier and
  preserved normal TextBlob behavior.
- `git diff --check` and `git fsck --strict` passed.
