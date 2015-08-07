#!/usr/bin/env python
# coding=utf-8

import logging
from datetime import datetime
import http.server
import socketserver
import os
import shutil
from . import models
from .importer.votingimporter import fetch
from .utils import import_dump, dump_database, pushd
from .render import renderer

logger = logging.getLogger(__name__)
filename = 'build/data.sql'


def render():
    if not os.path.exists(filename):
        logger.error('There is no data to render!')
    # Flush existing dir
    if os.path.exists('build/site'):
        shutil.rmtree('build/site')

    os.makedirs('build/site')
    import_dump(models.database, filename)
    renderer.render()


def serve(host='0.0.0.0', port=8080):
    with pushd('build/site'):
        logger.info('Serve at http://{0}:{1}'.format(host, port))
        logger.info('Use Ctrl+C to quit')
        server_address = (host, port)
        httpd = http.server.HTTPServer(
            server_address, http.server.SimpleHTTPRequestHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt as e:
            logger.info('Stopped by user...')


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
