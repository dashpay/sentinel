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
from models import Superblock, Proposal, GovernanceObject
from models import VoteSignals, VoteOutcomes
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import socket

"""
 scripts/crontab.py
 -------------------------------
 FLAT MODULE FOR PROCESSING SENTINEL EVENTS

 - perform_dashd_object_sync
 - attempt_superblock_creation
 - check_object_validity
"""

# sync dashd gobject list with our local relational DB backend
def perform_dashd_object_sync(dashd):
    GovernanceObject.sync(dashd)

def attempt_superblock_creation(dashd):
    print "IN attempt_superblock_creation"
    import dashlib

    # extra check @ top, can be commented for testing
    if not dashd.is_masternode():
        print "We are not a Masternode... can't submit superblocks!"
        return

    event_block_height = dashd.next_superblock_height()
    current_height = dashd.rpc_command('getblockcount')

    # query votes for this specific ebh... if we have voted for this specific
    # ebh, then it's voted on. since we track votes this is all done using joins
    # against the votes table
    #
    # has this masternode voted on *any* superblocks at the given event_block_height?
    # have we voted FUNDING=YES for a superblock for this specific event_block_height?

    if Superblock.is_voted_funding(event_block_height):
       print "ALREADY VOTED! 'til next time!"
       return
    else:
       print "not yet voted! will continue."


    # ok, now we're here, we've clearly not yet voted for a Superblock at this
    # particular EBH... so it's vote time!
    #
    # first we must create a SB deterministically
    #
    # then see if it already exists on the network (will be in the DB b/c of the sync)
    #
    # then see if we win. If yes, submit it, if no, then... wait 'til next time I guess, then try and upvote/ -OR- submit again (b/c we might win the next election if one's not yet been submitted).

    # 3-day period for govobj maturity
    # only continue once we've entered the maturity phase...
    maturity_phase_delta = 1662 #  ~(60*24*3)/2.6
    if config.network == 'testnet':
        maturity_phase_delta = 24    # testnet

    maturity_phase_start_block = event_block_height - maturity_phase_delta
    print "current_height = %d" % current_height
    print "event_block_height = %d" % event_block_height
    print "maturity_phase_delta = %d" % maturity_phase_delta
    print "maturity_phase_start_block = %d" % maturity_phase_start_block

    if (current_height < maturity_phase_start_block):
        print "Not in maturity phase yet -- will not attempt Superblock"
        return

    proposal_quorum = dashd.governance_quorum()
    max_budget = dashd.next_superblock_max_budget()
    proposals = Proposal.approved_and_ranked(proposal_quorum, max_budget)

    print "\t%s = %s" % ('proposal_quorum', proposal_quorum)
    print "\t%s = %s" % ('max_budget', max_budget)
    print "\t%s = %s" % ('proposals', proposals)

    sb = dashlib.create_superblock(dashd, proposals, event_block_height)
    if not sb:
        print "No superblock created, sorry. Returning."
        return

    print "sb hash: %s" % sb.hex_hash()

    # vote here if found on network...
    if misc.is_hash(sb.object_hash):
        sb.vote(dashd, 'funding', 'yes')
        print "VOTED FUNDING FOR SB! We're done here 'til next month."
        return

    # find the elected MN vin for superblock creation...
    current_block_hash = dashd.current_block_hash()
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
        print "we are the winner! Submit SB to network"
        # if we already submitted it, DO NOT submit it again
        if not misc.is_hash(sb.object_hash):
            sb.submit(dashd)

    print "LEAVING attempt_superblock_creation"


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

def delete_orphaned_records():
    for go in GovernanceObject.orphans():
        go.delete_instance()

def fake_upvote_proposals(dashd):
    import dashlib
    max_budget = dashd.next_superblock_max_budget()
    for prop in Proposal.valid(max_budget):
        go = prop.governance_object
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

    # due to non-optimal DB design, it's currently possible to have orphan'ed govobj records:
    delete_orphaned_records()

    # TODO: fake upvote some proposals here...
    #fake_upvote_proposals(dashd)

    # auto vote network objects as valid/invalid
    check_object_validity(dashd)

    # create a Superblock if necessary
    attempt_superblock_creation(dashd)
