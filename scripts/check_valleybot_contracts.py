#!/usr/bin/env python3
"""Dependency-free route contract checks for the legacy Bottle app."""
import ast
import base64
import importlib.util
import hashlib
import hmac
import io
import json
import os
import sys
import time
import types
from urllib.parse import urlencode
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
MESSENGER_REPLAY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-messenger-message-replay-guard.md"
)
MESSENGER_BATCH_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-messenger-batch-processing-bound.md"
)
MAKE_ROOT_PROTECTION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-14-make-root-override-protection.md"
)
MODERATION_REVIEW_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-14-moderation-review-guide.md"
)
CODEQL_ANALYSIS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-14-codeql-analysis.md"
)
MESSENGER_CHALLENGE_ESCAPE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-14-messenger-challenge-escaping.md"
)
MAKEFILE_LOCATION_ROOT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-15-makefile-location-root.md"
)
MESSENGER_REPLY_HTTP_STATUS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-15-messenger-reply-http-status.md"
)
MESSENGER_DEBUG_FIELD_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-16-messenger-debug-field.md"
)
SLACK_SIGNING_SECRET_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-16-slack-signing-secret-verification.md"
)
SLACK_REPLAY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-17-slack-request-replay-guard.md"
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


class FakeHttpResponse:
    def __init__(self, error=None):
        self.content = b'{"recipient_id": "user-1"}'
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error


class FakeRequests(types.SimpleNamespace):
    def __init__(self):
        super(FakeRequests, self).__init__()
        self.calls = []
        self.response_error = None

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeHttpResponse(self.response_error)


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
    settings.slack_signing_secret = "slack-signing-secret"
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


def slack_signature(body, timestamp, secret="slack-signing-secret"):
    base = "v0:{0}:{1}".format(timestamp, body).encode("utf-8")
    return "v0=" + hmac.new(
        secret.encode("utf-8"), base, hashlib.sha256
    ).hexdigest()


def configure_slack_request(request, text, timestamp=None, signature=None):
    timestamp = str(int(time.time()) if timestamp is None else timestamp)
    body = urlencode({"text": text})
    request.body = io.BytesIO(body.encode("utf-8"))
    request.forms = {"text": text}
    request.headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": signature or slack_signature(body, timestamp),
    }
    return body, timestamp


def signed_slack_event(text, timestamp="1000", base64_encoded=False):
    body = urlencode({"text": text})
    event_body = (
        base64.b64encode(body.encode("utf-8")).decode("ascii")
        if base64_encoded else body
    )
    return {
        "headers": {
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": slack_signature(body, timestamp),
        },
        "body": event_body,
        "isBase64Encoded": base64_encoded,
    }


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


