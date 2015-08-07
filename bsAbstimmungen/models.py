import os
import sys
import peewee

database = peewee.Proxy()


def create_tables():
    db = peewee.SqliteDatabase(':memory:')
    database.initialize(db)
    database.connect()
    database.create_tables(BaseModel.__subclasses__(), safe=True)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Fraction(BaseModel):

    id = peewee.PrimaryKeyField()
    abbrevation = peewee.CharField(max_length=10)


GROUP_TYPES = ('private', 'public', 'governmental')


class Group(BaseModel):

    id = peewee.PrimaryKeyField()
    name = peewee.CharField()
    kind = peewee.CharField(max_length=1, constraints=[
        peewee.Check("kind in ('{0}')".format("','".join(GROUP_TYPES)))]
    )


class Councillor(BaseModel):

    id = peewee.PrimaryKeyField()
    fullname = peewee.CharField(unique=True)
    firstname = peewee.CharField(null=True)
    lastname = peewee.CharField(null=True)
    fraction = peewee.ForeignKeyField(Fraction, related_name='councillors')
    # votings = relationship("Voting", backref="councillor")


class GroupMembership(BaseModel):
    councillor = peewee.ForeignKeyField(Fraction, related_name='groups')
    group = peewee.ForeignKeyField(Fraction, related_name='members')
    comment = peewee.CharField()


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
