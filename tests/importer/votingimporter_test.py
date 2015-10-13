from bsAbstimmungen.importer import votingimporter
from datetime import datetime
from mock import patch
import os
import shutil
from ..utils import mockdb


@patch('bsAbstimmungen.importer.votingimporter.VotingScraper.find')
@patch('bsAbstimmungen.importer.votingimporter.VotingParser.parse')
@patch('bsAbstimmungen.importer.votingimporter.utils.download')
def test_fetch(download, parse, find, mockdb):

    f = datetime(year=2014, month=2, day=1)
    t = datetime(year=2014, month=2, day=28)

    find.return_value = [
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2014-2015/'
        '2014.02.12/Abst_0475_20140212_092150_0001_0000_ab.pdf',
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2014-2015/'
        '2014.02.12/Abst_0493_20140212_114415_0017_0000_sa.pdf']

    votingimporter.fetch(mockdb, f, t, directory='test_cache')

    # Verify the scraper is called
    find.assert_called_with(f, t)

    # Verify the download calls
    assert 2 == len(download.mock_calls)
    download.assert_any_call(
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2014-2015/'
        '2014.02.12/Abst_0475_20140212_092150_0001_0000_ab.pdf',
        'test_cache/Abst_0475_20140212_092150_0001_0000_ab.pdf',

    )
    download.assert_any_call(
        'http://abstimmungen.grosserrat-basel.ch/archiv/Amtsjahr_2014-2015/'
        '2014.02.12/Abst_0493_20140212_114415_0017_0000_sa.pdf',
        'test_cache/Abst_0493_20140212_114415_0017_0000_sa.pdf'
    )

    # Verify the parse method was called for both
    assert 2 == len(parse.mock_calls)
    parse.assert_any_call(
        'test_cache/Abst_0493_20140212_114415_0017_0000_sa.pdf'
    )
    parse.assert_any_call(
        'test_cache/Abst_0475_20140212_092150_0001_0000_ab.pdf'
    )

    # Clean up...
    shutil.rmtree('test_cache')
