import logging
import base64
from urllib.parse import parse_qs
import settings
import bot
from slack_auth import MAX_SLACK_REQUEST_BYTES, verify_slack_request


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def slack_handler(event, now=None):
    if not isinstance(event, dict):
        return "forbidden"

    headers = event.get("headers")
    body = event.get("body")
    if not isinstance(headers, dict) or not isinstance(body, str):
        return "forbidden"

    is_base64_encoded = event.get("isBase64Encoded") is True
    max_encoded_length = ((MAX_SLACK_REQUEST_BYTES + 2) // 3) * 4
    if len(body) > (
            max_encoded_length if is_base64_encoded else MAX_SLACK_REQUEST_BYTES):
        return "payload too large"

    normalized_headers = {
        str(name).lower(): value for name, value in headers.items()
    }
    try:
        raw_body = (
            base64.b64decode(body, validate=True)
            if is_base64_encoded
            else body.encode("utf-8")
        )
    except (UnicodeEncodeError, ValueError):
        return "forbidden"
    if len(raw_body) > MAX_SLACK_REQUEST_BYTES:
        return "payload too large"

    if not verify_slack_request(
            raw_body,
            normalized_headers.get("x-slack-request-timestamp"),
            normalized_headers.get("x-slack-signature"),
            settings.slack_signing_secret,
            now=now):
        return "forbidden"

    try:
        form = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    except UnicodeDecodeError:
        return "forbidden"
    command_text = clean_text_value(form.get("text", [None])[0])
    if command_text is None:
        return "missing text"

    return bot.respond(command_text)


def clean_text_value(value):
    if value is None:
        return None

    try:
        text_types = (basestring,)
    except NameError:
        text_types = (str,)

    if not isinstance(value, text_types):
        return None

    value = value.strip()
    return value or None
