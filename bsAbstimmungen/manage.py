#!/usr/bin/env python
# coding=utf-8

import logging
from datetime import datetime
from pymongo import MongoClient
import http.server
import socketserver
import os
import shutil
from .importer.votingimporter import fetch
from .utils import pushd
from .render import renderer

logger = logging.getLogger(__name__)


client = MongoClient('localhost', 27017)
db = client.bsabstimmungen


def render():
    # TODO: check if DB is empty!

    # Flush existing dir
    if os.path.exists('build/site'):
        shutil.rmtree('build/site')

    os.makedirs('build/site')
    renderer.render(db)


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
    # Fetch the data....
    fetch(db, from_date, to_date)
