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

CONFIRMATIONS_REQUIRED = 7

def clear_events():
    return Event.delete().execute()

def clear_governance_objects():
    return GovernanceObject.delete().execute()

def clear_superblocks():
    return Superblock.delete().execute()

def clear_proposals():
    return Proposal.delete().execute()

def reset():
    clear_events()
    clear_governance_objects()
    clear_superblocks()
    clear_proposals()



# prepare queued local events for submission to the Dash network (includes
# paying collateral TX fee)
def prepare_events(dashd):

    for event in Event.new():
        govobj = event.governance_object

        print "# PREPARING EVENTS FOR DASH NETWORK"
        print
        # pdb.set_trace()
        print " -- cmd : [%s]" % govobj.get_prepare_command()
        print

        result = dashd.rpc_command(govobj.get_prepare_command())
        print " -- executing event ... getting fee_tx hash"

        # todo: what should it do incase of error?
        if misc.is_hash(result):
            hashtx = misc.clean_hash(result)
            print " -- got hash:", hashtx

            govobj.object_fee_tx = hashtx
            event.prepare_time = misc.get_epoch()

            with govobj._meta.database.atomic():
                govobj.save()
                event.save()

            return 1

        else:
            print " -- got error:", result

            event.error_time = misc.get_epoch()
            event.error_message = result
            event.save()

    return 0


# submit pending local events to the Dash network
def submit_events(dashd):

    for event in Event.prepared():
        govobj = event.governance_object
        hash = govobj.object_fee_tx

        print "# SUBMIT PREPARED EVENTS FOR DASH NETWORK"
        print
        print " -- cmd : ", govobj.get_submit_command()
        print
        print " -- executing event ... getting fee_tx hash"

        if misc.is_hash(hash):
            tx = dashd.CTransaction()
            if tx.load(hash):
                print " -- confirmations: ", tx.get_confirmations()

                if tx.get_confirmations() >= CONFIRMATIONS_REQUIRED:
                    event.submit_time = misc.get_epoch()
                    print " -- executing event ... getting fee_tx hash"

                    result = dashd.rpc_command(govobj.get_submit_command())
                    if misc.is_hash(result):
                        print " -- got result", result
                        govobj.object_hash = result
                        with govobj._meta.database.atomic():
                            govobj.save()
                            event.save()

                        return 1
                    else:
                        print " -- got error", result
                        event.error_time = misc.get_epoch()
                        event.error_message = result
                        event.save()

                else:
                    print " -- waiting for confirmation"

        return 0


# sync dashd gobject list with our local relational DB backend
def perform_dashd_object_sync(dashd):
    golist = dashd.rpc_command('gobject list')
    for item in golist.values():
        (go, subobj) = GovernanceObject.load_from_dashd( item )



def attempt_superblock_creation(dashd):
    from dashlib import current_block_hash, create_superblock
    height = dashd.rpc_command( 'getblockcount' )
    govinfo = dashd.rpc_command( 'getgovernanceinfo' )
    cycle = govinfo['superblockcycle']
    cycle = 5 # TODO: remove this test value
    diff = height % cycle
    event_block_height = height + diff

    # Number of blocks before a superblock to create superblock objects for auto vote
    SUPERBLOCK_CREATION_DELTA = 1
    if ( cycle - diff ) != SUPERBLOCK_CREATION_DELTA:
        return

    # return an array of proposals
    quorum    = dashd.governance_quorum()
    proposals = Proposal.approved_and_ranked(event_block_height, quorum)

    if len( proposals ) < 1:
        # Don't create empty superblocks
        return

    # find the elected MN vin for superblock creation...
    winner = elect_mn(block_hash=current_block_hash(), mnlist=dashd.get_masternodes())

    sb = dashlib.create_superblock( dashd, proposals, event_block_height )

    # if we are the elected masternode...
    if ( winner == dashd.get_current_masternode_vin() )
        # queue superblock submission
        sb.create_and_queue()

    # else if exists in network already, then upvote it?


def auto_vote_objects(dashd):

    # for all valid superblocks, vote yes for funding them
    for sb in Superblock.valid():
        sb.vote(dashd, 'funding', 'yes')

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
    perform_dashd_object_sync(dashd)

    # create superblock & submit if elected & valid
    attempt_superblock_creation(dashd)

    auto_vote_objects(dashd)

    # prepare/submit pending events
    prepare_events(dashd)
    submit_events(dashd)
