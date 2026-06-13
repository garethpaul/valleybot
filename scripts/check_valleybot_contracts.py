#!/usr/bin/env python3
"""Dependency-free route contract checks for the legacy Bottle app."""
import importlib.util
import hashlib
import hmac
import io
import json
import os
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WEBHOOK_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-valleybot-webhook-hardening.md"
STANDALONE_SLACK_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-08-valleybot-standalone-slack-token.md"
)
SLACK_COMMAND_TEXT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-08-valleybot-slack-command-text.md"
)
SLACK_NON_TEXT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-slack-non-text-command.md"
)
WEB_BOT_CHAT_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-valleybot-web-bot-chat.md"
REQUEST_TIMEOUT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-request-timeout.md"
)
BOT_JSON_REQUEST_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-json-request-guard.md"
)
WEB_TEMPLATE_ESCAPING_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-web-template-escaping.md"
)
MESSENGER_TEXT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-messenger-text-guard.md"
)
BOT_LOGGING_PRIVACY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-bot-log-privacy.md"
)
MESSENGER_OBJECT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-messenger-object-guard.md"
)
CI_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-10-ci-baseline.md"
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "check.yml"
RUNTIME_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-python3-runtime-modernization.md"
)
WEBHOOK_SIZE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-messenger-webhook-size-limit.md"
)
FILTER_FALLBACK_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-filtered-response-fallback.md"
)
MESSENGER_CONTENT_TYPE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-12-messenger-json-content-type.md"
)
MESSENGER_ECHO_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-messenger-echo-guard.md"
)


class FakeBottle:
    def get(self, _route):
        return lambda func: func

    def post(self, _route):
        return lambda func: func


class MutableRequest:
    def __init__(self):
        self.forms = {}
        self.query = {}
        self.json = None
        self.body = io.BytesIO(b"")
        self.content_length = 0
        self.headers = {
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=" + hmac.new(
                b"app-secret", b"", hashlib.sha256).hexdigest()
        }


class MutableResponse:
    def __init__(self):
        self.status = 200
        self.content_type = None


class FakeRequests(types.SimpleNamespace):
    def __init__(self):
        super(FakeRequests, self).__init__()
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return types.SimpleNamespace(content=b'{"recipient_id": "user-1"}')


def install_stubs():
    request = MutableRequest()
    response = MutableResponse()
    requests = FakeRequests()

    bottle = types.ModuleType("bottle")
    bottle.Bottle = lambda: FakeBottle()
    bottle.template = lambda _name, info: info
    bottle.request = request
    bottle.response = response
    bottle.debug = lambda _enabled: None

    bot = types.ModuleType("bot")
    bot.calls = []

    def respond(message):
        bot.calls.append(message)
        return "bot: {0}".format(message)

    bot.respond = respond

    settings = types.ModuleType("settings")
    settings.slack_token = "slack-secret"
    settings.messenger_token = "page-token"
    settings.messenger_verify_token = "verify-secret"
    settings.messenger_app_secret = "app-secret"
    settings.messenger_url = "https://graph.facebook.com/v2.6/me/messages"
    settings.request_timeout = 5

    sys.modules["bottle"] = bottle
    sys.modules["bot"] = bot
    sys.modules["requests"] = requests
    sys.modules["settings"] = settings
    return request, response, requests


