import logging.config
import logging
import os
import json
from contextlib import contextmanager


def setup_logging(default_path='logging.json',
                  default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """
        Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def dump_database(database, filename):
    with open(filename, 'w') as buffer:
        for line in database.get_conn().iterdump():
            buffer.write('%s\n' % line)


def import_dump(database, filename):
    with open(filename, 'r') as f:
        database.get_cursor().executescript(f.read())


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)
