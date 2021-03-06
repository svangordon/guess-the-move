import time
from datetime import datetime, timedelta

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
import jwt
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
import werkzeug.security as ws
import app

db = SQLAlchemy()


class User(db.Model):
    """User of chess website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    _password = db.Column("password", db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<User id={self.public_id} email={self.email}>"

    @property
    def duplicate_email(self):
        q = self.query.filter(User.email == self.email)
        return db.session.query(q.exists()).first()[0]

    @property
    def duplicate_username(self):
        q = self.query.filter(User.username == self.username)
        return db.session.query(q.exists()).first()[0]

    @property
    def exists(self):
        """Check to see if a user is already registered in the database."""
        # duplicate_email = User.query.filter_by(email=self.email).first()
        # duplicate_username = self.query.filter_by(username=self.username).first()
        if self.duplicate_email or self.duplicate_username:
            return True
        return False

    def create(self):
        """Add the user to the db."""
        # # Check username to see if its unique
        if self.exists:
            raise ValueError("Trying to add duplicate user.")

        self.password = self._hashed_password
        db.session.add(self)
        db.session.commit()
        return True

    def login(self):
        if not self.exists:
            raise ValueError("User does not exist.")
        #     return jsonify({"error": "user does not exist"})

        auth_user = (
            User.get(username=self.username)
            if self.username
            else User.get(email=self.email)
        )

        if ws.check_password_hash(auth_user.password, self.password.encode("utf-8")):
            token = jwt.encode(
                {
                    "public_id": auth_user.public_id,
                    "exp": datetime.utcnow() + timedelta(days=365),
                },
                current_app.config["SECRET_KEY"],
            )
            return {"token": token.decode("utf-8"), "username": auth_user.username}

        return {
            "error": "Could not log in.",
            "they": auth_user.password,
            "you": self.password.encode("utf-8"),
            "result": ws.check_password_hash(
                auth_user.password, self.password.encode("utf-8")
            ),
        }

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @property
    def password(self):
        """Return the user's password. Will have been hashed by the setter."""

        return self._password

    @property
    def _hashed_password(self):
        return ws.generate_password_hash(self._password)

    @password.setter
    def password(self, password):
        self._password = password
        # self._password = ws.generate_password_hash(password)


class ChessPlayer(db.Model):
    """One of the chess players whose games we're analyzing. Paul Morphy,
    Mikhail Tal, etc."""

    __tablename__ = "chessplayers"

    chessplayer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    firstname = db.Column(
        db.String(64), nullable=True
    )  # Some people, like Greco or N.N., might only have one name
    lastname = db.Column(db.String(64), nullable=False)

    games = relationship("ChessGame", secondary="game_player_link")

    # games = db.relationship("ChessGame", secondary="chess_game_players")

    # chessgameplayers = db.relationship(
    #     "ChessGamePlayers", cascade="save-update, merge, delete"
    # )

    def create(self):
        db.session.add(self)
        db.session.commit()

    # @classmethod
    def get(self):
        return self.query.filter_by(
            firstname=self.firstname, lastname=self.lastname
        ).first()

    @classmethod
    def search(cls, **kwargs):
        return cls.query.filter_by(**kwargs).all()


class ChessGamePlayerLink(db.Model):
    """Association table to join games and players."""

    __tablename__ = "game_player_link"

    gameplayer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    player_id = db.Column(
        db.Integer, db.ForeignKey("chessplayers.chessplayer_id"), primary_key=True
    )
    game_id = db.Column(
        db.Integer, db.ForeignKey("chessgames.chessgame_id"), primary_key=True
    )

    # player = db.relationship(backref=db.backref(""))

    # white_id = db.Column(db.Integer, db.ForeignKey("chessplayers.chessplayer_id"))
    # black_id = db.Column(db.Integer, db.ForeignKey("chessplayers.chessplayer_id"))
    # chessgame_id = db.Column(db.Integer, db.ForeignKey("chessgames.chessgame_id"))

    # # white = db.relationship("ChessPlayer", foreign_keys=[white_id])
    # # black = db.relationship("ChessPlayer", foreign_keys=[black_id])

    # # chessplayers = db.relationship("ChessPlayer")
    # white = db.relationship("ChessPlayer", foreign_keys=[white_id])
    # black = db.relationship("ChessPlayer", foreign_keys=[black_id])
    # # chessplayers = db.relationship("ChessPlayer", foreign_keys=[white_id, black_id])
    # chessgames = db.relationship("ChessGame")
    # def create(self):
    #     db.session.add(self)
    #     db.session.commit()


