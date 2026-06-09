#!/usr/bin/env python3
"""Dependency-free route contract checks for the legacy Bottle app."""
import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-valleybot-webhook-hardening.md"


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
    bot.respond = lambda message: "bot: {0}".format(message)

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


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError("{0}: expected {1!r}, got {2!r}".format(label, expected, actual))


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def test_completed_plan_is_in_docs_plans():
    assert_true(PLAN_PATH.is_file(), "webhook hardening plan must live under docs/plans")
    plan_text = PLAN_PATH.read_text()
    assert_true("status: completed" in plan_text.lower(), "webhook hardening plan must be completed")
    assert_true("make check" in plan_text, "webhook hardening plan must document make check verification")


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


def main():
    tests = [
        test_completed_plan_is_in_docs_plans,
        test_messenger_verification_requires_matching_token,
        test_messenger_verification_accepts_matching_token,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_reply_uses_header_auth_and_timeout,
        test_slack_command_requires_matching_token,
        test_slack_command_accepts_matching_token,
    ]
    for test in tests:
        test()
    print("valleybot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
