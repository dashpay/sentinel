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
from models import Proposal
import dashlib

import time
from datetime import datetime

# ---------------------------------------------------------------------

""" SENTINEL AUTOCOMPLETE FOR CLI """

commands = {}

commands["proposal"] = [
    "--name",
    "--url",
    "--start_date",
    "--end_date",
    "--payment_address",
    "--payment_amount",
]

# ---------------------------------------------------------------------

"""
    Sentinel Shell (CLI)
"""

class SentinelShell(cmd.Cmd):
    intro = 'Welcome to the sentinel shell.   Type help or ? to list commands.\n'
    prompt = '(sentinel) '
    file = None

    def do_proposal(self, arg):
        'proposal --name="sb-test" --url="https://www.dashcentral.org/p/sb-test" --start_date=2016-12-01 --end_date=2017-04-01 --payment_address=yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui --payment_amount=23'

        parser = argparse.ArgumentParser(description='Create a dash proposal')

        # meta data
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
        # TODO: remove this and specify the exception type(s) to catch
        except:
            pass

        if not args:
            return

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

        proposal = Proposal(
            name = object_name,
            url = url,
            start_epoch = start_epoch,
            end_epoch = end_epoch,
            payment_address = payment_address,
            payment_amount = payment_amount
        )

        print "Please run these commands from your hot wallet:\n"
        print "To prepare:\n"
        print "\tgobject prepare 0 1 %s %s\n" % (int(time.time()), proposal.dashd_serialise())
        print "To submit:"
        print "(Note: You must paste the TXID value returned from the 'prepare' command):\n"
        print "\tgobject submit 0 1 %s %s <fee-txid-from-prepare>\n" % (int(time.time()), proposal.dashd_serialise())

        return

    # ----- quit the program -----
    def do_quit(self, arg):
        ' bye, see you later!'

        print "Goodbye! See you soon!"
        sys.exit(0)
        return

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(str, arg.split()))
"""
    Run the main cli
"""

import sys
args = sys.argv[1:]

# might just rip this out entirely, as there are no events
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

