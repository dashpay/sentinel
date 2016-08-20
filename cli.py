#!/usr/bin/env python

import argparse
import sys
sys.path.append("lib")
sys.path.append("scripts") 

import cmd
import misc
import libmysql
import config
import crontab
import cmd, sys
import govtypes
import random 
import json 

# PeeWee models -- to replace hand-coded versions
from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal

from datetime import datetime, date, time

from governance import GovernanceObject, GovernanceObjectMananger, Setting, Event
from dashd import CTransaction

# Enable only for testing:
crontab.CONFIRMATIONS_REQUIRED = 1

parent = GovernanceObject()
parent.init()

db_creds = config.db_config
db = libmysql.connect(db_creds['hostname'], db_creds['username'], db_creds['password'], db_creds['database'])

commands = {}

"""

    Sentinel - v1
    --------------------------------    

     - this is an exact copy of our existing functionality, just reimplemented in python using sentinel

    old commands: 
        mnbudget prepare beer-reimbursement2 www.dashwhale.org/p/beer-reimbursement2 1 481864 XfoGXXFJtobHvjwfszWnbMNZCBAHJWeN6G 50
        mnbudget submit beer-reimbursement2 www.dashwhale.org/p/beer-reimbursement2 1 481864 XfoGXXFJtobHvjwfszWnbMNZCBAHJWeN6G 50 REPLACE_WITH_COLLATERAL_HASH

    1. proposal --create --proposal_name="beer-reimbursement" --description_url="www.dashwhale.org/p/beer-reimbursement" --start-date="2017/1/1" --end-date="2017/6/1"
    2. cron process (will automatically submit the proposal to the network)

"""

# ---------------------------------------------------------------------

""" SENTINEL AUTOCOMPLETE FOR CLI """

# proposal --create [...] 
commands["proposal"] = [
    "--create",
    "--name",
    "--description_url",
    "--proposal_url",
    "--start_date",
    "--end_date"
]

# superblock --create [...] 
commands["trigger"] = [
    "--create",
    "--date",
    "--payments"
]

# crontab --task="(prepare_events|submit_events)"
commands["crontab"] = [
    "--clear_events",
    "--prepare_events",
    "--submit_events"
]

# ---------------------------------------------------------------------

"""

    Sentinel Shell (CLI)
"""

