import os
import tempfile

import pytest

from app import create_app, models

# import app.db
from app import app_db


@pytest.fixture
def client():
    db_client = app_db.App_Db("test")
    db_client.drop_db()
    db_client.create_db()
    # app = create_app("test")

    # client = app.test_client()

    yield db_client

    db.drop_db()


def test_hash_password():
    from app.auth import hash_password


# def test_create_user():
#     username = "claude"
#     app.db.create_user(username=username, email=email, password=hashed_password)
