# Deployment Packaging Boundary

Deployment packaging tells a provider how to install and start Valleybot. It
must stay reviewable separately from chatbot responses, routes, authentication,
moderation, and webhook behavior.

## Packaging-Owned Files

Packaging-only changes own this narrow surface:

- `.python-version` selects the deployment Python line.
- `requirements.txt` pins installed Python packages.
- `Procfile` starts the Bottle application with the provider-supplied `PORT`.
- `app.json` provides non-secret application metadata.
- `bin/post_compile` prepares and verifies project-local TextBlob/NLTK data.

Packaging-only changes must not edit `app.py`, `bot.py`, `slack.py`,
`slack_auth.py`, `slack_replay.py`, `settings.py`, `config.py`, or `views/`.
Changes to routes, environment-variable meaning, authentication, moderation,
responses, request limits, retry behavior, or provider API calls are behavior
changes and require their own focused PR and tests.

## Configuration Boundary

Deployment secrets remain provider configuration and do not belong in
`app.json`, the `Procfile`, source files, logs, or screenshots. Configure
`SLACK_SIGNING_SECRET`, `MESSENGER_TOKEN`, `MESSENGER_VERIFY_TOKEN`, and
`MESSENGER_APP_SECRET` through the provider's secret store. `REQUEST_TIMEOUT`
is optional and `PORT` is supplied by the runtime.

`bin/post_compile` may download the TextBlob `lite` corpora during deployment.
It writes only to the repository's `nltk_data` directory and uses the provider's
selected Python interpreter.

## Validation

From an activated supported virtual environment, packaging changes must run:

```bash
python -m json.tool app.json >/dev/null
bash -n bin/post_compile
make check PYTHON="$(command -v python)"
```

Review the `Procfile` command and `.python-version` as text because starting a
real provider dyno is outside the offline gate. Dependency updates must also
retain exact pins and pass the hosted Python 3.10, 3.12, and 3.14 matrix before
merge.

## Change And Rollback Discipline

Keep packaging changes in a dedicated PR. Record the previous Python line,
dependency pins, start command, or post-compile behavior in the PR so rollback
is a direct revert. Do not combine a packaging rollback with bot behavior
changes; restore packaging first, then diagnose behavior separately.
