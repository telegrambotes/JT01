import os
import threading

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config


def start() -> scoped_session:
    engine = create_engine(Config.DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()

INSERTION_LOCK = threading.RLock()

class Thumbnail(BASE):
    __tablename__ = "thumbnail"
    id = Column(Integer, primary_key=True)
    msg_id = Column(Integer)
    
    def __init__(self, id, msg_id):
        self.id = id
        self.msg_id = msg_id

Thumbnail.__table__.create(checkfirst=True)

async def df_thumb(id, msg_id):
    with INSERTION_LOCK:
        msg = SESSION.query(Thumbnail).get(id)
        if not msg:
            msg = Thumbnail(id, msg_id)
            SESSION.add(msg)
            SESSION.flush()
        else:
            SESSION.delete(msg)
            file = Thumbnail(id, msg_id)
            SESSION.add(file)
        SESSION.commit()

async def del_thumb(id):
    with INSERTION_LOCK:
        msg = SESSION.query(Thumbnail).get(id)
        SESSION.delete(msg)
        SESSION.commit()

async def thumb(id):
    try:
        t = SESSION.query(Thumbnail).get(id)
        return t
    finally:
        SESSION.close()


##############################

import pymongo, os
from config import DB_URI, DB_NAME


dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]


user_data = database['users']



async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return
