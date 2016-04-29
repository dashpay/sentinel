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
        '   --create --revision=1 --pubkey=XPubkey --username="user-cid" '
        '   --delete --revision=1 --username="user-cid" '
        '   --amend --revision="next" --username="user-cid" --class="employee" --managed_by="user-terra" --project="release-dash-core-12.1x"'
        '   --set-best-revision="newest" --username="user-cid" '

        parser = argparse.ArgumentParser(description='Create a dash evolution user using sentinel.')

        # desired action
        parser.add_argument('-a', '--create', help="create") #
        parser.add_argument('-b', '--delete', help="delete") #
        parser.add_argument('-g', '--amend', help="amend")
        parser.add_argument('-h', '--set-best-revision', help='tell sentinel which revision to prefer')

        # object identity (existentially... what does it mean to be a pubkey?)
        parser.add_argument('-k', '--pubkey', help='your public key for this username (only required for --create)')

        # meta data (create or amend)
        parser.add_argument('-r', '--revision', help="this revision number")
        parser.add_argument('-u', '--username', help='your evolution username')
        parser.add_argument('-c', '--class', help="classes available: none, employee, manager")
        parser.add_argument('-m', '--managed_by', help='Who manages you?')
        parser.add_argument('-p', '--project', help='What project are you working on?')

        # process

        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return

        ### ------ SET BEST REVISION METHOD -------- ####

        if args.set_best_revision:
            print "unimplemented"
            return

        ### ------ CREATE METHOD -------- ####

        if args.create:
            #--create --revision=1 --pubkey=XPubkey --username="user-cid" 
            if args.username:
                print "user creation requires a username"
                return

            print "unimplemented"
            return

        ### ------ DELETE METHOD -------- ####

        if args.delete:
            # --delete --revision=1 --username="user-cid"
            if not args.revision or not args.pubkey or not args.username or not args.pubkey:
                print "user create requires a valid revision, pubkey, username"
                return

            print "unimplemented"
            return

        ### ------ AMEND METHOD -------- ####

        if args.amend:
            #--amend --revision="next" --username="user-cid" --class="employee" 
            if not args.revision or not args.pubkey or not args.username:
                print "user create requires a valid revision, pubkey, username"

            #--managed_by="user-terra" --project="release-dash-core-12.1x"'
            if not args.class or not args.managed_by or not args.project:
                print "user amendment requires a valid reason for the update, either --class or --managed_by or --project "

            print "unimplemented"
            return


    # ----- alter a payday record -----
    def do_payday(self, arg):
        'create a new payday for your dash evolution user'
        ' --create --username="username-cid" --date="2017-01-01" --income="342 DASH" --expenses="523 USD" --signature_one="s1" --signature_two="s2" '

        parser = argparse.ArgumentParser(description='Create a dash evolution payday using sentinel.')

        # desired action
        parser.add_argument('-a', '--create', help="create") #

        # meta data (create or amend)
        parser.add_argument('-u', '--username', help='your evolution username')
        parser.add_argument('-d', '--date', help='The agreed upon expenses for this period')
        parser.add_argument('-i', '--income', help='The agreed upon pay for this period')
        parser.add_argument('-e', '--expenses', help='The agreed upon pay for this period')
        parser.add_argument('-s', '--signature_one', help='Ask primary manager to sign off')
        parser.add_argument('-t', '--signature_two', help='Ask secondary manager to sign off')

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
            # --create --username="username-cid" --date="2017-01-01" --income="342 DASH" --expenses="523 USD" --signature_one="s1" --signature_two="s2" 
            print "unimplemented"
            return


    # ----- alter a project record -----
    def do_project(self, arg):
        'create/amend/delete a project'
        ' project --create --name="release-dash-core-12.1x" --description="devops for 12.1x"'

        parser = argparse.ArgumentParser(description='Create a dash evolution project.')

        # desired action
        parser.add_argument('n', '--new', help="new") #

        # meta data (create or amend)
        parser.add_argument('-c', '--class', help="available classes: software, hardware, legal, etc?")
        parser.add_argument('-e', '--name', help="this project name")
        parser.add_argument('-d', '--description', help="classes available: none, employee, manager")
        
        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        ### ------ NEW METHOD -------- ####

        if args.new:
            if args.name or args.class or args.description:
                print "unimplemented"
                return

    # ----- alter a project record -----
    def do_report(self, arg):
        'create/amend/delete a project'
        ' report --new --project_name --url'

        parser = argparse.ArgumentParser(description='Create a dash evolution user using sentinel.')

        # desired action
        parser.add_argument('-n', '--new', help="make a new report") #

        # meta data (create or amend)
        parser.add_argument('-p', '--project_name', help="this project name")
        parser.add_argument('-u', '--url', help="where is the url for the report?")
        parser.add_argument('-d', '--description', help="the description of what the report is for")


        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        if not misc.is_valid_address(args):    
            print "Correct usage is create username first last address1 address2 city state country"


    # ----- alter a project record -----
    def do_project(self, arg):
        'create/amend/delete a project'
        ' project --create --name="release-dash-core-12.1x" --description="devops for 12.1x"'

        parser = argparse.ArgumentParser(description='Create a dash evolution project.')

        # desired action
        parser.add_argument('n', '--new', help="new") #

        # meta data (create or amend)
        parser.add_argument('-c', '--class', help="available classes: software, hardware, legal, etc?")
        parser.add_argument('-e', '--name', help="this project name")
        parser.add_argument('-d', '--description', help="classes available: none, employee, manager")
        
        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        ### ------ NEW METHOD -------- ####

        if args.new:
            if args.name or args.class or args.description:
                print "unimplemented"
                return

    # ----- use your masternodes to vote yes on an object -----
    def do_support(self, arg):
        ' support --name="release-dash-core-12.1x"'

        parser = argparse.ArgumentParser(description='Create a dash evolution support.')

        # meta data (create or amend)
        parser.add_argument('-e', '--name', help="this support name")
        
        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        ### ------ NAME METHOD -------- ####

        if args.name:
            print "unimplemented"
            return

    # ----- use your masternodes to vote no on an object -----
    def do_abandon(self, arg):
        ' abandon --name="release-dash-core-12.1x"'

        parser = argparse.ArgumentParser(description='Create a dash evolution abandon.')

        # meta data (create or amend)
        parser.add_argument('-e', '--name', help="this support name")
        
        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        ### ------ NAME METHOD -------- ####

        if args.name:
            print "unimplemented"
            return

    # ----- use your masternodes to vote abstain on an object -----
    def do_abstain(self, arg):
        ' abstain --name="release-dash-core-12.1x"'

        parser = argparse.ArgumentParser(description='Create a dash evolution abstain.')

        # meta data (create or amend)
        parser.add_argument('-e', '--name', help="this support name")
        
        args = None
        try:
            args = parser.parse_args(parse(arg))
        except:
            pass

        if not args:
            return
    
        ### ------ NAME METHOD -------- ####

        if args.name:
            print "unimplemented"
            return

    
    # ----- (internal) vote on something -----
    def do___internal_vote(self, arg):
        'Command action on the dash network'
        ' __internal_vote --times=22 --type=funding --outcome=yes [--hash=governance-hash --name=obj-name --pubkey]'

        parser = argparse.ArgumentParser(description='Vote on governance objects and signal what dash should do with them.')

        #voting
        parser.add_argument('-t', '--times')
        parser.add_argument('-p', '--type')
        parser.add_argument('-o', '--outcome')
        parser.add_argument('-h', '--hash')
        parser.add_argument('-n', '--name')
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
    elif args[0] == "payday":
        SentinelShell().do_payday(" ".join(args[1:]))
    else:
        SentinelShell().cmdloop()

