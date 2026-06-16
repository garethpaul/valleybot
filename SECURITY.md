# Security Policy

## Supported Versions

The supported security scope for `valleybot` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: A chatbot for FB, Slack, Web and more that responds as a "typical" character from Silicon Valley.

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/valleybot` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a Python web API or service project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found infrastructure, deployment, proxy, or cloud configuration; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: requirements.txt. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- GitHub Actions runs the dependency-free `make check` baseline; review workflow, checker, and deployment-script changes as part of the supply-chain surface.
- CodeQL analyzes GitHub Actions and Python with immutable action pins and an
  upload permission scoped to the analysis job.

## Service and API Notes

Messenger POST webhooks are accepted only when `X-Hub-Signature-256` matches
the raw request body under `MESSENGER_APP_SECRET`. Keep that secret distinct
from page and verification tokens and rotate it if webhook logs expose it.
Verified Messenger GET challenges are escaped before response delivery so a
valid verification token cannot reflect executable markup into a browser.
Messenger GET verification requires the exact `subscribe` mode after token
authentication and before any challenge is reflected.
Webhook bodies larger than 1 MiB are rejected with HTTP 413 before signature
verification, JSON parsing, response generation, or outbound API calls.
Messenger POST requests must use the `application/json` media type; optional
parameters and case differences are accepted, while other types return 415
before signature verification or JSON parsing.
Recent non-empty Messenger message IDs are claimed before outbound replies in a
bounded process-local cache. Duplicate deliveries are acknowledged without a
second reply, and outbound exceptions release their claim. This protection
does not span multiple workers or process restarts.
Provider HTTP errors propagate through the webhook handler and release any
message-ID claim so a later provider delivery can retry the outbound reply.
Each signed webhook processes at most 20 valid user messages in payload order,
limiting outbound reply amplification while preserving per-message replay
claims and failure release.

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

Messenger webhook events should only generate bot replies when sender IDs and
message text are textual and nonblank. Non-message, blank, or non-text events
should be acknowledged without response generation.

Slack command events should only generate bot replies after token validation
and when command text is textual and nonblank. Missing, blank, or non-text
command values should return the existing missing-text response.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
