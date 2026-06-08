import os
slack_token = os.environ.get('SLACK_TOKEN', '')
messenger_token = os.environ.get('MESSENGER_TOKEN', '')
messenger_verify_token = os.environ.get('MESSENGER_VERIFY_TOKEN', messenger_token)
messenger_url = "https://graph.facebook.com/v2.6/me/messages"
request_timeout = float(os.environ.get('REQUEST_TIMEOUT', '5'))
