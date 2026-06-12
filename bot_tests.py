import unittest
import os
import hashlib
import hmac

os.environ.setdefault('SLACK_TOKEN', 'test-slack-token')
os.environ.setdefault('MESSENGER_TOKEN', 'test-page-token')
os.environ.setdefault('MESSENGER_VERIFY_TOKEN', 'test-verify-token')
os.environ.setdefault('MESSENGER_APP_SECRET', 'test-app-secret')

import bot
import nltk
nltk.data.path.append(os.getcwd() + '/nltk_data')
from textblob import TextBlob
from webtest import TestApp
import json
import app

test_app = TestApp(app.app)


class BotTest(unittest.TestCase):

    def setUp(self):
        self.greeting = TextBlob("hello there")
        self.pronoun = TextBlob("On saturday I will meet joe.")
        self.verb = TextBlob("She smells the pizza.")
        self.noun = TextBlob("She smells the pizza.")
        self.adjective = TextBlob("This shop is much nicer")
        self.construct = TextBlob("What a beautiful car, you look great")

    def testGreeting(self):
        self.assertTrue(bot.check_for_greeting(self.greeting))

    def testVowel(self):
        word = "acorn"
        self.assertTrue(bot.starts_with_vowel(word))

    def testJson(self):
        json_payload = {"data": "hello iam good?"}
        self.assertTrue(bot.json_request(json_payload=json_payload,
                                         context=None))

    def testPronoun(self):
        pronoun = bot.find_pronoun(self.pronoun)
        self.assertEqual(pronoun, "You")

    def testVerb(self):
        r = bot.find_verb(self.verb)
        self.assertEqual(r[0], "smells")

    def testNoun(self):
        r = bot.find_noun(self.noun)
        self.assertEqual(r, "pizza")

    def testAdjective(self):
        r = bot.find_adjective(self.adjective)
        self.assertEqual(r, "much")

    def testConstructResp(self):
        pronoun = bot.find_pronoun(self.construct)
        noun = bot.find_noun(self.construct)
        verb = bot.find_verb(self.construct)
        r = bot.construct_response(pronoun, noun, verb)
        self.assertTrue("car" in r)

    def testFilteredResponseUsesReviewedFallback(self):
        blocked_response = next(iter(bot.config.FILTER_WORDS))
        original_choice = bot.random.choice
        bot.random.choice = lambda responses: responses[0]
        try:
            response = bot.safe_response(blocked_response)
        finally:
            bot.random.choice = original_choice

        self.assertEqual(response, bot.config.NONE_RESPONSES[0])

    def testAcceptableResponsePassesThroughFilter(self):
        response = "reviewed response"

        self.assertEqual(bot.safe_response(response), response)


class TestBottleApp(unittest.TestCase):

    def setUp(self):
            pass

    def test_app(self):
        # get response for index
        response = test_app.get('/')
        # Response status should be HTTP 200 OK
        self.assertEqual(response.status_int, 200)

    def test_bot(self):
        # test bot response
        response = test_app.get('/bot?chat=hello there tom')
        self.assertEqual(response.status_int, 200)


class TestSlack(unittest.TestCase):
    def test_slack(self):
        """
        A simple test for the slackbot.
        """
        response = test_app.post('/slack',
                                 {'text': 'do you work in finance',
                                  'token': app.settings.slack_token})
        self.assertEqual(response.status_int, 200)
        self.assertTrue(len(response.body) >= 1)

    def test_slack_rejects_bad_token(self):
        """
        Slack requests must include the configured verification token.
        """
        response = test_app.post('/slack',
                                 {'text': 'do you work in finance',
                                  'token': 'bad-token'},
                                 expect_errors=True)
        self.assertEqual(response.status_int, 403)


