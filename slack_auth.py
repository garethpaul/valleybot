import hashlib
import hmac
import time


SLACK_SIGNATURE_VERSION = "v0"
SLACK_REQUEST_MAX_AGE_SECONDS = 5 * 60
MAX_SLACK_REQUEST_BYTES = 1024 * 1024


def verify_slack_request(raw_body, timestamp, signature, signing_secret, now=None):
    if not isinstance(raw_body, bytes):
        return False
    if not all(isinstance(value, str) and value for value in (
            timestamp, signature, signing_secret)):
        return False
    if not timestamp.isdigit():
        return False

    request_time = int(timestamp)

    current_time = int(time.time() if now is None else now)
    if request_time > current_time:
        return False
    if current_time - request_time > SLACK_REQUEST_MAX_AGE_SECONDS:
        return False

    try:
        timestamp_bytes = timestamp.encode("ascii")
    except UnicodeEncodeError:
        return False
    version = SLACK_SIGNATURE_VERSION.encode("ascii")
    base = version + b":" + timestamp_bytes + b":" + raw_body
    expected = SLACK_SIGNATURE_VERSION + "=" + hmac.new(
        signing_secret.encode("utf-8"), base, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
