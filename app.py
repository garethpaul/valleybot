#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from bottle import Bottle, template, request, response, debug
import bot
import hmac
import json
import requests
import settings

debug(True)

app = Bottle()


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

    command_text = request.forms.get('text')
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
    data = request.json
    if not isinstance(data, dict):
        response.status = 400
        return "invalid payload"

    sender, message = parse_messenger_message(data)
    if not (sender and message):
        return "ok"

    # send message to get bot
    if not data.get('debug'):
        messenger_reply(sender, str(message))

    # must send back response quickly
    return "ok"


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


def parse_messenger_message(data):
    """
    Return the first sender/text pair from a Messenger payload if present.
    """
    entries = data.get('entry')
    if not isinstance(entries, list):
        return None, None

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        events = entry.get('messaging')
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            sender = event.get('sender') or {}
            message = event.get('message') or {}
            sender_id = sender.get('id')
            message_text = message.get('text')
            if sender_id and message_text:
                return sender_id, message_text

    return None, None


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
    chat = request.query['chat']
    response.content_type = 'application/json'
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
