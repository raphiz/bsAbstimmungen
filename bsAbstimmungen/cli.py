#!/usr/bin/env python
# coding=utf-8

import logging
from datetime import datetime
import os
from . import models
from .importer.votingimporter import fetch
from .utils import import_dump, dump_database


logger = logging.getLogger(__name__)
filename = 'data.sql'


def import_data():
    if os.path.exists(filename):
        import_dump(models.database, filename)
    else:
        models.create_tables()

    # Fetch the data....
    t = datetime(year=2014, month=2, day=28)
    f = datetime(year=2014, month=2, day=1)
    fetch(f, t)

    # Dump the imported data
    dump_database(models.database, 'data.sql')
