#!/usr/bin/env python3
"""Mutation-sensitive contract for the public web-chat input boundary."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"
LIMITS_PATH = ROOT / "channel_limits.py"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(source, limits_source):
    require(
        "MAX_CHANNEL_MESSAGE_CHARACTERS = 1000" in limits_source.splitlines(),
        "shared channel message limit must remain explicit",
    )
    require(
        "MAX_WEB_CHAT_CHARACTERS = MAX_CHANNEL_MESSAGE_CHARACTERS"
        in source.splitlines(),
        "web chat must use the shared channel message limit",
    )
    start = source.index("def chat():")
    end = source.index("\n\n@app.get('/')", start)
    route = source[start:end]
    trim = route.index("chat = chat.strip()")
    limit = route.index("if len(chat) > MAX_WEB_CHAT_CHARACTERS:")
    status = route.index("response.status = 413", limit)
    error = route.index('return json.dumps({"error": "chat too long"})', status)
    bot_call = route.index('return json.dumps({"data": bot.respond(chat)})')
    require(
        route.count("bot.respond(chat)") == 1,
        "web chat route must call the bot exactly once",
    )
    require(
        trim < limit < status < error < bot_call,
        "trimmed input must be bounded before response generation",
    )


def replace_once(source, old, new):
    require(source.count(old) == 1, "mutation target must appear exactly once")
    return source.replace(old, new, 1)


def main():
    source = APP_PATH.read_text(encoding="utf-8")
    limits_source = LIMITS_PATH.read_text(encoding="utf-8")
    validate(source, limits_source)
    mutations = {
        "expanded limit": (
            source,
            replace_once(
                limits_source,
                "MAX_CHANNEL_MESSAGE_CHARACTERS = 1000",
                "MAX_CHANNEL_MESSAGE_CHARACTERS = 10000",
            ),
        ),
        "encoded-byte measurement": (
            replace_once(
                source,
                "if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
                'if len(chat.encode("utf-8")) > MAX_WEB_CHAT_CHARACTERS:',
            ),
            limits_source,
        ),
        "off-by-one comparison": (
            replace_once(
                source,
                "if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
                "if len(chat) >= MAX_WEB_CHAT_CHARACTERS:",
            ),
            limits_source,
        ),
        "bot call before limit": (
            replace_once(
                source,
                "if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
                "bot.respond(chat)\n    if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
            ),
            limits_source,
        ),
        "non-JSON error": (
            replace_once(
                source,
                'return json.dumps({"error": "chat too long"})',
                'return "chat too long"',
            ),
            limits_source,
        ),
    }
    for label, mutation in mutations.items():
        try:
            validate(*mutation)
        except (AssertionError, ValueError):
            continue
        raise AssertionError("{0} mutation unexpectedly passed".format(label))
    print("web chat length contract passed (5 mutations rejected)")


if __name__ == "__main__":
    main()
