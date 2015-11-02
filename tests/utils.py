# from peewee import SqliteDatabase
# from playhouse.test_utils import test_database
# import functools
from pymongo import MongoClient
import pytest


@pytest.fixture
def mockdb():
    client = MongoClient('127.0.0.1', 27017, serverSelectionTimeoutMS=0)
    if 'bsabstimmungen_test' in client.database_names():
        client.drop_database('bsabstimmungen_test')
    return client.bsabstimmungen_test
