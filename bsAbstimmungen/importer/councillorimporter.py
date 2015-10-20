from bs4 import BeautifulSoup, element
from ..exceptions import ParserException, AlreadyImportedException
from . import utils
import requests
import datetime
import json
import logging
import os
import re


logger = logging.getLogger(__name__)


# TODO: allow to make a diff
class CouncillorImporter():
    def __init__(self, db, avatar_directory='build/avatars'):
        self.db = db
        self.avatar_directory = avatar_directory
        if not os.path.exists(self.avatar_directory):
            os.makedirs(self.avatar_directory)

    def parse(self):
        names = self.available()
        logger.info("Found data for {0} councillors".format(len(names)))
        for councillor in self.db['councillors'].find():
            real_name = self.name_for(councillor['fullname'], names.keys())
            # Skip if no mapping found
            if real_name is None:
                continue

            # TODO: adapt to support 'updates' - eg.
            # if one leaves an organisation / comission
            url = names[real_name]
            details = self.details(url, councillor)
            self.db['councillors'].replace_one({'_id': councillor['_id']}, councillor)

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

    def details(self, url, councillor):
        # This would allow accessing the email
        # url = url + '&showemail=1'

        councillor['source'] = url

        # Sanitize request from <br> tags
        txt = requests.get(url).text
        txt = re.sub('<[\/]?br>', '</br>', txt)
        soup = BeautifulSoup(txt, "html.parser")

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
                councillor[attribute] = None
                continue
            councillor[attribute] = td.parent.parent.contents[1].string

        # Convert birthdate into date field
        councillor['birthdate'] = datetime.datetime.strptime(
            councillor['birthdate'], '%d.%m.%Y')

        # # Parse fraction
        # fraction_c = soup.find('h4', text='Fraktion').next_sibling
        # councillor['fraction'] = re.search('\(([A-Z\-\/]*)\)',
        #                                    fraction_c.string).group(1)

        # Parse commissions
        p_commissions = self._parse_contents(
            soup, 'h4', 'Kommissionen')
        commissions = []
        if p_commissions is not None:
            p_commissions = p_commissions.split('\n')
            for idx in range(0, len(p_commissions), 2):
                commissions.append(p_commissions[idx])
        councillor['commissions'] = commissions

        # Parse employer
        councillor['employer'] = self._parse_contents(soup, 'h4',
                                                      'Arbeitgeber')

        #  Parse Membership in Leading and supervisor committies
        member_nonstate = self._parse_contents(
            soup, 'h4',
            'Mitgliedschaften in F&uumlhrungs-; und Aufsichtsgremien')
        c_member_nonstate = []
        if member_nonstate is not None:
            for item in member_nonstate.split('\n'):
                if len(item.strip()) > 0:
                    c_member_nonstate.append(item)
        councillor['member_nonstate'] = c_member_nonstate

        #  Parse Membership in Leading and supervisor committies
        member_state = self._parse_contents(
            soup, 'h4', 'Mitgliedschaften in staatlichen, nicht durch '
            'den Grossen Rat gewählten Kommissionen')
        c_member_state = []
        if member_state is not None:
            for item in member_state.split('\n'):
                if len(item.strip()) > 0:
                    c_member_state.append(item)
        councillor['member_state'] = c_member_state

        # Download avatar
        avatar_url = soup.findAll(attrs={"title": "Grosses Bild anzeigen"})[0]['href']
        avatar_url = 'http://www.grosserrat.bs.ch/' + avatar_url
        councillor['avatar'] = avatar_url[avatar_url.rindex('/')+1:]
        dst = os.path.join(self.avatar_directory, councillor['avatar'])
        utils.download(avatar_url, dst)

        return councillor

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
        if its is None:
            return None
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
