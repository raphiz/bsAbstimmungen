from bs4 import BeautifulSoup
from ..exceptions import ParserException, AlreadyImportedException
import requests
import logging
import os
from ..models import *
import re
from difflib import SequenceMatcher


logger = logging.getLogger(__name__)


class CouncillorParser():
    def name_for(self, given, all_names):
        match = None
        similarity = 0
        for name in all_names:
            current_similarity = SequenceMatcher(None, given, name).ratio()
            if current_similarity > similarity:
                similarity = current_similarity
                match = name
        return match


class CouncillorScraper():

    def available_councillors(self):
        ur = 'http://www.grosserrat.bs.ch/de/mitglieder-gremien/mitglieder-a-z'
        soup = BeautifulSoup(requests.get(ur).text)
        result = {}
        for councillor_li in soup.select('.ri_fe_miglieder_li'):
            direct = councillor_li.a['href']

            # Convert the name into a string
            name = self._parse_name(councillor_li)
            result[name] = direct
        return result

    def _parse_name(self, councillor_li):
        s = councillor_li.select('.ri_fe_miglieder_div1')[0].stripped_strings

        # Reverse the name order (since this is how it's stored
        # in the fullname field)
        last = next(s)
        first = next(s)

        # # Remove shortend second names (eg. John M. -> John )
        # if first.find(' ') > 0:
        #     first = first[:first.find(' ')]
        #
        # # Remove shortend second names (eg. John M. -> John )
        # if last.find('-') > 0:
        #     last = last[:last.find('-')]

        return "{0} {1}".format(first, last)