def load_app():
    request, response, requests = install_stubs()
    spec = importlib.util.spec_from_file_location("valleybot_app", str(ROOT / "app.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, request, response, requests


def load_slack_module():
    install_stubs()
    spec = importlib.util.spec_from_file_location("valleybot_slack", str(ROOT / "slack.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, sys.modules["bot"]


def load_bot_module():
    nltk = types.ModuleType("nltk")
    nltk.data = types.SimpleNamespace(path=[])
    textblob = types.ModuleType("textblob")
    textblob.TextBlob = object
    sys.modules["nltk"] = nltk
    sys.modules["textblob"] = textblob
    sys.modules.pop("valleybot_bot", None)

    spec = importlib.util.spec_from_file_location("valleybot_bot", str(ROOT / "bot.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls = []

    def fake_chatback(message):
        calls.append(message)
        return "bot: {0}".format(message)

    module.chatback = fake_chatback
    return module, calls


def load_settings_with_request_timeout(value):
    original = os.environ.get("REQUEST_TIMEOUT")
    if value is None:
        os.environ.pop("REQUEST_TIMEOUT", None)
    else:
        os.environ["REQUEST_TIMEOUT"] = value

    try:
        spec = importlib.util.spec_from_file_location(
            "valleybot_settings_test", str(ROOT / "settings.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.request_timeout
    finally:
        if original is None:
            os.environ.pop("REQUEST_TIMEOUT", None)
        else:
            os.environ["REQUEST_TIMEOUT"] = original


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError("{0}: expected {1!r}, got {2!r}".format(label, expected, actual))


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def assert_completed_plan(path, label):
    assert_true(path.is_file(), "{0} plan must live under docs/plans".format(label))
    plan_text = path.read_text()
    assert_true("status: completed" in plan_text.lower(), "{0} plan must be completed".format(label))
    assert_true("make check" in plan_text, "{0} plan must document make check verification".format(label))


def test_completed_plans_are_in_docs_plans():
    assert_completed_plan(WEBHOOK_PLAN_PATH, "webhook hardening")
    assert_completed_plan(STANDALONE_SLACK_PLAN_PATH, "standalone Slack token")
    assert_completed_plan(SLACK_COMMAND_TEXT_PLAN_PATH, "Slack command text")
    assert_completed_plan(SLACK_NON_TEXT_PLAN_PATH, "Slack non-text command")
    assert_completed_plan(WEB_BOT_CHAT_PLAN_PATH, "web bot chat")
    assert_completed_plan(REQUEST_TIMEOUT_PLAN_PATH, "request timeout")
    assert_completed_plan(BOT_JSON_REQUEST_PLAN_PATH, "bot JSON request")
    assert_completed_plan(WEB_TEMPLATE_ESCAPING_PLAN_PATH, "web template escaping")
    assert_completed_plan(MESSENGER_TEXT_PLAN_PATH, "Messenger text")
    assert_completed_plan(BOT_LOGGING_PRIVACY_PLAN_PATH, "bot logging privacy")
    assert_completed_plan(MESSENGER_OBJECT_PLAN_PATH, "Messenger object")
    assert_completed_plan(CI_PLAN_PATH, "CI baseline")
    assert_completed_plan(RUNTIME_PLAN_PATH, "Python 3 runtime modernization")
    assert_completed_plan(WEBHOOK_SIZE_PLAN_PATH, "Messenger webhook size limit")
    assert_completed_plan(FILTER_FALLBACK_PLAN_PATH, "filtered response fallback")
    assert_completed_plan(MESSENGER_CONTENT_TYPE_PLAN_PATH, "Messenger JSON content type")
    assert_completed_plan(MESSENGER_ECHO_PLAN_PATH, "Messenger echo guard")


def test_runtime_and_ci_contracts():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for requirement in (
            "bottle==0.13.4",
            "nltk==3.9.4",
            "requests==2.34.2",
            "textblob==0.20.0",
            "WebTest==3.0.7"):
        assert_true(requirement in requirements, "missing runtime pin {0}".format(requirement))

    assert_equal((ROOT / ".python-version").read_text(encoding="utf-8").strip(), "3.14", "deployment Python line")
    assert_true(not (ROOT / "runtime.txt").exists(), "deprecated runtime.txt must remain removed")

    assert_true(CI_WORKFLOW_PATH.is_file(), "GitHub Actions check workflow must exist")
    workflow = CI_WORKFLOW_PATH.read_text(encoding="utf-8")
    for contract in (
            "push:\n  pull_request:",
            "permissions:\n  contents: read",
            "concurrency:",
            "cancel-in-progress: true",
            "runs-on: ubuntu-24.04",
            "timeout-minutes: 15",
            'python-version: ["3.10", "3.12", "3.14"]',
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
            "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
            "persist-credentials: false",
            "python -m pip install -r requirements.txt",
            "make check PYTHON=python",
            'make -f "$GITHUB_WORKSPACE/Makefile" check PYTHON=python'):
        assert_true(contract in workflow, "missing CI contract {0}".format(contract))
    assert_true("@v" not in workflow, "CI actions must use immutable commits")
    assert_true("ubuntu-latest" not in workflow, "CI must not use a floating Ubuntu runner")
    assert_true("pull_request_target" not in workflow, "CI must not run untrusted code with target-branch privileges")
    assert_true("branches:" not in workflow, "CI push checks must cover every branch")
    assert_true("# v6.0.3" in workflow, "checkout pin annotation must identify the exact release")
    assert_true("# v6.2.0" in workflow, "setup-python pin annotation must identify the exact release")
    assert_equal(workflow.count("persist-credentials:"), 1, "checkout credential setting count")
    assert_true("persist-credentials: true" not in workflow, "checkout credentials must not persist")

    action_uses = []
    for line in workflow.splitlines():
        action_line = line.strip()
        if action_line.startswith("- "):
            action_line = action_line[2:]
        if action_line.startswith("uses: "):
            action_uses.append(action_line)
    assert_equal(len(action_uses), 2, "CI action count")
    assert_equal(
        set(action_uses),
        {
            "uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3",
            "uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0",
        },
        "CI action allowlist",
    )
    workflow_files = list((ROOT / ".github" / "workflows").glob("*.y*ml"))
    assert_equal(workflow_files, [CI_WORKFLOW_PATH], "CI workflow file set")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert_true("GitHub Actions" in readme, "README must document the GitHub Actions check")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert_true("!.github/workflows/check.yml" in gitignore, "workflow file must not be hidden by dotfile ignores")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    for security_contract in ("X-Hub-Signature-256", "MESSENGER_APP_SECRET", "1 MiB"):
        assert_true(security_contract in security, "SECURITY.md must document {0}".format(security_contract))

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert_true("ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile, "Makefile must resolve the repository root")
    assert_true('find "$(ROOT)"' in makefile, "Makefile cleanup must stay inside the repository")
    assert_true('"$(ROOT)/scripts/check_valleybot_contracts.py"' in makefile, "Makefile must use the rooted contract path")
    assert_true('$(MAKE) -f "$(ROOT)/Makefile" clean' in makefile, "recursive cleanup must use the repository Makefile")

    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")
    assert_true("debug(True)" not in app_source, "Bottle debug mode must not be enabled by default")
    assert_true("verify_messenger_signature" in app_source, "Messenger POST signatures must remain required")
    assert_true("MAX_MESSENGER_WEBHOOK_BYTES = 1024 * 1024" in app_source, "Messenger webhook size limit must remain 1 MiB")
    assert_true("request.body.read(MAX_MESSENGER_WEBHOOK_BYTES + 1)" in app_source, "Messenger body reads must be bounded")
    assert_true("test_facebook_webhook_rejects_oversized_payload" in runtime_tests, "Bottle/WebTest must cover oversized Messenger payloads")
    assert_true("is_json_content_type" in app_source, "Messenger POST requests must require JSON media types")
    assert_true("test_facebook_webhook_rejects_non_json_content_type" in runtime_tests, "Bottle/WebTest must cover non-JSON Messenger payloads")


def test_messenger_post_rejects_oversized_declared_body():
    app, request, response, requests = load_app()
    request.content_length = app.MAX_MESSENGER_WEBHOOK_BYTES + 1

    body = app.messenger_post()

    assert_equal(response.status, 413, "oversized declared Messenger body status")
    assert_equal(body, "payload too large", "oversized declared Messenger body response")
    assert_equal(requests.calls, [], "oversized declared Messenger body must not reply")


def test_messenger_post_rejects_oversized_streamed_body():
    app, request, response, requests = load_app()
    request.content_length = None
    request.body = io.BytesIO(b"x" * (app.MAX_MESSENGER_WEBHOOK_BYTES + 1))

    body = app.messenger_post()

    assert_equal(response.status, 413, "oversized streamed Messenger body status")
    assert_equal(body, "payload too large", "oversized streamed Messenger body response")
    assert_equal(requests.calls, [], "oversized streamed Messenger body must not reply")


def test_messenger_post_rejects_invalid_signature():
    app, request, response, requests = load_app()
    request.headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=invalid",
    }
    request.json = {"object": "page", "entry": []}

    body = app.messenger_post()

    assert_equal(response.status, 403, "invalid Messenger signature status")
    assert_equal(body, "forbidden", "invalid Messenger signature response")
    assert_equal(requests.calls, [], "invalid Messenger signature must not reply")


def test_messenger_post_accepts_json_content_type_parameters():
    app, request, response, requests = load_app()
    request.headers["Content-Type"] = "Application/JSON; charset=UTF-8"
    request.json = {"object": "page", "entry": []}

    body = app.messenger_post()

    assert_equal(response.status, 200, "parameterized JSON Messenger status")
    assert_equal(body, "ok", "parameterized JSON Messenger response")
    assert_equal(requests.calls, [], "empty parameterized JSON event must not reply")


def test_messenger_post_rejects_non_json_content_types_before_authentication():
    for content_type in (None, "text/plain", "application/jsonp", "application/ld+json"):
        app, request, response, requests = load_app()
        request.headers = {"X-Hub-Signature-256": "sha256=invalid"}
        if content_type is not None:
            request.headers["Content-Type"] = content_type
        request.json = {"object": "page", "entry": []}

        body = app.messenger_post()

        assert_equal(response.status, 415, "non-JSON Messenger status {0!r}".format(content_type))
        assert_equal(body, "unsupported media type", "non-JSON Messenger response {0!r}".format(content_type))
        assert_equal(requests.calls, [], "non-JSON Messenger payload must not reply")


def test_messenger_verification_requires_matching_token():
    app, request, response, _requests = load_app()

    request.query = {"hub.challenge": "challenge-1", "hub.verify_token": "wrong"}
    response.status = 200

    body = app.messenger_webhook()

    assert_true(body != "challenge-1", "must not echo challenge for invalid verify token")
    assert_equal(response.status, 403, "invalid verify token status")


def test_messenger_verification_accepts_matching_token():
    app, request, response, _requests = load_app()

    request.query = {"hub.challenge": "challenge-1", "hub.verify_token": "verify-secret"}
    response.status = 200

    body = app.messenger_webhook()

    assert_equal(body, "challenge-1", "valid verify token challenge")
    assert_equal(response.status, 200, "valid verify token status")


def test_messenger_post_ignores_non_message_events():
    app, request, response, requests = load_app()

    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "delivery": {"mids": ["mid-1"]}
            }]
        }]
    }
    response.status = 200

    body = app.messenger_post()

    assert_equal(body, "ok", "non-message event response")
    assert_equal(requests.calls, [], "non-message events must not call messenger reply")


def test_messenger_post_ignores_echoes_and_continues_scanning():
    app, request, response, requests = load_app()
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [
                {
                    "sender": {"id": "page-1"},
                    "message": {"text": "page reply", "is_echo": True}
                },
                {
                    "sender": {"id": "user-1"},
                    "message": {"text": "hello from user"}
                }
            ]
        }]
    }
    response.status = 200

    body = app.messenger_post()

    assert_equal(body, "ok", "Messenger echo event response")
    assert_equal(len(requests.calls), 1, "only the user message should trigger a reply")
    _url, kwargs = requests.calls[0]
    assert_equal(kwargs["json"]["recipient"]["id"], "user-1", "post-echo sender")
    assert_equal(
        kwargs["json"]["message"]["text"],
        "bot: hello from user",
        "post-echo message",
    )


