#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from bottle import Bottle, template, request, response, debug
import bot
import json
import slack

debug(True)

app = Bottle()


@app.post('/slack')
def slack_handler():
    """
    Handler for slack
    """
    return slack.slack_handler(request.json)


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
