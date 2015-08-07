#!/usr/bin/env python
# coding=utf-8
import json
from nose.tools import *
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
    assert_raises(
        AlreadyImportedException,
        parser.parse,
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )


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
    assert_equal(2, Vote.select().count())
    assert_equal(124, Councillor.select().count())


@mockdb
def test_multiline_affairs():
    parser = VotingParser()
    parser.parse(
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    vote = Vote.select()[0]
    assert_equal('Bericht der Umwelt-, Verkehrs- und '
                 'Energiekommission zum Ratschlag Nr. 12.0788.01 '
                 'Rahmenausgabenbewilligung zur weiteren Umsetzung '
                 'von Tempo 30. Projektierung und Umsetzung von '
                 'Massnahmen aus dem aktualisierten Tempo 30-Konzept '
                 'sowie Bericht zu zehn Anzügen und zu zwei '
                 'Petitionen sowie Bericht der Kommissionsminderheit',
                 vote.affair
                 )


@mockdb
def test_parser_extracts_data():
    parser = VotingParser()
    parser.parse(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    # Check the rough numbers
    assert_equal(1, Vote.select().count())
    assert_equal(100, Councillor.select().count())
    assert_equal(8, Fraction.select().count())

    # Load verification details
    verification = json.load(open(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.json'
    ))

    # Verify the imported vote
    vote = Vote.select()[0]
    assert_equal(verification['vote']['timestamp'],
                 vote.timestamp.isoformat())
    assert_equal(verification['vote']['nr'], vote.nr)
    assert_equal(verification['vote']['affair'], vote.affair)
    assert_equal(verification['vote']['proposal'], vote.proposal)
    assert_equal(verification['vote']['question'], vote.question)
    assert_equal(verification['vote']['type'], vote.type)
    assert_equal(len(verification['votings']), 100)

    # Verify all counillors
    for councillor in verification['votings']:
        loaded = Voting.select()\
            .join(Councillor) \
            .where(Councillor.fullname == councillor['name'])[0]
        assert_equal(councillor['name'], loaded.councillor.fullname)
        assert_equal(councillor['fraction'],
                     loaded.councillor.fraction.abbrevation)
        assert_equal(councillor['voting'], loaded.voting)