def test_messenger_post_requires_boolean_true_echo_flag():
    app, request, response, requests = load_app()
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "hello", "is_echo": "false"}
            }]
        }]
    }
    response.status = 200

    body = app.messenger_post()

    assert_equal(body, "ok", "non-boolean echo flag response")
    assert_equal(len(requests.calls), 1, "non-boolean echo flag reply count")


def test_messenger_post_ignores_non_text_or_blank_messages():
    invalid_text_values = [None, "", " \t\n", {"text": "hello"}, ["hello"]]
    for text_value in invalid_text_values:
        app, request, response, requests = load_app()
        request.json = {
            "object": "page",
            "entry": [{
                "messaging": [{
                    "sender": {"id": "user-1"},
                    "message": {"text": text_value}
                }]
            }]
        }
        response.status = 200

        body = app.messenger_post()

        assert_equal(body, "ok", "invalid Messenger text event response")
        assert_equal(requests.calls, [], "invalid Messenger text must not call messenger reply")


def test_messenger_post_trims_sender_and_message_text_before_reply():
    app, request, response, requests = load_app()
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": " user-1 "},
                "message": {"text": " hello from messenger "}
            }]
        }]
    }
    response.status = 200

    body = app.messenger_post()

    assert_equal(body, "ok", "trimmed Messenger text event response")
    assert_equal(len(requests.calls), 1, "trimmed Messenger text post count")
    _url, kwargs = requests.calls[0]
    assert_equal(kwargs["json"]["recipient"]["id"], "user-1", "trimmed Messenger sender")
    assert_equal(kwargs["json"]["message"]["text"], "bot: hello from messenger", "trimmed Messenger text")


