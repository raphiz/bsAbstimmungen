import os
import sys
import peewee

database = peewee.SqliteDatabase(':memory:')


def create_tables():
    database.connect()
    database.create_tables(BaseModel.__subclasses__())


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Fraction(BaseModel):

    id = peewee.PrimaryKeyField()
    abbrevation = peewee.CharField(max_length=10)


class Councillor(BaseModel):

    id = peewee.PrimaryKeyField()
    fullname = peewee.CharField(unique=True)
    firstname = peewee.CharField(null=True)
    lastname = peewee.CharField(null=True)
    fraction = peewee.ForeignKeyField(Fraction, related_name='councillors')
    # votings = relationship("Voting", backref="councillor")


class Vote(BaseModel):

    id = peewee.PrimaryKeyField()
    nr = peewee.IntegerField()
    timestamp = peewee.DateTimeField()
    affair = peewee.TextField()
    proposal = peewee.TextField()
    question = peewee.TextField()
    type = peewee.CharField()


VOTING_TYPES = ('yes', 'no', 'abstain', 'away', 'president')


class Voting(BaseModel):
    id = peewee.PrimaryKeyField()
    councillor = peewee.ForeignKeyField(Councillor, related_name='votings')
    vote = peewee.ForeignKeyField(Vote, related_name='votings')
    voting = peewee.CharField(max_length=1, constraints=[
        peewee.Check("voting in ('{0}')".format("','".join(VOTING_TYPES)))]
    )
