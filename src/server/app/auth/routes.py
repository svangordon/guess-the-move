from app.auth import bp
from app import testing_options_dir

import os

from flask import current_app


# from secrets import password
import datetime
import itertools
from functools import wraps
import os

# import path
import string
import time

from flask_mail import Message
from flask_mail import Mail
from operator import itemgetter
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    session,
    make_response,
    send_from_directory,
)
from jinja2 import StrictUndefined
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt

# from app.model import (
#     Student,
#     StudentGroup,
#     Item,
#     Group,
#     GroupNote,
#     StudentItem,
#     StudentTestResult,
#     ReadingLevel,
#     connect_to_db,
#     db,
#     User,
# )


@bp.route("/register", methods=["POST"])
@cross_origin()
def add_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    hashed_password = generate_password_hash(password)
    existing_user_name = User.query.filter_by(username=username).first()
    existing_user_email = User.query.filter_by(email=email).first()
    if existing_user_name:
        return jsonify({"error": "username already in use"})
    if existing_user_email:
        return jsonify({"error": "email already in use"})
    new_user = User(
        public_id=str(uuid.uuid4()),
        username=username,
        email=email,
        password=hashed_password,
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"username": username})


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    auth_user = User.query.filter_by(username=username).first()
    if not auth_user:
        return jsonify({"error": "user does not exist"})
    if auth_user and check_password_hash(auth_user.password, password.encode("utf-8")):
        token = jwt.encode(
            {
                "public_id": auth_user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=365),
            },
            current_app.config["SECRET_KEY"],
        )
        return jsonify({"token": token.decode("utf-8"), "username": auth_user.username})
    else:
        return jsonify({"error": "incorrect password"})


@bp.route("/request-reset-password", methods=["POST"])
def request_reset_password():
    email = request.get_json()
    user = User.query.filter_by(email=email).first()
    user_created = str(user.created)
    user_created = user_created.replace(" ", "-")
    password_link = user.password + "-" + user_created
    msg = Message(
        "New password link",
        body=f"http://localhost:3000/reset-password/{password_link}/",
        sender="foo@gmail.com",
        recipients=[email],
    )
    return mail.send(msg)


@bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    new_password = data.get("password")
    user = data.get("user")
    old_password = user[0:-27]
    user = User.query.filter_by(password=old_password).first()
    if not user:
        return jsonify({"error": "try again"})
    hashed_password = generate_password_hash(new_password)
    user.password = hashed_password
    db.session.commit()
    return jsonify({"username": user.username})

