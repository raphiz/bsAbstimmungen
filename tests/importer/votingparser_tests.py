#!/usr/bin/env python
# coding=utf-8

import unittest
import json
from nose.tools import *
from bsAbstimmungen.importer import VotingParser
from bsAbstimmungen.models import create_tables
from bsAbstimmungen.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

session = None


def init_db():
    global session
    engine = create_engine('sqlite:///:memory:')
    initialize(engine)
    create_tables(engine)
    session = sessionmaker(bind=engine)()


@with_setup(init_db)
def test_raise_exception_when_alread_parsed():
    parser = VotingParser()
    parser.parse(
        session,
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    assert_raises(
        Exception,
        parser.parse,
        session,
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )


@with_setup(init_db)
def test_reuse_existing_councillors():
    parser = VotingParser()
    parser.parse(
        session,
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    parser.parse(
        session,
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    # Check the rough numbers
    assert_equal(2, session.query(Vote).count())
    assert_equal(124, session.query(Councillor).count())


@with_setup(init_db)
def test_multiline_affairs():
    parser = VotingParser()
    parser.parse(
        session,
        'tests/data/Abst_0205_20130109_111125_0003_0000_sa.pdf'
    )
    vote = session.query(Vote).one()
    assert_equal('Bericht der Umwelt-, Verkehrs- und '
                 'Energiekommission zum Ratschlag Nr. 12.0788.01 '
                 'Rahmenausgabenbewilligung zur weiteren Umsetzung '
                 'von Tempo 30. Projektierung und Umsetzung von '
                 'Massnahmen aus dem aktualisierten Tempo 30-Konzept '
                 'sowie Bericht zu zehn Anzügen und zu zwei '
                 'Petitionen sowie Bericht der Kommissionsminderheit',
                 vote.affair
                 )


@with_setup(init_db)
def test_parser_extracts_data():
    # TODO: don't create the tables here...
    parser = VotingParser()
    parser.parse(
        session,
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.pdf'
    )

    # Check the rough numbers
    assert_equal(1, session.query(Vote).count())
    assert_equal(100, session.query(Councillor).count())
    assert_equal(8, session.query(Fraction).count())

    # Load verification details
    verification = json.load(open(
        'tests/data/Abst_0147_20130605_090518_0001_0000_ab.json'
    ))

    # Verify the imported vote
    vote = session.query(Vote).one()
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
        loaded = session.query(Voting) \
            .join(Councillor) \
            .filter(Councillor.fullname == councillor['name']) \
            .one()
        assert_equal(councillor['name'], loaded.councillor.fullname)
        assert_equal(councillor['fraction'],
                     loaded.councillor.fraction.abbrevation)
        assert_equal(councillor['voting'], loaded.voting)