class ChessGame(db.Model):
    """A record of a chess game played between two players. Fischer vs. Petrossian, etc."""

    __tablename__ = "chessgames"

    chessgame_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # chessgameplayers_id = db.Column(
    #     db.Integer, db.ForeignKey("chessgameplayers.chessgameplayers_id")
    # )
    event = db.Column(db.String(200), nullable=True, unique=False)
    site = db.Column(db.String(200), nullable=True, unique=False)
    date = db.Column(db.DateTime)
    round = db.Column(db.Integer, nullable=True)

    players = relationship(ChessPlayer, secondary="game_player_link")

    # white_id = db.Column(db.Integer, db.ForeignKey("chessplayer.chessplayer_id"))
    # black_id = db.Column(db.Integer, db.ForeignKey("chessplayer.chessplayer_id"))

    # white = db.relationship("ChessPlayer", foreign_keys=[white_id])
    # black = db.relationship("ChessPlayer", foreign_keys=[black_id])

    # result = db.Column(db.Integer, db.ForeignKey("chessresults.chessresult_id"))
    pgn = db.Column(db.String(2048))

    # players = db.relationship(ChessPlayer, secondary=ChessGamePlayers)

    # chessgameplayers = db.relationship(
    #     "ChessGamePlayers", cascade="save-update, merge, delete"
    # )

    def create(self, white, black=None):
        # Create the association table
        db.session.add(self)
        # db.session.commit()
        game_players = ChessGamePlayers(
            white_id=white.chessplayer_id,
            # black_id=black.chessplayer_id,
            chessgame_id=self.chessgame_id,
        )
        # add the chess game
        db.session.add(game_players)
        db.session.commit()

    def get(self):
        return self.query.filter_by(chessgame_id=self.chessgame_id).first()

    # @classmethod
    # def search(cls, **kwargs):
    #     return ChessGamePlayers.query.filter_by(**kwargs).all()


class ChessResult(db.Model):
    """Outcomes of chess games: win, loss, draw."""

    __tablename__ = "chessresults"

    chessresult_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    text = db.Column(db.String(10), nullable=False)


# Some simple associative boilerplate we're dropping in
class Department(db.Model):
    __tablename__ = "department"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    employees = relationship("Employee", secondary="department_employee_link")


class Employee(db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    hired_on = db.Column(db.DateTime, default=func.now())
    departments = relationship(Department, secondary="department_employee_link")


class DepartmentEmployeeLink(db.Model):
    __tablename__ = "department_employee_link"
    department_id = db.Column(
        db.Integer, db.ForeignKey("department.id"), primary_key=True
    )
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), primary_key=True)


# class Student(db.Model):
#     """table of students"""

#     __tablename__ = "students"

#     student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     name = db.Column(db.String(64), nullable=False)

#     users = db.relationship("User")
#     studentitems = db.relationship("StudentItem", cascade="save-update, merge, delete")
#     studentgroups = db.relationship(
#         "StudentGroup", cascade="save-update, merge, delete"
#     )
#     readinglevels = db.relationship(
#         "ReadingLevel", cascade="save-update, merge, delete"
#     )
#     studenttestresults = db.relationship(
#         "StudentTestResult", cascade="save-update, merge, delete"
#     )

#     def __repr__(self):
#         return f"<Student student_id={self.student_id} first_name={self.name}>"


# class ReadingLevel(db.Model):
#     __tablename__ = "readinglevels"
#     reading_level_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     student_id = db.Column(
#         db.Integer, db.ForeignKey("students.student_id"), nullable=False, unique=True
#     )
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     reading_level = db.Column(db.String(25), nullable=False)
#     update_date = db.Column(
#         db.DateTime, nullable=True, default=db.func.current_timestamp()
#     )

