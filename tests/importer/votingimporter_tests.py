from nose.tools import *
from bsAbstimmungen.importer import VotingImporter
from datetime import datetime
from mock import patch
import os
import shutil


@patch('bsAbstimmungen.importer.votingimporter.VotingScraper.find')
@patch('bsAbstimmungen.importer.votingimporter.VotingParser.parse')
def test_fetch(parse, find):
    importer = VotingImporter('test_cache')

    f = datetime(year=2014, month=2, day=1)
    t = datetime(year=2014, month=2, day=28)

    find.return_value = [
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2014-2015/'
        '2014.02.12/Abst_0475_20140212_092150_0001_0000_ab.pdf',
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2014-2015/'
        '2014.02.12/Abst_0493_20140212_114415_0017_0000_sa.pdf']

    importer.fetch(None, f, t)

    # Verify the files were downloaded...
    assert_true(
        os.path.exists('test_cache/Abst_0475_20140212_092150_0001_0000_ab.pdf')
    )
    assert_true(
        os.path.exists('test_cache/Abst_0493_20140212_114415_0017_0000_sa.pdf')
    )

    # Verify the scraper is called
    find.assert_called_with(f, t)

    # Verify the parse method was called for both
    assert_equals(2, len(parse.mock_calls))
    parse.assert_any_call(
        None, 'test_cache/Abst_0493_20140212_114415_0017_0000_sa.pdf'
    )
    parse.assert_any_call(
        None, 'test_cache/Abst_0475_20140212_092150_0001_0000_ab.pdf'
    )

    # Clean up...
    shutil.rmtree('test_cache')


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
