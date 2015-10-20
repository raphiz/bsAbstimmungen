from bsAbstimmungen.importer.councillorimporter import CouncillorImporter
import vcr
import os
from ..utils import mockdb
import json
import datetime


def test_name_for():
    """
    Test the name mapping...
    """
    verification = json.load(open(
        'tests/data/names.json'
    ))

    parser = CouncillorImporter(None)
    all_names = verification.values()
    for in_pdf, from_scraper in verification.items():
        assert from_scraper == parser.name_for(in_pdf, all_names)


def test_importer(mockdb):
    # Create test data...
    mockdb['councillors'].insert({'fullname': 'Ruedi Rechsteiner',
                                  'fraction': 'SP', 'votings': []})

    with vcr.use_cassette('build/fixtures/councillor.yaml'):
        importer = CouncillorImporter(mockdb)
        importer.parse()

    ruedi = mockdb['councillors'].find_one({'fullname': 'Ruedi Rechsteiner'})

    assert ruedi['firstname'] == 'Rudolf'
    assert ruedi['lastname'] == 'Rechsteiner'

    assert ruedi['zip'] == '4058'
    assert ruedi['title'] == 'Dr. rer. pol.'
    assert ruedi['phone_business'] == '061 222 24 78'
    assert ruedi['phone_mobile'] is None
    assert ruedi['phone_private'] is None
    assert ruedi['fax_business'] is None
    assert ruedi['fax_private'] is None
    assert ruedi['job'] == 'Inhaber Beratungsbüro'
    assert ruedi['locality'] == 'Basel'
    assert ruedi['birthdate'] == datetime.datetime(1958, 10, 27)
    assert ruedi['employer'] == 'Beratungsbüro re-solution.ch, Inhaber'
    assert ruedi['website'] == 'www.rechsteiner-basel.ch'
    assert ruedi['address'] == 'Römergasse 30'

    # Assert commissions
    assert 1 == len(ruedi['commissions'])
    assert 'Wirtschafts- und Abgabekommission (WAK)' == ruedi['commissions'][0]

    assert 1 == len(ruedi['member_state'])
    assert 5 == len(ruedi['member_nonstate'])

    # Verify the avatar was downloaded
    assert os.path.exists(os.path.join('build/avatars', str(ruedi['avatar'])))


def test_available():
    with vcr.use_cassette('build/fixtures/available_councillors.yaml'):
        scraper = CouncillorImporter(None)
        result = scraper.available()
        verification = json.load(open(
            'tests/data/names.json'
        ))

        all_names = result.keys()
        assert 100 == len(all_names)

        for expected in all_names:
            assert expected in verification.values()
