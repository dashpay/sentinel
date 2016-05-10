#!/usr/bin/env python

"""
Dashd interface
----

"""

import os
import config
import subprocess

def rpc_command(params):
    dashcmd = config.dashd_path + " --datadir=" + config.datadir
    
    #print "'%s' '%s'" % (dashcmd, params)

    proc = subprocess.Popen(dashcmd + " " + params, shell=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ""
    while (True):
        # Read line from stdout, break if EOF reached, append line to output
        line = proc.stdout.readline()
        line = line.decode()
        if (line == ""): break
        output += line

    return output

class CTransaction():
    def __init__(self):
        return None

    def load(self, txid):
        return True

    def get_hash(self):
      return None
