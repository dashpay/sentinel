#!/usr/bin/env python
import random
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..') )
import config
import misc
from dashd import DashDaemon
from dash_config import DashConfig
from models import Superblock, Proposal, GovernanceObject
from models import VoteSignals, VoteOutcomes
import socket
from misc import printdbg

"""
 scripts/crontab.py
 -------------------------------
 FLAT MODULE FOR PROCESSING SENTINEL EVENTS

 - perform_dashd_object_sync
 - check_object_validity
 - attempt_superblock_creation
"""

# sync dashd gobject list with our local relational DB backend
def perform_dashd_object_sync(dashd):
    GovernanceObject.sync(dashd)

def attempt_superblock_creation(dashd):
    import dashlib

    if not dashd.is_masternode():
        print "We are not a Masternode... can't submit superblocks!"
        return

    # query votes for this specific ebh... if we have voted for this specific
    # ebh, then it's voted on. since we track votes this is all done using joins
    # against the votes table
    #
    # has this masternode voted on *any* superblocks at the given event_block_height?
    # have we voted FUNDING=YES for a superblock for this specific event_block_height?

    event_block_height = dashd.next_superblock_height()

    if Superblock.is_voted_funding(event_block_height):
       printdbg("ALREADY VOTED! 'til next time!")
       return

    if not dashd.is_govobj_maturity_phase():
        printdbg("Not in maturity phase yet -- will not attempt Superblock")
        return

    proposals = Proposal.approved_and_ranked(dashd)
    sb = dashlib.create_superblock(dashd, proposals, event_block_height)
    if not sb:
        printdbg("No superblock created, sorry. Returning.")
        return

    try:
        dbrec = Superblock.get(Superblock.sb_hash == sb.hex_hash())
        dbrec.vote(dashd, VoteSignals.funding, VoteOutcomes.yes)
        printdbg("VOTED FUNDING FOR SB! We're done here 'til next superblock cycle.")
        return

        # TODO: then vote any other Superblocks for the same event_block_height as 'no'
        # maybe not necessary, but for completeness...
        #
        # this can be done simply via a DB query for all Superblocks for this
        # EBH which have not been voted on for 'funding', e.g. the opposite of
        # event.voted_on(signal=VoteSignals.funding)
        #
        # maybe a custom method/query for this specific case

    except Superblock.DoesNotExist as e:
        printdbg("The correct superblock wasn't found on the network...")

    # if we are the elected masternode...
    if (dashd.we_are_the_winner()):
        printdbg("we are the winner! Submit SB to network")
        sb.submit(dashd)
    #TODO: prune this & let it fly...
    else:
        printdbg("we lost the election... FAKING IT!")
        sb.submit(dashd)

def check_object_validity(dashd):
    # vote invalid objects
    for gov_class in [Proposal, Superblock]:
        for obj in gov_class.select():
            if not obj.voted_on(signal=VoteSignals.valid):
                obj.vote_validity(dashd)


def is_dashd_port_open(dashd):
    # test socket open before beginning, display instructive message to MN
    # operators if it's not
    port_open = False
    try:
        info = dashd.rpc_command('getinfo')
        port_open = True
    except socket.error as e:
        print "%s" % e

    return port_open

# TODO: remove this...
def fake_upvote_proposals(dashd):
    import dashlib
    max_budget = dashd.next_superblock_max_budget()
    for prop in Proposal.select():
        if prop.is_valid(dashd):
            go = prop.go
            go.yes_count += 1000
            go.absolute_yes_count += 1000
            go.save()

if __name__ == '__main__':
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

    # check dashd connectivity
    if not is_dashd_port_open(dashd):
        print "Cannot connect to dashd. Please ensure dashd is running and the JSONRPC port is open to Sentinel."
        sys.exit(2)

    # check database engine connectivity
    import models
    if not models.BaseModel.is_database_connected():
        print "Cannot connect to database. Please ensure MySQL database service is running and the JSONRPC port is open to Sentinel."
        sys.exit(2)

    # check dashd sync
    if not dashd.is_synced():
        print "dashd not synced with network! Awaiting full sync before running Sentinel."
        sys.exit(2)

    # ========================================================================
    # general flow:
    # ========================================================================
    #
    # load "gobject list" rpc command data & create new objects in local MySQL DB
    perform_dashd_object_sync(dashd)

    # TODO: remove this
    fake_upvote_proposals(dashd)

    # auto vote network objects as valid/invalid
    check_object_validity(dashd)

    # create a Superblock if necessary
    attempt_superblock_creation(dashd)
