import time
import re
import datetime

"""
    take any non-meta attributes and serialize them into a register
"""

sentinel_options = []

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
    return int(time.time())

def add_sentinel_option(param):
    sentinel_options.append(param)

## check parameters from the user

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

class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