def registered_main_tests(source):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for statement in node.body:
                if (
                        isinstance(statement, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "tests"
                                for target in statement.targets)
                        and isinstance(statement.value, (ast.List, ast.Tuple))):
                    return {
                        element.id for element in statement.value.elts
                        if isinstance(element, ast.Name)
                    }
    return set()


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
    assert_completed_plan(MESSENGER_REPLAY_PLAN_PATH, "Messenger replay guard")
    assert_completed_plan(MESSENGER_BATCH_PLAN_PATH, "Messenger batch processing bound")
    assert_completed_plan(MAKE_ROOT_PROTECTION_PLAN_PATH, "Make root override protection")
    assert_completed_plan(MODERATION_REVIEW_PLAN_PATH, "moderation review guide")
    assert_completed_plan(CODEQL_ANALYSIS_PLAN_PATH, "CodeQL analysis")
    assert_completed_plan(MESSENGER_CHALLENGE_ESCAPE_PLAN_PATH, "Messenger challenge escaping")
    assert_completed_plan(MAKEFILE_LOCATION_ROOT_PLAN_PATH, "Makefile location root")
    assert_completed_plan(MESSENGER_REPLY_HTTP_STATUS_PLAN_PATH, "Messenger reply HTTP status")
    assert_completed_plan(MESSENGER_DEBUG_FIELD_PLAN_PATH, "Messenger debug field handling")
    assert_completed_plan(SLACK_SIGNING_SECRET_PLAN_PATH, "Slack signing secret")
    assert_completed_plan(SLACK_REPLAY_PLAN_PATH, "Slack request replay guard")
    registered = registered_main_tests(
        (ROOT / "scripts" / "check_valleybot_contracts.py").read_text(encoding="utf-8")
    )
    assert_true(
        "test_slack_replay_source_contracts" in registered,
        "Slack replay source contracts must remain registered",
    )


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
            "name: CodeQL (${{ matrix.language }})",
            "security-events: write",
            "language: [actions, python]",
            "github/codeql-action/init@8aad20d150bbac5944a9f9d289da16a4b0d87c1e",
            "languages: ${{ matrix.language }}",
            "build-mode: none",
            "github/codeql-action/analyze@8aad20d150bbac5944a9f9d289da16a4b0d87c1e",
            "persist-credentials: false",
            "python -m pip install -r requirements.txt",
            "make check PYTHON=python",
            'make -C "$GITHUB_WORKSPACE" check PYTHON=python'):
        assert_true(contract in workflow, "missing CI contract {0}".format(contract))
    assert_true("@v" not in workflow, "CI actions must use immutable commits")
    assert_true("ubuntu-latest" not in workflow, "CI must not use a floating Ubuntu runner")
    assert_true("pull_request_target" not in workflow, "CI must not run untrusted code with target-branch privileges")
    assert_true("branches:" not in workflow, "CI push checks must cover every branch")
    assert_true("# v6.0.3" in workflow, "checkout pin annotation must identify the exact release")
    assert_true("# v6.2.0" in workflow, "setup-python pin annotation must identify the exact release")
    assert_equal(workflow.count("persist-credentials:"), 2, "checkout credential setting count")
    assert_true("persist-credentials: true" not in workflow, "checkout credentials must not persist")
    assert_equal(workflow.count("security-events: write"), 1, "CodeQL upload permission count")

    action_uses = []
    for line in workflow.splitlines():
        action_line = line.strip()
        if action_line.startswith("- "):
            action_line = action_line[2:]
        if action_line.startswith("uses: "):
            action_uses.append(action_line)
    assert_equal(len(action_uses), 5, "CI action count")
    assert_equal(
        set(action_uses),
        {
            "uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3",
            "uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0",
            "uses: github/codeql-action/init@8aad20d150bbac5944a9f9d289da16a4b0d87c1e # v4",
            "uses: github/codeql-action/analyze@8aad20d150bbac5944a9f9d289da16a4b0d87c1e # v4",
        },
        "CI action allowlist",
    )
    assert_equal(
        action_uses.count(
            "uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3"
        ),
        2,
        "credential-free checkout job count",
    )
    workflow_files = list((ROOT / ".github" / "workflows").glob("*.y*ml"))
    assert_equal(workflow_files, [CI_WORKFLOW_PATH], "CI workflow file set")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert_true("GitHub Actions" in readme, "README must document the GitHub Actions check")
    assert_true("Actions and Python" in readme, "README must document CodeQL languages")
    assert_true("security-events: write" in readme, "README must document scoped CodeQL upload permission")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert_true("!.github/workflows/check.yml" in gitignore, "workflow file must not be hidden by dotfile ignores")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    for security_contract in ("X-Hub-Signature-256", "MESSENGER_APP_SECRET", "1 MiB"):
        assert_true(security_contract in security, "SECURITY.md must document {0}".format(security_contract))
    assert_true("CodeQL analyzes GitHub Actions and Python" in security, "SECURITY.md must document CodeQL coverage")
    vision = (ROOT / "VISION.md").read_text(encoding="utf-8")
    assert_true("Keep pinned CodeQL coverage" in vision, "VISION.md must preserve CodeQL coverage")
    changes = (ROOT / "CHANGES.md").read_text(encoding="utf-8")
    assert_true("least-privilege CodeQL analysis" in changes, "CHANGES.md must record CodeQL analysis")
    codeql_plan = CODEQL_ANALYSIS_PLAN_PATH.read_text(encoding="utf-8")
    for plan_contract in (
            "The repository and external-directory `make check` passed.",
            "Four hostile CodeQL workflow mutations were rejected"):
        assert_true(plan_contract in codeql_plan, "CodeQL plan must record {0}".format(plan_contract))
    challenge_plan = MESSENGER_CHALLENGE_ESCAPE_PLAN_PATH.read_text(encoding="utf-8")
    for plan_contract in (
            "The repository and external-directory `make check` passed.",
            "hostile source mutation that restored the raw challenge return was"):
        assert_true(plan_contract in challenge_plan, "challenge plan must record {0}".format(plan_contract))
    assert_true("HTML-escaped before response delivery" in readme, "README must document challenge escaping")
    assert_true("valid verification token cannot reflect executable markup" in security, "SECURITY.md must document challenge escaping")
    assert_true("Escape verified Messenger challenge responses" in vision, "VISION.md must preserve challenge escaping")
    assert_true("reflected-XSS" in changes, "CHANGES.md must record challenge escaping")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    makefile_lines = set(makefile.splitlines())
    assert_true(
        "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))"
        in makefile_lines,
        "Makefile must protect the loaded Makefile directory as the repository root",
    )
    assert_true("$(CURDIR)" not in makefile, "Makefile root must not trust the caller directory")
    assert_true("PYTHON ?= python3" in makefile_lines, "Makefile must preserve the Python command override")
    assert_true('find "$(ROOT)"' in makefile, "Makefile cleanup must stay inside the repository")
    assert_true('"$(ROOT)/scripts/check_valleybot_contracts.py"' in makefile, "Makefile must use the rooted contract path")
    assert_true('$(MAKE) -C "$(ROOT)" clean' in makefile, "recursive cleanup must select the repository directory")

    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")
    assert_true("debug(True)" not in app_source, "Bottle debug mode must not be enabled by default")
    assert_true("verify_messenger_signature" in app_source, "Messenger POST signatures must remain required")
    assert_true("MAX_MESSENGER_WEBHOOK_BYTES = 1024 * 1024" in app_source, "Messenger webhook size limit must remain 1 MiB")
    assert_true("request.body.read(MAX_MESSENGER_WEBHOOK_BYTES + 1)" in app_source, "Messenger body reads must be bounded")
    assert_true("test_facebook_webhook_rejects_oversized_payload" in runtime_tests, "Bottle/WebTest must cover oversized Messenger payloads")
    assert_true("is_json_content_type" in app_source, "Messenger POST requests must require JSON media types")
    assert_true("test_facebook_webhook_rejects_non_json_content_type" in runtime_tests, "Bottle/WebTest must cover non-JSON Messenger payloads")
    assert_true("from html import escape" in app_source, "Messenger challenge responses must use standard HTML escaping")
    assert_true("return escape(challenge, quote=True)" in app_source, "verified Messenger challenges must be escaped")
    assert_true("test_facebook_challenge_escapes_reflected_markup" in runtime_tests, "Bottle/WebTest must cover reflected challenge markup")
    assert_true(
        "test_facebook_challenge_requires_subscribe_mode" in runtime_tests,
        "Bottle/WebTest must cover Messenger verification mode",
    )
    assert_true("test_messenger_verification_escapes_reflected_markup" in Path(__file__).read_text(encoding="utf-8"), "dependency-free contracts must cover reflected challenge markup")


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

    request.query = {
        "hub.challenge": "challenge-1",
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong",
    }
    response.status = 200

    body = app.messenger_webhook()

    assert_true(body != "challenge-1", "must not echo challenge for invalid verify token")
    assert_equal(response.status, 403, "invalid verify token status")


