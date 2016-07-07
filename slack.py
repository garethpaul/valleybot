from urlparse import parse_qs
import logging
import settings
import bot

expected_token = settings.slack_token

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def slack_handler(event):
    req_body = event['body']
    params = parse_qs(req_body)
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match exptected", token)
        raise Exception("Invalid request token")
    command_text = params['text'][0]
    return bot.respond(command_text)
