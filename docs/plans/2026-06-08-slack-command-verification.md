# Slack command verification hardening

## Context

The repo-local review found that `POST /slack` accepted command form data without validating that the request came from Slack.

## Plan

1. Reuse the existing `SLACK_TOKEN` setting as the legacy Slack verification token.
2. Reject Slack command requests whose submitted form token does not match the configured token with constant-time comparison.
3. Extend the baseline check so the route cannot regress to unauthenticated command handling.
4. Remove the resolved repo-local bug file from the branch.

## Verification

- `scripts/check-baseline.sh`
- `git diff --check`
- local bug scanner for `garethpaul/valleybot`