def test_messenger_verification_accepts_matching_token():
    app, request, response, _requests = load_app()

    request.query = {
        "hub.challenge": "challenge-1",
        "hub.mode": "subscribe",
        "hub.verify_token": "verify-secret",
    }
    response.status = 200

    body = app.messenger_webhook()

    assert_equal(body, "challenge-1", "valid verify token challenge")
    assert_equal(response.status, 200, "valid verify token status")


def test_messenger_verification_escapes_reflected_markup():
    app, request, response, _requests = load_app()

    request.query = {
        "hub.challenge": '<script>alert("xss")</script>',
        "hub.mode": "subscribe",
        "hub.verify_token": "verify-secret",
    }
    response.status = 200

    body = app.messenger_webhook()

    assert_equal(
        body,
        "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;",
        "verified challenge markup must be escaped",
    )
    assert_equal(response.status, 200, "escaped challenge status")


def test_messenger_verification_requires_exact_subscribe_mode():
    for mode in (None, "", "Subscribe", "unsubscribe", " subscribe "):
        app, request, response, _requests = load_app()
        request.query = {
            "hub.challenge": "challenge-1",
            "hub.verify_token": "verify-secret",
        }
        if mode is not None:
            request.query["hub.mode"] = mode
        response.status = 200

        body = app.messenger_webhook()

        assert_equal(response.status, 400, "invalid verification mode status {0!r}".format(mode))
        assert_true(body != "challenge-1", "invalid verification mode must not reflect challenge")


def test_messenger_verification_mode_source_contracts():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")
    checker_source = Path(__file__).read_text(encoding="utf-8")
    plan = (ROOT / "docs" / "plans" / "2026-06-16-messenger-verification-mode.md").read_text(
        encoding="utf-8"
    )

    for contract in (
        'verification_mode = request.query.get("hub.mode")',
        'if verification_mode != "subscribe":',
        'return "invalid mode"',
    ):
        assert_true(contract in source, "missing Messenger verification mode contract {0}".format(contract))

    token_check = source.index("if not secure_compare(verify_token, expected_token):")
    mode_check = source.index('if verification_mode != "subscribe":')
    challenge_check = source.index("if not challenge:")
    challenge_return = source.index("return escape(challenge, quote=True)")
    assert_true(
        token_check < mode_check < challenge_check < challenge_return,
        "Messenger verification must authenticate, validate mode, validate challenge, then escape",
    )

    assert_true(
        "test_facebook_challenge_requires_subscribe_mode" in runtime_tests,
        "Bottle/WebTest must retain invalid Messenger mode coverage",
    )
    assert_true(
        "test_messenger_verification_requires_exact_subscribe_mode"
        in registered_main_tests(checker_source),
        "dependency-free Messenger mode coverage must remain registered",
    )
    guidance = "Messenger GET verification requires the exact `subscribe` mode"
    for relative_path in ("README.md", "SECURITY.md", "VISION.md", "CHANGES.md"):
        document = (ROOT / relative_path).read_text(encoding="utf-8")
        assert_true(guidance in document, "{0} must document exact Messenger mode".format(relative_path))
    for contract in (
        "Status: Completed",
        "test_messenger_verification_requires_exact_subscribe_mode",
        "repository and external-directory `make check` passed",
        "hostile mutations were rejected",
    ):
        assert_true(contract in plan, "verification-mode plan must keep {0}".format(contract))


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


def messenger_payload(message_id="mid-1"):
    message = {"text": "hello from messenger"}
    if message_id is not None:
        message["mid"] = message_id
    return {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": message,
            }]
        }]
    }


def messenger_batch_payload(events, debug=False):
    payload = {
        "object": "page",
        "entry": [{"messaging": events}],
    }
    if debug:
        payload["debug"] = True
    return payload


def messenger_event(sender, text, message_id=None, is_echo=False):
    message = {"text": text}
    if message_id is not None:
        message["mid"] = message_id
    if is_echo:
        message["is_echo"] = True
    return {"sender": {"id": sender}, "message": message}


def test_messenger_post_processes_valid_batch_in_payload_order():
    app, request, _response, requests = load_app()
    request.json = messenger_batch_payload([
        messenger_event("user-1", "first", "mid-batch-1"),
        messenger_event("page", "echo", "mid-echo", is_echo=True),
        {"sender": ["malformed"], "message": {"text": "ignored"}},
        {"sender": {"id": "ignored"}, "message": ["malformed"]},
        messenger_event("user-2", "second", "mid-batch-2"),
    ])

    assert_equal(app.messenger_post(), "ok", "ordered Messenger batch response")
    assert_equal(len(requests.calls), 2, "ordered Messenger batch reply count")
    assert_equal(
        [call[1]["json"]["recipient"]["id"] for call in requests.calls],
        ["user-1", "user-2"],
        "ordered Messenger batch recipients",
    )


def test_messenger_post_caps_valid_batch():
    app, request, _response, requests = load_app()
    request.json = messenger_batch_payload([
        messenger_event(
            "user-{0}".format(index),
            "message-{0}".format(index),
            "mid-cap-{0}".format(index),
        )
        for index in range(app.MAX_MESSENGER_MESSAGES_PER_WEBHOOK + 1)
    ])

    assert_equal(app.messenger_post(), "ok", "capped Messenger batch response")
    assert_equal(
        len(requests.calls),
        app.MAX_MESSENGER_MESSAGES_PER_WEBHOOK,
        "capped Messenger batch reply count",
    )
    assert_equal(
        requests.calls[-1][1]["json"]["recipient"]["id"],
        "user-19",
        "capped Messenger batch final recipient",
    )


