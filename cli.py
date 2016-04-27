#!/usr/bin/env python

import argparse
import sys
sys.path.append("lib")
sys.path.append("scripts") 

from govobj import GovernanceObject
import misc
import mysql
import config
import events
import cmd, sys

db = mysql.connect(config.hostname, config.username, config.password, config.database)

class SentinelShell(cmd.Cmd):
    intro = 'Welcome to the sentinel shell.   Type help or ? to list commands.\n'
    prompt = '(sentinel) '
    file = None

    # ----- alter a user record -----
    def do_user(self, arg):
        'create a new governance object'
        ' user [--create --delete --amend] '
        '    --revision=2 --pubkey=XPubkey --name="cid" '
        '    --first_name --last_name --address1 --address2 --city --state --country '

        parser = argparse.ArgumentParser(description='Create a dash evolution user using sentinel.')

        # governance objects
        parser.add_argument('-k', '--create', help="create") #
        parser.add_argument('-l', '--delete', help="delete") #
        parser.add_argument('-o', '--amend', help="amend")
        parser.add_argument('-p', '--revision', help="revision")
        parser.add_argument('-m', '--subclass', help="subclass")
        parser.add_argument('-s', '--set-best-revision', help='set best revision')

        # identity
        parser.add_argument('-y', '--pubkey', help='pubkey')

        # meta data
        parser.add_argument('-a', '--name', help='name')
        parser.add_argument('-b', '--first_name', help='first_name')
        parser.add_argument('-c', '--last_name', help='last_name')

        parser.add_argument('-e', '--address1', help='address1')
        parser.add_argument('-f', '--address2', help='address2')
        parser.add_argument('-g', '--city', help='city') #h
        parser.add_argument('-i', '--state', help='state')
        parser.add_argument('-j', '--country', help='country')

        # process

        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return

        ## creation requires a valid name, address, pubkey, etc
        if not args.create:    
            if not 'username' in args.__dict__:
                print "user creation requires --username"

            if not misc.is_name_valid(args):    
                print "user create requires a valid name --first_name and --last_name"

            if not misc.is_valid_address(args):    
                print "user create requires a valid name --address1 --address2 --city --state --country"

    # ----- alter a party -----
    def do_party(self, arg):
        'create/amend/delete a party'
        ' party [--create --delete --amend] --name="dragon" --primary-manager="terra=100" --secondary-manager="cyan:50" --primary-employee="cid:300"'

        parser = argparse.ArgumentParser(description='Create a new party and do cool stuff.')

        # generice governance object instruction
        parser.add_argument('-j', '--create', help="create") #
        parser.add_argument('-k', '--delete', help="delete") #
        parser.add_argument('-l', '--amend', help="amend")
        parser.add_argument('-m', '--revision', help="revision")
        parser.add_argument('-n', '--name', help="name")

        #party instructions
        parser.add_argument('-q', '--manager1')
        parser.add_argument('-r', '--manager2')
        parser.add_argument('-s', '--employee1')
        parser.add_argument('-t', '--employee2')
        parser.add_argument('-u', '--employee3')
        parser.add_argument('-v', '--employee4')
        parser.add_argument('-w', '--employee5')

    # ----- alter a project -----
    def do_project(self, arg):
        'create/amend/delete a project'
        ' project --(create|delete|amend) --name --revision --bounty1 --bounty2 --bounty3 --pubkey'
        ' project --assign-party=name'
        ' project --release-bounty=1 to 3'

        parser = argparse.ArgumentParser(description='Create a dash evolution user using sentinel.')

        # generice governance object instruction
        parser.add_argument('-j', '--create', help="create") #
        parser.add_argument('-k', '--delete', help="delete") #
        parser.add_argument('-l', '--amend', help="amend")
        parser.add_argument('-m', '--revision', help="revision")

        # bounties
        parser.add_argument('-b', '--bounty1', help="set-bounty-1")
        parser.add_argument('-c', '--bounty2', help="set-bounty-2")
        parser.add_argument('-d', '--bounty3', help="set-bounty-3")
        parser.add_argument('-e', '--release-bounty', help="release bounty 1, 2 or 3")

        # party
        parser.add_argument('-p', '--assign-party', help="assign a party to this project")

        # process arg

        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        if not misc.is_valid_address(args):    
            print "Correct usage is create username first last address1 address2 city state country"

    # ----- alter a expense -----
    def do_expense(self, arg):
        'create a new governance object'
        '  expense --project_name=2017-promotion --user_name=cid --amount='

        parser = argparse.ArgumentParser(description='Create a dash evolution user using sentinel.')

        # governance objects
        parser.add_argument('-n', '--project_name', help="project_name")
        parser.add_argument('-u', '--username', help="username")
        parser.add_argument('-a', '--amount', help="amount") 

        # process arg

        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return

        " this is an expense. Each has a project and an employee. If the user is the project mananger we'll submit it as a bid, otherwise it's an ask "
        "   -- the matching engine will pay when specific criterion are met"

        # process
    
    # ----- vote on something -----
    def do_vote(self, arg):
        'Command action on the dash network'
        ' vote --times=22 --type=funding --outcome=yes [--hash=governance-hash --name=obj-name --pubkey]'

        parser = argparse.ArgumentParser(description='Vote on governance objects and signal what dash should do with them.')

        #voting
        parser.add_argument('-t', '--times')
        parser.add_argument('-p', '--type')
        parser.add_argument('-o', '--outcome')
        parser.add_argument('-h', '--hash')
        parser.add_argument('-n', '--name')
        parser.add_argument('-k', '--pubkey')

    # ----- (internally used) make a new payment from the dash blockchain -----
    def do_payment(self, arg):
        'Do a payment'

        parser = argparse.ArgumentParser(description='Vote on governance objects and signal what dash should do with them.')

        #voting
        parser.add_argument('-t', '--type')
        parser.add_argument('-p', '--parent_id')
        parser.add_argument('-s', '--start_time')
        parser.add_argument('-a', '--amount')
        parser.add_argument('-k', '--pubkey')

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(str, arg.split()))

