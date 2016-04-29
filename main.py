#!/usr/bin/env python

import argparse
import sys
sys.path.append("lib")
sys.path.append("scripts") 

from governance  import GovernanceObject
import misc
import mysql
import config
import events

db = mysql.connect(config.hostname, config.username, config.password, config.database)

if __name__ == '__main__':

    """
        # How to create sib on the network
        --create="user" --name="user-sib-2016" --revision=1 --subclass="employee" --dash_monthly=233.32 --first_name="sib" --last_name="duffield"
        --address1="123 w. main ave" --address2="#123" --city="Phoenix" --state="Arizona" --country="US"

        # we'll get a hash
        >> new object hash

        # These are only valid, if the network thinks they're valid (cast 22 votes randomly over hours)
        --vote-times=22 --vote-type="funding" --vote-outcome="yes"

    """

    parser = argparse.ArgumentParser()

    """
        vote(times=22, action="funding", outcome="yes", on="governance-hash")
        
    """

    #ownership
    parser.add_argument('-y', '--pubkey')
    parser.add_argument('-k', '--events_process')
    parser.add_argument('-l', '--events_clear')

    #voting
    parser.add_argument('-u', '--vote_times')
    parser.add_argument('-w', '--vote_type')
    parser.add_argument('-x', '--vote_outcome')
    parser.add_argument('-t', '--vote_on')

    #governance objects
    parser.add_argument('-n', '--create') #
    parser.add_argument('-n', '--delete') #
    parser.add_argument('-o', '--amend')
    parser.add_argument('-p', '--revision')
    parser.add_argument('-q', '--dash_monthly')
    parser.add_argument('-m', '--subclass')

    parser.add_argument('-a', '--name')
    parser.add_argument('-b', '--first_name')
    parser.add_argument('-c', '--last_name')

    parser.add_argument('-e', '--address1')
    parser.add_argument('-f', '--address2')
    parser.add_argument('-g', '--city') #h
    parser.add_argument('-i', '--state')
    parser.add_argument('-j', '--country')


    parser.add_argument('-v', dest='verbose', action='store_true')
    args = parser.parse_args()

## figure out what to do ##

if not args.vote_times and not args.create and not args.amend and not args.events_process:
    print "Would you like to vote(--vote-times), create(--create) or amend(--amend) a record?"


if args.vote_times:
    if not args.vote_type and not args.vote_outcome and not args.vote_on:
        print """

        What would you like to vote on? 

            --vote-type=(funding|valid|delete|clear_registers|endorsed) 
            --vote_outcome=(yes|no|abstain)"
            --vote_on=(target_object_name)

        example: 

            vote_times=22 --vote-type=funding --vote-outcome=yes --vote-name="eduffield-2016"

        """

if args.create or args.amend:
    if not args.name or not args.subclass or not args.dash_monthly or not args.first_name or not args.last_name or \
        not args.address1 or not args.address2 or not args.city or not args.state or not args.country: 
        print """

        What type of record would you like to create or amend?

        --create=(user|relationship|expense)
        --subclass=
                user: employee|employer|evo
                relationship: 
                relationship|expense)
        --amend(user|employee|employer|expense)
        --dash_monthly=0 (only employees can do this)
        --first_name="First"
        --last_name="Last"
        --address1="Pobox 123"
        --address2=""
        --city="Phoenix"
        --state="Arizona"
        --country="USA"

        """
    
    if args.create: args.__dict__["govobj_type"] = args.create
    if args.amend: args.__dict__["govobj_type"] = args.amend

    obj = GovernanceObject()
    obj.load_from_args(args)

    if not obj.is_valid():
        print "obj is not valid"

    obj.save()

if args.events_process:
    print """Processing queued events"""
    events.prepare()
    #events.submit()

if args.events_clear:
    print """Clearing queued events"""
    events.clear()
