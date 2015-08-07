from nose.tools import *
from datetime import datetime
from bsAbstimmungen.models import *
from .utils import mockdb


@mockdb
def test_fraction_councillor():
    # Create some test fractions
    sp = Fraction.create(abbrevation='SP')
    ldp = Fraction.create(abbrevation='LDP')

    # Create an some example councillors
    Councillor.create(fullname='Peter F', fraction=sp)
    Councillor.create(fullname='Jeff K', fraction=sp)
    Councillor.create(fullname='John Y', fraction=ldp)

    # Assert the correct amount of councillors on the fractions
    assert sp.councillors.count() == 2
    assert ldp.councillors.count() == 1


@mockdb
def test_votings():
    sp = Fraction.create(abbrevation='SP')
    peter = Councillor.create(fullname='Peter F', fraction=sp)

    vote = Vote.create(nr=1, timestamp=datetime.now(),
                       affair='affair', proposal='proposal',
                       question='question', type='type')
    voting = Voting.create(councillor=peter, vote=vote, voting='yes')

    assert 1 == Voting.select().where(Voting.voting == 'yes').count()
    assert voting == Voting.get(Voting.voting == 'yes')
