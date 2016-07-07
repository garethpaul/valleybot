import logging
import settings
import bot

expected_token = settings.slack_token

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def slack_handler(event):
    command_text = event['text']
    return bot.respond(command_text)
