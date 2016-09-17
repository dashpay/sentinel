# -*- coding: utf-8 -*-
import pdb
from pprint import pprint
import re
import sys,  os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config
from models import Superblock, Proposal, GovernanceObject, Setting
from peewee import PeeweeException #, OperationalError, IntegrityError
from time import time
from dashd import DashDaemon
from dashd import DashConfig
import dashlib
dashd = DashDaemon.from_dash_conf(config.dash_conf)
from models import Signal, Vote, Outcome
from decimal import Decimal
# ==============================================================================
# do shit here

#pr = Proposal(
#    name='我想喝一點點無龍茶',
#    url='blah.com',
#    payment_address='yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV',
#    payment_amount=39.23,
#)

pr = Proposal(
    name='beer-reimbursement-7',
    url='https://dashcentral.com/beer-reimbursement-7',
    payment_address='yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui',
    payment_amount=7,
)

print "pr = %s" % pr.__dict__
print "dashd hex = %s" % pr.dashd_serialise()