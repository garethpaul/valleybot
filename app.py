#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from collections import OrderedDict
import os
import threading
from bottle import Bottle, template, request, response, debug
import bot
import hmac
import hashlib
import json
import requests
import settings

debug(os.environ.get("BOTTLE_DEBUG", "").strip().lower() == "true")

app = Bottle()
MAX_MESSENGER_WEBHOOK_BYTES = 1024 * 1024
MAX_RECENT_MESSENGER_MESSAGE_IDS = 1024
MAX_MESSENGER_MESSAGES_PER_WEBHOOK = 20


class RecentMessageIds(object):
    def __init__(self, max_entries):
        self.max_entries = max_entries
        self._ids = OrderedDict()
        self._lock = threading.Lock()

    def claim(self, message_id):
        with self._lock:
            if message_id in self._ids:
                return False
            self._ids[message_id] = None
            while len(self._ids) > self.max_entries:
                self._ids.popitem(last=False)
            return True

    def release(self, message_id):
        with self._lock:
            self._ids.pop(message_id, None)


recent_messenger_message_ids = RecentMessageIds(
    MAX_RECENT_MESSENGER_MESSAGE_IDS)


# SLACK INTEGRATION
@app.post('/slack')
def slack_handler():
    """
    Handler for slack
    """
    token = request.forms.get('token')
    if not secure_compare(token, settings.slack_token):
        response.status = 403
        return "forbidden"

    command_text = clean_text_value(request.forms.get('text'))
    if command_text is None:
        response.status = 400
        return "missing text"

    return bot.respond(command_text)


# FACEBOOK MESSENGER INTEGRATION
@app.get('/messenger/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get("hub.verify_token")
    expected_token = getattr(settings, "messenger_verify_token", None)
    challenge = request.query.get("hub.challenge")
    if not secure_compare(verify_token, expected_token):
        response.status = 403
        return "forbidden"
    if not challenge:
        response.status = 400
        return "missing challenge"
    return challenge


@app.post('/messenger/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    content_length = getattr(request, "content_length", None)
    if content_length is not None and content_length > MAX_MESSENGER_WEBHOOK_BYTES:
        response.status = 413
        return "payload too large"

    if not is_json_content_type(request.headers.get("Content-Type")):
        response.status = 415
        return "unsupported media type"

    raw_body = request.body.read(MAX_MESSENGER_WEBHOOK_BYTES + 1)
    if len(raw_body) > MAX_MESSENGER_WEBHOOK_BYTES:
        response.status = 413
        return "payload too large"
    try:
        request.body.seek(0)
    except (AttributeError, IOError):
        pass
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_messenger_signature(
            raw_body, signature, settings.messenger_app_secret):
        response.status = 403
        return "forbidden"

    data = request.json
    if not isinstance(data, dict):
        response.status = 400
        return "invalid payload"
    if data.get('object') != 'page':
        response.status = 400
        return "invalid payload"

    messages = parse_messenger_messages(data)
    if not messages:
        return "ok"

    # send message to get bot
    if not data.get('debug'):
        for sender, message, message_id in messages:
            if message_id and not recent_messenger_message_ids.claim(message_id):
                continue
            try:
                messenger_reply(sender, message)
            except Exception:
                if message_id:
                    recent_messenger_message_ids.release(message_id)
                raise

    # must send back response quickly
    return "ok"


def is_json_content_type(value):
    if not isinstance(value, str):
        return False

    media_type = value.split(";", 1)[0].strip().lower()
    return media_type == "application/json"


def verify_messenger_signature(raw_body, signature, app_secret):
    if not (raw_body is not None and signature and app_secret):
        return False
    if isinstance(raw_body, str):
        raw_body = raw_body.encode("utf-8")
    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return secure_compare(signature, expected)


def secure_compare(left, right):
    """
    Compare webhook tokens without short-circuiting on partial matches.
    """
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


def clean_text_value(value):
    """
    Return trimmed text from form/query payloads or None for non-text values.
    """
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


def parse_messenger_messages(data):
    """
    Return a bounded list of sender/text/message-ID tuples in payload order.
    """
    entries = data.get('entry')
    if not isinstance(entries, list):
        return []

    messages = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        events = entry.get('messaging')
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            sender = event.get('sender')
            message = event.get('message')
            if not isinstance(sender, dict) or not isinstance(message, dict):
                continue
            if message.get('is_echo') is True:
                continue
            sender_id = sender.get('id')
            message_text = message.get('text')
            message_id = message.get('mid')
            try:
                sender_id = sender_id.strip()
                message_text = message_text.strip()
            except AttributeError:
                continue
            try:
                message_id = message_id.strip()
            except AttributeError:
                message_id = None
            if sender_id and message_text:
                messages.append((sender_id, message_text, message_id or None))
                if len(messages) >= MAX_MESSENGER_MESSAGES_PER_WEBHOOK:
                    return messages

    return messages


def messenger_reply(user_id, msg):
    """
    Function for returning data back to facebook
    """
    data = {
        "recipient": {"id": user_id},
        "message": {"text": bot.respond(msg)}
    }
    headers = {"Authorization": "Bearer {0}".format(settings.messenger_token)}
    resp = requests.post(
        settings.messenger_url,
        json=data,
        headers=headers,
        timeout=settings.request_timeout)
    return resp.content


# WEB BOT INTEGRATION
@app.get('/bot')
def chat():
    """
    Chat handler for returning a bot response
    Returns json response
    """
    response.content_type = 'application/json'
    chat = request.query.get('chat')
    if chat is None:
        response.status = 400
        return json.dumps({"error": "missing chat"})

    chat = chat.strip()
    if not chat:
        response.status = 400
        return json.dumps({"error": "missing chat"})

    return json.dumps({"data": bot.respond(chat)})


@app.get('/')
def index():
    """
    Index handler for posting chats
    Returns html page
    """
    info = {'title': 'Valley Bot!',
            'content': 'The Valley Bot Chat'
            }
    return template('index.tpl', info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=argv[1])
