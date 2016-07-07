import os
slack_token = os.environ['SLACK-TOKEN']
messenger_token = os.environ['MESSENGER-TOKEN']
messenger_url = "https://graph.facebook.com/v2.6/me/messages?access_token=" + messenger_token
