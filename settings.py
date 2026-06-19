import math
import os


def positive_float_from_env(name, default):
    try:
        value = float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return float(default)

    if value <= 0 or math.isnan(value) or math.isinf(value):
        return float(default)
    return value


slack_signing_secret = os.environ.get('SLACK_SIGNING_SECRET', '')
messenger_token = os.environ.get('MESSENGER_TOKEN', '')
messenger_verify_token = os.environ.get('MESSENGER_VERIFY_TOKEN', '')
messenger_app_secret = os.environ.get('MESSENGER_APP_SECRET', '')
messenger_url = "https://graph.facebook.com/v2.6/me/messages"
request_timeout = positive_float_from_env('REQUEST_TIMEOUT', 5.0)
