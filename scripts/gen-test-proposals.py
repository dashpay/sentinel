import pdb
from pprint import pprint
import re
import sys,  os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config
from models import Event, Superblock, Proposal, GovernanceObject
from peewee import PeeweeException #, OperationalError, IntegrityError
from time import time
import dashlib
from decimal import Decimal
# ==============================================================================

def fake_proposal_name(fake):
    return fake.domain_word() + '-' + str(fake.random_int())

def create_fake_proposal_data():
    from faker import Faker
    fake = Faker()

    name = fake_proposal_name(fake)
    while GovernanceObject.object_with_name_exists(name):
        name = fake_proposal_name(fake)

    dikt = {
        'name': name,
        'url': "http://dashcentral.org/%s" % name,
        'payment_address': 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui',
        'payment_amount': Decimal(5.75),
        'start_epoch': 1483250400,
        'end_epoch': 1491368400,
    }

    return dikt



num = 2
for i in range(num):
    data = create_fake_proposal_data()
    proposal = Proposal(**data)
    proposal.create_and_queue()