def test_messenger_post_applies_replay_claims_per_batch_message():
    app, request, _response, requests = load_app()
    request.json = messenger_batch_payload([
        messenger_event("user-1", "first", "mid-same"),
        messenger_event("user-2", "duplicate", "mid-same"),
        messenger_event("user-3", "without id"),
    ])

    app.messenger_post()

    assert_equal(len(requests.calls), 2, "batch replay and ID-less reply count")
    assert_equal(
        [call[1]["json"]["recipient"]["id"] for call in requests.calls],
        ["user-1", "user-3"],
        "batch replay and ID-less recipients",
    )


def test_messenger_post_debug_field_does_not_suppress_replies():
    app, request, _response, requests = load_app()
    request.json = messenger_batch_payload([
        messenger_event("user-1", "first", "mid-debug-1"),
        messenger_event("user-2", "second", "mid-debug-2"),
    ], debug=True)

    app.messenger_post()

    assert_equal(len(requests.calls), 2, "debug-field Messenger batch reply count")


def test_messenger_debug_field_source_contracts():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")
    checker_source = Path(__file__).read_text(encoding="utf-8")

    assert_true(
        "data.get('debug')" not in source and 'data.get("debug")' not in source,
        "Messenger request bodies must not control reply suppression",
    )
    assert_true(
        "test_facebook_debug_field_does_not_suppress_reply" in runtime_tests,
        "Bottle/WebTest must cover client-controlled debug fields",
    )
    assert_true(
        "test_messenger_post_debug_field_does_not_suppress_replies"
        in registered_main_tests(checker_source),
        "dependency-free debug-field coverage must remain registered",
    )

    docs = {
        "README.md": "Unknown top-level Messenger fields cannot suppress valid replies",
        "SECURITY.md": "Unknown top-level fields, including `debug`, do not suppress valid Messenger replies",
        "VISION.md": "Keep Messenger reply behavior independent of client-controlled debug fields",
        "CHANGES.md": "Removed the client-controlled Messenger `debug` reply bypass",
    }
    for relative_path, phrase in docs.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(encoding="utf-8"),
            "{0} must document Messenger debug-field handling".format(relative_path),
        )


def test_messenger_post_releases_only_failing_batch_claim():
    app, request, _response, _requests = load_app()
    request.json = messenger_batch_payload([
        messenger_event("user-1", "first", "mid-success"),
        messenger_event("user-2", "second", "mid-failure"),
    ])

    def fail_second(sender, _message):
        if sender == "user-2":
            raise RuntimeError("provider unavailable")

    app.messenger_reply = fail_second
    try:
        app.messenger_post()
        raise AssertionError("failed batch reply must propagate")
    except RuntimeError:
        pass

    assert_true(
        not app.recent_messenger_message_ids.claim("mid-success"),
        "successful earlier batch claim must remain protected",
    )
    assert_true(
        app.recent_messenger_message_ids.claim("mid-failure"),
        "failing batch claim must be released",
    )


def test_messenger_post_suppresses_replayed_message_ids():
    app, request, _response, requests = load_app()
    request.json = messenger_payload("mid-replayed")

    assert_equal(app.messenger_post(), "ok", "first Messenger delivery")
    assert_equal(app.messenger_post(), "ok", "replayed Messenger delivery")

    assert_equal(len(requests.calls), 1, "replayed message ID must send one reply")


def test_messenger_post_preserves_messages_without_ids():
    app, request, _response, requests = load_app()
    request.json = messenger_payload(None)

    app.messenger_post()
    app.messenger_post()

    assert_equal(len(requests.calls), 2, "messages without IDs must preserve compatibility")


def test_recent_message_ids_evicts_oldest_claims_at_bound():
    app, _request, _response, _requests = load_app()
    recent = app.RecentMessageIds(2)

    assert_true(recent.claim("mid-1"), "first replay claim")
    assert_true(recent.claim("mid-2"), "second replay claim")
    assert_true(recent.claim("mid-3"), "third replay claim")
    assert_true(not recent.claim("mid-3"), "newest replay claim must remain protected")
    assert_true(recent.claim("mid-1"), "oldest replay claim must be evicted")


def test_messenger_post_releases_claim_when_reply_fails():
    app, request, _response, _requests = load_app()
    request.json = messenger_payload("mid-retry")
    reply_calls = []

    def failing_reply(sender, message):
        reply_calls.append((sender, message))
        raise RuntimeError("provider unavailable")

    app.messenger_reply = failing_reply
    try:
        app.messenger_post()
        raise AssertionError("failed Messenger replies must propagate")
    except RuntimeError:
        pass

    app.messenger_reply = lambda sender, message: reply_calls.append((sender, message))
    assert_equal(app.messenger_post(), "ok", "retry after Messenger reply failure")
    assert_equal(len(reply_calls), 2, "failed claim must be released for retry")


def test_messenger_post_ignores_malformed_message_ids_for_compatibility():
    app, request, _response, requests = load_app()
    request.json = messenger_payload({"not": "text"})

    app.messenger_post()
    app.messenger_post()

    assert_equal(len(requests.calls), 2, "malformed IDs must not suppress valid text messages")


