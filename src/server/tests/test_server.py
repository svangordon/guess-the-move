import os
import tempfile

import pytest

from app import create_app, models
from app import app_db


@pytest.fixture
def client():
    db = app_db.App_Db("test")
    db.reset()
    app = create_app("test")

    client = app.test_client()

    yield client

    db.drop_db()


########
# Utils
########

#
# Login / logout
#
def login(client, username, password):
    return client.post(
        "/auth/login",
        json=dict(username=username, password=password),
        follow_redirects=True,
    ).get_json()


def logout(client):
    return client.get("/logout", follow_redirects=True)


#
# Registering new users
#
def register(client, username, email, password):
    return client.post(
        "/auth/register",
        json=dict(username=username, email=email, password=password),
        follow_redirects=True,
    ).get_json()


# def

# #
# # API
# #
# def get_items(client, token):
#     return client.get(
#         "api/item_list/words", headers={"x-access-token": token["token"]}
#     ).get_json()


# #########
# # Tests
# #########

# #
# # Login / logout
# #
# @pytest.mark.auth
# def test_login_logout(client):
#     """Make sure login and logout works."""

#     users = [["claude", "asdf"]]

#     for uname, pword in users:
#         # Test login
#         rv = login(client, uname, pword)
#         assert rv["username"] == "claude"

#         # Test that login catches bad usernames
#         rv = login(client, uname + "x", pword)
#         assert rv["error"] == "user does not exist"

#         # Test that the login catches bad passwords
#         rv = login(client, uname, pword + "x")
#         assert rv["error"] == "incorrect password"


# @pytest.mark.auth
# def test_register_user(client):
#     """Test registering a new user."""

#     new_users = [["bebop", "asdf", "bebop@doowop.com"]]

#     old_users = [
#         ["claude", "asdf", "asdfasdfasdf@asdf.com", "username already in use"],
#         ["boogie", "asdf", "asdf@asdf.com", "email already in use"],
#     ]

#     for uname, pword, email in new_users:
#         rv = register(client, uname, pword, email)
#         assert rv["username"] == uname

#     for uname, pword, email, error_message in old_users:
#         rv = register(client, uname, pword, email)
#         assert rv["error"] == error_message


# @pytest.mark.api
# def test_get_items(client):
#     token = login(client, "claude", "asdf")
#     rv = get_items(client, token)
#     assert rv == {
#         "itemType": "words",
#         "items": {
#             "./testing-options/words/dolch-2": [
#                 "always",
#                 "around",
#                 "because",
#                 "been",
#                 "before",
#                 "best",
#                 "both",
#                 "buy",
#                 "call",
#                 "cold",
#                 "does",
#                 "don't",
#                 "fast",
#                 "first",
#                 "five",
#                 "found",
#                 "gave",
#                 "goes",
#                 "green",
#                 "its",
#                 "made",
#                 "many",
#                 "off",
#                 "or",
#                 "pull",
#                 "read",
#                 "right",
#                 "sing",
#                 "sit",
#                 "sleep",
#                 "tell",
#                 "their",
#                 "these",
#                 "those",
#                 "upon",
#                 "us",
#                 "use",
#                 "very",
#                 "wash",
#                 "which",
#                 "why",
#                 "wish",
#                 "work",
#                 "would",
#                 "write",
#                 "your",
#             ],
#             "./testing-options/words/dolch-pre-primer": [
#                 "a",
#                 "and",
#                 "away",
#                 "big",
#                 "blue",
#                 "can",
#                 "come",
#                 "down",
#                 "find",
#                 "for",
#                 "funny",
#                 "go",
#                 "help",
#                 "here",
#                 "I",
#                 "in",
#                 "is",
#                 "it",
#                 "jump",
#                 "little",
#                 "look",
#                 "make",
#                 "me",
#                 "my",
#                 "not",
#                 "one",
#                 "play",
#                 "red",
#                 "run",
#                 "said",
#                 "see",
#                 "the",
#                 "three",
#                 "to",
#                 "two",
#                 "up",
#                 "we",
#                 "where",
#                 "yellow",
#                 "you",
#             ],
#             "./testing-options/words/dolch-primer": [
#                 "all",
#                 "am",
#                 "are",
#                 "at",
#                 "ate",
#                 "be",
#                 "black",
#                 "brown",
#                 "but",
#                 "came",
#                 "did",
#                 "do",
#                 "eat",
#                 "four",
#                 "get",
#                 "good",
#                 "have",
#                 "he",
#                 "into",
#                 "like",
#                 "must",
#                 "new",
#                 "no",
#                 "now",
#                 "on",
#                 "our",
#                 "out",
#                 "please",
#                 "pretty",
#                 "ran",
#                 "ride",
#                 "saw",
#                 "say",
#                 "she",
#                 "so",
#                 "soon",
#                 "that",
#                 "there",
#                 "they",
#                 "this",
#                 "too",
#                 "under",
#                 "want",
#                 "was",
#                 "well",
#                 "went",
#                 "what",
#                 "white",
#                 "who",
#                 "will",
#                 "with",
#                 "yes",
#             ],
#             "./testing-options/words/other-words": [
#                 "after",
#                 "also",
#                 "an",
#                 "any",
#                 "as",
#                 "back",
#                 "boy",
#                 "by",
#                 "can't",
#                 "could",
#                 "day",
#                 "eight",
#                 "even",
#                 "from",
#                 "girl",
#                 "give",
#                 "has",
#                 "her",
#                 "his",
#                 "how",
#                 "just",
#                 "last",
#                 "less",
#                 "may",
#                 "more",
#                 "most",
#                 "next",
#                 "nice",
#                 "nine",
#                 "of",
#                 "only",
#                 "other",
#                 "over",
#                 "people",
#                 "seven",
#                 "six",
#                 "small",
#                 "some",
#                 "ten",
#                 "than",
#                 "them",
#                 "then",
#                 "time",
#                 "way",
#                 "were",
#                 "when",
#                 "won't",
#                 "year",
#             ],
#         },
#     }


# @pytest.mark.api
# def test_create_items(client):
#     token = login(client, "claude", "asdf")

