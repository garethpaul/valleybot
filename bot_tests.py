import unittest
import bot
import nltk
import os
nltk.data.path.append(os.getcwd() + '/nltk_data')
from textblob import TextBlob
from webtest import TestApp

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

if __name__ == '__main__':
    unittest.main()
