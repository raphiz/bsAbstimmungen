from bs4 import BeautifulSoup, element
from ..exceptions import ParserException, AlreadyImportedException
import requests
import datetime
import json
import logging
import os
from ..models import *
import re


logger = logging.getLogger(__name__)


class CouncillorImporter():

    def parse(self):
        names = self.available()
        for councillor in Councillor.select():
            real_name = self.name_for(councillor.fullname, names.keys())
            # Skip if no mapping found
            if real_name is None:
                continue

            # TODO: adapt to support 'updates' - eg. if one leaves an organisation / comission
            url = names[real_name]
            details = self.details(url)

            attrs = ['firstname', 'lastname', 'zip', 'title', 'phone_business',
                     'phone_mobile', 'phone_private', 'fax_business',
                     'fax_private', 'job', 'locality', 'birthdate', 'employer',
                     'website', 'address']

            for attr in attrs:
                if attr in details:
                    setattr(councillor,  attr, details[attr])

            for commission in details['commissions']:
                # TODO: check if comission is already atached to the councillor
                match = re.fullmatch(
                    '(.*)\s\(([A-Z]*)\)\sseit\s(\d{2}\.\d{2}\.\d{4})',
                    commission)
                commission = self._get_commission_for(
                    match.group(1), match.group(2))
                member_since = datetime.datetime.strptime(
                    match.group(3), '%d.%m.%Y').date()

                GroupMembership.create(
                    councillor=councillor,
                    group=commission,
                    member_since=member_since
                )
            for commission in details['commissions']:
                # TODO: check if comission is already atached to the councillor
                match = re.fullmatch(
                    '(.*)\s\(([A-Z]*)\)\sseit\s(\d{2}\.\d{2}\.\d{4})',
                    commission)
                commission = self._get_commission_for(
                    match.group(1), match.group(2))
                member_since = datetime.datetime.strptime(
                    match.group(3), '%d.%m.%Y').date()

                GroupMembership.create(
                    councillor=councillor,
                    group=commission,
                    member_since=member_since
                )
            # TODO: member_nonstate
            # TODO: member_state

            councillor.save()

            # print(json.dumps(details))
    def _get_commission_for(self, name, abbrevation):
        q = Group.select().where(Group.kind == 'commission',
                                 Group.abbrevation == abbrevation)
        if q.count() > 0:
            print('OK')
        else:
            Group.create(kind='commission', abbrevation=abbrevation, name=name)
        return q[0]

    def name_for(self, given, all_names):
        # TODO: what if the user is not available anymore?
        mappings = json.load(open('mapping.json'))

        if given in all_names:
            return given
        elif given in mappings['removed']:
            logger.info('Ignoring remoed councillor {0}.'.format(given))
            return None
        elif given in mappings['renamed'].keys():
            return mappings['renamed'][given]
        else:
            logger.warn('No match found for councillor {0}. Please '
                        'consider adding it to the mapping.json'.format(given))
            return None

    def details(self, url):
        # This allows us to access the email
        url = url + '&showemail=1'

        # Sanitize request from <br> tags
        txt = requests.get(url).text
        txt = re.sub('<[\/]?br>', '</br>', txt)
        soup = BeautifulSoup(txt, "html.parser")

        data = {}
        # Look for these attributes in the Detailansicht
        attributes = {"lastname": "Name", "firstname": "Vorname",
                      "address": "Adresse", "zip": "PLZ", "locality": "Ort",
                      "birthdate": "Geb. Datum", "phone_business": "Telefon G",
                      "phone_mobile": "Mobile", "job": "Berufliche Tätigkeit",
                      "website": "Homepage",
                      "ward": "Wahlkreis", "title": "Titel",
                      "phone_private": "Telefon P",
                      "fax_business": "Fax G", "fax_private": "Fax P"}

        dtable = soup.select('#gr_cms_mit_div_content_detail table table')[0]
        for attribute, label in attributes.items():
            td = dtable.find(text=label)
            if not td:
                continue
            value = td.parent.parent.contents[1].string
            data[attribute] = value

        # Convert birthdate into date field
        data['birthdate'] = datetime.datetime.strptime(
            data['birthdate'], '%d.%m.%Y').date()

        # Parse fraction
        fraction_c = soup.find('h4', text='Fraktion').next_sibling
        data['fraction'] = re.search('\(([A-Z\/]*)\)',
                                     fraction_c.string).group(1)

        # Parse commissions
        p_commissions = self._parse_contents(
            soup, 'h4', 'Kommissionen').split('\n')
        commissions = []
        for idx in range(0, len(p_commissions), 2):
            commissions.append(p_commissions[idx] + p_commissions[idx+1])
        data['commissions'] = commissions

        # Parse employer
        data['employer'] = self._parse_contents(soup, 'h4', 'Arbeitgeber')

        #  Parse Membership in Leading and supervisor committies
        member_nonstate = self._parse_contents(
            soup, 'h4',
            'Mitgliedschaften in F&uumlhrungs-; und Aufsichtsgremien')
        data['member_nonstate'] = [item
                                   for item
                                   in member_nonstate.split('\n')
                                   if len(item.strip()) > 0]

        #  Parse Membership in Leading and supervisor committies
        member_state = self._parse_contents(
            soup, 'h4', 'Mitgliedschaften in staatlichen, nicht durch '
            'den Grossen Rat gewählten Kommissionen')
        data['member_state'] = [item
                                for item
                                in member_state.split('\n')
                                if len(item.strip()) > 0]

        # Parlamentarische Vorstösse' # Anz. vorstösse + link
        return data

    def available(self):
        ur = 'http://www.grosserrat.bs.ch/de/mitglieder-gremien/mitglieder-a-z'
        soup = BeautifulSoup(requests.get(ur).text, "html.parser")
        result = {}
        for councillor_li in soup.select('.ri_fe_miglieder_li'):
            direct = councillor_li.a['href']

            # Convert the name into a string
            name = self._parse_name(councillor_li)
            result[name] = direct
        return result

    def _parse_contents(self, soup, heading, text):
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

    def _parse_name(self, councillor_li):
        s = councillor_li.select('.ri_fe_miglieder_div1')[0].stripped_strings

        # Reverse the name order (since this is how it's stored
        # in the fullname field)
        last = next(s)
        first = next(s)
        return "{0} {1}".format(first, last)
