#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from bottle import template, get, request, response, debug, run
import bot
debug(True)

@get('/bot')
def chat():
    chat = request.query['chat']
    response.content_type = 'application/json'
    return bot.respond(chat)

@get('/')
def index():
    info = {'title': 'Valley Bot!',
            'content': 'The Valley Bot Chat'
            }
    return template('index.tpl', info)

run(host='0.0.0.0', port=argv[1])
