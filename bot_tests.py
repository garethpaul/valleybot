import unittest
import bot
import nltk
import os
nltk.data.path.append(os.getcwd() + '/nltk_data')
from textblob import TextBlob
from webtest import TestApp
import json
import app

test_app = TestApp(app.app)


class BotTest(unittest.TestCase):

    def setUp(self):
        pass

    def testGreeting(self):
        greeting = TextBlob("hello there")
        self.assertTrue(bot.check_for_greeting(greeting))

    def testVowel(self):
        word = "acorn"
        self.assertTrue(bot.starts_with_vowel(word))

    def testJson(self):
        json_payload = {"data": "hello iam good?"}
        self.assertTrue(bot.json_request(json_payload=json_payload,
                                         context=None))

    def testPronoun(self):
        sentence = TextBlob("On saturday I will meet joe.")
        pronoun = bot.find_pronoun(sentence)
        self.assertEqual(pronoun, "You")

    def testVerb(self):
        sentence = TextBlob("She smells the pizza.")
        r = bot.find_verb(sentence)
        self.assertEqual(r[0], "smells")

    def testNoun(self):
        sentence = TextBlob("She smells the pizza.")
        r = bot.find_noun(sentence)
        self.assertEqual(r, "pizza")

    def testAdjective(self):
        sentence = TextBlob("This shop is much nicer")
        r = bot.find_adjective(sentence)
        self.assertEqual(r, "much")

    def testConstructResp(self):
        sentence = TextBlob("What a beautiful car, you look great")
        pronoun = bot.find_pronoun(sentence)
        noun = bot.find_noun(sentence)
        verb = bot.find_verb(sentence)
        r = bot.construct_response(pronoun, noun, verb)
        self.assertTrue("car" in r)


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
                                 {'text': 'do you work in finance'})
        self.assertEqual(response.status_int, 200)
        self.assertTrue(len(response.body) >= 1)


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
        r = test_app.post_json('/messenger/webhook', self.data)
        self.assertEqual(r.status_int, 200)

    def test_facebook_response(self):
        """
        A test to send a FB message test
        """
        r = app.messenger_reply(self.user_id, "hello this is a test")
        self.assertTrue(len(r) >= 1)
        self.assertTrue(json.loads(r)['recipient_id'] == self.user_id)

    def test_facebook_challenge(self):
        """
        Test that the webhook returns a challenge
        """
        r = test_app.get('/messenger/webhook?hub.challenge=' + self.challenge)
        self.assertTrue(r.body == self.challenge)

if __name__ == '__main__':
    unittest.main()
