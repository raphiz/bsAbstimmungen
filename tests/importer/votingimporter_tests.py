import shutil
from nose.tools import *
from bsAbstimmungen.importer import VotingImporter
from bsAbstimmungen.models import create_tables
from bsAbstimmungen.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime


def test_fetch():

    engine = create_engine('sqlite:///:memory:')
    initialize(engine)
    create_tables(engine)
    session = sessionmaker(bind=engine)()
    importer = VotingImporter()

    f = datetime(year=2014, month=2, day=1)
    t = datetime(year=2014, month=2, day=28)

    importer.fetch(session, f, t)
    assert_equal(29, session.query(Vote).count())


def test_download():
    # TODO: test skip if already exists...
    files = [
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2013-2014'
        '/2013.02.06/Abst_0004_20130206_110027_0007_0000_ow.pdf',
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2013-2014'
        '/2013.03.20/Abst_0072_20130320_094625_0011_0000_ab.pdf'
    ]
    importer = VotingImporter(directory='test_cache')
    shutil.rmtree('test_cache')
    os.makedirs('test_cache')
    result = importer._download(files)
    assert_equal(2, len(result))
    assert_equal(
        'test_cache/Abst_0004_20130206_110027_0007_0000_ow.pdf',
        result[0]
    )
    assert_equal(
        'test_cache/Abst_0072_20130320_094625_0011_0000_ab.pdf',
        result[1]
    )
    assert_true(os.path.exists(result[0]))
    assert_true(os.path.getsize(result[0]) > 0)
    assert_true(os.path.exists(result[1]))
    assert_true(os.path.getsize(result[1]) > 0)
    shutil.rmtree('test_cache')
