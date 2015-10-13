from . import utils
from datetime import datetime
import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from ..exceptions import ParserException, AlreadyImportedException

logger = logging.getLogger(__name__)


def fetch(db, fromDate, toDate, directory='build/cache'):
    scraper = VotingScraper()
    logger.info('Searching for votes....')
    docs = scraper.find(fromDate, toDate)
    logger.info('Found {0} votes'.format(len(docs)))
    saved = _download(docs, directory)
    parser = VotingParser(db)
    for current in saved:
        try:
            parser.parse(current)
        except AlreadyImportedException as e:
            logger.info(e)


# TODO: spit - one part into fetch, the other into utils
def _download(docs, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    saved = []
    for doc in docs:
        local_filename = os.path.join(directory, doc.split('/')[-1])
        utils.download(doc, local_filename)
        saved.append(local_filename)
    return saved


class VotingScraper:

    BASE = 'http://abstimmungen.grosserrat-basel.ch/'

    def find(self, fromDate, toDate):
        legislations = self._fetch_legislations(fromDate, toDate)
        dates = self._fetch_meeting_dates(legislations, fromDate, toDate)
        return self._fetch_votings(dates)

    def _fetch_votings(self, dates):
        result = []
        for date in dates:
            soup = BeautifulSoup(self._page(date), "html.parser")
            for link in soup.find_all('a'):
                if re.match('^[0-9]*$', link.string):
                    result.append(self.BASE + link['href'])
        return result

    def _fetch_meeting_dates(self, legislations, fromDate, toDate):
        result = []
        for legislation in legislations:
            soup = BeautifulSoup(self._page(legislation), "html.parser")
            for link in soup.find_all('a'):
                if re.match('^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$', link.string):
                    date = self._date(link.string)
                    if self._in_timespan(fromDate, toDate, date):
                        result.append(link['href'])
        return result

    def _fetch_legislations(self, fromDate, toDate):
        soup = BeautifulSoup(self._page('index_archiv_v2.php'), "html.parser")
        result = []
        for span in soup.find_all('span'):
            link = span.find('a')
            if link is None:
                continue

            startswith = 'Amtsjahr'
            if len(link.string) > len(startswith) and \
               link.string[:len(startswith)] == startswith:
                begin = self._date(span.text[21:31])
                end = self._date(span.text[34:44])
                if self._in_timespan(fromDate, toDate, begin, end):
                    result.append(link['href'])
        return result

    def _page(self, page):
        return requests.get(self.BASE + page).text

    def _in_timespan(self, fromDate, toDate, begin, end=None):
        if end is None:
            end = begin
        # If the end date was earlier than the fromDate
        # or If begin date was later than the toDate
        if end < fromDate or begin > toDate:
            return False
        return True

    def _date(self, string):
        return datetime.strptime(string, '%d.%m.%Y')


class VotingParser:

    enum_mapping = {'J': 'yes',
                    'N': 'no',
                    'E': 'abstain',
                    'A':  'away',
                    'P': 'president'}

    lines = None

    def __init__(self, db):
        self.db = db

    def parse(self, file):
        self.idx = -1

        basename = os.path.basename(file)
        if self.db['votes'].find({'source': basename}).count() > 0:
            raise AlreadyImportedException(
                'The vote from source {0} is already imported'.format(basename))

        self.lines = utils.get_pdf_content(file)

        vote = self._parseVote(basename)

        for i in range(0, 100):
            self._parseVoting(vote)

    def _parseVoting(self, vote):

        match = re.fullmatch('([^\(\)]*)\s\(([a-zA-Z\/]*)\)', self.token())

        fullname = match.group(1)
        fraction = match.group(2)

        self._create_councillor_if_not_exists(fullname, fraction)
        self.db['councillors'].update_one(
            {'fullname': fullname, 'fraction': fraction},
            {'$push': {'votings': {
                    'vote': vote['_id'],
                    'voting': self.enum_mapping.get(self.token(), None)
                }}
             })

    def _create_councillor_if_not_exists(self, fullname, fraction):
        councillor = self.db['councillors'].find_one({"fullname": fullname})
        if councillor is None:
            councillor = {"fullname": fullname, "fraction": fraction, "votings": []}
            self.db['councillors'].insert(councillor)

    def _parseVote(self, basename):
        vote = {
            'source': basename
        }

        self._assertToken('Grosser Rat des Kantons Basel-Stadt')
        self._assertToken('Ratssekretariat')
        self._assertToken('Nr')

        vote['nr'] = int(self.token())
        vote['timestamp'] = datetime.strptime(
            '%s %s' % (self.token(), self.token()),
            '%d.%m.%Y %H:%M:%S'
        )
        vote['type'] = self.token()

        query = self.db['votes'].find(
            {'nr': vote['nr'], 'timestamp': vote['timestamp']})

        if query.count() > 0:
            raise AlreadyImportedException(
                'The vote nr {0} from {1} is already imported'.format(
                 vote['nr'], vote['timestamp']))

        self._assertToken('Ergebnis der Abstimmung')
        self._assertToken('Geschäft')

        vote['affair'] = self._parseUntil('Gegenstand / Antrag')
        vote['proposal'] = self._parseUntil('Abstimmungsfrage')

        vote['question'] = self._parseUntil('([^\(\)\s]*\s)*\([A-Z]*\)', True)
        self._step_back()

        self.db['votes'].insert(vote)
        return vote

    def _parseUntil(self, stopper, regex=False):
        text = ''
        nextLine = self.token()
        while(
            (not regex and nextLine != stopper) or
            (regex and re.fullmatch(stopper, nextLine) is None)
        ):
            # TODO: handle words with a dash
            if(len(text) == 0):
                text = nextLine
            else:
                text = '%s %s' % (text, nextLine)
            nextLine = self.token()
        return text

    def _assertToken(self, expected):
        actual = self.token()
        if(actual != expected):
            raise ParserException(
                'Unexpected message in PDF. Excepted "%s" but recieved "%s"' %
                (expected, actual)
            )

    def _step_back(self):
        self.idx = self.idx-1

    def token(self):
        self.idx = self.idx+1
        return self.lines[self.idx]