def test_messenger_post_rejects_invalid_json_shape():
    app, request, response, _requests = load_app()

    request.json = None
    response.status = 200

    body = app.messenger_post()

    assert_equal(response.status, 400, "invalid json status")
    assert_true(body != "ok", "invalid json should not be acknowledged as a valid event")


def test_messenger_post_rejects_non_page_object():
    app, request, response, requests = load_app()

    request.json = {
        "object": "user",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "hello from messenger"}
            }]
        }]
    }
    response.status = 200

    body = app.messenger_post()

    assert_equal(response.status, 400, "non-page Messenger object status")
    assert_true(body != "ok", "non-page Messenger objects must not be acknowledged as valid")
    assert_equal(requests.calls, [], "non-page Messenger objects must not call messenger reply")


def test_messenger_reply_uses_header_auth_and_timeout():
    app, _request, _response, requests = load_app()

    body = app.messenger_reply("user-1", "hello")

    assert_equal(body, b'{"recipient_id": "user-1"}', "messenger reply body")
    assert_equal(len(requests.calls), 1, "messenger reply post count")
    url, kwargs = requests.calls[0]
    assert_true("access_token=" not in url, "access token must not be embedded in URL")
    assert_equal(kwargs.get("timeout"), 5, "messenger request timeout")
    assert_equal(
        kwargs.get("headers", {}).get("Authorization"),
        "Bearer page-token",
        "messenger authorization header",
    )


