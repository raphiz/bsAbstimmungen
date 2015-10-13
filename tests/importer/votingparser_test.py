#!/usr/bin/env python
# coding=utf-8
import json
import pytest
from bsAbstimmungen.importer.votingimporter import VotingParser
from bsAbstimmungen.exceptions import AlreadyImportedException
from ..utils import mockdb


def test_raise_exception_when_alread_parsed(mockdb):
    parser = VotingParser(mockdb)
    parser.parse(
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    with pytest.raises(AlreadyImportedException) as excinfo:
        parser.parse('tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf')


def test_reuse_existing_councillors(mockdb):
    parser = VotingParser(mockdb)
    parser.parse(
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    parser.parse(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    # Check the rough numbers
    assert 2 == mockdb['votes'].count()
    assert 124 == mockdb['councillors'].count()


def test_multiline_affairs(mockdb):
    parser = VotingParser(mockdb)
    parser.parse('tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf')
    vote = mockdb['votes'].find()[0]
    assert ('Bericht der Umwelt-, Verkehrs- und '
            'Energiekommission zum Ratschlag Nr. 12.0788.01 '
            'Rahmenausgabenbewilligung zur weiteren Umsetzung '
            'von Tempo 30. Projektierung und Umsetzung von '
            'Massnahmen aus dem aktualisierten Tempo 30-Konzept '
            'sowie Bericht zu zehn Anzügen und zu zwei '
            'Petitionen sowie Bericht der Kommissionsminderheit' ==
            vote['affair'])


def test_parser_extracts_data(mockdb):
    parser = VotingParser(mockdb)
    parser.parse(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    assert 1 == mockdb['votes'].count()
    assert 100 == mockdb['councillors'].count()

    # Load verification details
    verification = json.load(open(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.json'
    ))

    # Verify the imported vote
    vote = mockdb['votes'].find_one({'nr': verification['vote']['nr']})
    assert verification['vote']['timestamp'] == vote['timestamp'].isoformat()
    assert verification['vote']['affair'] == vote['affair']
    assert verification['vote']['proposal'] == vote['proposal']
    assert verification['vote']['question'] == vote['question']
    assert verification['vote']['type'] == vote['type']

    # Verify all counillors
    for councillor in verification['votings']:
        loaded = mockdb['councillors'].find_one({'fullname':
                                                 councillor['name']})
        assert councillor['name'] == loaded['fullname']
        assert councillor['fraction'] == loaded['fraction']
        assert councillor['voting'] == loaded['votings'][0]['voting']
