#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

# Sentences we'll respond with if the user greeted us
GREETING_KEYWORDS = ("hello", "hi", "greetings", "hey",)
GREETING_RESPONSES = ["AMAZING! Haven't seen you in ages!",
                      "hey, i'm so busy!", "*nods*",
                      "hey you get my snap?"]

SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "Were you aware I was a serial entrepreneur in the {noun} sector?",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
    "We were just talking about {noun}!",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My team always ask me about {noun}",
    "I wrote the wikipedia page about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]

# Sentences we'll respond with if we have no idea what the user just said
NONE_RESPONSES = [
    "oh that's awesome!",
    "want to grab some coffee at blue bottle?",
    "we should hang out sometime",
    "I can't believe how cold it is",
    "Don't get me started on the house prices in this city",
    "Tahoe was great last weekend",
]


# If the user tries to tell us something about ourselves, use one of these responses
COMMENTS_ABOUT_SELF = [
    "Yeah I have {} new followers now".format(random.randint(300, 500)),
    "I worked really hard on that",
    "My Klout score is {}".format(random.randint(100, 500)),
]


FILTER_WORDS = set([
    "skank",
    "wetback",
    "bitch",
    "cunt",
    "dick",
    "douchebag",
    "dyke",
    "fag",
    "nigger",
    "tranny",
    "trannies",
    "paki",
    "pussy",
    "retard",
    "slut",
    "titt",
    "tits",
    "wop",
    "whore",
    "chink",
    "fatass",
    "shemale",
    "nigga",
    "daygo",
    "dego",
    "dago",
    "gook",
    "kike",
    "kraut",
    "spic",
    "twat",
    "lesbo",
    "homo",
    "fatso",
    "lardass",
    "jap",
    "biatch",
    "tard",
    "gimp",
    "gyp",
    "chinaman",
    "chinamen",
    "golliwog",
    "crip",
    "raghead",
    "negro",
    "hooker"])
