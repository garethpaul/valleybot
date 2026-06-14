# Moderation And Content Review Guide

## Status: Completed

## Context

Valleybot intentionally generates stereotype-based responses and protects all
channels with a prefix content filter plus reviewed generic fallbacks. The
repository does not yet define how a contributor should review additions to
response templates, filter terms, or fallback text.

## Priority

Add an auditable human-review checklist that keeps content changes explicit,
testable, privacy-preserving, and consistent across web, Slack, Messenger, and
terminal entry points.

## Requirements

- Require reviewers to inspect every added or changed response template and
  blocked term in context.
- Require review for slurs, profanity, harassment, protected-class stereotypes,
  sexual content, threats, self-harm, and demeaning identity language.
- Require a documented rationale for filter additions and removals.
- Preserve the reviewed generic fallback and verify blocked generated text does
  not escape through any channel.
- Require regression fixtures for both accepted and rejected boundaries.
- Prohibit real conversation transcripts, user identifiers, tokens, or private
  payloads in review fixtures.
- Record reviewer, date, scope, commands, and unresolved concerns in the PR or
  plan evidence.
- Add fail-closed documentation, source, suite, roadmap, changelog, and plan
  contracts plus hostile mutations.

## Verification

- Focused moderation-guide and filter/fallback contracts passed.
- The repository and external-directory `make check` passed.
- Ten hostile moderation-guide mutations were rejected across review scope,
  harmful categories, rationale, fallback, fixtures, channels, privacy,
  reviewer evidence, roadmap, and plan-status contracts.
- Final artifact, credential, and exact-diff audits passed. Hosted verification
  is recorded against the exact pull-request head after push.

## Scope Boundary

This change does not add stereotype content, remove blocked terms, classify
real users, replace human review with automation, or claim that the current
filter catches every harmful response.
