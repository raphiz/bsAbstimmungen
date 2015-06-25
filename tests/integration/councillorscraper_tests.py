#!/usr/bin/env python
# coding=utf-8

from nose.tools import *
from bsAbstimmungen.importer.councillorimporter import CouncillorScraper
import vcr
import json


def test_happy_path():
    with vcr.use_cassette('build/fixtures/councillors.yaml'):
        scraper = CouncillorScraper()
        result = scraper.available_councillors()
        verification = json.load(open(
            'tests/data/names.json'
        ))

        all_names = result.keys()
        assert_equals(100, len(all_names))

        for expected in verification.values():
            assert_true(expected in all_names)
