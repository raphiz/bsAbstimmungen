
from peewee import *

database = SqliteDatabase('db.db')


class BaseModel(Model):
    class Meta:
        database = database


class Example(BaseModel):
    username = CharField(unique=True)


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
