#!/usr/bin/env python

"""
Dash-Voter
----

"""

def cmd(exe, params):
    dashcmd = dashd_path + " --datadir=" + datadir
    p = subprocess.Popen(dashcmd + " " + params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
      retcode = p.poll() #returns None while subprocess is running
      line = p.stdout.readline()
      yield line
      if(retcode is not None):
        break


class CTransaction():
    def __init__(self):
        return None

    def load(self, txid):
        return True

    def get_hash(self):
      return None