class TestFacebook(unittest.TestCase):
    """
    Test Cases for FB Messenger Chat Bot Integration
    """
    def setUp(self):
        """
        Setup the data for the test.
        """
        self.data = {'object': 'page',
                     'debug': True,
                     'entry': [{'id': u'1115484138511624',
                                'time': 1467905719502,
                                'messaging': [{'message': {'seq': 159,
                                                           'text': 'testing 123',
                                                           'mid': 'mid.1467905719433:9e270686881a8e2a05'},
                                               'sender': {'id': '1096099507121740'},
                                               'recipient': {'id': '1115484138511624'},
                                               'timestamp': 1467905719439}]}]}
        self.user_id = '1096099507121740'
        self.challenge = '123'

    def test_facebook_webhook(self):
        """
        A test with a sample payload for the messenger bot.
        """
        r = self.post_signed_json(self.data)
        self.assertEqual(r.status_int, 200)

    def test_facebook_response(self):
        """
        A test to send a FB message test
        """
        calls = []
        original_post = app.requests.post

        class FakeResponse(object):
            def __init__(self, user_id):
                self.content = json.dumps({'recipient_id': user_id})

        def fake_post(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse(self.user_id)

        app.requests.post = fake_post
        try:
            r = app.messenger_reply(self.user_id, "hello this is a test")
        finally:
            app.requests.post = original_post

        self.assertTrue(len(r) >= 1)
        self.assertTrue(json.loads(r)['recipient_id'] == self.user_id)
        self.assertTrue('access_token=' not in calls[0][0])
        self.assertEqual(calls[0][1]['headers']['Authorization'],
                         'Bearer ' + app.settings.messenger_token)
        self.assertEqual(calls[0][1]['timeout'], app.settings.request_timeout)

    def test_facebook_challenge(self):
        """
        Test that the webhook returns a challenge
        """
        r = test_app.get('/messenger/webhook?hub.challenge=' +
                         self.challenge +
                         '&hub.verify_token=' +
                         app.settings.messenger_verify_token)
        self.assertEqual(r.text, self.challenge)

    def test_facebook_challenge_rejects_bad_token(self):
        """
        Test that the webhook rejects invalid verification tokens
        """
        r = test_app.get('/messenger/webhook?hub.challenge=' +
                         self.challenge +
                         '&hub.verify_token=bad-token',
                         expect_errors=True)
        self.assertEqual(r.status_int, 403)

    def test_facebook_delivery_event_is_ignored(self):
        """
        Test that non-message webhook events are acknowledged without replies
        """
        data = {'object': 'page',
                'entry': [{'messaging': [{'sender': {'id': self.user_id},
                                          'delivery': {'mids': ['mid-1']}}]}]}
        r = self.post_signed_json(data)
        self.assertEqual(r.status_int, 200)

    def test_facebook_webhook_rejects_invalid_signature(self):
        body = json.dumps(self.data).encode('utf-8')
        r = test_app.post(
            '/messenger/webhook',
            body,
            headers={'X-Hub-Signature-256': 'sha256=invalid'},
            content_type='application/json',
            expect_errors=True)
        self.assertEqual(r.status_int, 403)

    def test_facebook_webhook_accepts_json_content_type_parameters(self):
        r = self.post_signed_json(
            self.data,
            content_type='Application/JSON; charset=UTF-8')
        self.assertEqual(r.status_int, 200)

    def test_facebook_webhook_rejects_non_json_content_type(self):
        body = json.dumps(self.data).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            app.settings.messenger_app_secret.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        r = test_app.post(
            '/messenger/webhook',
            body,
            headers={'X-Hub-Signature-256': signature},
            content_type='text/plain',
            expect_errors=True)
        self.assertEqual(r.status_int, 415)

    def test_facebook_webhook_rejects_oversized_payload(self):
        data = {'object': 'page',
                'padding': 'x' * app.MAX_MESSENGER_WEBHOOK_BYTES}
        body = json.dumps(data).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            app.settings.messenger_app_secret.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        r = test_app.post(
            '/messenger/webhook',
            body,
            headers={'X-Hub-Signature-256': signature},
            content_type='application/json',
            expect_errors=True)
        self.assertEqual(r.status_int, 413)

    def post_signed_json(self, payload, content_type='application/json'):
        body = json.dumps(payload).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            app.settings.messenger_app_secret.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        return test_app.post(
            '/messenger/webhook',
            body,
            headers={'X-Hub-Signature-256': signature},
            content_type=content_type)

if __name__ == '__main__':
    unittest.main()
