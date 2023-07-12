import pandas as pd
from github import Github
import base64
import os
import sqlite3
import streamlit as st
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine, Column, Integer, String, Sequence, Float, PrimaryKeyConstraint, ForeignKey, \
    Boolean, DateTime, UniqueConstraint

pd.options.display.max_columns = None
pd.options.display.max_rows = None
Base = declarative_base()

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")

# get the current working directory
cwd = os.getcwd()

# check if the app directory exists
# if os.path.exists(os.path.join(cwd, "app")):
#     app_dir = os.path.join(cwd, "app")
#     logging.info("The app directory is located at:", app_dir)
# else:
#     logging.info("The app directory does not exist in the current directory.")

# g = Github("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")
# repo = g.get_repo("Devsixth/TeleNinja")
# file_path = "DBEngine.db"
# contents = repo.get_contents(file_path)
# file_content = contents.content.encode("utf-8")
# decoded_content = base64.b64decode(file_content)
# with open("database.db", "wb") as f:
#     f.write(decoded_content)
#     db_file_path = os.path.abspath("database.db")
#     logging.info(db_file_path)
#     st.write(db_file_path)
# # Connect to the database


class NinjaCalls(Base):
    __tablename__ = "NinjaCalls"
    SNo = Column(Integer, primary_key=True, autoincrement=True)
    Date = Column(String)
    Symbol = Column(String)
    Segment = Column(String)
    Signal = Column(String)
    Rate = Column(Float)
    SL = Column(Float)
    TGT = Column(Float)
    Closure = Column(String)
    ExitAt = Column(String)
    ExitRate = Column(Float)
    EntryAt = Column(String)
    QTY = Column(Integer)
    Mon = Column(String)


class DBManager(object):
    __shared_instance = 'DBManager'

    @staticmethod
    def instance():
        if DBManager.__shared_instance == 'DBManager':
            DBManager()
        return DBManager.__shared_instance

    def __init__(self):
        if DBManager.__shared_instance != 'DBManager':
            raise Exception("This class is a singleton class !")
        else:
            self.create_engine()
            self.register_tables()
            DBManager.__shared_instance = self

    def create_engine(self):
        # self.engine = create_engine(f'sqlite:///{file_path}')
        """add the downloaded database file path"""
        self.engine = create_engine(r'sqlite:///DBEngine.db')
        self.register_tables()
        self.create_session()

    def register_tables(self):
        NinjaCalls.__table__.create(bind=self.engine, checkfirst=True)

    def get_engine(self):
        return self.engine

    def create_session(self):
        Session = sessionmaker(bind=self.get_engine())
        self.session = Session()

    def get_session(self):
        return self.session


class DB(object):
    dbm = None

    def __init__(self):
        self.dbm = DBManager.instance()

    def get_engine(self):
        return self.dbm.get_engine()

    def get_session(self):
        return self.dbm.get_session()


class NinjaManager(DB):
    def __init__(self):
        super(NinjaManager, self).__init__()

    def get_all_customers(self):
        result1 = self.dbm.get_session().query(NinjaCalls).all()
        return result1


if __name__ == "__main__":
    nm = NinjaManager()

    # q = tm.get_session().query(Customer).filter(Customer.txns.has(Transaction.tgt_status == 'Open'))
    # df = pd.read_sql(q.statement,tm.get_session().bind)
    # print(df.shape)
    # print(df)

    # q = tm.get_session().query(Transaction)
    # q = q.where((Transaction.tgt_status == "Open"))

# tm.create_engine()
# print(tm.get_engin())
