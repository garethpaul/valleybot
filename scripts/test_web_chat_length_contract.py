#!/usr/bin/env python3
"""Mutation-sensitive contract for the public web-chat input boundary."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(source):
    require(
        "MAX_WEB_CHAT_CHARACTERS = 1000" in source.splitlines(),
        "web chat limit must remain explicit",
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
    validate(source)
    mutations = {
        "expanded limit": replace_once(
            source,
            "MAX_WEB_CHAT_CHARACTERS = 1000",
            "MAX_WEB_CHAT_CHARACTERS = 10000",
        ),
        "encoded-byte measurement": replace_once(
            source,
            "if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
            'if len(chat.encode("utf-8")) > MAX_WEB_CHAT_CHARACTERS:',
        ),
        "off-by-one comparison": replace_once(
            source,
            "if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
            "if len(chat) >= MAX_WEB_CHAT_CHARACTERS:",
        ),
        "bot call before limit": replace_once(
            source,
            "if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
            "bot.respond(chat)\n    if len(chat) > MAX_WEB_CHAT_CHARACTERS:",
        ),
        "non-JSON error": replace_once(
            source,
            'return json.dumps({"error": "chat too long"})',
            'return "chat too long"',
        ),
    }
    for label, mutation in mutations.items():
        try:
            validate(mutation)
        except (AssertionError, ValueError):
            continue
        raise AssertionError("{0} mutation unexpectedly passed".format(label))
    print("web chat length contract passed (5 mutations rejected)")


if __name__ == "__main__":
    main()