def test_messenger_replay_source_contracts():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    for contract in (
            "MAX_RECENT_MESSENGER_MESSAGE_IDS = 1024",
            "class RecentMessageIds(object):",
            "self._lock = threading.Lock()",
            "self._ids.popitem(last=False)",
            "message_id = message.get('mid')",
            "recent_messenger_message_ids.claim(message_id)",
            "recent_messenger_message_ids.release(message_id)"):
        assert_true(contract in source, "missing Messenger replay contract {0}".format(contract))

    claim_position = source.index("recent_messenger_message_ids.claim(message_id)")
    reply_position = source.index("messenger_reply(sender, message)")
    release_position = source.index("recent_messenger_message_ids.release(message_id)")
    assert_true(claim_position < reply_position < release_position, "claim, reply, and failure release must stay ordered")


def test_messenger_batch_source_contracts():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")
    for contract in (
            "MAX_MESSENGER_MESSAGES_PER_WEBHOOK = 20",
            "messages = parse_messenger_messages(data)",
            "for sender, message, message_id in messages:",
            "if not isinstance(sender, dict) or not isinstance(message, dict):",
            "messages.append((sender_id, message_text, message_id or None))",
            "if len(messages) >= MAX_MESSENGER_MESSAGES_PER_WEBHOOK:",
            "return messages"):
        assert_true(contract in source, "missing Messenger batch contract {0}".format(contract))
    assert_true(
        "return sender_id, message_text, message_id or None" not in source,
        "Messenger parser must not regress to first-message return semantics",
    )
    for test_name in (
            "test_facebook_webhook_replies_to_valid_messages_in_order",
            "test_facebook_webhook_caps_valid_message_batch"):
        assert_true(test_name in runtime_tests, "missing Bottle/WebTest batch coverage {0}".format(test_name))

    parse_position = source.index("messages = parse_messenger_messages(data)")
    loop_position = source.index("for sender, message, message_id in messages:")
    claim_position = source.index("recent_messenger_message_ids.claim(message_id)", loop_position)
    reply_position = source.index("messenger_reply(sender, message)", loop_position)
    release_position = source.index("recent_messenger_message_ids.release(message_id)", loop_position)
    assert_true(
        parse_position < loop_position < claim_position < reply_position < release_position,
        "bounded extraction and per-message claim, reply, and release must stay ordered",
    )

    docs = {
        "README.md": "Signed webhook batches process up to 20",
        "SECURITY.md": "Each signed webhook processes at most 20",
        "VISION.md": "Process Messenger message batches in order",
        "CHANGES.md": "Processed up to 20 valid Messenger user messages",
    }
    for relative_path, phrase in docs.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(encoding="utf-8"),
            "{0} must document bounded Messenger batches".format(relative_path),
        )


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


def test_messenger_post_releases_claim_after_provider_http_error():
    app, request, _response, requests = load_app()
    request.json = messenger_payload("mid-provider-http-error")
    requests.response_error = RuntimeError("provider rejected reply")

    try:
        app.messenger_post()
        raise AssertionError("Messenger provider HTTP errors must propagate")
    except RuntimeError as exc:
        assert_equal(str(exc), "provider rejected reply", "provider HTTP error")

    requests.response_error = None
    assert_equal(app.messenger_post(), "ok", "retry after provider HTTP error")
    assert_equal(len(requests.calls), 2, "provider HTTP error must release replay claim")


def test_messenger_reply_http_status_source_contracts():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")
    reply_start = source.index("def messenger_reply")
    reply_end = source.index("# WEB BOT INTEGRATION", reply_start)
    reply_source = source[reply_start:reply_end]
    post_position = reply_source.index("requests.post(")
    status_position = reply_source.index("resp.raise_for_status()")
    return_position = reply_source.index("return resp.content")
    assert_true(
        post_position < status_position < return_position,
        "Messenger reply must reject provider HTTP errors before returning content",
    )
    assert_true(
        "test_facebook_response_raises_for_http_error" in runtime_tests,
        "Bottle/WebTest suite must cover Messenger provider HTTP errors",
    )

    docs = {
        "README.md": "Unsuccessful provider HTTP responses raise",
        "SECURITY.md": "Provider HTTP errors propagate",
        "VISION.md": "Fail Messenger replies on provider HTTP errors",
        "CHANGES.md": "Rejected unsuccessful Messenger provider responses",
    }
    for relative_path, phrase in docs.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(encoding="utf-8"),
            "{0} must document Messenger provider HTTP failures".format(relative_path),
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


