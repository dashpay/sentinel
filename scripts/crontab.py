#!/usr/bin/env python

"""
    - look through events table, process what we're suppose to do
    - can include building fee transactions, submitting govobjs to the network

"""

import sys
sys.path.append("lib")

from governance  import GovernanceObject
import libmysql
import config
import misc
import dashd
import random
import govtypes

from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal, PeeWeeGovernanceObject

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
    return PeeWeeEvent.delete().execute()

def clear_governance_objects():
    return PeeWeeGovernanceObject.delete().execute()

def clear_superblocks():
    return PeeWeeSuperblock.delete().execute()

def clear_proposals():
    return PeeWeeProposal.delete().execute()

def reset():
    clear_events()
    clear_governance_objects()
    clear_superblocks()
    clear_proposals()

def prepare_events():
    sql = """
    select id
      from event
     where start_time < NOW()
       and error_time = 0
       and prepare_time = 0
     limit 1
    """

    pw_event = PeeWeeEvent.get(
        (PeeWeeEvent.start_time < misc.get_epoch() ) &
        (PeeWeeEvent.error_time == 0) &
        (PeeWeeEvent.prepare_time == 0)
    )

    # libmysql.db.query(sql)
    # res = libmysql.db.store_result()
    # row = res.fetch_row()
    if pw_event:
        # pw_event = PeeWeeEvent.get(PeeWeeEvent.id == row[0])
        # >>> User.get(User.id == 1)
        # event = Event()
        # event.load(row[0])

        govobj = GovernanceObject()
        # govobj.load(event.get_id())
        govobj.load(pw_event.governance_object_id)

        print "# PREPARING EVENTS FOR DASH NETWORK"
        print
        print " -- cmd : ", govobj.get_prepare_command()
        print

        result = dashd.rpc_command(govobj.get_prepare_command())
        print " -- executing event ... getting fee_tx hash"

        # todo: what should it do incase of error?
        if misc.is_hash(result):
            hashtx = misc.clean_hash(result)
            print " -- got hash:", hashtx
            govobj.update_field("object_fee_tx", hashtx)
            govobj.save()
            pw_event.prepare_time = misc.get_epoch()
            pw_event.save()
            # event.update_field("prepare_time", misc.get_epoch())
            # event.save()
            libmysql.db.commit()
            return 1

        else:
            print " -- got error:", result
            # event.update_field("error_time", misc.get_epoch())
            # event.save()
            pw_event.error_time = misc.get_epoch()
            pw_event.save()
            # separately update event error message -- NGM: why separately?
            # event.update_error_message(result)
            pw_event.error_message = result
            libmysql.db.commit()

    return 0


def submit_events():
    sql = """
    select id
      from event
     where start_time < NOW()
       and prepare_time < NOW()
       and prepare_time > 0
       and submit_time = 0
       limit 1
    """

    now = misc.get_epoch()
    pw_event = PeeWeeEvent.get(
        (PeeWeeEvent.start_time < now ) &
        (PeeWeeEvent.prepare_time < now ) &
        (PeeWeeEvent.prepare_time > 0 ) &
        (PeeWeeEvent.submit_time == 0)
    )

    # libmysql.db.query(sql)
    # res = libmysql.db.store_result()
    # row = res.fetch_row()
    # if row:
    if pw_event:
        # event = Event()
        # event.load(row[0])

        govobj = GovernanceObject()
        print pw_event.governance_object_id
        govobj.load(pw_event.governance_object_id)
        hash = govobj.get_field("object_fee_tx")

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
                    # event.set_submitted()
                    pw_event.submit_time = misc.get_epoch()
                    print " -- executing event ... getting fee_tx hash"

                    result = dashd.rpc_command(govobj.get_submit_command())
                    if misc.is_hash(result):
                        print " -- got result", result

                        govobj.update_field("object_hash", result)
                        pw_event.save()
                        govobj.save()
                        libmysql.db.commit()
                        return 1
                    else:
                        print " -- got error", result
                else:
                    print " -- waiting for confirmation"

        return 0