def test_request_timeout_accepts_positive_float_env():
    assert_equal(
        load_settings_with_request_timeout("2.5"),
        2.5,
        "positive REQUEST_TIMEOUT env",
    )


def test_request_timeout_defaults_for_invalid_env():
    for value in ("not-a-number", "0", "-3", "nan", "inf"):
        try:
            timeout = load_settings_with_request_timeout(value)
        except Exception as exc:
            raise AssertionError(
                "invalid REQUEST_TIMEOUT must not crash settings import: {0}".format(exc)
            )
        assert_equal(timeout, 5.0, "invalid REQUEST_TIMEOUT env {0!r}".format(value))


def test_bot_json_request_rejects_invalid_or_blank_payloads():
    bot, calls = load_bot_module()

    for payload in (None, [], {}, {"data": None}, {"data": ""}, {"data": "   "}, {"data": 12}):
        assert_equal(bot.json_request(payload, None), None, "invalid JSON request payload {0!r}".format(payload))

    assert_equal(calls, [], "invalid JSON request payloads must not call chatback")


def test_bot_json_request_trims_data_before_chatback():
    bot, calls = load_bot_module()

    body = bot.json_request({"data": "  hello valley  "}, None)

    assert_equal(body, "bot: hello valley", "trimmed JSON request response")
    assert_equal(calls, ["hello valley"], "JSON request must trim data before chatback")


def test_web_bot_rejects_missing_chat_query():
    app, request, response, _requests = load_app()

    request.query = {}
    response.status = 200

    body = app.chat()

    assert_equal(response.status, 400, "missing web bot chat status")
    assert_equal(json.loads(body), {"error": "missing chat"}, "missing web bot chat response")


