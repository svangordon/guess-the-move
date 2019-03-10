import datetime
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
    _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    _app.config["SQLALCHEMY_DATABASE_URI"] = db_client.uri
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


class TestChessPlayer:
    def test_create_player(self, client):
        with client.app_context():
            player = models.ChessPlayer(firstname="Paul", lastname="Morphy")
            assert player.get() is None  # Doesn't exist yet
            player.create()
            assert player.get() is not None


if True:

    class TestChessGame:
        def test_create_game(self, client):
            with client.app_context():
                player1 = models.ChessPlayer(firstname="James", lastname="McConnell")
                player1.create()
                player2 = models.ChessPlayer(firstname="Paul", lastname="Morphy")
                player2.create()
                game_date = datetime.date(1849, 1, 1)
                with open("./data/mcconnell_morphy_1849.pgn") as fp:
                    game_pgn = fp.read()

                game = models.ChessGame(
                    # white=player1.chessplayer_id,
                    # black=player2.chessplayer_id,
                    # date=game_date,
                    pgn=game_pgn
                )
                game.create(white=player1)
                # search_results = models.ChessGame.search(
                #     white=player1.chessplayer_id, black=player2.chessplayer_id
                # )
                # searched_game = search_results[0]
                # assert searched_game is not None
                # assert searched_game.pgn == game_pgn

                # print(searched_game.white)

                # white_player = searched_game

                # assert models.ChessPlayer(chessplayer_id=searched_game.white).get().firstname == player1.firstname
                # # game = models.ChessGame(date="1849", white=player2, black=player1, pgn=game_pgn, date=game_date)
