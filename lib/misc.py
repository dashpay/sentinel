#!/usr/bin/env python

"""
    take any non-meta attributes and serialize them into a register
"""

def convert_object_to_registers(obj):
    return dumps(obj)

def convert_register_to_object(obj):
    return loads(obj)
