import unittest
import os
import hashlib
import hmac
import importlib.util
import time
from urllib.parse import urlencode

os.environ.setdefault('SLACK_SIGNING_SECRET', 'test-slack-signing-secret')
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

    def test_bot_accepts_exact_character_limit(self):
        original_respond = app.bot.respond
        calls = []
        app.bot.respond = lambda text: calls.append(text) or 'bounded response'
        try:
            response = test_app.get(
                '/bot', params={'chat': 'x' * app.MAX_WEB_CHAT_CHARACTERS})
        finally:
            app.bot.respond = original_respond

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.json, {'data': 'bounded response'})
        self.assertEqual(calls, ['x' * app.MAX_WEB_CHAT_CHARACTERS])

    def test_bot_rejects_oversized_chat_before_response_generation(self):
        original_respond = app.bot.respond
        calls = []
        app.bot.respond = lambda text: calls.append(text) or 'unexpected'
        try:
            response = test_app.get(
                '/bot',
                params={'chat': '界' * (app.MAX_WEB_CHAT_CHARACTERS + 1)},
                expect_errors=True)
        finally:
            app.bot.respond = original_respond

        self.assertEqual(response.status_int, 413)
        self.assertEqual(response.json, {'error': 'chat too long'})
        self.assertEqual(calls, [])


