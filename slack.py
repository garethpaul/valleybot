import logging
import hmac
import settings
import bot

expected_token = settings.slack_token

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def slack_handler(event):
    token = event.get('token') if isinstance(event, dict) else None
    if not secure_compare(token, expected_token):
        return "forbidden"

    command_text = event.get('text')
    if command_text is None:
        return "missing text"
    command_text = command_text.strip()
    if not command_text:
        return "missing text"

    return bot.respond(command_text)


def secure_compare(left, right):
    if not (left and right):
        return False

    left = str(left)
    right = str(right)
    compare_digest = getattr(hmac, "compare_digest", None)
    if compare_digest:
        return compare_digest(left, right)

    if len(left) != len(right):
        return False

    result = 0
    for left_char, right_char in zip(left, right):
        result |= ord(left_char) ^ ord(right_char)
    return result == 0
