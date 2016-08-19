#!/usr/bin/env python

import json
import calendar
import time
import re
import datetime
import random
from time import sleep

"""
    take any non-meta attributes and serialize them into a register
"""

sentinel_options = []

def first_day_of_next_month():
    d = datetime.datetime.now() #todays date
    d + datetime.timedelta(days=29) #add 29 days
    return date(d.year, d.month, 1) #get first of month

def clean_hash(s):
    m = re.match('^([a-f0-9]+)$', s)
    if m: return m.group(1)
    return None

def is_hash(s):
    m = re.match('^([a-f0-9]+)$', s)
    if m: return True
    return False

def normalize(s):
    # args passes in enclosing quotations 
    return s.replace("'", "").replace("\"", "")

def get_epoch():
    return calendar.timegm(time.gmtime())

def add_sentinel_option(param):
    sentinel_options.append(param)

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

def completer(text, state):
    options = [i for i in commands if i.startswith(text)]
    options.extend(sentinel_options)

    if state < len(options):
        return options[state]
    else:
        return None

def startup():
    # python startup file 
    import readline 
    import rlcompleter 
    import atexit 
    import os 

    # tab completion 
    readline.parse_and_bind('tab: complete') 
    readline.set_completer(completer)

    # do not use - as delimiter
    old_delims = readline.get_completer_delims() # <-
    readline.set_completer_delims(old_delims.replace('-', '')) # <-

    # history file 
    histfile = os.path.join(os.environ['HOME'], '.pythonhistory') 
    try: 
        readline.read_history_file(histfile) 
    except IOError: 
        pass 
    atexit.register(readline.write_history_file, histfile) 
    del os, histfile, readline, rlcompleter

    import readline