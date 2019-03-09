import os

from flask import Flask


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

# from app.model import Student, StudentGroup, Item, Group, GroupNote, StudentItem, StudentTestResult, ReadingLevel, connect_to_db, db, User
from app import models

testing_options_dir = "./testing-options"
tablenames = ["users", "chessplayers", "chessgames", "chessresults"]
duplicate_user = 1

def create_app(db_name):
    mail = None
    template_dir = os.path.abspath("../../client/build")
    static_dir = os.path.abspath("../../client/build/static")
    app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    api = Api(app)
    app.debug = True
    app.config["SECRET_KEY"] = "super-secret"

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///{}".format(db_name)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # db.app = app
    models.db.init_app(app)

    # These are all things that will be moved to their own files, eventually
    app.config.update(
        # EMAIL SETTINGS
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_SSL=False,
        MAIL_USERNAME="foo@gmail.com",
        # MAIL_PASSWORD = os.environ['PASSWORD'],
        MAIL_SUPPRESS_SEND=False,
        MAIL_DEFAULT_SENDER="foo@gmail.com",
        MAIL_USE_TLS=True,
        TESTING=False,
        MAIL_DEBUG=True,
        MAIL_FAIL_SILENTLY=False,
    )
    # mail = Mail(app)

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    # from app import routes

    return app

