# Python And NLTK Setup

status: completed

## Context

The README installed dependencies with the caller's `python` command but then
ran Make without a `PYTHON` override. Make intentionally defaults to
`/usr/bin/python3`, so an activated virtual environment could receive the
packages while corpus preparation and verification used a different
interpreter.

## Requirements

- Recommend the deployment-equivalent Python 3.14 line while preserving the
  tested Python 3.10 and 3.12 support boundary.
- Create and activate a repository-local virtual environment.
- Pass the activated interpreter's absolute path to corpus preparation and
  verification.
- Explain which TextBlob/NLTK resources are installed, where they live, and
  when network access is required.
- Provide a recovery path for missing-resource errors without relying on
  user-global NLTK state.
- Remove the completed setup item from the roadmap.

## Work Completed

- Added a same-interpreter setup sequence from clone through `make check`.
- Documented the TextBlob `lite` corpus contents and project-local
  `nltk_data` verification boundary.
- Added missing-resource troubleshooting that preserves the reviewed local
  data path.
- Added a dependency-free documentation contract and changelog record.
- Removed the completed Python and NLTK/TextBlob setup priority from VISION.

## Verification Completed

- Reproduced the missing documentation as a failing dependency-free contract.
- Ran the focused setup documentation contract.
- Created the documented Python 3.14 `.venv`, installed the pinned
  requirements, and ran `make check` with its absolute interpreter path.
- Passed 76 dependency-free contracts, 43 Bottle/bot runtime tests, six Slack
  replay mutations, five web-chat length mutations, corpus verification, and
  the 40-case Make authority matrix.
- Confirmed `git diff --check` passes.