"""
    Test Flow (to be moved into unit tests):

    1.)  create our required users
         user --create --revision=1 --pubkey=XPubkey --name="user-terra" 
         user --create --revision=1 --pubkey=XPubkey --name="user-cid"

    2.)  self-promote our people
         user --amend --revision=2 --name="user-terra" --class="manager" --managed_by="user-cyan"
         user --amend --revision=2 --name="user-cid" --class="employee" --managed_by="user-cid"

    3.)  manual masternode action
         # masternodes will vote valid=yes on rev=1 and valid=no on all others
         user --set-best-revision=2 --name="user-terra" 
         user --set-best-revision=2 --name="user-cid" 

    4.) cid & terra privately make a deal for compensation
         payday --name="user-terra" --date="2017-1-1" --income="333 USD" --expense="0 USD" --signature1="HEXSIGNATURE" --signature2="HEXSIGNATURE2"
         payday --name="user-cid" --date="2017-1-1" --income="999 USD" --expense="0 USD" --signature1="HEXSIGNATURE" --signature2="HEXSIGNATURE2"

         # expenses and income are signed off on, the network will automatically switch revisions in this case

    5.) cid & terra privately make a deal for expenses
         payday --name="user-terra" --date="2017-01-15" --income="0 USD" --expense="333 USD" --signature1="HEXSIGNATURE" --signature2="HEXSIGNATURE2"
         payday --name="user-cid" --date="2017-01-15" --income="0 USD" --expense="999 USD" --signature1="HEXSIGNATURE" --signature2="HEXSIGNATURE2"

         

"""