#!/usr/bin/env python
# coding=utf-8

from bsAbstimmungen.importer.councillorimporter import CouncillorScraper
import vcr
import json


def test_details():
    url = ('http://www.grosserrat.bs.ch/de/mitglieder-gremien/'
           'mitglieder-a-z?such_kategorie=5&content_detail=3323')
    with vcr.use_cassette('build/fixtures/councillor_details.yaml'):
        scraper = CouncillorScraper()
        result = scraper.details(url)


def test_available():
    with vcr.use_cassette('build/fixtures/available_councillors.yaml'):
        scraper = CouncillorScraper()
        result = scraper.available()
        verification = json.load(open(
            'tests/data/names.json'
        ))

        all_names = result.keys()
        assert 100 == len(all_names)

        for expected in verification.values():
            assert expected in all_names
