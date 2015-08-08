#!/usr/bin/env python
# coding=utf-8

import os
import sys
from datetime import datetime

from invoke import run, task
from invoke.util import log

from bsAbstimmungen.utils import setup_logging
from bsAbstimmungen import manage


@task
def test():
    run('py.test tests/ --pep8 --cov bsAbstimmungen --cov-report term-missing')


@task(name='import', help={
    'from-date': "The first date to importing data from (eg. 24.03.2015)",
    'to-date': "The last date to import data from (eg. 24.03.2015)"}
)
def import_data(from_date, to_date):
    from_date = datetime.strptime(from_date, '%d.%m.%Y')
    to_date = datetime.strptime(to_date, '%d.%m.%Y')

    manage.import_data(from_date, to_date)


@task
def serve(host='0.0.0.0', port=8080):
    manage.serve(host, port)


@task
def clean():
    run('find . -name *.pyc -delete')
    run('find . -name *.pyo -delete')
    run('find . -name *~ -delete')
    run('find . -name __pycache__ -delete')
    run('find . -name .coverage -delete')
    run('rm -rf dist/')
    run('rm -rf .cache/')
    run('rm -rf .eggs/')
    run('rm -rf bsAbstimmungen.egg-info')
    run('rm -rf build/')
    log.info('cleaned up')


@task
def render():
    manage.render()


@task
def release(push_tags=False):
    # Are you sure to release?
    try:
        input("Is everything commited? Are you ready to release? "
              "Press any key to continue - abort with Ctrl+C")
    except KeyboardInterrupt as e:
        print("Release aborted...")
        exit()

    run('bumpversion --message "Release version {current_version}" '
        '--no-commit release')
    run('python setup.py sdist bdist_wheel')
    run('bumpversion --message "Preparing next version {new_version}" '
        '--no-tag patch')

    # Push tags if enabled
    if push_tags:
        run('git push origin master --tags')
    else:
        print("Don't forget to push the tags (git push origin master --tags)!")


# Setup logging
setup_logging()

# Warn the user when not using virtualenv
if not hasattr(sys, 'real_prefix'):
    print('YOU ARE NOT RUNNING INSIDE A VIRTUAL ENV!')
