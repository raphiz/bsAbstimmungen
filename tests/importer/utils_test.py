#!/usr/bin/env python
# coding=utf-8
import logging
from bsAbstimmungen.importer import utils


def test_get_pdf_content_returns_array():
    res = utils.get_pdf_content(
        'tests/data/Abst_0561_20140514_092348_0003_0000_sa.pdf'
    )

    assert len(res) == 281
    assert res[0] == 'Grosser Rat des Kantons Basel-Stadt'
    assert res[1] == 'Ratssekretariat'
    assert res[2] == 'Nr'
    assert res[3] == '561'