class SentinelShell(cmd.Cmd):
    intro = 'Welcome to the sentinel shell.   Type help or ? to list commands.\n'
    prompt = '(sentinel) '
    file = None

    """
        Network Proposal Tasks

    """
    def do_proposal(self, arg):
        'proposal --create --proposal_name="sb-test" --description_url="www.dashwhale.org/p/sb-test" --start_date="2016/8/1" --end_date="2017/1/1" --payment_address="ydE7B1A7htNwSTvvER6xBdgpKZqNDbbEhPydE7B1A7htNwSTvvER6xBdgpKZqNDbbEhP" --payment_amount="23"'

        parser = argparse.ArgumentParser(description='Create a dash proposal')

        # desired action
        parser.add_argument('-c', '--create', help="create", action='store_true')

        # object identity (existentially... what does it mean to be a pubkey?)
        parser.add_argument('-k', '--pubkey', help='your public key for this username (only required for --create)')

        # meta data (create or amend)
        parser.add_argument('-p', '--proposal_name', help='the proposal name (must be unique)')
        parser.add_argument('-d', '--description_url', help='your proposals url where a description of the project can be found')
        parser.add_argument('-s', '--start_date', help='starting data, must be the first of the month. Example : 2017/1/1')
        parser.add_argument('-e', '--end_date', help='ending data, must be the first of the month. Example : 2017/6/1')
        parser.add_argument('-x', '--payment_address', help='the payment address where you wish to receive the funds')
        parser.add_argument('-a', '--payment_amount', help='how much to send in each payment to the payment address')

        # process

        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return

        ### ------ CREATE METHOD -------- ####

        if args.create:
            #--create --revision=1 --pubkey=XPubkey --username="user-cid" 
            if not args.proposal_name:
                print "proposal creation requires a proposal name, use --proposal_name"
                return

            if not args.description_url:
                print "proposal creation requires a description url, use --description_url"
                return

            if not args.start_date:
                print "start creation requires a start date, use --start_date"
                return

            if not args.end_date:
                print "end creation requires a end date, use --end_date"
                return

            if not args.payment_address:
                print "payment creation requires a valid base58 payment address, use --payment_address"
                return

            if not args.payment_amount:
                print "payment creation requires a valid payment amount, use --payment_amount"
                return

            ### ---- CONVERT AND CHECK EPOCHS -----

            start_epoch = 0
            end_epoch = 0

            try:
                start_epoch = datetime.strptime(args.start_date, '%d/%m/%y').strftime('%s')
                end_epoch = datetime.strptime(args.end_date, '%d/%m/%y').strftime('%s')
            except:
                try:
                    start_epoch = datetime.strptime(args.start_date, '%Y/%m/%d').strftime('%s')
                    end_epoch = datetime.strptime(args.end_date, '%Y/%m/%d').strftime('%s')
                except:
                    pass
            
            if start_epoch == 0 or end_epoch == 0:
                print "start or end date has invalid format, YYYY/MM/DD or DD/MM/YY is required";
                return

            ### ---- CHECK NAME UNIQUENESS -----
            if GovernanceObjectMananger.object_with_name_exists(args.proposal_name):
                print "governance object with that name already exists"
                return

            # -- gets bcconfirmations...
            fee_tx = CTransaction()

            newObj = GovernanceObject()
            newObj.create_new(parent, args.proposal_name, govtypes.proposal, govtypes.FIRST_REVISION, fee_tx)
            last_id = newObj.save()

            print last_id

            if last_id != None:
                # ADD OUR PROPOSAL AS A SUB-OBJECT WITHIN GOVERNANCE OBJECT

                pw_proposal = PeeWeeProposal()
                pw_proposal.governance_object_id = last_id
                pw_proposal.proposal_name = args.proposal_name
                pw_proposal.description_url = args.description_url
                pw_proposal.start_epoch = start_epoch
                pw_proposal.end_epoch = end_epoch
                pw_proposal.payment_address = args.payment_address
                pw_proposal.payment_amount = args.payment_amount

                # APPEND TO GOVERNANCE OBJECT

                newObj.add_subclass("proposal", pw_proposal)
                newObj.save()

                # CREATE EVENT TO TALK TO DASHD / PREPARE / SUBMIT OBJECT
                
                pwevent = PeeWeeEvent()
                pwevent.governance_object_id = last_id
                pwevent.save()
                #event = Event()
                #event.create_new(last_id)
                #event.save()
                libmysql.db.commit()

                print "event queued successfully"
            else:
                print "error:", newObj.last_error()

                # abort mysql commit

            return

        ### ------- ELSE PRINT HELP --------------- ### 

        parser.print_help()

        ### ------ CREATE METHOD -------- ####



    """
        Superblock 

    """
    def do_superblock(self, arg):
        'superblock --create --event_block_height="28224" --payments="yLipDagwb1gM15RaUq3hpcaTxzDsFsSy9a=100"'
        'superblock --create --event_date="2017/1/1" --payments="Addr1=amount,Addr2=amount,Addr3=amount"'

        parser = argparse.ArgumentParser(description='Create a dash proposal')

        # desired action
        parser.add_argument('-c', '--create', help="create", action='store_true')

        # meta data (create or amend)
        parser.add_argument('-p', '--payments', help='the payments desired in the superblock, serialized as a list. example: {"Addr1": amount,"Addr2": amount}')
        parser.add_argument('-b', '--event_block_height', help='block height to issue superblock')

        # process

        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return

        ### ------ CREATE METHOD -------- ####

        if args.create:
            #--create --revision=1 --pubkey=XPubkey --username="user-cid" 
            if not args.payments:
                print "superblock creation requires a payment descriptions, use --payments"
                return

            if not args.event_block_height:
                print "superblock creation requires a event_block_height, use --event_block_height"
                return

            ### ---- CONVERT AND CHECK EPOCHS -----

            payments = misc.normalize(args.payments).split(",")
            if len(payments) > 0:
                pass

            # COMPILE LIST OF ADDRESSES AND AMOUNTS 

            list_addr = []
            list_amount = []
            for payment in payments:
                print payment
                addr,amount = payment.split("=")
                list_addr.append(addr)
                list_amount.append(amount)

            print list_amount
            print list_addr

            # CREATE NAME ACCORDING TO STARTING DATE (NON-UNIQUE IS NOT AN ATTACK)
            superblock_name = "sb" + str(random.randint(1000000, 9999999))

            # DOES THIS ALREADY EXIST?
            if GovernanceObjectMananger.object_with_name_exists(superblock_name):
                print "governance object with that name already exists"
                return

            event_block_height = misc.normalize(args.event_block_height);

            print event_block_height

            fee_tx = CTransaction()

            newObj = GovernanceObject()
            newObj.create_new(parent, superblock_name, govtypes.trigger, govtypes.FIRST_REVISION, fee_tx)
            last_id = newObj.save()

            #pWnewObj = PeeWeeGovernanceObject()
            #pWnewObj.create_new(parent, superblock_name, govtypes.trigger,
            #                    govtypes.FIRST_REVISION, fee_tx)
            #last_id = pWnewObj.save()

            print last_id

            if last_id != None:
                # ADD OUR PROPOSAL AS A SUB-OBJECT WITHIN GOVERNANCE OBJECT

                pwsb = PeeWeeSuperblock()
                pwsb.governance_object_id = last_id
                #pwsb.type = govtypes.trigger
                #pwsb.subtype = 'superblock'
                pwsb.superblock_name = superblock_name
                pwsb.event_block_height = event_block_height
                pwsb.payment_addresses = ("|".join(list_addr))
                pwsb.payment_amounts = ("|".join(list_amount))

                # APPEND TO GOVERNANCE OBJECT

                newObj.add_subclass("trigger", pwsb)
                newObj.save()

                # CREATE EVENT TO TALK TO DASHD / PREPARE / SUBMIT OBJECT

                #event = Event()
                #event.create_new(last_id)
                #event.save()
                pwevent = PeeWeeEvent()
                pwevent.governance_object_id = last_id
                pwevent.save()
                libmysql.db.commit()

                print "event queued successfully"
            else:
                print "error:", newObj.last_error()

                # abort mysql commit

            return

        ### ------- ELSE PRINT HELP --------------- ### 

        parser.print_help()

        ### ------ CREATE METHOD -------- ####

    """
        Crontab Tasks

    """
    def do_crontab(self, arg):
        ' crontab [--clear_events --prepare_events --submit_events]"'

        parser = argparse.ArgumentParser(description='Do a crontab task')

        # meta data (create or amend)
        parser.add_argument('-p', '--prepare_events', help="Submit any queued governance objects pending submission (stage 2: submission of colateral tx and governance object)", action="store_true")
        parser.add_argument('-s', '--submit_events', help="Process any queued events pending creation (stage 1: prepare colateral tx)", action="store_true")
        parser.add_argument('-b', '--process_budget', help="Process superblock for monthly budget")
        parser.add_argument('-c', '--clear_events', help="Clear event queue (for testing only)", action="store_true")
        parser.add_argument('-r', '--reset', help="Hard reset (for testing only)", action="store_true")
        
        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        ### ------ NAME METHOD -------- ####

        if args.clear_events:
            count = crontab.clear_events()
            print count, "events cleared"
            return

        if args.reset:
            print "Hard Reset:"
            count = crontab.clear_events()
            print count, "events cleared"
            count = crontab.clear_governance_objects()
            print count, "governance objects cleared"
            count = crontab.clear_superblocks()
            print count, "superblocks cleared"
            count = crontab.clear_proposals()
            print count, "proposals cleared"
            return

        ### --- EXECUTED DESIRED CRONTAB FOR USER --- ####

        if args.process_budget:
            print crontab.process_budget()
            return

        if args.prepare_events:
            count = crontab.prepare_events()
            print count, "events successfully prepared (stage 1)"
            return

        elif args.submit_events:
            count = crontab.submit_events()
            print count, "events successfully submitted (stage 2)"
            return
        else:
            print "unknown command"
            return

        ### ------- ELSE PRINT HELP --------------- ### 

        parser.print_help()

    def complete_crontab(self, text, line, start_index, end_index):
        if text:
            return [command for command in commands["crontab"]
                    if command.startswith(text)]
        else:
            return commands

    """

        Vote on a specific proposal

    """


    # ----- (internal) vote on something -----
    def do_vote(self, arg):
        'Command action on the dash network'
        ' vote --times=22 --type=funding --outcome=yes [--hash=governance-hash --name=obj-name]'

        parser = argparse.ArgumentParser(description='Vote on governance objects and signal what dash should do with them.')

        #voting
        parser.add_argument('-t', '--times')
        parser.add_argument('-p', '--type')
        parser.add_argument('-o', '--outcome')
        parser.add_argument('-n', '--hash')
        parser.add_argument('-k', '--pubkey')

        ### ------- ELSE PRINT HELP --------------- ### 

        parser.print_help()

    # ----- quit the program -----
    def do_quit(self, arg):
        ' bye, see you later!'

        print "Goodbye! See you soon!"
        sys.exit(0)
        return

    def emptyline(self):
             pass

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(str, arg.split()))


"""

    Run the main cli
"""

import sys
args = sys.argv[1:]

misc.add_sentinel_option("clear_events")
misc.add_sentinel_option("prepare_events")
misc.add_sentinel_option("submit_events")
misc.startup()

if __name__ == '__main__':

    if len(args) > 1:
        if args[0] == "proposal":
            SentinelShell().do_proposal(" ".join(args[1:]))
        elif args[0] == "vote":
            SentinelShell().do_vote(" ".join(args[1:]))
        elif args[0] == "crontab":
            SentinelShell().do_crontab(" ".join(args[1:]))
        elif args[0] == "superblock":
            SentinelShell().do_superblock(" ".join(args[1:]))
    else:
        SentinelShell().cmdloop()

"""
    Test Flow (to be moved into unit tests):

    1.)  create an example proposal
        proposal --create --proposal_name="beer-reimbursement" --description_url="www.dashwhale.org/p/beer-reimbursement" --start_date="2017/1/1" --end_date="2017/6/1"

    2.)  vote on the funding proposal
         vote --times=22 --type=funding --outcome=yes [--hash=governance-hash --name=obj-name]

         

"""
