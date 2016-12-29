# -*- coding: utf-8 -*-
import pdb
from pprint import pprint
import re
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config
from models import Superblock, Proposal, GovernanceObject, Setting, Signal, Vote, Outcome, Watchdog
from models import VoteSignals, VoteOutcomes
from peewee import PeeweeException #, OperationalError, IntegrityError
from dashd import DashDaemon
import dashlib
from decimal import Decimal
dashd = DashDaemon.from_dash_conf(config.dash_conf)
# ==============================================================================
# do shit here

#pr = Proposal(
#    name='proposal7',
#    url='https://dashcentral.com/proposal7',
#    payment_address='yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV',
#    payment_amount=39.23,
#    start_epoch=1483250400,
#    end_epoch=1491022800,
#)

#sb = Superblock(
#    event_block_height = 62500,
#    payment_addresses = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
#    payment_amounts  = "5|3"
#)

pdb.set_trace()
#dashd.get_object_list()

# ==============================================================================
#pdb.set_trace()
1
