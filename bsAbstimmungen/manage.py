#!/usr/bin/env python
# coding=utf-8

import logging
from datetime import datetime
import os
from . import models
from .importer.votingimporter import fetch
from .utils import import_dump, dump_database


logger = logging.getLogger(__name__)
filename = 'build/data.sql'


def import_data(from_date, to_date):
    if os.path.exists(filename):
        logger.info('Importing existing data...')
        import_dump(models.database, filename)
    else:
        logger.info('Setting up schema....')
        models.create_tables()

    # Fetch the data....
    fetch(from_date, to_date)

    # Dump the imported data
    logger.info('Exporting data...')
    dump_database(models.database, filename)
