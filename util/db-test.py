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
from dashd import DashDaemon
from dashd import DashConfig
import dashlib
dashd = DashDaemon.from_dash_conf(config.dash_conf)
from models import Signal, Vote, Outcome
from decimal import Decimal
# ==============================================================================
# do shit here

pr = Proposal(
    name='我想喝一點點無龍茶',
    url='blah.com',
    payment_address='yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV',
    payment_amount=39.23,
)

pdb.set_trace()

sb = Superblock.latest()
sb.voted_on()

# sb.voted_on(VoteSignals.valid)

# sb.is_valid(dashd)
# if (not sb.voted_on(VoteSignals.valid) and sb.is_valid(dashd))

# ==============================================================================
pdb.set_trace()
z = 1