class TestSettings(unittest.TestCase):

    def test_messenger_verify_token_missing_does_not_fallback_to_page_token(self):
        original_messenger_token = os.environ.get('MESSENGER_TOKEN')
        original_verify_token = os.environ.get('MESSENGER_VERIFY_TOKEN')
        os.environ['MESSENGER_TOKEN'] = 'page-access-token'
        os.environ.pop('MESSENGER_VERIFY_TOKEN', None)
        try:
            spec = importlib.util.spec_from_file_location(
                'valleybot_settings_missing_verify_token',
                os.path.join(os.getcwd(), 'settings.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            if original_messenger_token is None:
                os.environ.pop('MESSENGER_TOKEN', None)
            else:
                os.environ['MESSENGER_TOKEN'] = original_messenger_token
            if original_verify_token is None:
                os.environ.pop('MESSENGER_VERIFY_TOKEN', None)
            else:
                os.environ['MESSENGER_VERIFY_TOKEN'] = original_verify_token

        self.assertEqual(module.messenger_token, 'page-access-token')
        self.assertEqual(module.messenger_verify_token, '')
        self.assertNotEqual(
            module.messenger_verify_token,
            module.messenger_token)


class TestSlack(unittest.TestCase):
    def setUp(self):
        app.recent_slack_signatures = app.RecentSlackSignatures()

    def post_signed_slack(self, text, timestamp=None, signature=None,
                          expect_errors=False):
        body = urlencode({'text': text})
        timestamp = str(int(time.time()) if timestamp is None else timestamp)
        if signature is None:
            base = 'v0:{0}:{1}'.format(timestamp, body).encode('utf-8')
            signature = 'v0=' + hmac.new(
                app.settings.slack_signing_secret.encode('utf-8'),
                base,
                hashlib.sha256).hexdigest()
        return test_app.post(
            '/slack',
            body,
            headers={
                'X-Slack-Request-Timestamp': timestamp,
                'X-Slack-Signature': signature,
            },
            content_type='application/x-www-form-urlencoded',
            expect_errors=expect_errors)

    def test_slack(self):
        """
        A simple test for the slackbot.
        """
        response = self.post_signed_slack('do you work in finance')
        self.assertEqual(response.status_int, 200)
        self.assertTrue(len(response.body) >= 1)

    def test_slack_suppresses_replayed_signature(self):
        original_respond = app.bot.respond
        calls = []
        app.bot.respond = lambda text: calls.append(text) or 'first response'
        timestamp = int(time.time())
        try:
            first = self.post_signed_slack('replayed command', timestamp=timestamp)
            second = self.post_signed_slack('replayed command', timestamp=timestamp)
        finally:
            app.bot.respond = original_respond

        self.assertEqual(first.text, 'first response')
        self.assertEqual(second.text, 'ok')
        self.assertEqual(calls, ['replayed command'])

    def test_slack_releases_signature_after_bot_failure(self):
        original_respond = app.bot.respond
        timestamp = int(time.time())

        def fail(_text):
            raise RuntimeError('bot failed')

        app.bot.respond = fail
        try:
            failed = self.post_signed_slack(
                'retry command', timestamp=timestamp, expect_errors=True)
            self.assertEqual(failed.status_int, 500)
            app.bot.respond = lambda text: 'recovered: ' + text
            retry = self.post_signed_slack('retry command', timestamp=timestamp)
        finally:
            app.bot.respond = original_respond

        self.assertEqual(retry.text, 'recovered: retry command')

    def test_slack_rejects_bad_signature_without_bot_call(self):
        """
        Slack requests must include a valid signing-secret signature.
        """
        original_respond = app.bot.respond
        calls = []
        app.bot.respond = lambda text: calls.append(text)
        try:
            response = self.post_signed_slack(
                'do you work in finance',
                signature='v0=' + ('0' * 64),
                expect_errors=True)
        finally:
            app.bot.respond = original_respond
        self.assertEqual(response.status_int, 403)
        self.assertEqual(calls, [])

    def test_slack_rejects_stale_timestamp(self):
        response = self.post_signed_slack(
            'do you work in finance',
            timestamp=int(time.time()) - 301,
            expect_errors=True)

        self.assertEqual(response.status_int, 403)

    def test_slack_rejects_malformed_timestamp(self):
        response = self.post_signed_slack(
            'do you work in finance',
            timestamp='not-a-time',
            expect_errors=True)

        self.assertEqual(response.status_int, 403)

    def test_slack_rejects_oversized_body_before_bot_call(self):
        original_respond = app.bot.respond
        calls = []
        app.bot.respond = lambda text: calls.append(text)
        try:
            response = test_app.post(
                '/slack',
                b'x' * (app.MAX_SLACK_REQUEST_BYTES + 1),
                headers={
                    'X-Slack-Request-Timestamp': str(int(time.time())),
                    'X-Slack-Signature': 'v0=' + ('0' * 64),
                },
                content_type='application/x-www-form-urlencoded',
                expect_errors=True)
        finally:
            app.bot.respond = original_respond

        self.assertEqual(response.status_int, 413)
        self.assertEqual(calls, [])


class TestFacebook(unittest.TestCase):
    """
    Test Cases for FB Messenger Chat Bot Integration
    """
    def setUp(self):
        """
        Setup the data for the test.
        """
        app.recent_messenger_message_ids = app.RecentMessageIds(
            app.MAX_RECENT_MESSENGER_MESSAGE_IDS)
        self.data = {'object': 'page',
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
        calls = []
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        try:
            r = self.post_signed_json(self.data)
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(calls, [(self.user_id, 'testing 123')])

    def test_facebook_debug_field_does_not_suppress_reply(self):
        calls = []
        data = dict(self.data)
        data['debug'] = True
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        try:
            r = self.post_signed_json(data)
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(calls, [(self.user_id, 'testing 123')])

    def test_facebook_response(self):
        """
        A test to send a FB message test
        """
        calls = []
        original_post = app.requests.post

        class FakeResponse(object):
            def __init__(self, user_id):
                self.content = json.dumps({'recipient_id': user_id})

            def raise_for_status(self):
                return None

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

    def test_facebook_response_raises_for_http_error(self):
        original_post = app.requests.post

        class FailedResponse(object):
            content = b'provider error'

            def raise_for_status(self):
                raise RuntimeError('provider rejected reply')

        app.requests.post = lambda _url, **_kwargs: FailedResponse()
        try:
            with self.assertRaisesRegex(RuntimeError, 'provider rejected reply'):
                app.messenger_reply(self.user_id, 'hello this is a test')
        finally:
            app.requests.post = original_post

    def test_facebook_challenge(self):
        """
        Test that the webhook returns a challenge
        """
        r = test_app.get('/messenger/webhook?hub.challenge=' +
                         self.challenge +
                         '&hub.mode=subscribe' +
                         '&hub.verify_token=' +
                         app.settings.messenger_verify_token)
        self.assertEqual(r.text, self.challenge)

    def test_facebook_challenge_escapes_reflected_markup(self):
        r = test_app.get(
            '/messenger/webhook',
            params={
                'hub.challenge': '<script>alert("xss")</script>',
                'hub.mode': 'subscribe',
                'hub.verify_token': app.settings.messenger_verify_token,
            },
        )
        self.assertEqual(
            r.text,
            '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;',
        )

    def test_facebook_challenge_rejects_bad_token(self):
        """
        Test that the webhook rejects invalid verification tokens
        """
        r = test_app.get('/messenger/webhook?hub.challenge=' +
                         self.challenge +
                         '&hub.mode=subscribe' +
                         '&hub.verify_token=bad-token',
                         expect_errors=True)
        self.assertEqual(r.status_int, 403)

    def test_facebook_challenge_requires_subscribe_mode(self):
        for mode in (None, '', 'Subscribe', 'unsubscribe'):
            params = {
                'hub.challenge': self.challenge,
                'hub.verify_token': app.settings.messenger_verify_token,
            }
            if mode is not None:
                params['hub.mode'] = mode

            r = test_app.get(
                '/messenger/webhook',
                params=params,
                expect_errors=True,
            )

            self.assertEqual(r.status_int, 400)
            self.assertNotEqual(r.text, self.challenge)

    def test_facebook_delivery_event_is_ignored(self):
        """
        Test that non-message webhook events are acknowledged without replies
        """
        data = {'object': 'page',
                'entry': [{'messaging': [{'sender': {'id': self.user_id},
                                          'delivery': {'mids': ['mid-1']}}]}]}
        r = self.post_signed_json(data)
        self.assertEqual(r.status_int, 200)

    def test_facebook_echo_message_is_ignored(self):
        calls = []
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        data = {'object': 'page',
                'entry': [{'messaging': [{
                    'sender': {'id': self.user_id},
                    'message': {'text': 'page reply', 'is_echo': True}
                }]}]}
        try:
            r = self.post_signed_json(data)
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(calls, [])

    def test_facebook_echo_does_not_hide_later_user_message(self):
        calls = []
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        data = {'object': 'page',
                'entry': [{'messaging': [
                    {'sender': {'id': self.user_id},
                     'message': {'text': 'page reply', 'is_echo': True}},
                    {'sender': {'id': 'user-2'},
                     'message': {'text': 'real user message'}}
                ]}]}
        try:
            r = self.post_signed_json(data)
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(calls, [('user-2', 'real user message')])

    def test_facebook_webhook_replies_to_valid_messages_in_order(self):
        calls = []
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        data = {'object': 'page',
                'entry': [
                    {'messaging': [
                        {'sender': {'id': 'user-1'},
                         'message': {'text': 'first', 'mid': 'batch-runtime-1'}},
                        {'sender': {'id': 'page'},
                         'message': {'text': 'echo', 'is_echo': True}},
                        {'sender': ['malformed'],
                         'message': {'text': 'ignored'}},
                    ]},
                    {'messaging': [
                        {'sender': {'id': 'ignored'},
                         'message': ['malformed']},
                        {'sender': {'id': 'user-2'},
                         'message': {'text': 'second', 'mid': 'batch-runtime-2'}}
                    ]}
                ]}
        try:
            r = self.post_signed_json(data)
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(calls, [('user-1', 'first'), ('user-2', 'second')])

    def test_facebook_webhook_caps_valid_message_batch(self):
        calls = []
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        events = [
            {'sender': {'id': 'user-{0}'.format(index)},
             'message': {'text': 'message-{0}'.format(index),
                         'mid': 'batch-cap-runtime-{0}'.format(index)}}
            for index in range(app.MAX_MESSENGER_MESSAGES_PER_WEBHOOK + 1)
        ]
        try:
            r = self.post_signed_json(
                {'object': 'page', 'entry': [{'messaging': events}]})
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(len(calls), app.MAX_MESSENGER_MESSAGES_PER_WEBHOOK)
        self.assertEqual(calls[0], ('user-0', 'message-0'))
        self.assertEqual(calls[-1], ('user-19', 'message-19'))

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
        calls = []
        original_reply = app.messenger_reply
        app.messenger_reply = lambda sender, message: calls.append(
            (sender, message))
        try:
            r = self.post_signed_json(
                self.data,
                content_type='Application/JSON; charset=UTF-8')
        finally:
            app.messenger_reply = original_reply

        self.assertEqual(r.status_int, 200)
        self.assertEqual(calls, [(self.user_id, 'testing 123')])

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
