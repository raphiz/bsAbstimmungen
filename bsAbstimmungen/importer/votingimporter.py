from .votingparser import VotingParser
from .votingscraper import VotingScraper
import os
import requests


class VotingImporter:

    def __init__(self, directory='cache'):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def fetch(self, session, fromDate, toDate):
        docs = self._scrape(fromDate, toDate)
        saved = self._download(docs)
        self._parse(session, saved)

    def _scrape(self, fromDate, toDate):
        scraper = VotingScraper()
        return scraper.find(fromDate, toDate)

    def _download(self, docs):
        saved = []
        for doc in docs:
            local_filename = os.path.join(self.directory, doc.split('/')[-1])
            if(os.path.exists(local_filename)):
                # Skipping already downloaded file...
                # TODO: log it!
                saved.append(local_filename)
                continue
            r = requests.get(doc)
            if r.status_code != 200:
                raise Exception('Failed to download %s' % doc)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            saved.append(local_filename)
        return saved

    def _parse(self, session, saved):
        parser = VotingParser()
        for current in saved:
            parser.parse(session, current)
