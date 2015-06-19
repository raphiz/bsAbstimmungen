import os
import sys
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def initialize(engine):
    Base.metadata.bind = engine


def create_tables(engine):
    # Create all tables in the engine.
    Base.metadata.create_all(engine)


class Fraction(Base):

    __tablename__ = 'fraction'

    id = Column(Integer, primary_key=True)
    abbrevation = Column(String(255))
    councillors = relationship("Councillor", backref="fraction")


class Councillor(Base):

    __tablename__ = 'councillor'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(250), nullable=False)
    firstname = Column(String(250))
    lastname = Column(String(250))
    fraction_id = Column(Integer, ForeignKey('fraction.id'))
    votings = relationship("Voting", backref="councillor")


class Vote(Base):
    __tablename__ = 'vote'

    id = Column(Integer, primary_key=True)
    nr = Column(Integer)
    timestamp = Column(DateTime())
    affair = Column(String(1024))
    proposal = Column(String(1024))
    question = Column(String(1024))
    type = Column(String(100))
    votings = relationship("Voting", backref="vote")


class Voting(Base):

    __tablename__ = 'voting'

    id = Column(Integer, primary_key=True)
    councillor_id = Column(Integer, ForeignKey('councillor.id'))
    vote_id = Column(Integer, ForeignKey('vote.id'))
    enum_mapping = {'J': 'YES',
                    'N': 'NO',
                    'E': 'ABSTAIN',
                    'A': 'AWAY',
                    'P': 'PRESIDENT',
                    }
    voting = Column(Enum('YES', 'NO', 'AWAY', 'ABSTAIN', 'PRESIDENT'))
