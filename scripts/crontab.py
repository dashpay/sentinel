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

 - prepare_events

    This process creates the collateral/burned transaction which allows the governance object to propagate

 - submit_events

    Upon maturation of the collateral tranasction, the system will submit an rpc command,
    propagating the object thoughout the network

"""

# from dash/src/governance.hL43 -- GOVERNANCE_FEE_CONFIRMATIONS
CONFIRMATIONS_REQUIRED = 6

# prepare queued local events for submission to the Dash network (includes
# paying collateral TX fee)
def prepare_events(dashd):

    for event in Event.new():
        govobj = event.governance_object

        print "# PREPARING EVENTS FOR DASH NETWORK"
        print
        print " -- cmd : [%s]" % govobj.get_prepare_command()
        print

        try:
            collateral_tx = dashd.rpc_command(*govobj.get_prepare_command())
            print " -- executing prepare ... getting collateral_tx hash"
            print " -- got hash: [%s]" % collateral_tx

            govobj.object_fee_tx = collateral_tx
            event.prepare_time = misc.get_epoch()

            with govobj._meta.database.atomic():
                govobj.save()
                event.save()

        except JSONRPCException as e:
            print "error: %s" % e.message
            event.error_time = misc.get_epoch()
            event.error_message = e.message
            event.save()


# submit pending local events to the Dash network
def submit_events(dashd):

    for event in Event.prepared():
        govobj = event.governance_object

        print "# SUBMIT PREPARED EVENTS FOR DASH NETWORK"
        print
        print " -- submit cmd : ", govobj.get_submit_command()
        print

        tx = dashd.rpc_command('gettransaction', govobj.object_fee_tx)
        num_bc_confirmations = tx['bcconfirmations']

        print " -- confirmations: [%d]" % num_bc_confirmations
        print " -- CONFIRMATIONS_REQUIRED: [%d]" % CONFIRMATIONS_REQUIRED

        if num_bc_confirmations < CONFIRMATIONS_REQUIRED:
            print " -- waiting for confirmations"
            continue

        try:
            print " -- executing submit ... getting object hash"
            object_hash = dashd.rpc_command(*govobj.get_submit_command())
            print " -- got hash: [%s]" % object_hash

            event.submit_time = misc.get_epoch()
            govobj.object_hash = object_hash

            # save all
            with govobj._meta.database.atomic():
                govobj.save()
                event.save()

        except JSONRPCException as e:
            print "error: %s" % e.message
            event.error_time = misc.get_epoch()
            event.error_message = e.message
            event.save()

# sync dashd gobject list with our local relational DB backend
def perform_dashd_object_sync(dashd):
    GovernanceObject.sync(dashd)

def attempt_superblock_creation(dashd):
    import dashlib
    height = dashd.rpc_command('getblockcount')
    cycle = dashd.superblockcycle()
    diff = height % cycle
    event_block_height = (height + (cycle - (height % cycle)))

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

    print "current_block_hash: [%s]" % current_block_hash
    print "MN election winner: [%s]" % winner
    print "current masternode VIN: [%s]" % dashd.get_current_masternode_vin()

    # if we are the elected masternode...
    if ( winner == dashd.get_current_masternode_vin() ):
        # queue superblock submission
        print "we are the winner! Create and queue SB"
        sb.create_and_queue()
    else:
        # if the exact same deterministic Superblock exists on the network
        # already, then vote it up
        print "We did NOT the election... search and upvote SB if found on network"
        pass


def auto_vote_objects(dashd):

    # for all valid superblocks, vote yes for funding them
    for sb in Superblock.valid():
        sb.vote(dashd, 'funding', 'yes')

    # TODO: refactor this to start from composed objects, not GOs (which should
    # theoretically not have knowledge of the composing objects, as it's
    # data-agnostic)
    # vote invalid objects
    for go in GovernanceObject.invalid():
        go.vote(dashd, 'valid', 'no')



if __name__ == '__main__':
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

    # ========================================================================
    # general flow:
    # ========================================================================
    #
    # load "gobject list" rpc command data & create new objects in local MySQL DB

    # don't wanna sync votes, b/c testing superblocks right now...
    #perform_dashd_object_sync(dashd)

    # create superblock & submit if elected & valid
    attempt_superblock_creation(dashd)
    #auto_vote_objects(dashd)

    # prepare/submit pending events
    #prepare_events(dashd)
    #submit_events(dashd)
