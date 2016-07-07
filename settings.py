import os
slack_token = os.environ['SLACK_TOKEN']
messenger_token = os.environ['MESSENGER_TOKEN']
messenger_url = "https://graph.facebook.com/v2.6/me/messages?access_token=" + messenger_token
