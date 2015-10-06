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


class Ward(BaseModel):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField(max_length=10)

GROUP_TYPES = ('private', 'public', 'commission')

from playhouse.hybrid import hybrid_property
class Group(BaseModel):

    id = peewee.PrimaryKeyField()
    name = peewee.CharField()
    abbrevation = peewee.CharField(null=True)
    kind = peewee.CharField(max_length=1, constraints=[
        peewee.Check("kind in ('{0}')".format("','".join(GROUP_TYPES)))]
    )


class Councillor(BaseModel):

    id = peewee.PrimaryKeyField()
    fullname = peewee.CharField(unique=True)
    firstname = peewee.CharField(null=True)
    lastname = peewee.CharField(null=True)

    zip = peewee.CharField(null=True, max_length=4)
    title = peewee.CharField(null=True)
    phone_business = peewee.CharField(null=True)
    phone_mobile = peewee.CharField(null=True)
    phone_private = peewee.CharField(null=True)
    fax_business = peewee.CharField(null=True)
    fax_private = peewee.CharField(null=True)
    job = peewee.CharField(null=True)
    locality = peewee.CharField(null=True)
    birthdate = peewee.DateField(null=True)
    employer = peewee.CharField(null=True)
    website = peewee.CharField(null=True)
    address = peewee.CharField(null=True)

    fraction = peewee.ForeignKeyField(Fraction, related_name='councillors')
    ward = peewee.ForeignKeyField(Ward, null=True, related_name='councillors')

    @hybrid_property
    def commission_memberships(self):
        return self.groups.select().join(Group).where(
            Group.kind == 'commission')

    @hybrid_property
    def nonstate_membership(self):
        return self.groups.select().join(Group).where(Group.kind == 'nonstate')

    @hybrid_property
    def state_membership(self):
        return self.groups.select().join(Group).where(Group.kind == 'state')


class GroupMembership(BaseModel):
    councillor = peewee.ForeignKeyField(Councillor, related_name='groups')
    group = peewee.ForeignKeyField(Group, related_name='members')
    position = peewee.CharField(null=True)
    member_since = peewee.DateField(null=True)
    comment = peewee.CharField(null=True)


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
