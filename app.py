#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from bottle import Bottle, template, request, response, debug
import bot
import json
import requests
import settings

debug(True)

app = Bottle()


@app.post('/slack')
def slack_handler():
    """
    Handler for slack
    """
    command_text = request.forms.get('text')
    return bot.respond(command_text)


@app.get('/messenger/webhook')
def messenger_webhook():
    challenge = request.query.get("hub.challenge")
    return challenge


@app.post('/messenger/webhook')
def messenger_post():
    data = request.json
    print data
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    reply(sender, message[::-1])
    return "ok"


def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post(settings.messenger_url, json=data)
    print(resp.content)


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
