from bs4 import BeautifulSoup, element
from ..exceptions import ParserException, AlreadyImportedException
import requests
import re
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
    def parse_contents(self, soup, heading, text):
        its = soup.find(heading, text=text)
        val = ''
        for it in its.next_siblings:
            if type(it) is element.Tag and it.name[:1] == 'h':
                break
            elif type(it) is element.NavigableString:
                val += '\n'+it
            elif it.string is not None and len(it.string) > 0:
                val += '\n'+it.string
        return val[1:]

    def details(self, url):
        # This allows us to access the email
        url = url + '&showemail=1'

        # Sanitize request from <br> tags
        txt = requests.get(url).text
        txt = re.sub('<[\/]?br>', '</br>', txt)
        soup = BeautifulSoup(txt)

        data = {}
        # Look for these attributes in the Detailansicht
        attributes = ["Name", "Vorname", "Adresse", "PLZ", "Ort", "Geb. Datum",
                      "Berufliche Tätigkeit", "Telefon G", "Mobile", "E-Mail",
                      "Homepage", "Bemerkungen", "Wahlkreis", "Titel",
                      "Telefon P", "Fax G", "Fax P"]

        dtable = soup.select('#gr_cms_mit_div_content_detail table table')[0]
        for attribute in attributes:
            td = dtable.find(text=attribute)
            if not td:
                continue
            value = td.parent.parent.contents[1].string
            data[attribute] = value

        # Parse fraction
        fraction_c = soup.find('h4', text='Fraktion').next_sibling
        data['fraction'] = re.search('\(([A-Z\/]*)\)',
                                     fraction_c.string).group(1)

        # Parse commissions
        # TODO: what if it has more than one? How to store this?
        data['commissions'] = self.parse_contents(soup, 'h4', 'Kommissionen')
        # Bau- und Raumplanungskommission (BRK)
        # seit 06.02.2013

        print(data['commissions'])

        # Parse employer
        data['employer'] = self.parse_contents(soup, 'h4', 'Arbeitgeber')

        #  Parse Membership in Leading and supervisor committies
        data['member_nonstate'] = self.parse_contents(
            soup, 'h4',
            'Mitgliedschaften in F&uumlhrungs-; und Aufsichtsgremien')

        #  Parse Membership in Leading and supervisor committies
        data['member_state'] = self.parse_contents(
            soup, 'h4', 'Mitgliedschaften in staatlichen, nicht durch '
            'den Grossen Rat gewählten Kommissionen')

        # Parlamentarische Vorstösse' # Anz. vorstösse + link

    # Check attrs her!
    # 'Kommissionen', # -> string + link
    # 'Arbeitgeber', # -> string
    # 'Mitgliedschaften in F&uumlhrungs-; und Aufsichtsgremien', # -> string
    # 'Mitgliedschaften in staatlichen, nicht durch den Grossen Rat gewählten \
    #        Kommissionen', # -> string
    # 'Parlamentarische Vorstösse' # Anz. vorstösse + link
    # ]

    def available(self):
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
