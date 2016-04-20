#!/usr/bin/env python

import calendar
import time

class GovernanceObject:
    # all arguments for this object
    obj = {}

    # convert to governance object
    govobj_type = 0
    hash_parent = ""
    priority = 0
    revision = 0
    time = 0
    name = ""
    start_time = 0
    end_time = 0

    # register data for specific classes
    registers = []

    def __init__(self, args):
        hash_parent = 

        # load object up
        for i in arg:
            obj[i] = arg[i]

        self.hash_parent = 0 #place under root
    
        if args.type in ['contract', "proposal"]:
            self.priority = args.priority

        self.govobj_type = convert_govobj_name_to_type(arg.govobj_type)
        self.revision = args.revision
        self.time = calendar.timegm(time.gmtime())
        self.start_time = calendar.timegm(time.strptime(args.start_date, '%Y-%m-%d'))
        self.end_time = calendar.timegm(time.strptime(args.end_date, '%Y-%m-%d'))

        if arg.govobj_type == "user":
            self.registers[0] = convert_object_to_registers({
                'first_name' : arg.first_name, 
                'last_name' : arg.last_name, 
                'address1' : arg.address1, 
                'address2' : arg.address2, 
                'city' : arg.city,
                'state' : arg.state,
                'country' : arg.country
            })

        if arg.govobj_type == "group":
            pass #groups have no register data (for now)

        if arg.govobj_type == "company":
            self.registers[0] = convert_object_to_registers({
                'first_name' : arg.first_name, 
                'last_name' : arg.last_name, 
                'address1' : arg.address1, 
                'address2' : arg.address2, 
                'city' : arg.city,
                'state' : arg.state,
                'country' : arg.country
            })

        if arg.govobj_type == "proposal":
            self.registers[0] = convert_object_to_registers({
                'monthly_dash_amount' : arg.monthly_dash_amount, 
                'to_pubkey' : arg.to_pubkey
            })

        if arg.govobj_type == "contract":
            self.registers[0] = convert_object_to_registers({
                'monthly_dash_amount' : arg.monthly_dash_amount, 
                'to_pubkey' : arg.to_pubkey
            })

    def is_valid():
        pass

        """
            - check tree position validity
            - check signatures of owners 
            - check validity of revision (must be n+1)
            - check validity of field data (address format, etc)
        """

    def save():
        pass

        """
            -- save objects in relational form (user, groups, etc)
            -- add new "event" to be processed by scripts/events.py
        """

    def load_vote_data():
        pass

    def get_dashd_command(prepare_or_submit, hashtx):
        if not prepare_or_submit in ["prepare", "submit"]: return False
        return "mngovernance " + prepare_or_submit
        # mngovernance prepare <proposal-name> <url> <payment-count> <block-start> <dash-address> <monthly-payment-dash>'");
