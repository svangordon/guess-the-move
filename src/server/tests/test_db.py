import os
import tempfile

import pytest

from app import create_app, models

# import app.db
from app import app_db


@pytest.fixture
def client():
    db_client = app_db.DbAdmin("test")
    db_client.drop_db()
    db_client.create_db()
    db_client.init_db()
    # app = app.create_app("test")

    # client = app.test_client()

    yield db_client

    db_client.drop_db()


# @pytest.fixture
# def hash_password():


@pytest.mark.parametrize(
    "username,email,password", [("claude", "asdf@asdf.com", "my_passwrd")]
)
def test_hash_password(username, email, password):
    user = models.User(username=username, email=email, password=password)
    print("User password, hashed: ", user.password)
    assert user.password != password


@pytest.mark.parametrize(
    "username,email,password", [("claude", "asdf@asdf.com", "my_passwrd")]
)
def test_create_user(client, username, email, password):
    user = models.User(username=username, email=email, password=password)
    user.create()
