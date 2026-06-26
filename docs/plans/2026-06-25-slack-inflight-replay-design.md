# Slack In-Flight Replay Claims Design

Status: Approved

## Current State

Both Slack entry points verify the signed raw request, normalize command text,
claim the signature, and release the claim if bot generation raises. The
process-local replay cache stores pending and successful claims in one bounded
`OrderedDict`.

Capacity eviction can therefore remove the oldest signature while its bot call
is still running. A concurrent retry of that exact signed request can claim the
signature again and execute the command twice.

## External Evidence

- Slack requires signed-request verification using the raw request body,
  timestamp, and `X-Slack-Signature` header:
  <https://docs.slack.dev/authentication/verifying-requests-from-slack>
- Slack documents a three-second acknowledgement boundary and retry behavior
  for delayed event delivery, making overlapping deliveries a supported
  operational condition:
  <https://docs.slack.dev/apis/events-api#retries>

The retry documentation is for the Events API rather than this repository's
legacy slash-command adapter, so the concurrency conclusion is an inference:
network retries and concurrent duplicate delivery must not re-enter bot work
while the original signed request remains pending.

## Constraints

- Preserve the current process-local, bounded replay scope.
- Preserve duplicate acknowledgement as `ok`.
- Preserve retry recovery when bot generation raises.
- Keep Bottle and standalone event adapters behaviorally identical.
- Avoid holding a lock while generating a bot response.

## Considered Approaches

### Recommended: Separate in-flight and completed signatures

Keep pending signatures in an unbounded-by-capacity set and successful
signatures in the existing bounded `OrderedDict`. `claim()` rejects either
state, `complete()` moves a pending signature to completed state, and
`release()` removes both states after failure.

This matches the Messenger replay state machine already maintained in
`app.py`, preserves concurrency, and bounds only entries safe to evict.

### Rejected: Make the single cache unbounded

This prevents pending eviction but permits permanent process memory growth
from successful requests.

### Rejected: Hold the replay lock through bot generation

This prevents eviction races but serializes unrelated Slack commands and makes
slow NLP work a global request bottleneck.

## Validation

- RED: calling the required `complete()` transition must fail before the
  implementation exists.
- Prove capacity pressure never makes an in-flight signature reclaimable.
- Prove completed signatures remain bounded and oldest-first evicted.
- Prove both handlers complete only after successful bot generation and release
  after exceptions.
- Run dependency-free contracts, runtime tests, hostile mutations, and
  `make check` before review.