#     # update_date = db.Column(db.DateTime, server_default=func.now())

#     students = db.relationship("Student")
#     users = db.relationship("User")


# class Group(db.Model):
#     __tablename__ = "groups"
#     group_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     group_name = db.Column(db.String(100), nullable=False, unique=True)
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     users = db.relationship("User")
#     studentgroups = db.relationship(
#         "StudentGroup", cascade="save-update, merge, delete"
#     )
#     groupnotes = db.relationship("GroupNote", cascade="save-update, merge, delete")


# class StudentGroup(db.Model):
#     __tablename__ = "studentgroups"
#     student_group_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     student_id = db.Column(
#         db.Integer, db.ForeignKey("students.student_id"), nullable=False
#     )
#     group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"), nullable=False)
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     students = db.relationship("Student")
#     users = db.relationship("User")
#     groups = db.relationship("Group")


# class GroupNote(db.Model):
#     __tablename__ = "groupnotes"
#     group_notes_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"), nullable=False)
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     note = db.Column(db.String(200), nullable=False, unique=True)
#     date_added = db.Column(db.DateTime, nullable=False, default=datetime.today)
#     users = db.relationship("User")
#     groups = db.relationship("Group")


# class Item(db.Model):
#     """table of items"""

#     __tablename__ = "items"
#     item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     item_type = db.Column(db.String(25), nullable=False)
#     item = db.Column(db.String(25), nullable=False)
#     date_added = db.Column(db.DateTime, nullable=False, default=datetime.today)
#     # date_added = db.Column(db.DateTime, nullable=False, default=time.time)
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     custom = db.Column(db.Boolean, unique=False, default=False)
#     studentitems = db.relationship("StudentItem", cascade="save-update, merge, delete")
#     users = db.relationship("User")

#     def __repr__(self):
#         return f"<Item item_id={self.item_id} item={self.item}>"


# class StudentItem(db.Model):
#     """table of student items"""

#     __tablename__ = "studentitems"

#     student_item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
#     student_id = db.Column(
#         db.Integer, db.ForeignKey("students.student_id"), nullable=False
#     )
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     item_type = db.Column(db.String(25), nullable=False)
#     added_to_student = db.Column(db.DateTime, nullable=False, default=datetime.today)
#     correct_count = db.Column(db.Integer, default=0, nullable=True)
#     incorrect_count = db.Column(db.Integer, default=0, nullable=True)
#     Learned = db.Column(db.Boolean, unique=False, default=False)

#     students = db.relationship("Student")
#     items = db.relationship("Item")
#     users = db.relationship("User")

#     def __repr__(self):
#         return f"<StudentItem student_item_id={self.student_item_id}>"


# class StudentTestResult(db.Model):
#     """table of student tests"""

#     __tablename__ = "studenttestresults"

#     student_test_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     student_id = db.Column(
#         db.Integer, db.ForeignKey("students.student_id"), nullable=False
#     )
#     user_id = db.Column(db.String(50), db.ForeignKey("users.public_id"), nullable=False)
#     test_type = db.Column(db.String(25), nullable=False)
#     score = db.Column(db.Float)
#     test_date = db.Column(db.DateTime, nullable=True, default=datetime.today)
#     correct_items = db.Column(db.ARRAY(db.String(25)))
#     incorrect_items = db.Column(db.ARRAY(db.String(25)))

#     students = db.relationship("Student")
#     users = db.relationship("User")

#     def __repr__(self):
#         return f"<StudentTestResults student_test_id={self.student_test_id}>"

#     # def __repr__(self):
#     #     return f"<StudentTestResults student_test_id={self.student_test_id}>"


# def connect_to_db(app):
#     """Connect the database to our Flask app."""
#     app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///students"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#     db.app = app
#     db.init_app(app)


# if __name__ == "__main__":
#     from server import app

#     connect_to_db(app)
#     print("Connected to DB.")

