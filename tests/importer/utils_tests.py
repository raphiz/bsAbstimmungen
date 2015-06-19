#!/usr/bin/env python
# coding=utf-8
import logging
from bsAbstimmungen.importer import utils
from nose.tools import *


def test_get_pdf_content_returns_array():
    res = utils.get_pdf_content(
        'tests/data/Abst_0561_20140514_092348_0003_0000_sa.pdf'
    )
    assert_equal(len(res), 281)
    assert_equal(res[0], 'Grosser Rat des Kantons Basel-Stadt')
    assert_equal(res[1], 'Ratssekretariat')
    assert_equal(res[2], 'Nr')
    assert_equal(res[3], '561')
