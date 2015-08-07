#!/usr/bin/env python
# coding=utf-8

from invoke import run, task
from datetime import datetime
import os


@task(name='import', help={
    'from-date': "The first date to importing data from (eg. 24.03.2015)",
    'to-date': "The last date to import data from (eg. 24.03.2015)"}
)
def import_data(from_date, to_date):
    from bsAbstimmungen import manage

    from_date = datetime.strptime(from_date, '%d.%m.%Y')
    to_date = datetime.strptime(to_date, '%d.%m.%Y')

    manage.import_data(from_date, to_date)


@task
def serve(host='0.0.0.0', port=8080):
    from bsAbstimmungen import manage
    manage.serve(host, port)


@task
def render():
    from bsAbstimmungen import manage
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
