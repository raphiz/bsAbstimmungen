from bsAbstimmungen.importer.councillorimporter import CouncillorImporter
import vcr
from bsAbstimmungen.models import *
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

    parser = CouncillorImporter()
    all_names = verification.values()
    for in_pdf, from_scraper in verification.items():
        assert from_scraper == parser.name_for(in_pdf, all_names)


@mockdb
def test_importer():
    # Create test data...
    sp = Fraction.create(abbrevation='SP')
    Councillor.create(fullname='Ruedi Rechsteiner', fraction=sp)
    # Group.create(kind='commission', abbrevation='WAK', name='Wirtschafts- und Abgabekommission')

    importer = CouncillorImporter()
    importer.parse()

    ruedi = Councillor.filter(Councillor.fullname == 'Ruedi Rechsteiner')[0]

    assert ruedi.firstname == 'Rudolf'
    assert ruedi.lastname == 'Rechsteiner'

    assert ruedi.zip == '4058'
    assert ruedi.title == 'Dr. rer. pol.'
    assert ruedi.phone_business == '061 222 24 78'
    assert ruedi.phone_mobile is None
    assert ruedi.phone_private is None
    assert ruedi.fax_business is None
    assert ruedi.fax_private is None
    assert ruedi.job == 'Inhaber Beratungsbüro'
    assert ruedi.locality == 'Basel'
    assert ruedi.birthdate == datetime.date(1958, 10, 27)
    assert ruedi.employer == 'Beratungsbüro re-solution.ch, Inhaber'
    assert ruedi.website == 'www.rechsteiner-basel.ch'
    assert ruedi.address == 'Römergasse 30'

    # Assert commissions
    assert 1 == ruedi.commission_memberships.count()
    wak_mebership = ruedi.commission_memberships[0]
    assert wak_mebership.group.abbrevation == 'WAK'
    assert wak_mebership.group.name == 'Wirtschafts- und Abgabekommission'
    assert wak_mebership.member_since == datetime.date(2013, 2, 6)

    # assert
    # assert 1 == GroupMembership.select().join(Councillor).join(Group).where(
    # Councillor.fullname == ruedi.fullname, Group.kind == 'comission').count()
    # assert ruedi.groups == 'Römergasse 30'
    # commissions
    # member_nonstate
    # member_state



def test_scrape_details():
    url = ('http://www.grosserrat.bs.ch/de/mitglieder-gremien/'
           'mitglieder-a-z?such_kategorie=5&content_detail=3323')
    with vcr.use_cassette('build/fixtures/councillor_details.yaml'):
        scraper = CouncillorImporter()
        result = scraper.details(url)
        verification = json.load(open(
            'tests/data/councillor_details.json'
        ))

        # Assert the verification data has the same lenght
        assert len(verification.items()) == len(result.items())

        # Verify each value step-by-step
        for k, v in verification.items():
            assert v == result[k]


def test_available():
    with vcr.use_cassette('build/fixtures/available_councillors.yaml'):
        scraper = CouncillorImporter()
        result = scraper.available()
        verification = json.load(open(
            'tests/data/names.json'
        ))

        all_names = result.keys()
        assert 100 == len(all_names)

        for expected in verification.values():
            assert expected in all_names
