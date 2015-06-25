from bsAbstimmungen.importer.councillorimporter import CouncillorParser
from nose.tools import *
import json


def test_name_for():
    """
    Test the name mapping...
    """
    verification = json.load(open(
        'tests/data/names.json'
    ))

    parser = CouncillorParser()
    all_names = verification.keys()
    for in_pdf, from_scraper in verification.items():
        assert_equals(in_pdf, parser.name_for(from_scraper, all_names))
