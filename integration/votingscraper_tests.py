#!/usr/bin/env python
# coding=utf-8

from nose.tools import *
from datetime import datetime
from bsAbstimmungen.importer.votingimporter import VotingScraper


# TODO: test each sub method!
def test_happy_path():
    t = datetime(year=2014, month=2, day=28)
    f = datetime(year=2014, month=2, day=1)
    scraper = VotingScraper()
    result = scraper.find(f, t)
    assert_equal(29, len(result))
