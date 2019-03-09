import os
import tempfile

from flask import Flask, jsonify
import pytest

from app import create_app, models

# import app.db
from app import app_db


@pytest.fixture
def client():
    db_client = app_db.DbAdmin("test")
    db_client.drop_db()
    db_client.create_db()

    _app = Flask(__name__)
    _app.config["SECRET_KEY"] = b"a dark and terrible secret"
    models.db.init_app(_app)
    with _app.app_context():
        models.db.create_all()

    yield _app
    # db_client.init_db()
    # app = create_app("test")

    # _app = Flask(__name__)
    # models.db.init_app(_app)
    with _app.app_context():
        models.db.drop_all()

    # client = app.test_client()

    # yield db_client

    db_client.drop_db()


# @pytest.fixture
# def hash_password():


class TestUser:
    @pytest.mark.parametrize(
        "username,email,password", [("claude", "asdf@asdf.com", "my_passwrd")]
    )
    def test_hash_password(self, username, email, password):
        user = models.User(username=username, email=email, password=password)
        print("User password, hashed: ", user.password)
        assert user._hashed_password != password

    # @pytest.mark.parametrize(
    #     "username,email,password", [("claude", "asdf@asdf.com", "my_passwrd")]
    # )
    def test_duplicate(self, client):
        with client.app_context():
            user = models.User(
                username="claude", email="asdf@asdf.com", password="my_passwrd"
            )
            assert user.duplicate_email is False
            assert user.duplicate_username is False
            assert user.exists is False
            user.create()
            assert user.exists is True
            with pytest.raises(ValueError):
                user.create()

    @pytest.mark.parametrize(
        "username,email,password", [("claude", "asdf@asdf.com", "my_passwrd")]
    )
    def test_create_user(self, client, username, email, password):
        with client.app_context():
            user = models.User(username=username, email=email, password=password)
            user.create()
            # assert user.get(username=username).username == user.username
            user.exists is True
            assert models.User.get(username=username).username == user.username
            assert models.User.get(email=email).email == user.email

    @pytest.mark.parametrize(
        "username,email,password", [("claude", "asdf@asdf.com", "my_passwrd")]
    )
    def test_login_user(self, client, username, email, password):
        with client.app_context():
            user = models.User(username=username, email=email, password=password)
            with pytest.raises(ValueError):
                user.login()
            # assert user.login()["error"] == "user does not exist"
            user.create()
            user = models.User(username=username, email=email, password=password)
            result = user.login()
            assert "error" not in result
            assert "token" in result
