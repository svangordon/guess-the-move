import time
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
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

    def check_duplicate_email(self):
        duplicate_email = User.query.filter_by(email=self.email).first()
        return duplicate_email

    @property
    def unique(self):
        duplicate_email = User.query.filter_by(email=self.email).first()
        duplicate_username = self.query.filter_by(username=self.username).first()
        if duplicate_email or duplicate_username:
            return False
        return True

    def create(self):
        # # Check username to see if its unique
        if not self.unique:
            return False

        db.session.add(self)
        db.session.commit()
        return True

    @property
    def password(self):
        """Return the user's password. Will have been hashed by the setter."""

        return self._password

    @password.setter
    def password(self, password):
        self._password = ws.generate_password_hash(password)


class ChessPlayer(db.Model):
    """One of the chess players whose games we're analyzing. Paul Morphy,
    Mikhail Tal, etc."""

    __tablename__ = "chessplayers"

    chessplayer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    firstname = db.Column(
        db.String(64), nullable=True
    )  # Some people, like Greco or N.N., might only have one name
    lastname = db.Column(db.String(64), nullable=False)


class ChessGame(db.Model):
    """A record of a chess game played between two players. Fischer vs. Petrossian, etc."""

    __tablename__ = "chessgames"

    chessgame_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    event = db.Column(db.String(200), nullable=True, unique=False)
    site = db.Column(db.String(200), nullable=True, unique=False)
    date = db.Column(db.DateTime)
    round = db.Column(db.Integer)
    white = db.Column(db.Integer, db.ForeignKey("chessplayers.chessplayer_id"))
    black = db.Column(db.Integer, db.ForeignKey("chessplayers.chessplayer_id"))
    result = db.Column(db.Integer, db.ForeignKey("chessresults.chessresult_id"))


class ChessResult(db.Model):
    """Outcomes of chess games: win, loss, draw."""

    __tablename__ = "chessresults"

    chessresult_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    text = db.Column(db.String(10), nullable=False)


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

