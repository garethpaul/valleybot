#!/usr/bin/env python3
"""Dependency-free route contract checks for the legacy Bottle app."""
import importlib.util
import json
import os
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBHOOK_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-valleybot-webhook-hardening.md"
STANDALONE_SLACK_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-08-valleybot-standalone-slack-token.md"
)
SLACK_COMMAND_TEXT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-08-valleybot-slack-command-text.md"
)
WEB_BOT_CHAT_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-valleybot-web-bot-chat.md"
REQUEST_TIMEOUT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-valleybot-request-timeout.md"
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
    assert_completed_plan(WEB_BOT_CHAT_PLAN_PATH, "web bot chat")
    assert_completed_plan(REQUEST_TIMEOUT_PLAN_PATH, "request timeout")


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


def test_messenger_post_rejects_invalid_json_shape():
    app, request, response, _requests = load_app()

    request.json = None
    response.status = 200

    body = app.messenger_post()

    assert_equal(response.status, 400, "invalid json status")
    assert_true(body != "ok", "invalid json should not be acknowledged as a valid event")


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


def main():
    tests = [
        test_completed_plans_are_in_docs_plans,
        test_messenger_verification_requires_matching_token,
        test_messenger_verification_accepts_matching_token,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_reply_uses_header_auth_and_timeout,
        test_request_timeout_accepts_positive_float_env,
        test_request_timeout_defaults_for_invalid_env,
        test_web_bot_rejects_missing_chat_query,
        test_web_bot_rejects_blank_chat_query,
        test_web_bot_trims_chat_before_bot_call,
        test_slack_command_requires_matching_token,
        test_slack_command_accepts_matching_token,
        test_slack_command_rejects_blank_text,
        test_slack_command_trims_text_before_bot_call,
        test_standalone_slack_handler_requires_matching_token,
        test_standalone_slack_handler_accepts_matching_token,
        test_standalone_slack_handler_rejects_blank_text,
    ]
    for test in tests:
        test()
    print("valleybot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
