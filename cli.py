#!/usr/bin/env python

# NGM/TODO: extract command-line parsing into a "parser".py script and focus on
# business/dash logic

import pdb
import argparse
import sys
sys.path.append("lib")
sys.path.append("scripts")

import cmd
import misc
import config
import cmd, sys
import random
import json

import peewee
from models import Event, Superblock, Proposal, GovernanceObject
import dashlib

from datetime import datetime, date, time

"""

    Sentinel - v1
    --------------------------------

     - this is an exact copy of our existing functionality, just reimplemented in python using sentinel

    old commands:
        mnbudget prepare beer-reimbursement2 https://www.dashwhale.org/p/beer-reimbursement2 1 481864 XfoGXXFJtobHvjwfszWnbMNZCBAHJWeN6G 50
        mnbudget submit beer-reimbursement2 https://www.dashwhale.org/p/beer-reimbursement2 1 481864 XfoGXXFJtobHvjwfszWnbMNZCBAHJWeN6G 50 REPLACE_WITH_COLLATERAL_HASH

    1. proposal --create --name="beer-reimbursement" --url="https://www.dashwhale.org/p/beer-reimbursement" --start-date="2017-01-01" --end-date="2017-06-01"
    2. cron process (will automatically submit the proposal to the network)

"""

# ---------------------------------------------------------------------

""" SENTINEL AUTOCOMPLETE FOR CLI """

commands = {}

# proposal --create [...]
commands["proposal"] = [
    "--create",
    "--name",
    "--url",
    "--proposal_url",
    "--start_date",
    "--end_date"
]

# superblock --create [...]
commands["superblock"] = [
    "--create",
    "--date",
    "--payments"
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
        'proposal --create --name="sb-test" --url="https://www.dashcentral.org/p/sb-test" --start_date=2016-12-01 --end_date=2017-04-01 --payment_address=yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui --payment_amount=23'

        parser = argparse.ArgumentParser(description='Create a dash proposal')

        # desired action
        parser.add_argument('-c', '--create', help="create", action='store_true')

        # object identity (existentially... what does it mean to be a pubkey?)
        parser.add_argument('-k', '--pubkey', help='your public key for this username (only required for --create)')

        # meta data (create or amend)
        parser.add_argument('-p', '--name', help='the proposal name (must be unique)')
        parser.add_argument('-u', '--url', help='your proposals url where a description of the project can be found')
        parser.add_argument('-s', '--start_date', help='start date, ISO8601 format. Must be the first of the month. Example : 2017-01-01')
        parser.add_argument('-e', '--end_date', help='end date, ISO8601 format. Must be the first of the month. Example : 2017-06-01')
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
            if not args.name:
                print "proposal creation requires a proposal name, use --name"
                return

            if not args.url:
                print "proposal creation requires a description url, use --url"
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

            # check valid payment address
            if not dashlib.is_valid_dash_address( args.payment_address, config.network ):
                print "%s is not a valid %s payment address" % (args.payment_address, config.network)
                return

            # sentinel values...
            start_epoch = 0
            end_epoch   = 0

            # using standard ISO8601 date format to prevent ambiguity
            # also: https://xkcd.com/1179/
            start_epoch = datetime.strptime(args.start_date, '%Y-%m-%d').strftime('%s')
            end_epoch   = datetime.strptime(args.end_date  , '%Y-%m-%d').strftime('%s')

            if start_epoch == 0 or end_epoch == 0:
                print "start or end date has invalid format, ISO8601 date format (YYYY-MM-DD) required";
                return

            # == ngm /parser logic, begin Dash logic
            #
            # == so, really don't like to see 'args' below this line... will
            # try and extract, isolate the inputs and not mix with this
            # creation logic (e.g. 'dependency injection' i believe this is
            # called)
            #
            object_name = args.name

            # unique to proposal
            url = args.url
            payment_address = args.payment_address
            payment_amount = args.payment_amount

            # TODO: remove check here (and redundancy), check elsewhere
            ### ---- CHECK NAME UNIQUENESS -----
            if GovernanceObject.object_with_name_exists(object_name):
                print "governance object with that name already exists"
                return

            proposal = Proposal(
                name = object_name,
                url = url,
                start_epoch = start_epoch,
                end_epoch = end_epoch,
                payment_address = payment_address,
                payment_amount = payment_amount
            )

            try:
                proposal.create_and_queue()
                print "event queued successfully"
            except peewee.PeeweeException as e:
                # will auto-rollback as a result of atomic()...
                print "error: %s" % e[1]

            return

        ### ------- ELSE PRINT HELP --------------- ###

        parser.print_help()

        ### ------ CREATE METHOD -------- ####



    """
        Superblock
    """
    def do_superblock(self, arg):
        'superblock --create --event_block_height="28224" --payments="yLipDagwb1gM15RaUq3hpcaTxzDsFsSy9a=100"'
        'superblock --create --event_date="2017-01-01" --payments="Addr1=amount,Addr2=amount,Addr3=amount"'

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

            # NGM/TODO: use event block height
            superblock_name = "sb" + str(random.randint(1000000, 9999999))

            # NGM: might be easier to perform sanitization further up and
            # separate from the actual logic...
            event_block_height = misc.normalize(args.event_block_height)
            object_name  = superblock_name

            # DOES THIS ALREADY EXIST?
            if GovernanceObject.object_with_name_exists(object_name):
                print "governance object with that name already exists"
                return

            superblock = Superblock(
                name = object_name,
                event_block_height = event_block_height,
                payment_addresses = ("|".join(list_addr)),
                payment_amounts = ("|".join(list_amount))
            )

            # create_and_queue
            # atomic write for all 3 objects, alles oder nichts
            try:
                superblock.create_and_queue()
            except PeeweeException as e:
                # will auto-rollback as a result of atomic()...
                print "error: %s" % e[1]

            print "event queued successfully"

            return

        ### ------- ELSE PRINT HELP --------------- ###

        parser.print_help()

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
        command = args[0]
        subcmd_args = " ".join(args[1:])

        try:
            getattr( SentinelShell(), "do_" + command )(subcmd_args)
        except AttributeError as e:
            print "command '%s' not implemented" % command
    else:
        SentinelShell().cmdloop()


"""
    Test Flow (to be moved into unit tests):

    1.)  create an example proposal
        proposal --create --name="beer-reimbursement" --url="https://www.dashwhale.org/p/beer-reimbursement" --start_date="2017-01-01" --end_date="2017-06-01"

    2.)  vote on the funding proposal
         vote --times=22 --type=funding --outcome=yes [--hash=governance-hash --name=obj-name]

"""
