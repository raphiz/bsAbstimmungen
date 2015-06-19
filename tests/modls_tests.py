from nose.tools import *
from peewee import *
from playhouse.test_utils import test_database
from bsAbstimmungen.modls import User, Example

test_db = SqliteDatabase(':memory:')


def test_db_foo():
        models = (User, Example)
        with test_database(test_db, models):
            User.create(username='user-%d' % 1, password='1', email='f@b.com')