def test_web_bot_rejects_blank_chat_query():
    app, request, response, _requests = load_app()

    request.query = {"chat": "   "}
    response.status = 200

    body = app.chat()

    assert_equal(response.status, 400, "blank web bot chat status")
    assert_equal(json.loads(body), {"error": "missing chat"}, "blank web bot chat response")


def test_web_bot_trims_chat_before_bot_call():
    app, request, response, _requests = load_app()

    request.query = {"chat": "  hello valley  "}
    response.status = 200

    body = app.chat()

    assert_equal(response.status, 200, "trimmed web bot chat status")
    assert_equal(json.loads(body), {"data": "bot: hello valley"}, "trimmed web bot chat response")


def test_web_template_escapes_chat_strings():
    template = (ROOT / "views" / "index.tpl").read_text()

    assert_true(
        "encodeURIComponent(chat)" in template,
        "web chat query must be URL-encoded",
    )
    assert_true(
        ".text(text)" in template,
        "reply text must be inserted as text, not HTML",
    )
    assert_true(
        "appendReply(" in template,
        "web chat replies must share the escaped append helper",
    )
    assert_true(
        " + chat +" not in template,
        "user chat text must not be concatenated into HTML",
    )
    assert_true(
        " + data['data'] +" not in template,
        "bot response text must not be concatenated into HTML",
    )


def test_bot_logging_avoids_private_message_text():
    source = (ROOT / "bot.py").read_text()

    assert_true(
        "logger.setLevel(logging.WARNING)" in source,
        "bot logging must default below raw conversation detail",
    )
    assert_true(
        "logger.info(" not in source,
        "bot logic must not log private message text at info level",
    )
    for phrase in (
        "Chatback: respond to %s",
        "Returning phrase '%s'",
        "Found noun: %s",
        "Pronoun=%s",
    ):
        assert_true(phrase not in source, "bot logs must not include {0}".format(phrase))
    assert_true(
        "logger.debug(\"Chatback: received message\")" in source,
        "bot may keep generic debug traces without message contents",
    )
    assert_true(
        "logger.debug(\"Generated response\")" in source,
        "bot may keep generic response traces without response contents",
    )


def test_filtered_responses_use_reviewed_fallback():
    source = (ROOT / "bot.py").read_text()
    runtime_tests = (ROOT / "bot_tests.py").read_text()

    assert_true("return safe_response(resp)" in source, "respond must pass generated text through the safe response boundary")
    assert_true("except UnacceptableUtteranceException:" in source, "content filter rejections must be contained")
    assert_true("return random.choice(config.NONE_RESPONSES)" in source, "content filter rejections must use reviewed fallback responses")
    assert_true("Generated response rejected by content filter" in source, "content filter rejections must keep a content-free diagnostic")
    assert_true("testFilteredResponseUsesReviewedFallback" in runtime_tests, "runtime tests must cover filtered response fallback")
    assert_true("testAcceptableResponsePassesThroughFilter" in runtime_tests, "runtime tests must cover accepted response passthrough")


def test_slack_command_requires_matching_token():
    app, request, response, _requests = load_app()

    request.forms = {"text": "do you work in finance", "token": "wrong"}
    response.status = 200

    body = app.slack_handler()

    assert_true(body != "bot: do you work in finance", "invalid Slack token response")
    assert_equal(response.status, 403, "invalid Slack token status")


def test_slack_command_accepts_matching_token():
    app, request, response, _requests = load_app()

    request.forms = {"text": "do you work in finance", "token": "slack-secret"}
    response.status = 200

    body = app.slack_handler()

    assert_equal(body, "bot: do you work in finance", "valid Slack token response")
    assert_equal(response.status, 200, "valid Slack token status")


def test_slack_command_rejects_blank_text():
    app, request, response, _requests = load_app()

    request.forms = {"text": "   ", "token": "slack-secret"}
    response.status = 200

    body = app.slack_handler()

    assert_equal(body, "missing text", "blank Slack text response")
    assert_equal(response.status, 400, "blank Slack text status")


