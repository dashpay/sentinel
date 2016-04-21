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