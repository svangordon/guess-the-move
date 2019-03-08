from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_white_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player_white = db.relationship("Player", backref=db.backref("games", lazy=True))

    white_fname = db.Column(db.String(80), unique=False, nullable=False)
    white_lname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


# class Player(db.Model):
#     id = db.Column(db.Integer)
