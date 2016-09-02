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


def prepare_events():
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

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
            govobj.save()

            event.prepare_time = misc.get_epoch()
            event.save()

            return 1

        else:
            print " -- got error:", result

            event.error_time = misc.get_epoch()
            event.error_message = result
            event.save()

    return 0


# TODO: description of what exactly this method does
def submit_events():

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
                        # NGM/TODO: atomic?
                        event.save()
                        govobj.save()

                        return 1
                    else:
                        print " -- got error", result
                        event.error_time = misc.get_epoch()
                        event.error_message = result
                        event.save()

                else:
                    print " -- waiting for confirmation"

        return 0


if __name__ == '__main__':
    prepare_events()
