#!/usr/bin/env python
# coding=utf-8
import json
import pytest
from bsAbstimmungen.importer.votingimporter import VotingParser
from bsAbstimmungen.models import *
from bsAbstimmungen.exceptions import AlreadyImportedException
from ..utils import mockdb


@mockdb
def test_raise_exception_when_alread_parsed():
    parser = VotingParser()
    parser.parse(
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    with pytest.raises(AlreadyImportedException) as excinfo:
        parser.parse('tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf')


@mockdb
def test_reuse_existing_councillors():
    parser = VotingParser()
    parser.parse(
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    parser.parse(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    # Check the rough numbers
    assert 2 == Vote.select().count()
    assert 124 == Councillor.select().count()


@mockdb
def test_multiline_affairs():
    parser = VotingParser()
    parser.parse('tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf')
    vote = Vote.select()[0]
    assert ('Bericht der Umwelt-, Verkehrs- und '
            'Energiekommission zum Ratschlag Nr. 12.0788.01 '
            'Rahmenausgabenbewilligung zur weiteren Umsetzung '
            'von Tempo 30. Projektierung und Umsetzung von '
            'Massnahmen aus dem aktualisierten Tempo 30-Konzept '
            'sowie Bericht zu zehn Anzügen und zu zwei '
            'Petitionen sowie Bericht der Kommissionsminderheit'
            == vote.affair)


@mockdb
def test_parser_extracts_data():
    parser = VotingParser()
    parser.parse(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    # Check the rough numbers
    assert 1 == Vote.select().count()
    assert 100 == Councillor.select().count()
    assert 8 == Fraction.select().count()

    # Load verification details
    verification = json.load(open(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.json'
    ))

    # Verify the imported vote
    vote = Vote.select()[0]
    assert verification['vote']['timestamp'] == vote.timestamp.isoformat()
    assert verification['vote']['nr'] == vote.nr
    assert verification['vote']['affair'] == vote.affair
    assert verification['vote']['proposal'] == vote.proposal
    assert verification['vote']['question'] == vote.question
    assert verification['vote']['type'] == vote.type
    assert len(verification['votings']) == 100

    # Verify all counillors
    for councillor in verification['votings']:
        loaded = Voting.select()\
            .join(Councillor) \
            .where(Councillor.fullname == councillor['name'])[0]
        assert councillor['name'] == loaded.councillor.fullname
        assert (councillor['fraction'] ==
                loaded.councillor.fraction.abbrevation)
        assert councillor['voting'] == loaded.voting
