#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from bottle import Bottle, template, request, response, debug, run
import bot
debug(True)

app = Bottle()


@app.get('/bot')
def chat():
    """
    Chat handler for returning a bot response
    Returns json response
    """
    chat = request.query['chat']
    response.content_type = 'application/json'
    return bot.respond(chat)


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
    run(host='0.0.0.0', port=argv[1])
