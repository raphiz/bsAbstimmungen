from bsAbstimmungen import models
from peewee import SqliteDatabase
from playhouse.test_utils import test_database
import functools


def mockdb(fn):
    """
    This is a simple decorator that sets up a mocked DB for testing...
    """
    @functools.wraps(fn)
    def inner():
        test_db = SqliteDatabase(':memory:')
        with test_database(test_db, models.BaseModel.__subclasses__()):
            x = fn()
        return x
    return inner
