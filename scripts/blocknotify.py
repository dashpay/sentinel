#!/usr/bin/env python

import json
from dashd import DashDaemon
from dashd import DashConfig

import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

from governance  import GovernanceObject

"""
    - this script is ran ~2.5/minutes and processes updates to the governance system

"""

dashd = DashDaemon.from_dash_conf(config.dash_conf)

difflist = json.loads(dashd.rpc_command('gobject', 'diff'))
# this currently isn't being used anyway
# for item in difflist:
    # NGM: TODO: ensure proper loading of these (need to test gobject diff output)
	# obj = GovernanceObject(item)
	# obj.save()
    #
	# if obj.is_valid():
	# 	obj.vote(VOTE_ACTION_VALID, VOTE_OUTCOME_NO)
pass
