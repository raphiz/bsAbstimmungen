from .utils import get_pdf_content
from ..models import *
from datetime import datetime
import re


class VotingParser:

    lines = None

    def parse(self, session, file):
        # TODO: skip if already parsed!
        self.idx = -1
        self.lines = get_pdf_content(file)
        self.session = session

        vote = self._parseVote()

        for i in range(0, 100):
            self._parseVoting(vote)

    def _parseVoting(self, vote):

        match = re.fullmatch('([^\(\)]*)\s\(([a-zA-Z\/]*)\)', self.token())

        fullname = match.group(1)
        fraction = match.group(2)

        councillor = self._get_councillor_for(fullname, fraction)
        voting = Voting(
            vote=vote,
            councillor=councillor,
            voting=Voting.enum_mapping.get(self.token(), None)
        )
        self.session.add(voting)
        self.session.commit()

    def _get_fraction_for(self, abbrevation):
        res = self.session.query(Fraction)\
            .filter(Fraction.abbrevation == abbrevation)
        if(res.count() == 0):
            fraction = Fraction(abbrevation=abbrevation)
            self.session.add(fraction)
            self.session.commit()
            return fraction
        return res.one()

    def _get_councillor_for(self, fullname, fraction):
        res = self.session.query(Councillor) \
            .join(Councillor.fraction) \
            .filter(Councillor.fullname == fullname)
        if(res.count() == 0):
            councillor = Councillor(fullname=fullname)
            councillor.fraction = self._get_fraction_for(fraction)
            self.session.add(councillor)
            self.session.commit()
            return councillor
        return res.one()

    def _parseVote(self):
        vote = Vote()

        self._assertToken('Grosser Rat des Kantons Basel-Stadt')
        self._assertToken('Ratssekretariat')
        self._assertToken('Nr')

        vote.nr = self.token()
        vote.timestamp = datetime.strptime(
            '%s %s' % (self.token(), self.token()),
            '%d.%m.%Y %H:%M:%S'
        )
        vote.type = self.token()

        exists = self.session.query(Vote) \
            .filter(Vote.nr == vote.nr) \
            .filter(Vote.timestamp == vote.timestamp) \
            .count()
        if(exists > 0):
            raise Exception(
                'The vote nr %s from %s is already imported' %
                (vote.nr, vote.timestamp)
            )

        self._assertToken('Ergebnis der Abstimmung')
        self._assertToken('Geschäft')

        vote.affair = self._parseUntil('Gegenstand / Antrag')
        vote.proposal = self._parseUntil('Abstimmungsfrage')

        vote.question = self._parseUntil('([^\(\)\s]*\s)*\([A-Z]*\)', True)
        self._step_back()

        self.session.add(vote)
        self.session.commit()

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
            raise Exception(
                'Unexpected message in PDF. Excepted "%s" but recieved "%s"' %
                (expected, actual)
            )

    def _step_back(self):
        self.idx = self.idx-1

    def token(self):
        self.idx = self.idx+1
        return self.lines[self.idx]