def test_slack_command_rejects_non_text_values():
    for text_value in ({"message": "hello"}, b"hello"):
        app, request, response, _requests = load_app()

        request.forms = {"text": text_value, "token": "slack-secret"}
        response.status = 200

        body = app.slack_handler()

        assert_equal(body, "missing text", "non-text Slack text response")
        assert_equal(response.status, 400, "non-text Slack text status")
        assert_equal(sys.modules["bot"].calls, [], "non-text Slack text must not call bot")


def test_slack_command_trims_text_before_bot_call():
    app, request, response, _requests = load_app()

    request.forms = {"text": "  do you work in finance  ", "token": "slack-secret"}
    response.status = 200

    body = app.slack_handler()

    assert_equal(body, "bot: do you work in finance", "trimmed Slack text response")
    assert_equal(response.status, 200, "trimmed Slack text status")


def test_standalone_slack_handler_requires_matching_token():
    slack, bot = load_slack_module()

    body = slack.slack_handler({"text": "do you work in finance", "token": "wrong"})

    assert_equal(body, "forbidden", "standalone invalid Slack token response")
    assert_equal(bot.calls, [], "standalone invalid Slack token must not call bot")


def test_standalone_slack_handler_accepts_matching_token():
    slack, bot = load_slack_module()

    body = slack.slack_handler({"text": "do you work in finance", "token": "slack-secret"})

    assert_equal(body, "bot: do you work in finance", "standalone valid Slack token response")
    assert_equal(bot.calls, ["do you work in finance"], "standalone valid Slack token bot call")


def test_standalone_slack_handler_rejects_blank_text():
    slack, bot = load_slack_module()

    body = slack.slack_handler({"text": "   ", "token": "slack-secret"})

    assert_equal(body, "missing text", "standalone blank Slack text response")
    assert_equal(bot.calls, [], "standalone blank Slack text must not call bot")


def test_standalone_slack_handler_rejects_non_text_values():
    for text_value in ({"message": "hello"}, b"hello"):
        slack, bot = load_slack_module()

        body = slack.slack_handler({"text": text_value, "token": "slack-secret"})

        assert_equal(body, "missing text", "standalone non-text Slack text response")
        assert_equal(bot.calls, [], "standalone non-text Slack text must not call bot")


def main():
    tests = [
        test_completed_plans_are_in_docs_plans,
        test_runtime_and_ci_contracts,
        test_messenger_post_rejects_oversized_declared_body,
        test_messenger_post_rejects_oversized_streamed_body,
        test_messenger_post_rejects_invalid_signature,
        test_messenger_post_accepts_json_content_type_parameters,
        test_messenger_post_rejects_non_json_content_types_before_authentication,
        test_messenger_verification_requires_matching_token,
        test_messenger_verification_accepts_matching_token,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_ignores_echoes_and_continues_scanning,
        test_messenger_post_requires_boolean_true_echo_flag,
        test_messenger_post_ignores_non_text_or_blank_messages,
        test_messenger_post_trims_sender_and_message_text_before_reply,
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_post_rejects_non_page_object,
        test_messenger_reply_uses_header_auth_and_timeout,
        test_request_timeout_accepts_positive_float_env,
        test_request_timeout_defaults_for_invalid_env,
        test_bot_json_request_rejects_invalid_or_blank_payloads,
        test_bot_json_request_trims_data_before_chatback,
        test_web_bot_rejects_missing_chat_query,
        test_web_bot_rejects_blank_chat_query,
        test_web_bot_trims_chat_before_bot_call,
        test_web_template_escapes_chat_strings,
        test_bot_logging_avoids_private_message_text,
        test_filtered_responses_use_reviewed_fallback,
        test_slack_command_requires_matching_token,
        test_slack_command_accepts_matching_token,
        test_slack_command_rejects_blank_text,
        test_slack_command_rejects_non_text_values,
        test_slack_command_trims_text_before_bot_call,
        test_standalone_slack_handler_requires_matching_token,
        test_standalone_slack_handler_accepts_matching_token,
        test_standalone_slack_handler_rejects_blank_text,
        test_standalone_slack_handler_rejects_non_text_values,
    ]
    for test in tests:
        test()
    print("valleybot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
