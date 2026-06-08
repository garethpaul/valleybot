#!/usr/bin/env bash
set -euo pipefail

if grep -R "access_token=" -n settings.py app.py; then
  echo "Messenger access token must not be embedded in a configured URL" >&2
  exit 1
fi

grep -q "def messenger_params" settings.py
grep -q "params=settings.messenger_params()" app.py
grep -q "timeout=REQUEST_TIMEOUT" app.py
grep -q "resp.raise_for_status()" app.py
grep -q "debug(env_flag('BOTTLE_DEBUG'))" app.py
grep -q "def messenger_messages" app.py
grep -q "request.forms.get('token')" app.py
grep -q "settings.slack_token" app.py
grep -q "data.get('entry')" app.py
grep -q "msg_data.get('message')" app.py
grep -q "hub.verify_token" app.py
grep -q "hmac.compare_digest" app.py
grep -q "slack_token = os.environ\\['SLACK_TOKEN'\\]" settings.py
grep -q "messenger_verify_token" settings.py

for file in \
  docs/bugs/p2-python-access-token-in-url-query-9e8d7be7d1c5e1c6.md \
  docs/bugs/p2-python-http-call-without-timeout-a07c6a4bb0ee865f.md \
  docs/bugs/p2-python-slack-command-without-verification-1246b423a1a865c0.md \
  docs/bugs/p2-python-unvalidated-webhook-json-indexing-76ec6430a57cb399.md \
  docs/bugs/p2-python-webhook-challenge-without-verify-token-1afa52712275a3ff.md; do
  if [ -f "$file" ]; then
    echo "resolved bug file remains: $file" >&2
    exit 1
  fi
done

python2 -m py_compile app.py settings.py 2>/dev/null || python3 - <<'PY'
from pathlib import Path

for path in ("app.py", "settings.py"):
    compile(Path(path).read_text(), path, "exec")
PY
