# Moderation And Content Review

Valleybot is a historical stereotype-based chatbot. Every change to response
templates, blocked terms, or fallback text requires human content review before
merge. The prefix filter in `bot.filter_response` is a narrow final-output
guard, not a complete moderation system.

## Review Scope

Review every added, removed, or changed value in these sources:

- response templates and fallback text in `config.py`
- response construction and filtering in `bot.py`
- channel adapters that deliver generated text
- moderation fixtures and expected output in tests

Review the text in context, including substitutions and prefixes that can turn
an otherwise neutral template into harmful output.

## Harm Checklist

Check for slurs, profanity, harassment, protected-class stereotypes, sexual
content, threats, self-harm language, and demeaning identity language. Also
consider combinations of accepted fragments, misspellings, capitalization,
punctuation, and prefix matches.

For every blocked-term addition or removal, record the rationale and affected
examples. Do not remove a term solely to make a generated response pass.

## Required Verification

1. Add accepted-boundary and rejected-boundary regression fixtures.
2. Prove blocked generated text reaches `safe_response` and returns only a
   reviewed value from `config.NONE_RESPONSES`.
3. Verify the same response boundary protects web, Slack, Messenger, terminal,
   and low-level JSON entry points.
4. Run `make check` and record the result.
5. Record reviewer, review date, changed content scope, commands, and unresolved
   concerns in the pull request or completed plan evidence.

Fixtures must be synthetic. Never add real conversation transcripts, user
identifiers, channel tokens, webhook payloads, or other private data.

## Review Boundary

Automated tests can prove routing and known-term behavior, but they cannot prove
that generated content is broadly appropriate. Human review remains required,
and unresolved harmful-content concerns block merge.