def test_moderation_review_guide_is_auditable():
    guide = (ROOT / "MODERATION.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    vision = (ROOT / "VISION.md").read_text(encoding="utf-8")
    changes = (ROOT / "CHANGES.md").read_text(encoding="utf-8")

    for phrase in (
            "human content review",
            "not a complete moderation system",
            "protected-class stereotypes",
            "record the rationale",
            "reviewed value from `config.NONE_RESPONSES`",
            "accepted-boundary and rejected-boundary regression fixtures",
            "web, Slack, Messenger, terminal",
            "Never add real conversation transcripts",
            "reviewer, review date, changed content scope",
            "unresolved harmful-content concerns block merge"):
        assert_true(phrase in guide, "moderation guide must include {0}".format(phrase))
    assert_true("See `MODERATION.md`" in readme, "README must link the moderation guide")
    assert_true("docs/plans/2026-06-14-moderation-review-guide.md" in readme, "README must link the moderation plan")
    assert_true("Require auditable human review" in vision, "VISION must preserve moderation review")
    assert_true("mandatory human moderation checklist" in changes, "CHANGES must record moderation guide")


def test_slack_command_requires_valid_signature():
    app, request, response, _requests = load_app()

    configure_slack_request(
        request,
        "do you work in finance",
        signature="v0=" + ("0" * 64),
    )
    response.status = 200

    body = app.slack_handler()

    assert_true(body != "bot: do you work in finance", "invalid Slack signature response")
    assert_equal(response.status, 403, "invalid Slack signature status")
    assert_equal(sys.modules["bot"].calls, [], "invalid signature must not call bot")


def test_slack_command_accepts_valid_signature():
    app, request, response, _requests = load_app()

    configure_slack_request(request, "do you work in finance")
    response.status = 200

    body = app.slack_handler()

    assert_equal(body, "bot: do you work in finance", "valid Slack signature response")
    assert_equal(response.status, 200, "valid Slack signature status")


def test_slack_command_suppresses_replayed_signature():
    app, request, response, _requests = load_app()
    configure_slack_request(request, "replayed command", timestamp=int(time.time()))

    first = app.slack_handler()
    second = app.slack_handler()

    assert_equal(first, "bot: replayed command", "first Slack replay response")
    assert_equal(second, "ok", "duplicate Slack replay acknowledgement")
    assert_equal(sys.modules["bot"].calls, ["replayed command"], "duplicate Slack bot calls")
    assert_equal(response.status, 200, "duplicate Slack replay status")


def test_slack_command_releases_replay_claim_after_failure():
    app, request, _response, _requests = load_app()
    configure_slack_request(request, "retry command", timestamp=int(time.time()))
    original_respond = sys.modules["bot"].respond

    def fail(_text):
        raise RuntimeError("bot failed")

    sys.modules["bot"].respond = fail
    try:
        app.slack_handler()
        raise AssertionError("Slack bot failures must propagate")
    except RuntimeError:
        pass
    finally:
        sys.modules["bot"].respond = original_respond

    assert_equal(app.slack_handler(), "bot: retry command", "Slack retry after bot failure")


def test_slack_command_rejects_blank_text():
    app, request, response, _requests = load_app()

    configure_slack_request(request, "   ")
    response.status = 200

    body = app.slack_handler()

    assert_equal(body, "missing text", "blank Slack text response")
    assert_equal(response.status, 400, "blank Slack text status")


def test_slack_command_rejects_non_text_values():
    for text_value in ({"message": "hello"}, b"hello"):
        app, request, response, _requests = load_app()

        configure_slack_request(request, "placeholder")
        request.forms = {"text": text_value}
        response.status = 200

        body = app.slack_handler()

        assert_equal(body, "missing text", "non-text Slack text response")
        assert_equal(response.status, 400, "non-text Slack text status")
        assert_equal(sys.modules["bot"].calls, [], "non-text Slack text must not call bot")


def test_slack_command_trims_text_before_bot_call():
    app, request, response, _requests = load_app()

    configure_slack_request(request, "  do you work in finance  ")
    response.status = 200

    body = app.slack_handler()

    assert_equal(body, "bot: do you work in finance", "trimmed Slack text response")
    assert_equal(response.status, 200, "trimmed Slack text status")


def test_slack_command_rejects_stale_and_future_timestamps():
    for timestamp in (int(time.time()) - 301, int(time.time()) + 1):
        app, request, response, _requests = load_app()
        body, timestamp_text = configure_slack_request(
            request, "do you work in finance", timestamp=timestamp
        )
        request.headers["X-Slack-Signature"] = slack_signature(
            body, timestamp_text
        )
        response.status = 200

        result = app.slack_handler()

        assert_equal(result, "forbidden", "stale/future Slack response")
        assert_equal(response.status, 403, "stale/future Slack status")
        assert_equal(sys.modules["bot"].calls, [], "stale/future request must not call bot")


def test_slack_handlers_reject_oversized_bodies():
    app, request, response, _requests = load_app()
    request.content_length = app.MAX_SLACK_REQUEST_BYTES + 1
    request.body = io.BytesIO(b"x")

    body = app.slack_handler()

    assert_equal(body, "payload too large", "oversized Bottle Slack response")
    assert_equal(response.status, 413, "oversized Bottle Slack status")
    assert_equal(sys.modules["bot"].calls, [], "oversized Bottle Slack request must not call bot")

    slack, bot = load_slack_module()
    oversized = "é" * 600000
    event = {
        "headers": {
            "X-Slack-Request-Timestamp": "1000",
            "X-Slack-Signature": slack_signature(oversized, "1000"),
        },
        "body": oversized,
        "isBase64Encoded": False,
    }

    assert_equal(slack.slack_handler(event, now=1000), "payload too large", "oversized event Slack response")
    assert_equal(bot.calls, [], "oversized event Slack request must not call bot")

    max_encoded_length = ((app.MAX_SLACK_REQUEST_BYTES + 2) // 3) * 4
    oversized_base64_event = {
        "headers": {},
        "body": "A" * (max_encoded_length + 1),
        "isBase64Encoded": True,
    }
    assert_equal(
        slack.slack_handler(oversized_base64_event, now=1000),
        "payload too large",
        "oversized encoded Slack response",
    )


def test_slack_signature_verifier_rejects_tampering_and_invalid_metadata():
    from slack_auth import verify_slack_request

    body = b"text=hello"
    timestamp = "1000"
    signature = slack_signature(body.decode("ascii"), timestamp)
    assert_true(
        verify_slack_request(
            body, timestamp, signature, "slack-signing-secret", now=1000
        ),
        "valid Slack signature",
    )
    candidates = (
        (b"text=tampered", timestamp, signature, "slack-signing-secret"),
        (body, "not-a-time", signature, "slack-signing-secret"),
        (body, "+1000", signature, "slack-signing-secret"),
        (body, " 1000", signature, "slack-signing-secret"),
        (body, "1001", slack_signature("text=hello", "1001"), "slack-signing-secret"),
        (body, "699", slack_signature("text=hello", "699"), "slack-signing-secret"),
        (body, timestamp, signature, ""),
        (body, timestamp, "invalid", "slack-signing-secret"),
    )
    for candidate in candidates:
        assert_true(
            not verify_slack_request(*candidate, now=1000),
            "invalid Slack signature metadata must fail closed",
        )


def test_slack_signing_secret_source_contracts():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    adapter_source = (ROOT / "slack.py").read_text(encoding="utf-8")
    auth_source = (ROOT / "slack_auth.py").read_text(encoding="utf-8")
    settings_source = (ROOT / "settings.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "bot_tests.py").read_text(encoding="utf-8")

    for contract in (
            'SLACK_SIGNATURE_VERSION = "v0"',
            "SLACK_REQUEST_MAX_AGE_SECONDS = 5 * 60",
            "if not timestamp.isdigit()",
            'version = SLACK_SIGNATURE_VERSION.encode("ascii")',
            'base = version + b":" + timestamp_bytes + b":" + raw_body',
            'expected = SLACK_SIGNATURE_VERSION + "="',
            "hmac.compare_digest(signature, expected)"):
        assert_true(contract in auth_source, "missing Slack auth contract {0}".format(contract))
    assert_true("request_time > current_time" in auth_source, "future Slack timestamps must fail")
    assert_true("current_time - request_time > SLACK_REQUEST_MAX_AGE_SECONDS" in auth_source, "stale Slack timestamps must fail")
    assert_true("request.body.read(MAX_SLACK_REQUEST_BYTES + 1)" in app_source, "Bottle Slack auth must bound the raw body")
    assert_true(app_source.index("request.body.read(MAX_SLACK_REQUEST_BYTES + 1)") < app_source.index("request.forms.get('text')"), "Bottle Slack auth must precede form parsing")
    assert_true("base64.b64decode(body, validate=True)" in adapter_source, "event Slack auth must decode declared base64 bodies")
    assert_true("parse_qs(raw_body.decode(\"utf-8\")" in adapter_source, "event Slack handler must parse the verified body")
    assert_true("SLACK_TOKEN" not in settings_source, "deprecated Slack token configuration must be removed")
    assert_true("slack_token" not in app_source + adapter_source, "Slack token fallback must not remain")
    assert_true("test_slack_rejects_bad_signature_without_bot_call" in runtime_tests, "Bottle runtime tests must cover signature rejection")

    for path in ("AGENTS.md", "README.md", "SECURITY.md", "VISION.md", "CHANGES.md"):
        content = (ROOT / path).read_text(encoding="utf-8")
        assert_true("Slack signing secret" in content, "{0} must document Slack signing secret verification".format(path))

    plan = SLACK_SIGNING_SECRET_PLAN_PATH.read_text(encoding="utf-8")
    for evidence in (
            "status: completed",
            "complete dependency-free suite passed with 60 tests",
            "complete pinned Bottle/WebTest suite passed with 34 tests",
            "repository and external-directory `make verify` passed",
            "Ten isolated hostile mutations were rejected"):
        assert_true(evidence in plan, "Slack signing-secret plan must record {0}".format(evidence))


def test_standalone_slack_handler_requires_valid_signature():
    slack, bot = load_slack_module()
    event = signed_slack_event("do you work in finance")
    event["headers"]["X-Slack-Signature"] = "v0=" + ("0" * 64)

    body = slack.slack_handler(event, now=1000)

    assert_equal(body, "forbidden", "standalone invalid Slack signature response")
    assert_equal(bot.calls, [], "standalone invalid signature must not call bot")


def test_standalone_slack_handler_accepts_valid_signature():
    slack, bot = load_slack_module()

    body = slack.slack_handler(
        signed_slack_event("do you work in finance"), now=1000
    )

    assert_equal(body, "bot: do you work in finance", "standalone valid Slack signature response")
    assert_equal(bot.calls, ["do you work in finance"], "standalone valid Slack signature bot call")


def test_standalone_slack_handler_suppresses_replayed_signature():
    slack, bot = load_slack_module()
    event = signed_slack_event("replayed command")

    first = slack.slack_handler(event, now=1000)
    second = slack.slack_handler(event, now=1000)

    assert_equal(first, "bot: replayed command", "standalone first replay response")
    assert_equal(second, "ok", "standalone duplicate replay acknowledgement")
    assert_equal(bot.calls, ["replayed command"], "standalone duplicate bot calls")


def test_standalone_slack_handler_releases_replay_claim_after_failure():
    slack, bot = load_slack_module()
    event = signed_slack_event("retry command")
    original_respond = bot.respond

    def fail(_text):
        raise RuntimeError("bot failed")

    bot.respond = fail
    try:
        slack.slack_handler(event, now=1000)
        raise AssertionError("standalone Slack bot failures must propagate")
    except RuntimeError:
        pass
    finally:
        bot.respond = original_respond

    assert_equal(
        slack.slack_handler(event, now=1000),
        "bot: retry command",
        "standalone Slack retry after bot failure",
    )


def test_recent_slack_signatures_evicts_oldest_claim():
    from slack_replay import RecentSlackSignatures

    recent = RecentSlackSignatures(2)
    assert_true(recent.claim("first"), "first Slack signature claim")
    assert_true(recent.claim("second"), "second Slack signature claim")
    assert_true(not recent.claim("first"), "duplicate Slack signature claim")
    assert_true(recent.claim("third"), "third Slack signature claim")
    assert_true(recent.claim("first"), "evicted Slack signature can be reclaimed")


def test_slack_replay_source_contracts():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    adapter_source = (ROOT / "slack.py").read_text(encoding="utf-8")
    replay_source = (ROOT / "slack_replay.py").read_text(encoding="utf-8")

    for contract in (
            "MAX_RECENT_SLACK_SIGNATURES = 1024",
            "class RecentSlackSignatures(object):",
            "with self._lock:",
            "while len(self._signatures) > self.max_entries:",
            "self._signatures.popitem(last=False)"):
        assert_true(contract in replay_source, "missing Slack replay contract {0}".format(contract))

    for source, label in ((app_source, "Bottle"), (adapter_source, "event")):
        verify_position = source.index("if not verify_slack_request(")
        text_position = source.index("command_text = clean_text_value", verify_position)
        claim_position = source.index("recent_slack_signatures.claim(slack_signature)", text_position)
        bot_position = source.index("bot.respond(command_text)", claim_position)
        release_position = source.index("recent_slack_signatures.release(slack_signature)", bot_position)
        assert_true(
            verify_position < text_position < claim_position < bot_position < release_position,
            "{0} Slack replay claim and release ordering".format(label),
        )
        assert_true(
            'return "ok"' in source[claim_position:bot_position],
            "{0} duplicate acknowledgement".format(label),
        )

    registered = registered_main_tests(
        (ROOT / "scripts" / "check_valleybot_contracts.py").read_text(encoding="utf-8")
    )
    for test_name in (
            "test_slack_command_suppresses_replayed_signature",
            "test_slack_command_releases_replay_claim_after_failure",
            "test_standalone_slack_handler_suppresses_replayed_signature",
            "test_standalone_slack_handler_releases_replay_claim_after_failure",
            "test_recent_slack_signatures_evicts_oldest_claim",
            "test_slack_replay_source_contracts"):
        assert_true(test_name in registered, "Slack replay test must remain registered: {0}".format(test_name))

    docs = {
        "README.md": "bounded process-local Slack signature claims",
        "SECURITY.md": "Bounded process-local Slack signature claims",
        "VISION.md": "Suppress repeated Slack signatures with bounded process-local state",
        "CHANGES.md": "Suppressed repeated Slack signatures in each running process",
    }
    for relative_path, phrase in docs.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(encoding="utf-8"),
            "{0} must document Slack replay suppression".format(relative_path),
        )


def test_standalone_slack_handler_rejects_blank_text():
    slack, bot = load_slack_module()

    body = slack.slack_handler(signed_slack_event("   "), now=1000)

    assert_equal(body, "missing text", "standalone blank Slack text response")
    assert_equal(bot.calls, [], "standalone blank Slack text must not call bot")


def test_standalone_slack_handler_rejects_missing_text():
    slack, bot = load_slack_module()
    body_text = "command=%2Fvalleybot"
    event = signed_slack_event("placeholder")
    event["body"] = body_text
    event["headers"]["X-Slack-Signature"] = slack_signature(
        body_text, "1000"
    )

    body = slack.slack_handler(event, now=1000)

    assert_equal(body, "missing text", "standalone missing Slack text response")
    assert_equal(bot.calls, [], "standalone missing Slack text must not call bot")


def test_standalone_slack_handler_accepts_signed_base64_body():
    slack, bot = load_slack_module()

    body = slack.slack_handler(
        signed_slack_event(
            "  do you work in finance  ", base64_encoded=True
        ),
        now=1000,
    )

    assert_equal(body, "bot: do you work in finance", "base64 Slack response")
    assert_equal(bot.calls, ["do you work in finance"], "base64 Slack bot call")


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
        test_messenger_verification_escapes_reflected_markup,
        test_messenger_verification_requires_exact_subscribe_mode,
        test_messenger_verification_mode_source_contracts,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_ignores_echoes_and_continues_scanning,
        test_messenger_post_requires_boolean_true_echo_flag,
        test_messenger_post_ignores_non_text_or_blank_messages,
        test_messenger_post_trims_sender_and_message_text_before_reply,
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_post_rejects_non_page_object,
        test_messenger_post_processes_valid_batch_in_payload_order,
        test_messenger_post_caps_valid_batch,
        test_messenger_post_applies_replay_claims_per_batch_message,
        test_messenger_post_debug_field_does_not_suppress_replies,
        test_messenger_debug_field_source_contracts,
        test_messenger_post_releases_only_failing_batch_claim,
        test_messenger_post_suppresses_replayed_message_ids,
        test_messenger_post_preserves_messages_without_ids,
        test_recent_message_ids_evicts_oldest_claims_at_bound,
        test_messenger_post_releases_claim_when_reply_fails,
        test_messenger_post_ignores_malformed_message_ids_for_compatibility,
        test_messenger_replay_source_contracts,
        test_messenger_batch_source_contracts,
        test_messenger_reply_uses_header_auth_and_timeout,
        test_messenger_post_releases_claim_after_provider_http_error,
        test_messenger_reply_http_status_source_contracts,
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
        test_moderation_review_guide_is_auditable,
        test_slack_command_requires_valid_signature,
        test_slack_command_accepts_valid_signature,
        test_slack_command_suppresses_replayed_signature,
        test_slack_command_releases_replay_claim_after_failure,
        test_slack_command_rejects_blank_text,
        test_slack_command_rejects_non_text_values,
        test_slack_command_trims_text_before_bot_call,
        test_slack_command_rejects_stale_and_future_timestamps,
        test_slack_handlers_reject_oversized_bodies,
        test_slack_signature_verifier_rejects_tampering_and_invalid_metadata,
        test_slack_signing_secret_source_contracts,
        test_slack_replay_source_contracts,
        test_standalone_slack_handler_requires_valid_signature,
        test_standalone_slack_handler_accepts_valid_signature,
        test_standalone_slack_handler_suppresses_replayed_signature,
        test_standalone_slack_handler_releases_replay_claim_after_failure,
        test_recent_slack_signatures_evicts_oldest_claim,
        test_standalone_slack_handler_rejects_blank_text,
        test_standalone_slack_handler_rejects_missing_text,
        test_standalone_slack_handler_accepts_signed_base64_body,
    ]
    for test in tests:
        test()
    print("valleybot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
