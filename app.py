#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from sys import argv
from bottle import Bottle, template, request, response, debug
import bot
import json
import requests
import settings

REQUEST_TIMEOUT = 10


def env_flag(name):
    return os.environ.get(name, '').lower() in ('1', 'true', 'yes', 'on')


debug(env_flag('BOTTLE_DEBUG'))

app = Bottle()


# SLACK INTEGRATION
@app.post('/slack')
def slack_handler():
    """
    Handler for slack
    """
    command_text = request.forms.get('text')
    return bot.respond(command_text)


# FACEBOOK MESSENGER INTEGRATION
@app.get('/messenger/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    challenge = request.query.get("hub.challenge")
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

    entries = data.get('entry')
    if not isinstance(entries, list):
        return "ok"

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        messages = entry.get('messaging')
        if not isinstance(messages, list):
            continue
        for msg_data in messages:
            if not isinstance(msg_data, dict):
                continue
            sender = msg_data.get('sender') or {}
            message = msg_data.get('message') or {}
            sender_id = sender.get('id') if isinstance(sender, dict) else None
            message_text = message.get('text') if isinstance(message, dict) else None
            if sender_id and message_text and not data.get('debug'):
                messenger_reply(sender_id, str(message_text))

    # must send back response quickly
    return "ok"


def messenger_reply(user_id, msg):
    """
    Function for returning data back to facebook
    """
    data = {
        "recipient": {"id": user_id},
        "message": {"text": bot.respond(msg)}
    }
    headers = {
        "Authorization": "Bearer " + settings.messenger_token
    }
    resp = requests.post(settings.messenger_url, json=data,
                         headers=headers,
                         timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
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
