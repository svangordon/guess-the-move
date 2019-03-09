import os
import sqlalchemy
import sqlalchemy_utils

# import pandas as pd

import app.models
from app import tablenames

# import server


class DbAdmin(object):
    def __init__(self, db_name, output_dir="seed-data"):
        self.db_name = db_name
        self.output_dir = output_dir

    @property
    def uri(self):
        # return "postgresql:///{}".format(self.db_name)
        return "postgresql+psycopg2:///{}".format(self.db_name)

    @property
    def engine(self):
        return sqlalchemy.create_engine(self.uri)

    def create_db(self):
        try:
            sqlalchemy_utils.create_database(self.engine.url)
        except sqlalchemy.exc.ProgrammingError:
            print("Cannot drop db: '{}'.".format(self.db_name))

    def drop_db(self):
        try:
            sqlalchemy_utils.drop_database(self.engine.url)
        except sqlalchemy.exc.ProgrammingError:
            # That db doesn't exist, which is fine
            print("Cannot drop db: '{}'.".format(self.db_name))

    # def dump_data(self):
    #     for tablename in tablenames:
    #         tb = pd.read_sql_table(tablename, self.engine)
    #         tb.to_csv(os.path.join(self.output_dir, tablename), index=False)

    def init_db(self):
        app.models.db.Model.metadata.create_all(bind=self.engine)

    # def load_data(self):
    #     uri = "postgresql+psycopg2:///{}".format(self.db_name)
    #     engine = sqlalchemy.create_engine(uri)
    #     for tablename in tablenames:
    #         tb = pd.read_csv(os.path.join(self.output_dir, tablename))
    #         tb.drop(
    #             tb.columns[[0]], axis=1, inplace=True
    #         )  # Drop the first column, id's, to not break autoincrement
    #         tb.to_sql(tablename, engine, if_exists="append", index=False)

    def reset(self):
        try:
            self.drop_db()
        except sqlalchemy.exc.OperationalError:
            pass

        self.create_db()
        self.init_db()
        self.load_data()

    def start(self):
        self.create_db()
        self.init_db()
        self.load_data()


if __name__ == "__main__":
    pass
    # students_db = App_Db("students")
    # students_db.reset()
    # students_db.drop_db()
    # students_db.create_db()
    # students_db.init_db()
    # students_db.load_data()
