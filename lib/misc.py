#!/usr/bin/env python

import json

"""
    take any non-meta attributes and serialize them into a register
"""

def convert_object_to_registers(obj):
    return json.dumps(obj)

def convert_register_to_object(obj):
    return json.loads(obj)

def convert_govobj_name_to_type(govname):
    if govname == "user": return 2

    return -1

def convert_govobj_type_to_name(govtype):
    if govtype == 2: return "user"

    return "error"

## check parameters from the user

def is_valid_address(args):
    try:
        if args.address1 or not args.address2 or not args.city or not args.state or not args.country: 
            return False
    except:
        pass
    return True

def is_valid_first_last_name(args):
    try:
        if args.first_name or not args.last_name: 
            return False
    except:
        pass
    return True