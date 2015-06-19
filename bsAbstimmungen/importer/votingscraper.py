from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime


class VotingScraper:

    BASE = 'http://abstimmungen.grosserrat-basel.ch/'

    def find(self, fromDate, toDate):
        legislations = self._fetch_legislations(fromDate, toDate)
        dates = self._fetch_meeting_dates(legislations, fromDate, toDate)
        return self._fetch_votings(dates)

    def _fetch_votings(self, dates):
        result = []
        for date in dates:
            soup = BeautifulSoup(self._page(date))
            for link in soup.find_all('a'):
                if re.match('^[0-9]*$', link.string):
                    result.append(self.BASE + link['href'])
        return result

    def _fetch_meeting_dates(self, legislations, fromDate, toDate):
        result = []
        for legislation in legislations:
            soup = BeautifulSoup(self._page(legislation))
            for link in soup.find_all('a'):
                if re.match('^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$', link.string):
                    date = self._date(link.string)
                    if self._in_timespan(fromDate, toDate, date):
                        result.append(link['href'])
        return result

    def _fetch_legislations(self, fromDate, toDate):
        soup = BeautifulSoup(self._page('index_archiv_v2.php'))
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