import sys
args = sys.argv[1:]

if __name__ == '__main__':

    if args[0] == "user":
        SentinelShell().do_user(" ".join(args[1:]))
    elif args[0] == "project":
        SentinelShell().do_project(" ".join(args[1:]))
    elif args[0] == "vote":
        SentinelShell().do_vote(" ".join(args[1:]))
    elif args[0] == "expense":
        SentinelShell().do_expense(" ".join(args[1:]))
    elif args[0] == "payment":
        SentinelShell().do_payment(" ".join(args[1:]))
    elif args[0] == "party":
        SentinelShell().do_party(" ".join(args[1:]))
    else:
        SentinelShell().cmdloop()

"""
    Test Flow (to be moved into unit tests):

    1.)  create our required users
         user --create --revision=1 --pubkey=XPubkey --name="user-terra" --first_name="terra" --last_name="" --address1="Pobox 456" --address2="" --city="Miami" --state="FL" --country="USA"
         user --create --revision=1 --pubkey=XPubkey --name="user-cyan" --first_name="cyan" --last_name="" --address1="Pobox 222" --address2="" --city="New York" --state="NY" --country="USA"
         user --create --revision=1 --pubkey=XPubkey --name="user-cid" --first_name="cid" --last_name="" --address1="Pobox 123" --address2="" --city="Phoenix" --state="AZ" --country="USA"
         user --create --revision=1 --pubkey=XPubkey --name="user-locke" --first_name="locke" --last_name="" --address1="Pobox 789" --address2="" --city="Portland" --state="OR" --country="USA"

    2.)  self-promote our people
         user --amend --revision=2 --name="user-terra" --subclass="manager"
         user --amend --revision=2 --name="user-cyan" --subclass="manager"
         user --amend --revision=2 --name="user-cid" --subclass="employee"
         user --amend --revision=2 --name="user-locke" --subclass="employee"

    3.)  manual masternode action
         # masternodes will vote valid=yes on rev=1 and valid=no on all others
         user --set-best-revision=2 --name="user-terra" 
         user --set-best-revision=2 --name="user-cyan" 
         user --set-best-revision=2 --name="user-cid" 
         user --set-best-revision=2 --name="user-locke"

    4.)  Rejoice! We have setup some simple records, now we need to create the party.

    5.)  create a party, which is a small group of people which work on projects
         party --create --revision=1 --name="dragon" --manager1="terra:100" --manager2="cyan:50 DASH" --employee1="cid:300 DASH" #terra signs
         party --create --revision=1 --name="dragon" --manager1="terra:100" --manager2="cyan:50 DASH" --employee1="cid:300 DASH" #cyan signs
         party --create --revision=1 --name="dragon" --manager1="terra:100" --manager2="cyan:50 DASH" --employee1="cid:300 DASH" #cid signs

    6.)  Someone creates a project
         project --create --name="dash-con" --bounty1="100 DASH"

    7.)  Network assigns a project to a party (best revision)
         project --assign-party="dragon" --name="dash-con"

    8.)  Request an expense get paid for 256
         expense --project-name="dash-con" --amount="256 DASH" #cid
         expense --project-name="dash-con" --amount="256 DASH" #terra
         expense --project-name="dash-con" --amount="256 DASH" #cyan

    9.)  Release project bounty
         project --name="dash-coin" --release-bounty==1 #terra
         project --name="dash-coin" --release-bounty==1 #cyan

"""