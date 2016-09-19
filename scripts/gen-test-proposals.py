import pdb
from pprint import pprint
import re
import sys,  os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config
from models import Proposal, GovernanceObject
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

    dikt = {
        'name': name,
        'url': "https://www.dashcentral.org/p/%s" % name,
        'payment_address': 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui',
        'payment_amount': Decimal(25.75),
        'start_epoch': 1474261086,
        'end_epoch': 1491368400,
    }

    return dikt


num = 2
for i in range(num):
    import dashlib
    data = create_fake_proposal_data()
    proposal = Proposal(**data)
    print "%s - %s" % (proposal.name, proposal.dashd_serialise())
