#!/usr/bin/env python

"""
    - look through events table, process what we're suppose to do
    - can include building fee transactions, submitting govobjs to the network
"""
import pdb
from pprint import pprint
import random
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..') )
import config
import misc
from dashd import DashDaemon
from dashd import DashConfig
from models import Event, Superblock, Proposal, GovernanceObject
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

"""
 scripts/crontab.py
 -------------------------------
 FLAT MODULE FOR PROCESSING SENTINEL EVENTS

 - perform_dashd_object_sync
 - attempt_superblock_creation
 - auto_vote_objects
 - prepare_events
 - submit_events
"""

"""
prepare queued local events for submission to the Dash network (includes
paying collateral TX fee)

This process creates the collateral/burned transaction which allows the
governance object to propagate
"""
def prepare_events(dashd):
    for event in Event.new():
        govobj = event.governance_object
        gov_class_object = govobj.subobject

        try:
            gov_class_object.prepare(dashd)
        except JSONRPCException as e:
            print "error: %s" % e.message

"""
submit prepared local events to the Dash network

Upon maturation of the collateral tranasction, the system will submit an rpc command,
propagating the object thoughout the network
"""
def submit_events(dashd):

    for event in Event.prepared():
        govobj = event.governance_object
        gov_class_object = govobj.subobject

        try:
            gov_class_object.submit(dashd)
        except JSONRPCException as e:
            print "error: %s" % e.message

# sync dashd gobject list with our local relational DB backend
def perform_dashd_object_sync(dashd):
    GovernanceObject.sync(dashd)

def attempt_superblock_creation(dashd):
    import dashlib
    event_block_height = dashd.next_superblock_height()

    print "IN attempt_superblock_creation"

    # Number of blocks before a superblock to create superblock objects for auto vote
    # TODO: where is this value defined?
    #
    # TODO: should probably move this closer to the winner/submission check --
    # we're not assured that blocks won't be found back-to-back within a second
    # or so
    #
    # SUPERBLOCK_CREATION_DELTA = 1
    # if ( cycle - diff ) != SUPERBLOCK_CREATION_DELTA:
    #     return

    proposal_quorum = dashd.governance_quorum()
    max_budget = dashlib.next_superblock_max_budget(dashd)
    proposals = Proposal.approved_and_ranked(proposal_quorum, max_budget)

    print "\t%s = %s" % ('proposal_quorum', proposal_quorum)
    print "\t%s = %s" % ('max_budget', max_budget)
    print "\t%s = %s" % ('proposals', proposals)

    sb = dashlib.create_superblock(dashd, proposals, event_block_height)
    if not sb:
        print "No superblock created, sorry. Returning."
        return
    # pprint(sb.__dict__)

    print "sb  (orig): %s" % sb.serialise()
    print "sb (dashd): %s" % dashlib.SHIM_serialise_for_dashd( sb.serialise() )
    print "sb hash: %x" % sb.hash()


    # find the elected MN vin for superblock creation...
    current_block_hash = dashlib.current_block_hash(dashd)
    mn_list = dashd.get_masternodes()
    winner = dashlib.elect_mn(block_hash=current_block_hash, mnlist=mn_list)
    my_vin = dashd.get_current_masternode_vin()

    print "current_block_hash: [%s]" % current_block_hash
    print "MN election winner: [%s]" % winner
    print "current masternode VIN: [%s]" % my_vin

    if ( winner != my_vin ):
        print "we lost the election... FAKING IT!"
        my_vin = winner

    # if we are the elected masternode...
    if ( winner == my_vin ):
        # queue superblock submission
        print "we are the winner! Create and queue SB"
        sb.create_and_queue()
    else:
        # if the exact same deterministic Superblock exists on the network
        # already, then vote it up
        print "We did NOT the election... search and upvote SB if found on network"
        pass

    print "LEAVING attempt_superblock_creation"

def auto_vote_objects(dashd):
    print "IN auto_vote_objects"

    # for all valid superblocks, vote yes for funding them
    #for sb in Superblock.valid():
    #    print "found valid Superblock, voting funding 'yes'"
    #    sb.vote(dashd, 'funding', 'yes')

    # vote invalid objects
    for gov_class in [Proposal]: #, Superblock]:
        for invalid in gov_class.invalid():
            print "found invalid %s!" % gov_class.__name__
            pprint(invalid.get_dict())
            print "voting invalid..."
            #pdb.set_trace()
            invalid.vote(dashd, 'valid', 'no')

    print "LEAVING auto_vote_objects"

if __name__ == '__main__':
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

    # ========================================================================
    # general flow:
    # ========================================================================
    #
    # load "gobject list" rpc command data & create new objects in local MySQL DB
    perform_dashd_object_sync(dashd)

    # create superblock & submit if elected & valid
    attempt_superblock_creation(dashd)
    auto_vote_objects(dashd)

    # prepare/submit pending events
    prepare_events(dashd)
    submit_events(dashd)
