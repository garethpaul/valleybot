#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hmac
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
    token = request.forms.get('token')
    if not hmac.compare_digest(str(token or ''), str(settings.slack_token)):
        response.status = 403
        return "Invalid Slack verification token"

    command_text = request.forms.get('text')
    return bot.respond(command_text)


# FACEBOOK MESSENGER INTEGRATION
@app.get('/messenger/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get("hub.verify_token")
    if not hmac.compare_digest(str(verify_token or ''),
                               str(settings.messenger_verify_token)):
        response.status = 403
        return "Invalid Request or Verification Token"

    challenge = request.query.get("hub.challenge")
    return challenge


@app.post('/messenger/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if not isinstance(data, dict):
        return "ignored"

    if not data.get('debug'):
        for sender, message in messenger_messages(data):
            messenger_reply(sender, str(message))

    # must send back response quickly
    return "ok"


def messenger_messages(data):
    if data.get('object') != 'page':
        return

    for entry in data.get('entry') or []:
        if not isinstance(entry, dict):
            continue
        for msg_data in entry.get('messaging') or []:
            if not isinstance(msg_data, dict):
                continue
            sender = (msg_data.get('sender') or {}).get('id')
            message = (msg_data.get('message') or {}).get('text')
            if sender and message:
                yield sender, message


def messenger_reply(user_id, msg):
    """
    Function for returning data back to facebook
    """
    data = {
        "recipient": {"id": user_id},
        "message": {"text": bot.respond(msg)}
    }
    resp = requests.post(settings.messenger_url,
                         params=settings.messenger_params(),
                         json=data,
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
