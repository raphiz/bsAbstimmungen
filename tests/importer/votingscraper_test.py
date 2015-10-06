#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
from bsAbstimmungen.importer.votingimporter import VotingScraper
import vcr


def test_happy_path():
    with vcr.use_cassette('build/fixtures/voting.yaml'):
        t = datetime(year=2014, month=2, day=28)
        f = datetime(year=2014, month=2, day=1)
        scraper = VotingScraper()
        result = scraper.find(f, t)
        assert 29 == len(result)
